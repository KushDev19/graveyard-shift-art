"""Extract the 4 visors and 4 decals Gemini painted ON characters in 45N_COS_VISORS_DECALS.
Each box is classified against a fixed background palette (helmet glass, rim, suit greys, magenta) plus
k-means item colours; background is keyed out and the rest traced with vtracer, in SOURCE pixel space.
LED smiles are rebuilt as exact circles from detected dots. Writes src/<id>_trace.svg + checks."""
import io, json, re, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import vtracer
from lib import ROOT, OUT, render, mae
from trace44 import kmeans

A = np.asarray(Image.open(ROOT / 'raw_originals/45N_COS_VISORS_DECALS.png').convert('RGB')).astype(int)
OUTLINE = (42, 30, 53)
BG = [(246, 5, 244), (46, 30, 69), (150, 164, 188), (203, 198, 205), (147, 139, 156), (225, 222, 228),
      (176, 170, 184), (120, 112, 130)]
DROP = {'decal_nametag_s': [(225, 222, 228)], 'decal_nametag_f': [(225, 222, 228)]}  # cream tag vs light suit
ITEMS = {  # id: (box x0,y0,x1,y1 in source px, k)
 'visor_aviator_s': ((520, 470, 935, 800), 9), 'visor_aviator_s2': ((1300, 470, 1720, 800), 9),
 'visor_heart_s': ((2230, 470, 2670, 840), 6), 'visor_star_f': ((2930, 440, 3660, 820), 7),
 'decal_nametag_s': ((640, 2440, 850, 2620), 5), 'decal_nametag_f': ((1120, 2440, 1410, 2630), 5),
 'decal_bolt_s': ((2390, 2420, 2610, 2620), 5), 'decal_smiley_s': ((3170, 2420, 3460, 2710), 5),
 'decal_flames_s': ((4190, 2440, 4540, 2810), 7), 'decal_flames_f': ((4630, 2440, 5300, 2840), 7)}
DOMEKEY = {'visor_aviator_s': 'aviator_s1', 'visor_aviator_s2': 'aviator_s2', 'visor_heart_s': 'heart_s', 'visor_star_f': 'star_f'}
LED = {'visor_led_s': (4180, 460, 4540, 840), 'visor_led_f': (4700, 440, 5230, 800)}


def dist_to(a, pal):
    return np.sqrt(((a[..., None, :] - np.array(pal)[None, None]) ** 2).sum(-1))


def check(name, doc, box, keep):
    x0, y0, x1, y1 = box
    a = A[y0:y1, x0:x1].astype(np.uint8)
    o = Image.fromarray(a)
    # composite the SVG over the original box (its real background)
    png = OUT / 'check' / f'_{name}.png'
    bgsvg = doc  # rendered transparent then composited
    render(bgsvg, png, x1 - x0, y1 - y0)
    r = Image.open(png).convert('RGBA'); png.unlink()
    # composite over a FLAT background (glass or suit grey) so anything the trace misses shows as an error
    flat = BG[1] if name.startswith('visor') else BG[3]
    comp = Image.new('RGBA', o.size, flat + (255,)); comp.alpha_composite(r); comp = comp.convert('RGB')
    mk = Image.fromarray((ndi.binary_dilation(keep, iterations=4) * 255).astype(np.uint8))
    e = mae(o, comp, mk)
    sbs = Image.new('RGB', (2 * o.width, o.height)); sbs.paste(o, (0, 0)); sbs.paste(comp, (o.width, 0))
    sbs.save(OUT / 'check' / f'{name}_side_by_side.png')
    Image.blend(o, r.convert('RGB'), 0.5).save(OUT / 'check' / f'{name}_onion.png')
    return e


