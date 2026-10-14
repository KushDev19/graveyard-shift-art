"""Trace raster pieces with vtracer, assemble named-layer SVGs, render with cairosvg."""
import io, re, numpy as np, cv2, vtracer, cairosvg
from PIL import Image

PATH_RE = re.compile(r'<path d="([^"]+)" fill="(#[0-9A-Fa-f]{6})" transform="translate\(([-\d.]+),([-\d.]+)\)"/>')


def trace(rgb, mask, speckle=4, prefilter=True, layer_diff=16, color_prec=6):
    """rgb HxWx3 uint8, mask HxW bool -> list of (d, fill) in local pixel units."""
    if prefilter:
        rgb = cv2.bilateralFilter(np.ascontiguousarray(rgb), 7, 30, 7)
    a = np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)])
    a[~mask, :3] = 0
    h, w = mask.shape
    svg = vtracer.convert_pixels_to_svg([tuple(p) for p in a.reshape(-1, 4)], size=(w, h), colormode='color',
                                        hierarchical='stacked', mode='spline', filter_speckle=speckle,
                                        color_precision=color_prec, layer_difference=layer_diff, corner_threshold=60,
                                        length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=1)
    out = []
    for d, fill, tx, ty in PATH_RE.findall(svg):
        tx, ty = float(tx), float(ty)
        out.append((_shift(d, tx, ty), fill.upper()))
    return out


def _shift(d, tx, ty):
    """Bake translate(tx,ty) into absolute path coords (vtracer emits only absolute M/C/L/Z)."""
    toks = re.findall(r'[MCLZ]|-?\d+(?:\.\d+)?(?:e-?\d+)?', d)
    res, i, isx = [], 0, True
    for t in toks:
        if t in 'MCLZ':
            res.append(t); isx = True
        else:
            v = float(t) + (tx if isx else ty)
            isx = not isx
            res.append(('%.1f' % v).rstrip('0').rstrip('.'))
    return ' '.join(res).replace(' Z', 'Z')


def group(gid, paths, transform=None, extra=''):
    t = f' transform="{transform}"' if transform else ''
    body = ''.join(f'<path d="{d}" fill="{f}"/>' for d, f in paths)
    return f'<g id="{gid}"{t}{extra}>{body}</g>'


def doc(w, h, body, title='', defs=''):
    d = f'<defs>{defs}</defs>' if defs else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>{title}</title>{d}{body}</svg>\n')


def render(svg_text, width):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=int(width))
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))


def trace_quant(rgb, mask, n=48, speckle=30, median=3):
    """For large smooth areas (room shells): posterise first so vtracer keeps soft gradients as bands."""
    from PIL import Image
    q = kmeans_quant(cv2.bilateralFilter(np.ascontiguousarray(rgb), 9, 25, 9), mask, n)
    q = cv2.medianBlur(q, median)
    return trace(q, mask, speckle=speckle, prefilter=False, layer_diff=4)


def kmeans_quant(rgb, mask, n):
    """Perceptual (Lab) k-means palette so small saturated areas (hazard orange) keep their own colour."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    idx = np.flatnonzero(mask.reshape(-1))
    rng = np.random.default_rng(0)
    smp = lab[rng.choice(idx, min(len(idx), 150000), replace=False)]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    cv2.setRNGSeed(1)
    _, _, cen = cv2.kmeans(smp, n, None, crit, 2, cv2.KMEANS_PP_CENTERS)
    out = np.empty(len(lab), np.int32)
    for i in range(0, len(lab), 400000):
        d = ((lab[i:i + 400000, None, :] - cen[None]) ** 2).sum(2)
        out[i:i + 400000] = d.argmin(1)
    q = cen[out].reshape(rgb.shape).astype(np.uint8)
    return cv2.cvtColor(q, cv2.COLOR_LAB2RGB)
