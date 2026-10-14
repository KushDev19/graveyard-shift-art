"""Shared helpers for job J: segment objects from the painting, vectorize, verify."""
import io, re, pathlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import vtracer, cairosvg

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parents[1]
K = 5504 / 2000  # ref (2000 px) -> source scale

def load(src):
    return np.asarray(Image.open(ROOT / 'raw_originals' / src).convert('RGB'))

def sc(pts):
    return [(round(x * K), round(y * K)) for x, y in pts]

def box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def poly_mask(shape, pts):
    im = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon(pts, fill=1)
    return np.asarray(im).astype(bool)

def outline_mask(img):
    a = img.astype(int)
    s = a.sum(2)
    m = (s < 240) & (a[..., 0] - a[..., 1] > 10)
    L = a.mean(2)
    th = ndi.grey_closing(L, size=(21, 21)) - L
    m |= (th > 22) | ((L < 70) & (a[..., 0] - a[..., 1] > 10))
    return ndi.binary_closing(m, iterations=2)

def object_mask(img, outl, region, taken, keep_frac=0.02, near=16, add=None, wall_tol=0):
    ys, xs = np.nonzero(region)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    R = region[y0:y1, x0:x1]
    O = outl[y0:y1, x0:x1]
    no = ~O & R
    lab, n = ndi.label(no)
    ring = R & ~ndi.binary_erosion(R, iterations=3, border_value=0)
    bg = np.unique(lab[ring])
    obj = (lab > 0) & ~np.isin(lab, bg)
    if wall_tol:
        # enclosed pockets that look like the nearby wall (e.g. inside hanger strings) stay in the shell
        C = img[y0:y1, x0:x1].astype(float)
        bgm = np.isin(lab, bg) & (lab > 0)
        for i in np.unique(lab[obj]):
            sel = lab == i
            if sel.sum() < 150: continue
            ys_, xs_ = np.nonzero(sel)
            sl = (slice(max(ys_.min() - 40, 0), ys_.max() + 41), slice(max(xs_.min() - 40, 0), xs_.max() + 41))
            ss = sel[sl]; Cs = C[sl]
            near_bg = ndi.binary_dilation(ss, structure=np.ones((1, 3), bool), iterations=60) & bgm[sl]
            diffs, wts = [], []
            for r in range(ss.shape[0]):
                if ss[r].any() and near_bg[r].sum() >= 4:
                    diffs.append(np.abs(Cs[r][ss[r]].mean(0) - Cs[r][near_bg[r]].mean(0)).max()); wts.append(ss[r].sum())
            if wts and np.average(diffs, weights=wts) < wall_tol:
                obj &= ~sel
    d = ndi.distance_transform_edt(~obj)
    m = obj | (O & R & (d <= near))
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=2)) & R
    lab2, n2 = ndi.label(m)
    if n2 > 1:
        sizes = ndi.sum(m, lab2, range(1, n2 + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s >= keep_frac * sizes.max()]
        m = np.isin(lab2, keep)
    full = np.zeros(region.shape, bool)
    full[y0:y1, x0:x1] = m
    return full & ~taken

VT = dict(colormode='color', hierarchical='stacked', mode='spline', filter_speckle=6,
          color_precision=6, layer_difference=14, corner_threshold=60, length_threshold=4.0,
          max_iterations=10, splice_threshold=45, path_precision=1)

def trace(rgba, scale=1, **kw):
    """Vectorize an RGBA array; returns list of path strings in its own pixel space * scale."""
    p = dict(VT); p.update(kw)
    im = Image.fromarray(rgba)
    if scale != 1:
        im = im.resize((round(im.width / scale), round(im.height / scale)), Image.LANCZOS)
        a = np.asarray(im).copy(); a[..., 3] = np.where(a[..., 3] > 127, 255, 0); im = Image.fromarray(a)
    b = io.BytesIO(); im.save(b, 'PNG')
    svg = vtracer.convert_raw_image_to_svg(b.getvalue(), img_format='png', **p)
    paths = re.findall(r'<path[^>]*/>', svg)
    if scale != 1:
        return [f'<g transform="scale({scale})">'] + paths + ['</g>']
    return paths

def svg_doc(w, h, body, gid=None, extra=''):
    inner = '\n'.join(body)
    if gid:
        inner = f'<g id="{gid}"{extra}>\n{inner}\n</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'{inner}\n</svg>\n')

def render(svg_path, w=None, h=None):
    b = cairosvg.svg2png(url=str(svg_path), output_width=w, output_height=h)
    return np.asarray(Image.open(io.BytesIO(b)).convert('RGBA'))

def over(base, rgba, x, y):
    out = base.astype(float).copy()
    h, w = rgba.shape[:2]
    a = rgba[..., 3:4] / 255.0
    out[y:y + h, x:x + w] = rgba[..., :3] * a + out[y:y + h, x:x + w] * (1 - a)
    return out

def mae4(a, b, mask=None):
    """Mean abs error (0-255) on a 4x box downscale, optionally restricted to mask."""
    def ds(x):
        h, w = x.shape[0] // 4 * 4, x.shape[1] // 4 * 4
        x = x[:h, :w].astype(float)
        return x.reshape(h // 4, 4, w // 4, 4, -1).mean((1, 3))
    d = np.abs(ds(a) - ds(b)).mean(-1)
    if mask is None:
        return float(d.mean())
    m = ds(mask[..., None].astype(float))[..., 0] > 0.5
    return float(d[m].mean())
