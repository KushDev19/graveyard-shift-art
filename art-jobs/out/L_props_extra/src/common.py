"""Shared helpers for Job L: keying, tracing (vtracer), rendering, MAE checks."""
import io, json, re, numpy as np, cairosvg, vtracer
from PIL import Image
from scipy import ndimage as ndi
SRC = '../../../raw_originals/38_PROPS_EXTRA.png'
PAD = 16
NAMES = ['med_scanner', 'med_scanner_active', 'security_desk', 'security_desk_on',
         'plant', 'floor_lamp', 'crate_stack', 'water_cooler',
         'locker', 'toolbox', 'mop_bucket', 'cactus']
_sheet = None

def sheet():
    global _sheet
    if _sheet is None:
        _sheet = np.asarray(Image.open(SRC).convert('RGB'))
    return _sheet

def boxes():
    raw = json.load(open('src/bboxes_raw.json'))
    out = {}
    for n, o in zip(NAMES, raw):
        out[n] = (o['x'] - PAD, o['y'] - PAD, o['w'] + 2 * PAD, o['h'] + 2 * PAD)
    return out

def crop(name):
    x, y, w, h = boxes()[name]
    return sheet()[y:y + h, x:x + w]

def key(rgb):
    """Alpha by unmixing against magenta: |p-M| / |O-M| (O = the sheet's plum outline).
    Returns (alpha 0..1, rgb with edge pixels decontaminated)."""
    a = rgb.astype(np.float32)
    M = np.array([247, 6, 247], np.float32); O = np.array([75, 20, 70], np.float32)
    alpha = np.clip(np.linalg.norm(a - M, axis=-1) / np.linalg.norm(O - M), 0, 1)
    near_bg = ndi.binary_dilation(alpha < 0.5, iterations=3)
    solid = (alpha > 0.97) | ~near_bg
    idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    clean = rgb[idx[0], idx[1]]
    return alpha, clean

def trace(rgba_img, **kw):
    buf = io.BytesIO(); Image.fromarray(rgba_img, 'RGBA').save(buf, 'PNG')
    opts = dict(colormode='color', hierarchical='stacked', mode='spline', filter_speckle=6,
                color_precision=7, layer_difference=10, corner_threshold=60,
                length_threshold=3.5, max_iterations=10, splice_threshold=45, path_precision=1)
    opts.update(kw)
    return vtracer.convert_raw_image_to_svg(buf.getvalue(), img_format='png', **opts)

def paths_of(svg):
    """Extract <path> elements from vtracer output (keeps fill + transform)."""
    return re.findall(r'<path[^>]*/>', svg)

_page = None
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

def render(svg_text, w=None, h=None):
    """Render with headless Chromium (full SVG filter support, like the game's browser)."""
    global _page
    if _page is None:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start(); br = pw.chromium.launch(executable_path=CHROME)
        _page = br.new_page()
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
    vw, vh = float(m.group(1)), float(m.group(2))
    w = w or (int(vw * h / vh) if h else int(vw)); h = h or int(round(vh * w / vw))
    body = re.sub(r'<svg ([^>]*?)width="[\d.]+" height="[\d.]+"', r'<svg \1', svg_text, count=1)
    body = body.replace('<svg ', f'<svg width="{w}" height="{h}" ', 1)
    _page.set_viewport_size({'width': w, 'height': h})
    _page.set_content(f'<html><body style="margin:0;background:transparent">{body}</body></html>')
    png = _page.locator('svg').first.screenshot(omit_background=True)
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))[:h, :w]

def over(top_rgba, bottom_rgb):
    a = top_rgba[..., 3:4].astype(np.float32) / 255
    return (top_rgba[..., :3] * a + bottom_rgb * (1 - a)).astype(np.uint8)

