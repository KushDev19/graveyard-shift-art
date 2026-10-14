"""Shared helpers for Job G: segment painted rooms into objects, repaint the shell, trace to SVG, verify.

Coordinates in the room configs are given in quarter scale (the 1376 px grid used while planning)
and multiplied by 4 into source pixels (5504 x 3072)."""
import io
import json
import pathlib
import re

import cairosvg
import numpy as np
import vtracer
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parents[1]
Q = 4  # quarter-scale grid -> source px

TRACE = dict(colormode="color", hierarchical="stacked", mode="spline", filter_speckle=4,
             color_precision=7, layer_difference=10, corner_threshold=60, length_threshold=4.0,
             splice_threshold=45, path_precision=1)


def load(name):
    return np.array(Image.open(ROOT / "raw_originals" / name).convert("RGB"))


def poly_mask(shape, poly, scale=Q):
    m = Image.new("L", (shape[1], shape[0]), 0)
    pts = [(x * scale, y * scale) for x, y in poly]
    if len(pts) == 2:  # rectangle given as two corners
        ImageDraw.Draw(m).rectangle(pts, fill=255)
    else:
        ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0


def outline_map(win, barrier_t=55, bh_t=50, k=31):
    """Dark plum outlines: absolutely dark green channel, or much darker than the local surroundings
    (black-hat), which also catches outlines brightened by painted lamp light."""
    import cv2
    g = win[..., 1]
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    return (g < barrier_t) | (bh > bh_t)


def segment(img, poly, claimed, barrier_t=55, mode="flood", core=0, grow=2, keep_largest=False, add=None, open_r=7):
    """Object mask = pixels inside `poly` not reachable from the polygon rim without crossing a dark
    plum outline (green channel < barrier_t). Works in the polygon's window for speed."""
    full = poly_mask(img.shape, poly)
    ys, xs = np.where(full)
    y0, y1, x0, x1 = max(ys.min() - 4, 0), ys.max() + 5, max(xs.min() - 4, 0), xs.max() + 5
    pm = full[y0:y1, x0:x1] & ~claimed[y0:y1, x0:x1]
    out = np.zeros(img.shape[:2], bool)
    if mode == "poly":
        out[y0:y1, x0:x1] = pm
        return out
    barrier = outline_map(img[y0:y1, x0:x1], barrier_t)
    free = pm & ~barrier
    lab, n = ndi.label(free)
    rim = pm & ~ndi.binary_erosion(pm, iterations=2)
    bg_ids = np.unique(lab[rim & free])
    bg = np.isin(lab, bg_ids[bg_ids > 0])
    obj = pm & ~bg
    obj = ndi.binary_fill_holes(obj) & pm
    obj = ndi.binary_opening(obj, iterations=2)
    lab, n = ndi.label(obj)
    if n:
        sizes = ndi.sum(obj, lab, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if (s == sizes.max() if keep_largest else s > 400)]
        obj = np.isin(lab, keep)
    if core:
        obj |= ndi.binary_erosion(pm, iterations=core)
    if open_r:  # trim thin wall/seam lines glued to the outline, then restore the outline itself
        import cv2
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * open_r + 1, 2 * open_r + 1))
        op = cv2.morphologyEx(obj.astype(np.uint8), cv2.MORPH_OPEN, k) > 0
        obj &= ndi.binary_dilation(op, iterations=open_r + 1)
    for a in add or []:
        obj |= poly_mask(img.shape, a)[y0:y1, x0:x1] & pm
    if grow:
        obj = ndi.binary_dilation(obj, iterations=grow) & pm
    out[y0:y1, x0:x1] = obj
    return out


def directional_fill(img, hole, direction="h", known=None, side="both"):
    """Repaint `hole` pixels by blending the nearest known pixels left/right (h) or along a slanted
    direction (dx per dy). Good for walls whose stripes run horizontally and for floor rows."""
    out = img.astype(np.float32).copy()
    known = ~hole if known is None else known
    H, W = hole.shape
    if direction == "h":
        rows = np.where(hole.any(1))[0]
        for y in rows:
            k = known[y]
            if not k.any():
                continue
            xs = np.arange(W)
            kx = xs[k]
            li = np.searchsorted(kx, xs, side="right") - 1
            ri = np.clip(li + 1, 0, len(kx) - 1)
            li = np.clip(li, 0, len(kx) - 1)
            lx, rx = kx[li], kx[ri]
            dl = np.abs(xs - lx).astype(np.float32) + 1
            dr = np.abs(rx - xs).astype(np.float32) + 1
            # sample a few px away from the edge to skip anti-aliased outline remains
            lxs = np.clip(lx - 12, 0, W - 1)
            rxs = np.clip(rx + 12, 0, W - 1)
            lxs = np.where(known[y, lxs], lxs, lx)
            rxs = np.where(known[y, rxs], rxs, rx)
            wl = dr / (dl + dr)
            if side == "left":
                wl = np.where(lx < xs, 1.0, 0.0).astype(np.float32)
            elif side == "right":
                wl = np.where(rx > xs, 0.0, 1.0).astype(np.float32)
            col = out[y, lxs] * wl[:, None] + out[y, rxs] * (1 - wl[:, None])
            hx = hole[y]
            out[y, hx] = col[hx]
    else:
        # slanted: shear so the direction becomes vertical, then fill columns like rows
        raise NotImplementedError
    return out.clip(0, 255).astype(np.uint8)


