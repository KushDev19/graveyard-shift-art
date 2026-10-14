"""Fit the traced items to the crew puppet and write the deliverables of job N.
Every cosmetic SVG uses a viewBox in PUPPET units (crew_puppet.svg, 640x800), so cosmetics.json x,y is simply
the viewBox origin: draw the file at (x,y) in puppet space, scaled with the puppet."""
import json, re
import numpy as np
from lib import ROOT, OUT, render
from trace44 import BOXES

PUP = (ROOT / 'frontend/public/assets/ship/crew/crew_puppet.svg').read_text()
DOMES = json.loads((OUT / 'build/domes.json').read_text())
DOMES['heart_s']['cx'] = DOMES['heart_s']['cx'] - DOMES['heart_s']['rx'] + 324  # heart covers the right rim
DOMES['heart_s']['rx'] = 324
STYLE = ('<style>.o{stroke:#2A1E35;stroke-width:10;stroke-linejoin:round;stroke-linecap:round}'
         '.suit{fill:var(--suit,#CDCCD4)}.shade{fill:var(--suit-shade,#A09FAA)}'
         '.light{fill:var(--suit-light,#E6E5EC)}.nofill{fill:none}'
         '.lightline{stroke:var(--suit-light,#E6E5EC);stroke-width:6;stroke-linecap:round;fill:none}</style>')
GLOW = '<filter id="vglow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="10"/></filter>'
BODY_S = 'M 152 448 C 140 500 140 570 158 620 C 175 656 230 674 300 674 C 372 674 426 662 450 632 C 472 600 480 540 470 488 C 467 472 462 462 456 458 Z'
BODY_F = 'M 172 468 C 158 520 152 580 164 630 C 178 678 240 702 320 702 C 400 702 462 678 476 630 C 488 580 482 520 468 468 Z'
DOME_IN = '<ellipse cx="320" cy="300" rx="196" ry="185"/>'


def src(name):
    t = (OUT / 'src' / f'{name}_trace.svg').read_text()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', t).group(1).split()]
    inner = re.search(r'<g id="[^"]+">\n(.*)\n</g>\n</svg>', t, re.S).group(1)
    return inner, vb


def m(s, tx, ty, sx=None):
    return f'matrix({(sx if sx is not None else s):.5f} 0 0 {s:.5f} {tx:.2f} {ty:.2f})'


def dome_map(key):
    d = DOMES[key]; s = 196 / d['rx']
    return s, 320 - d['cx'] * s, 300 - d['cy'] * s


def svg(vb, body, defs=''):
    x, y, w, h = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:g} {y:g} {w:g} {h:g}" width="{w:g}" height="{h:g}">\n'
            f'{STYLE}\n<defs>{GLOW}{defs}</defs>\n{body}\n</svg>\n')


def bbox_of(vb, s, tx, ty, sx=None, pad=6):
    sx = s if sx is None else sx
    xs = sorted([vb[0] * sx + tx, (vb[0] + vb[2]) * sx + tx]); ys = [vb[1] * s + ty, (vb[1] + vb[3]) * s + ty]
    return [round(xs[0] - pad), round(ys[0] - pad), round(xs[1] - xs[0] + 2 * pad), round(ys[1] - ys[0] + 2 * pad)]


ITEMS = []  # dicts for cosmetics.json; files written as we go


def write(fname, vb, body, defs=''):
    (OUT / fname).write_text(svg(vb, body, defs))
    return fname


# ---------- antenna toppers (replace the whole antenna: stalk + nub kept, ball replaced) ----------
STALK_S = ('<path d="M 300 92 C 300 72 294 56 280 44" fill="none" stroke="#2A1E35" stroke-width="18" stroke-linecap="round"/>'
           '<path d="M 300 92 C 300 72 294 56 280 44" fill="none" style="stroke:var(--suit,#CDCCD4)" stroke-width="7" stroke-linecap="round"/>'
           '<path class="suit" d="M 258 112 C 260 94 280 84 302 84 C 324 84 342 94 345 112 Z"/>'
           '<path class="lightline" d="M 280 96 C 292 91 306 90 318 92"/>'
           '<path class="o nofill" d="M 258 112 C 260 94 280 84 302 84 C 324 84 342 94 345 112 Z"/>')