def trace_item(name):
    (x0, y0, x1, y1), k = ITEMS[name]
    a = A[y0:y1, x0:x1]
    if name.startswith('visor'):  # inside the helmet: only glass, rim, highlight, magenta are background
        bg = [BG[0], BG[1], BG[2], (209, 196, 222)]
        thr = 30
    else:
        bg = [p for p in BG if p not in DROP.get(name, [])]
        thr = 28 if name in DROP else 45
    core = dist_to(a, bg + [OUTLINE]).min(-1) > thr
    if name.startswith('visor'):  # soft painted glow halo: background for labelling (glow is re-made as a blur)
        bg = bg + [(80, 53, 70), (67, 44, 64), (100, 62, 68), (120, 70, 66)]
    core = ndi.binary_opening(core, iterations=2)
    c = kmeans(a[core][np.random.default_rng(0).choice(core.sum(), min(core.sum(), 30000), replace=False)], k)
    pal = [tuple(v) for v in bg] + [OUTLINE] + [tuple(v) for v in c.round().astype(int)]
    nb = len(bg)
    lab = ndi.median_filter(dist_to(a, pal).argmin(-1), size=5)
    if name.startswith('visor_aviator'):  # dark ring hugging the item = its outline (too close to the glass colour)
        ring = ndi.binary_dilation(core, iterations=12) & ~core & (a.sum(-1) < 190)
        lab[ring] = nb
    keep = (lab >= nb) & ndi.binary_dilation(core, iterations=18)
    keep = ndi.binary_fill_holes(ndi.binary_closing(keep, iterations=2)) & (lab >= nb)
    if name in DOMEKEY:  # outside the glass keep only the item itself (+ its outline), never the helmet rim
        d = json.loads((OUT / 'build/domes.json').read_text())[DOMEKEY[name]]
        cx, rx = d['cx'], d['rx']
        if name == 'visor_heart_s': cx, rx = cx - rx + 324, 324
        cy = d['top'] + rx * 185 / 196
        yy, xx = np.mgrid[y0:y1, x0:x1]
        inside = ((xx - cx) / (rx - 10)) ** 2 + ((yy - cy) / (rx * 185 / 196 - 10)) ** 2 <= 1
        mx, mn = a.max(-1), a.min(-1)
        sat = (mx - mn) / np.maximum(mx, 1)
        magenta = (a[..., 1] < 100) & (a[..., 0] - a[..., 1] > 90) & (a[..., 2] - a[..., 1] > 90)
        item = ndi.binary_opening((sat > 0.4) & (mx > 110) & ~magenta, iterations=4)
        if name.startswith('visor_aviator'):  # the far lens is as dark as the helmet outline: keep its box
            item |= (xx > x0 + 0.68 * (x1 - x0)) & (yy > y0 + 40) & (yy < y0 + 230) & (lab >= nb)
        keep &= inside | ndi.binary_dilation(item & ~inside, iterations=13)
    q = np.array(pal)[lab].astype(np.uint8)
    rgba = np.dstack([q, (keep * 255).astype(np.uint8)])
    buf = io.BytesIO(); Image.fromarray(rgba, 'RGBA').save(buf, 'PNG')
    svg = vtracer.convert_raw_image_to_svg(buf.getvalue(), img_format='png', colormode='color', hierarchical='stacked',
                                         mode='spline', filter_speckle=10, color_precision=8, layer_difference=8,
                                         corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=1)
    out = []
    for d, f, tx, ty in re.findall(r'<path d="([^"]+)" fill="(#[0-9A-Fa-f]{6})" transform="translate\(([-\d.]+),([-\d.]+)\)"/>', svg):
        r_, g_, b_ = int(f[1:3], 16), int(f[3:5], 16), int(f[5:7], 16)
        p = min(pal[nb:], key=lambda p: (p[0]-r_)**2 + (p[1]-g_)**2 + (p[2]-b_)**2)
        if (p[0] > 110 and p[2] > 110 and p[1] < 100 and p[0] - p[1] > 70 and p[2] - p[1] > 70) or \
                min(sum((p[i] - q[i]) ** 2 for i in range(3)) for q in [BG[2], (209, 196, 222)]) < 900:
            continue  # anti-aliased magenta / helmet-rim stubs, not part of the item
        if name in ('visor_heart_s', 'visor_star_f') and max(p) > 150 and (max(p) - min(p)) / max(p) < 0.14:
            continue  # pale rim highlight crossing behind the item
        hx = '#2A1E35' if p == OUTLINE else '#%02X%02X%02X' % p
        out.append(f'<path d="{d}" transform="translate({float(tx)+x0:g},{float(ty)+y0:g})" fill="{hx}"/>')
    return finish(name, (x0, y0, x1, y1), '\n'.join(out), keep)


def led_item(name):
    x0, y0, x1, y1 = LED[name]
    a = A[y0:y1, x0:x1]
    m = (a[..., 0] > 190) & (a[..., 1] > 110) & (a[..., 2] < 140)
    m = ndi.binary_opening(m, iterations=1)
    lab, n = ndi.label(m)
    circ = []
    for i, s in enumerate(ndi.find_objects(lab)):
        area = (lab[s] == i + 1).sum()
        if area < 25: continue
        cy, cx = ndi.center_of_mass(lab == i + 1)
        circ.append((cx + x0, cy + y0, np.sqrt(area / np.pi)))
    col = '#%02X%02X%02X' % tuple(np.median(a[m], 0).astype(int))
    body = '\n'.join(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>' for cx, cy, r in circ)
    body = (f'<g id="glow" fill="#F59A3C" opacity="0.75" filter="url(#ledBlur)">{body}</g>\n'
            f'<g id="dots" fill="{col}">{body}</g>')
    defs = '<defs><filter id="ledBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter></defs>'
    return finish(name, (x0, y0, x1, y1), defs + body, ndi.binary_dilation(m, iterations=6), len(circ))


def finish(name, box, body, keep, extra=None):
    x0, y0, x1, y1 = box
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}">\n'
           f'<g id="{name}">\n{body}\n</g>\n</svg>\n')
    (OUT / 'src' / f'{name}_trace.svg').write_text(doc)
    e = check(name, doc, box, keep)
    print(f'{name:18s} MAE {e:5.2f} {len(doc)//1024} KB' + (f' dots={extra}' if extra else ''), flush=True)
    return round(e, 2)


if __name__ == '__main__':
    names = sys.argv[1:] or list(ITEMS) + list(LED)
    res = {n: (led_item(n) if n in LED else trace_item(n)) for n in names}
    f = OUT / 'build' / 'mae.json'
    old = json.loads(f.read_text()); old.update(res); f.write_text(json.dumps(old, indent=1))