def vfill(img, hole, known=None, side="both"):
    t = directional_fill(img.transpose(1, 0, 2), hole.T, known=None if known is None else known.T, side=side)
    return t.transpose(1, 0, 2)


def trace_rgba(rgba, **over):
    kw = dict(TRACE)
    kw.update(over)
    buf = io.BytesIO()
    Image.fromarray(rgba).save(buf, "PNG")
    svg = vtracer.convert_raw_image_to_svg(buf.getvalue(), img_format="png", **kw)
    paths = re.findall(r"<path [^>]*/>", svg)
    return "\n".join(compact(p) for p in paths)


def compact(p):
    p = re.sub(r"(\d+\.\d)\d+", r"\1", p)
    p = p.replace(".0 ", " ").replace(' transform="translate(0,0)"', "")
    return p


def crop_rgba(img, mask, pad=2):
    ys, xs = np.where(mask)
    x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
    x1, y1 = min(xs.max() + pad + 1, img.shape[1]), min(ys.max() + pad + 1, img.shape[0])
    rgba = np.dstack([img[y0:y1, x0:x1], (mask[y0:y1, x0:x1] * 255).astype(np.uint8)])
    rgba[..., :3][rgba[..., 3] == 0] = 0
    return rgba, (int(x0), int(y0), int(x1 - x0), int(y1 - y0))


def svg_doc(w, h, body, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"{extra}>\n'
            f"{body}\n</svg>\n")


def render(svg_text, width=None):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=width)
    return np.array(Image.open(io.BytesIO(png)).convert("RGBA"))


def composite(base, rgba, x, y):
    out = base.astype(np.float32).copy()
    h, w = rgba.shape[:2]
    a = rgba[..., 3:4] / 255.0
    out[y:y + h, x:x + w] = out[y:y + h, x:x + w] * (1 - a) + rgba[..., :3] * a
    return out.clip(0, 255).astype(np.uint8)


def mae(a, b, mask):
    """Mean abs error (0-255) over mask region on a 4x box downscale."""
    def ds(x):
        return np.array(Image.fromarray(x).resize((x.shape[1] // 4, x.shape[0] // 4), Image.BOX)).astype(np.float32)
    m = np.array(Image.fromarray((mask * 255).astype(np.uint8)).resize((mask.shape[1] // 4, mask.shape[0] // 4), Image.BOX)) > 127
    if not m.any():
        return 0.0
    return float(np.abs(ds(a) - ds(b))[m].mean())


def font(size):
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def save_json(path, data):
    path.write_text(json.dumps(data, indent=1))


_PW = {}


def render_chrome(svg_text, width=None):
    """Render with headless Chromium (supports feGaussianBlur, which cairosvg ignores)."""
    from playwright.sync_api import sync_playwright
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
    vw, vh = float(m.group(1)), float(m.group(2))
    width = width or int(vw)
    height = int(round(vh * width / vw))
    svg_text = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{width}" height="{height}"', svg_text, count=1)
    if "pw" not in _PW:
        _PW["ctx"] = sync_playwright().start()
        _PW["pw"] = _PW["ctx"].chromium.launch(executable_path="/opt/pw-browsers/chromium")
    page = _PW["pw"].new_page(viewport={"width": width, "height": height})
    page.set_content(f"<html><body style='margin:0;background:transparent'>{svg_text}</body></html>")
    png = page.screenshot(omit_background=True, full_page=False)
    page.close()
    return np.array(Image.open(io.BytesIO(png)).convert("RGBA"))


def delight(img, edge_t=5.0, min_area=1500):
    """Flatten soft painted lighting: every large region bounded by real edges takes its median color.
    Edges, outlines and small details keep their pixels. Returns the flat image."""
    import cv2
    g = cv2.GaussianBlur(img.astype(np.float32), (0, 0), 1.2)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)
    edge = np.hypot(gx, gy).max(2) / 4 > edge_t
    edge = ndi.binary_dilation(edge, iterations=1)
    lab, n = ndi.label(~edge)
    out = img.copy()
    sizes = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
    objs = ndi.find_objects(lab)
    for i, sl in enumerate(objs):
        if sizes[i] < min_area:
            continue
        sub = lab[sl] == i + 1
        px = img[sl][sub]
        out[sl][sub] = np.median(px, axis=0).astype(np.uint8)
    return out


def quantize(rgb, mask, k=24, seed=1):
    """Bilateral smooth + k-means palette inside mask: clean flat cel regions before tracing."""
    import cv2
    a = cv2.bilateralFilter(np.ascontiguousarray(rgb), 7, 30, 5)
    px = a[mask].astype(np.float32)
    k = int(min(k, max(2, len(px) // 50)))
    cv2.setRNGSeed(seed)
    _, lab, cen = cv2.kmeans(px, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5), 3,
                             cv2.KMEANS_PP_CENTERS)
    out = a.copy()
    out[mask] = cen[lab.ravel()].round().astype(np.uint8)
    return out