def mae(name, svg_text, region=None):
    """Composite render over the original crop's own background colour, 4x downscale MAE on object region."""
    orig = crop(name)
    h, w = orig.shape[:2]
    r = render(svg_text, w, h)
    bgc = np.array([245, 6, 243], np.uint8)
    comp = over(r, np.broadcast_to(bgc, orig.shape))
    alpha, _ = key(orig)
    reg = ndi.binary_dilation(alpha > 0.5, iterations=8) | (r[..., 3] > 128)
    if region is not None: reg &= region
    def ds(x): return np.asarray(Image.fromarray(x).resize((w // 4, h // 4), Image.BOX)).astype(np.float32)
    m = np.asarray(Image.fromarray(reg.astype(np.uint8) * 255).resize((w // 4, h // 4), Image.BOX)) > 127
    d = np.abs(ds(comp) - ds(orig)).mean(-1)
    return float(d[m].mean()), comp, r

def quantize(clean, mask, k=14, smooth=2, seed=1, extra=()):
    """K-means flatten the painted colours, then a majority filter to kill speckles."""
    from scipy.cluster.vq import kmeans2
    px = clean[mask].astype(np.float32)
    rng = np.random.default_rng(seed)
    sample = px[rng.choice(len(px), min(len(px), 60000), replace=False)]
    cent, _ = kmeans2(sample, k, minit='++', seed=seed, iter=30)
    keep = []
    for i in range(len(cent)):  # merge near-duplicate clusters (they cause wobbly double outlines)
        if all(np.linalg.norm(cent[i] - cent[j]) > 16 for j in keep): keep.append(i)
    cent = cent[keep]; k = len(cent)
    if len(extra): cent = np.vstack([cent, np.array(extra, np.float32)]); k = len(cent)
    lab = np.full(mask.shape, -1, np.int16)
    d = ((px[:, None, :] - cent[None]) ** 2).sum(-1)
    lab[mask] = d.argmin(1)
    # majority filter
    for _ in range(smooth):
        votes = np.stack([ndi.uniform_filter((lab == i).astype(np.float32), 7) for i in range(k)])
        best = votes.argmax(0).astype(np.int16)
        lab = np.where(mask, best, -1)
    out = np.zeros(mask.shape + (4,), np.uint8)
    out[mask, :3] = np.clip(cent[lab[mask]], 0, 255).astype(np.uint8)
    out[mask, 3] = 255
    return out, cent

def prep(name, k=14, thr=0.5, extra=()):
    c = crop(name); al, clean = key(c)
    mask = ndi.binary_opening(al > thr, iterations=1)
    clean = np.stack([ndi.median_filter(clean[..., i], 5) for i in range(3)], -1)
    q, cent = quantize(clean, mask, k, smooth=3, extra=extra)
    return q

def group(gid, svg_or_paths, attrs=''):
    body = svg_or_paths if isinstance(svg_or_paths, str) and not svg_or_paths.startswith('<?xml') else '\n'.join(paths_of(svg_or_paths))
    return f'<g id="{gid}"{(" " + attrs) if attrs else ""}>\n{body}\n</g>'

def wrap(name, inner, defs='', extra=''):
    x, y, w, h = boxes()[name] if name in NAMES else (0, 0) + name_size(name)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'data-src="raw_originals/38_PROPS_EXTRA.png" data-src-box="{x},{y},{w},{h}"{extra}>\n'
            + (f'<defs>{defs}</defs>\n' if defs else '') + inner + '\n</svg>\n')

def checks(name, svg_text, orig=None, tag=None):
    """Write check/<tag>_side_by_side.png and check/<tag>_onion.png, return MAE."""
    tag = tag or name
    m, comp, r = mae(name, svg_text) if orig is None else mae_vs(orig, svg_text)
    o = crop(name) if orig is None else orig
    s = 0.5
    def sm(x): return Image.fromarray(x).resize((int(x.shape[1] * s), int(x.shape[0] * s)), Image.LANCZOS)
    sbs = Image.new('RGB', (int(o.shape[1] * s) * 2 + 10, int(o.shape[0] * s)), (40, 30, 50))
    sbs.paste(sm(o), (0, 0)); sbs.paste(sm(comp), (int(o.shape[1] * s) + 10, 0))
    sbs.save(f'check/{tag}_side_by_side.png')
    onion = (o.astype(np.float32) * 0.5 + comp.astype(np.float32) * 0.5).astype(np.uint8)
    sm(onion).save(f'check/{tag}_onion.png')
    return m

def mae_vs(orig, svg_text):
    h, w = orig.shape[:2]
    r = render(svg_text, w, h)
    comp = over(r, np.broadcast_to(np.array([245, 6, 243], np.uint8), orig.shape))
    alpha, _ = key(orig)
    reg = ndi.binary_dilation(alpha > 0.5, iterations=8) | (r[..., 3] > 128)
    def ds(x): return np.asarray(Image.fromarray(x).resize((w // 4, h // 4), Image.BOX)).astype(np.float32)
    m = np.asarray(Image.fromarray(reg.astype(np.uint8) * 255).resize((w // 4, h // 4), Image.BOX)) > 127
    return float(np.abs(ds(comp) - ds(orig)).mean(-1)[m].mean()), comp, r