STALK_F = ('<path d="M 320 104 V 48" stroke="#2A1E35" stroke-width="18" stroke-linecap="round"/>'
           '<path d="M 320 104 V 48" style="stroke:var(--suit,#CDCCD4)" stroke-width="7" stroke-linecap="round"/>'
           '<path class="suit" d="M 277 116 C 279 98 297 88 320 88 C 344 88 362 98 364 116 Z"/>'
           '<path class="lightline" d="M 300 99 C 312 95 326 94 338 96"/>'
           '<path class="o nofill" d="M 277 116 C 279 98 297 88 320 88 C 344 88 362 98 364 116 Z"/>')
TOP_H, TOP_W = 118, 150
for name in [n for n in BOXES if n.startswith('top_')]:
    inner, vb = src(name)
    x0, y0, x1, y1 = BOXES[name]
    s = min(TOP_H / (y1 - y0), TOP_W / (x1 - x0))
    out = {}
    for view, (cx, bot, stalk, piv) in {'side': (270, 48, STALK_S, [300, 104]), 'front': (320, 52, STALK_F, [320, 108])}.items():
        tx = cx - (x0 + x1) / 2 * s; ty = bot - y1 * s
        box = bbox_of(vb, s, tx, ty); box[3] = max(box[3], 122 - box[1])  # include the nub
        body = (f'<g id="{name[4:]}_{view}" data-pivot="{piv[0]},{piv[1]}">\n<g id="stalk">{stalk}</g>\n'
                f'<g id="topper" transform="{m(s, tx, ty)}">\n{inner}\n</g>\n</g>')
        f = write(f'{name}_{view}.svg', box, body)
        out[view] = {'file': f, 'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3], 'pivot': piv}
    ITEMS.append({'id': name, 'slot': 'topper', 'side': out['side'], 'front': out['front'], 'hidesAntenna': True,
                  'replaces': {'side': ['antenna'], 'front': ['f_antenna']}, 'z': {'side': 'antenna', 'front': 'f_antenna'},
                  'layers': {'back': False, 'front': True}})

# ---------- backpacks (side only, drawn where #backpack is, behind the body) ----------
for name in [n for n in BOXES if n.startswith('pack_')]:
    inner, vb = src(name)
    x0, y0, x1, y1 = BOXES[name]
    s = min(236 / (y1 - y0), 196 / (x1 - x0))
    tx = 176 - x1 * s; ty = 530 - (y0 + y1) / 2 * s
    box = bbox_of(vb, s, tx, ty)
    f = write(f'{name}_side.svg', box, f'<g id="{name[5:]}" transform="{m(s, tx, ty)}">\n{inner}\n</g>')
    ITEMS.append({'id': name, 'slot': 'backpack', 'side': {'file': f, 'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3], 'pivot': None},
                  'front': None, 'hidesAntenna': False, 'replaces': {'side': ['backpack'], 'front': []},
                  'z': {'side': 'backpack', 'front': None}, 'layers': {'back': True, 'front': False}})


# ---------- visors (replace visor + visor_glow; glow is a blurred copy clipped to the dome glass) ----------
def visor_body(gid, art, glow_op=0.55):
    return (f'<g id="{gid}">\n<g id="glow" clip-path="url(#domeIn)" opacity="{glow_op}" filter="url(#vglow)">{art}</g>\n'
            f'<g id="art">{art}</g>\n</g>')


def visor_item(name, side_art, side_box, front_art, front_box):
    d = '<clipPath id="domeIn">' + DOME_IN + '</clipPath>'
    fs = write(f'{name}_side.svg', side_box, visor_body(f'{name[6:]}_side', side_art), d)
    ff = write(f'{name}_front.svg', front_box, visor_body(f'{name[6:]}_front', front_art), d)
    ITEMS.append({'id': name, 'slot': 'visor',
                  'side': {'file': fs, 'x': side_box[0], 'y': side_box[1], 'w': side_box[2], 'h': side_box[3], 'pivot': [416, 314]},
                  'front': {'file': ff, 'x': front_box[0], 'y': front_box[1], 'w': front_box[2], 'h': front_box[3]},
                  'hidesAntenna': False, 'replaces': {'side': ['visor', 'visor_glow'], 'front': ['f_visor', 'f_visor_glow']},
                  'z': {'side': 'visor', 'front': 'f_visor'}, 'layers': {'back': False, 'front': True}})


def led_box(name):
    t = (OUT / 'src' / f'{name}_trace.svg').read_text()
    c = np.array([[float(v) for v in re.findall(r'"([\d.]+)"', cc)] for cc in re.findall(r'<circle ([^/]+)/>', t)])
    return c[:, 0].min(), c[:, 1].min(), c[:, 0].max(), c[:, 1].max()


# LED smile: both views exist
gi, gvb = src('visor_led_s'); s, tx, ty = dome_map('led_s')
led_s_art = f'<g transform="{m(s, tx, ty)}">{gi}</g>'; led_s_box = bbox_of(gvb, s, tx, ty)
fi, fvb = src('visor_led_f'); s2, tx2, ty2 = dome_map('led_f')
led_f_art = f'<g transform="{m(s2, tx2, ty2)}">{fi}</g>'; led_f_box = bbox_of(fvb, s2, tx2, ty2)
visor_item('visor_led', led_s_art, led_s_box, led_f_art, led_f_box)
# front -> side affine measured on the LED pair (the only visor drawn in both views)
a, b = led_box('visor_led_f'), led_box('visor_led_s')
Fp = [a[0] * s2 + tx2, a[1] * s2 + ty2, a[2] * s2 + tx2, a[3] * s2 + ty2]
Sp = [b[0] * s + tx, b[1] * s + ty, b[2] * s + tx, b[3] * s + ty]
KX = (Sp[2] - Sp[0]) / (Fp[2] - Fp[0]); KY = (Sp[3] - Sp[1]) / (Fp[3] - Fp[1])
F2S = (KX, KY, Sp[0] - Fp[0] * KX, Sp[1] - Fp[1] * KY)

# Star: front exists, side derived with the LED front->side mapping (foreshortened)
si, svb = src('visor_star_f'); s, tx, ty = dome_map('star_f')
star_f = f'<g transform="{m(s, tx, ty)}">{si}</g>'; star_f_box = bbox_of(svb, s, tx, ty)
kx, ky, ox, oy = F2S
star_s = f'<g transform="matrix({kx:.4f} 0 0 {ky:.4f} {ox:.2f} {oy:.2f})">{star_f}</g>'
star_s_box = [round(star_f_box[0] * kx + ox), round(star_f_box[1] * ky + oy), round(star_f_box[2] * kx), round(star_f_box[3] * ky)]
visor_item('visor_star', star_s, star_s_box, star_f, star_f_box)

# Heart: side exists; front = same heart, same scale, centred on the front visor
hi, hvb = src('visor_heart_s'); s, tx, ty = dome_map('heart_s')
heart_s = f'<g transform="{m(s, tx, ty)}">{hi}</g>'; heart_s_box = bbox_of(hvb, s, tx, ty)
hx0, hy0, hx1, hy1 = 2262, 560, 2632, 812  # heart outline extent in source px
s_f = s * 1.08
txf = 321 - (hx0 + hx1) / 2 * s_f; tyf = 326 - (hy0 + hy1) / 2 * s_f
heart_f = f'<g transform="{m(s_f, txf, tyf)}">{hi}</g>'; heart_f_box = bbox_of([hx0 - 20, hy0 - 20, hx1 - hx0 + 40, hy1 - hy0 + 40], s_f, txf, tyf)
visor_item('visor_heart', heart_s, heart_s_box, heart_f, heart_f_box)

# Aviator: side = s1 (+ hand-drawn temple arm, too close to the glass colour to key out);
# front = the near lens and its mirror over the puppet's amber visor
ai, avb = src('visor_aviator_s'); s, tx, ty = dome_map('aviator_s1')
ARM = ('<path d="M 352 628 C 352 600 372 584 400 582 L 548 578" fill="none" stroke="#2A1E35" stroke-width="26" stroke-linecap="round"/>'
       '<path d="M 352 628 C 352 600 372 584 400 582 L 548 578" fill="none" stroke="#5A2B5F" stroke-width="11" stroke-linecap="round"/>')
av_s = f'<g transform="{m(s, tx, ty)}">{ARM}{ai}</g>'
av_s_box = bbox_of([340, avb[1], avb[0] + avb[2] - 340, avb[3]], s, tx, ty)
def not_amber(mm):
    h = re.search(r'fill="#(..)(..)(..)"', mm.group(0))
    r, g, bl = (int(v, 16) for v in h.groups())
    return '' if (r > 170 and 90 < g < 200 and bl < 130) else mm.group(0)
lens = re.sub(r'<path [^>]*/>', not_amber, ai)  # lenses, stripe and outline only
LX0, LX1, LY0, LY1 = 525, 792, 486, 752
lclip = f'<clipPath id="lensClip"><rect x="{LX0}" y="{LY0}" width="{LX1-LX0}" height="{LY1-LY0}"/></clipPath>'
sl = s * 0.95; lw = (LX1 - LX0) * sl; gap = 4
txl = 321 - gap / 2 - lw - LX0 * sl; tyl = 322 - (LY0 + LY1) / 2 * sl
L = f'<g clip-path="url(#lensClip)">{lens}</g>'
amber = ('<rect x="204" y="245" width="234" height="157" rx="54" fill="#F7AE4E" stroke="#C26E2C" stroke-width="10"/>')
bridge = '<path d="M 300 266 C 312 256 330 256 342 266" fill="none" stroke="#2A1E35" stroke-width="12" stroke-linecap="round"/>'
av_f = (amber + bridge + f'<g transform="{m(sl, txl, tyl)}">{L}</g>'
        f'<g transform="{m(sl, 642 - txl, tyl, -sl)}">{L}</g>')
av_f_box = [round(321 - lw - gap / 2 - 8), 236, round(2 * lw + gap + 16), 176]
(OUT / 'build' / '_lensclip.txt').write_text(lclip)
visor_item('visor_aviator', av_s, av_s_box, av_f, av_f_box)
for it in ITEMS[-1:]:
    p = OUT / it['front']['file']; p.write_text(p.read_text().replace('<defs>', '<defs>' + lclip, 1))

# ---------- decals (replace stripe; clipped to the body) ----------
def decal_item(name, side_art, side_box, front_art, front_box):
    ds = f'<clipPath id="bodyS"><path d="{BODY_S}"/></clipPath>'
    df = f'<clipPath id="bodyF"><path d="{BODY_F}"/></clipPath>'
    fs = write(f'{name}_side.svg', side_box, f'<g id="{name[6:]}_side" clip-path="url(#bodyS)">{side_art}</g>', ds)
    ff = write(f'{name}_front.svg', front_box, f'<g id="{name[6:]}_front" clip-path="url(#bodyF)">{front_art}</g>', df)
    ITEMS.append({'id': name, 'slot': 'decal',
                  'side': {'file': fs, 'x': side_box[0], 'y': side_box[1], 'w': side_box[2], 'h': side_box[3], 'pivot': None},
                  'front': {'file': ff, 'x': front_box[0], 'y': front_box[1], 'w': front_box[2], 'h': front_box[3]},
                  'hidesAntenna': False, 'replaces': {'side': ['stripe'], 'front': ['f_stripe']},
                  'z': {'side': 'stripe', 'front': 'f_stripe'}, 'layers': {'back': False, 'front': True}})


def place(name, center, scale_k=1.0, sx_k=1.0, dome='tag_s'):
    i, vb = src(name)
    s = 196 / DOMES[dome]['rx'] * scale_k; sx = s * sx_k
    tx = center[0] - (vb[0] + vb[2] / 2) * sx; ty = center[1] - (vb[1] + vb[3] / 2) * s
    return f'<g transform="{m(s, tx, ty, sx)}">{i}</g>', bbox_of(vb, s, tx, ty, sx)


DEC = json.loads((OUT / 'build' / 'decal_fit.json').read_text())
for d in ['nametag', 'bolt', 'smiley', 'flames']:
    c = DEC[d]
    sa, sb = place(c['side']['src'], c['side']['c'], c['side'].get('k', 1), c['side'].get('sx', 1), c['side']['dome'])
    fa, fb = place(c['front']['src'], c['front']['c'], c['front'].get('k', 1), c['front'].get('sx', 1), c['front']['dome'])
    decal_item('decal_' + d, sa, sb, fa, fb)

json.dump({'puppet': 'frontend/public/assets/ship/crew/crew_puppet.svg',
           'coords': 'puppet viewBox units (640x800). Draw file at (x,y) with size (w,h) in puppet space; files use the same units in their viewBox.',
           'tint': 'grey parts use var(--suit), var(--suit-shade), var(--suit-back), var(--suit-light) like the puppet',
           'items': ITEMS}, open(OUT / 'cosmetics.json', 'w'), indent=1)
print(len(ITEMS), 'items')
