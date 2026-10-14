"""Trace the 16 items of 44N_COS_TOPPERS_PACKS into flat layered SVG in SOURCE pixel space.
Pipeline: crop -> key out magenta -> k-means quantize (outline forced to plum) -> vtracer -> fill remap.
Backpack greys become var(--suit*) fills with the sampled grey as default, so the game can tint them."""
import io, json, re, sys, colorsys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import vtracer
from lib import ROOT, OUT, render, mae

SRC = Image.open(ROOT / 'raw_originals/44N_COS_TOPPERS_PACKS.png').convert('RGB')
A = np.asarray(SRC).astype(int)
MAG = np.array([245, 8, 240])
OUTLINE = (42, 30, 53)
BOXES = {  # x0,y0,x1,y1 in 5504 px source
 'top_star': (911, 82, 1532, 673), 'top_heart': (1940, 103, 2563, 649), 'top_moon': (2978, 67, 3567, 686),
 'top_cherries': (3983, 75, 4580, 681), 'top_bulb': (946, 730, 1496, 1437), 'top_eyeball': (1985, 840, 2518, 1375),
 'top_dish': (3039, 802, 3506, 1413), 'top_planet': (3854, 845, 4708, 1371),
 'pack_jetpack': (946, 1522, 1499, 2255), 'pack_thermos': (2036, 1515, 2469, 2254), 'pack_lunchbox': (2906, 1580, 3638, 2192),
 'pack_walkman': (3893, 1526, 4668, 2247), 'pack_plant': (946, 2311, 1499, 3038), 'pack_heater': (1934, 2361, 2565, 2987),
 'pack_bedroll': (2972, 2314, 3574, 3037), 'pack_toolbox': (3894, 2438, 4666, 2915)}
K = {'pack_heater': 13, 'pack_bedroll': 13, 'pack_plant': 12}
SUITVARS = ['--suit-light', '--suit', '--suit-shade', '--suit-back']


def kmeans(px, k, it=25, seed=1):
    rng = np.random.default_rng(seed)
    c = [px[rng.integers(len(px))].astype(float)]  # k-means++ init so small stripes keep their colour
    for _ in range(k - 1):
        d = np.min([((px - ci) ** 2).sum(1) for ci in c], 0)
        c.append(px[rng.choice(len(px), p=d / d.sum())].astype(float))
    c = np.array(c)
    for _ in range(it):
        d = ((px[:, None, :] - c[None]) ** 2).sum(2)
        l = d.argmin(1)
        for j in range(k):
            if (l == j).any(): c[j] = px[l == j].mean(0)
    return c


def is_bg(a, g=70, rb=170):
    return (a[..., 1] < g) & (a[..., 0] > rb) & (a[..., 2] > rb)


def fg_mask(name, a):
    if name == 'top_bulb':  # glow halo: keep only what the dark outline encloses
        dark = (a.sum(2) < 330)
        m = ndi.binary_fill_holes(ndi.binary_closing(dark, iterations=7))
        return ndi.binary_dilation(m, iterations=1)
    return ~is_bg(a)


def trace(name, pad=24):
    x0, y0, x1, y1 = BOXES[name]
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    a = A[y0:y1, x0:x1]
    m = fg_mask(name, a)
    px = a[m]
    sub = px[np.random.default_rng(0).choice(len(px), min(len(px), 40000), replace=False)]
    c = kmeans(sub, K.get(name, 11))
    # force the darkest cluster to the house outline colour
    c[np.argmin(c.sum(1))] = OUTLINE
    lab = ((a[:, :, None, :] - c[None, None]) ** 2).sum(3).argmin(2)
    q = c[lab].round().astype(np.uint8)
    # median-filter labels to remove painterly speckle
    lab2 = ndi.median_filter(lab, size=5)
    q = c[lab2].round().astype(np.uint8)
    rgba = np.dstack([q, (m * 255).astype(np.uint8)])
    buf = io.BytesIO(); Image.fromarray(rgba, 'RGBA').save(buf, 'PNG')
    svg = vtracer.convert_raw_image_to_svg(buf.getvalue(), img_format='png', colormode='color', hierarchical='stacked',
                                         mode='spline', filter_speckle=12, color_precision=8, layer_difference=8,
                                         corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=1)
    paths = re.findall(r'<path d="([^"]+)" fill="(#[0-9A-Fa-f]{6})" transform="translate\(([-\d.]+),([-\d.]+)\)"/>', svg)
    # snap each traced fill to its nearest palette colour
    pal = [tuple(int(v) for v in col) for col in c]
    def near(h):
        r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        return min(pal, key=lambda p: (p[0]-r)**2 + (p[1]-g)**2 + (p[2]-b)**2)
    greys = []
    if name.startswith('pack_'):
        for p in pal:
            h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in p])
            if s < 0.12 and 0.38 < l < 0.95: greys.append(p)
        greys.sort(key=lambda p: -sum(p))
    def fill(p):
        hx = '#%02X%02X%02X' % p
        if p == OUTLINE: return '#2A1E35'
        if p in greys:
            i = greys.index(p)
            var = SUITVARS[min(i, 3)] if len(greys) <= 4 else SUITVARS[min(round(i * 3 / (len(greys) - 1)), 3)]
            return f'var({var}, {hx})'
        return hx
    out = []
    for d, f, tx, ty in paths:
        p = near(f)
        tx, ty = float(tx) + x0, float(ty) + y0
        out.append(f'<path d="{d}" transform="translate({tx:g},{ty:g})" style="fill:{fill(p)}"/>')
    body = '\n'.join(out)
    if name == 'top_bulb':
        cx, cy = 1221, 1010
        body = (f'<defs><radialGradient id="bulbGlow"><stop offset="0.45" stop-color="#FFC94A" stop-opacity="0.85"/>'
                f'<stop offset="1" stop-color="#FFC94A" stop-opacity="0"/></radialGradient></defs>'
                f'<circle id="glow" cx="{cx}" cy="{cy}" r="290" fill="url(#bulbGlow)"/>\n' + body)
    vb = f'{x0} {y0} {x1-x0} {y1-y0}'
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n<g id="{name}">\n{body}\n</g>\n</svg>\n'
    (OUT / 'src' / f'{name}_trace.svg').write_text(doc)
    # verify: render at source size over the sheet background, compare to the original crop
    png = OUT / 'check' / f'_{name}.png'
    render(doc, png, x1 - x0, y1 - y0, bg='rgb(245,8,240)')
    r = Image.open(png).convert('RGB')
    o = Image.fromarray(a.astype(np.uint8))
    mk = Image.fromarray((ndi.binary_dilation(~is_bg(a, 30, 225), iterations=6) * 255).astype(np.uint8))
    e = mae(o, r, mk)
    sbs = Image.new('RGB', (2 * o.width, o.height)); sbs.paste(o, (0, 0)); sbs.paste(r, (o.width, 0))
    sbs.save(OUT / 'check' / f'{name}_side_by_side.png')
    Image.blend(o, r, 0.5).save(OUT / 'check' / f'{name}_onion.png')
    png.unlink()
    return e, len(doc)


if __name__ == '__main__':
    names = sys.argv[1:] or list(BOXES)
    res = {}
    for n in names:
        e, size = trace(n)
        res[n] = round(e, 2)
        print(f'{n:15s} MAE {e:5.2f}  {size//1024} KB', flush=True)
    f = OUT / 'build' / 'mae.json'
    old = json.loads(f.read_text()) if f.exists() else {}
    old.update(res); f.write_text(json.dumps(old, indent=1))
