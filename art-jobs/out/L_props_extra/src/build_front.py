"""Front-facing (room camera) redraws of the diagonal props of sheet 38.
Colours are the k-means samples of each prop; outline = the sheet's plum outline, 14 px at source scale."""
import sys
from common import *
OL = '#4E1648'; SW = 14
S = f'stroke="{OL}" stroke-width="{SW}" stroke-linejoin="round" stroke-linecap="round"'

def R(x, y, w, h, fill, r=0, extra=''):
    st = '' if 'stroke-width' in extra else S
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{r}" fill="{fill}" {st} {extra}/>'

def P(d, fill, extra=''):
    return f'<path d="{d}" fill="{fill}" {S} {extra}/>'

def L(x1, y1, x2, y2, w=SW, col=OL):
    return f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'

def E(cx, cy, rx, ry, fill, extra=''):
    return f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{fill}" {S} {extra}/>'

def svg(W, H, body, defs='', name=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'data-view="front" data-src="raw_originals/38_PROPS_EXTRA.png">\n'
            + (f'<defs>{defs}</defs>\n' if defs else '') + body + '\n</svg>\n')

def box(x, y, w, h, top, side, front, ftop, fside, ffront, r=18):
    """Front-facing box: top strip (height top), right side band (width side), front face. Returns svg."""
    return (P(f'M{x + 10} {y + top} L{x + 22} {y + 6} Q{x + 26} {y} {x + 40} {y} L{x + w - 40} {y} Q{x + w - 26} {y} {x + w - 22} {y + 6} L{x + w - 10} {y + top} Z', ftop)
            + R(x, y + top, w, h - top, ffront, r)
            + P(f'M{x + w - side} {y + top} L{x + w - r} {y + top} Q{x + w} {y + top} {x + w} {y + top + r} L{x + w} {y + h - r} Q{x + w} {y + h} {x + w - r} {y + h} L{x + w - side} {y + h} Z', fside))

FRONTS = {}

def topped(x, y, w, h, top, ftop, ffront, r=40, rt=40):
    """Front face with a visible top face above it (room camera looks slightly down)."""
    return (P(f'M{x} {y + top + 20} L{x} {y + rt} Q{x} {y} {x + rt} {y} L{x + w - rt} {y} Q{x + w} {y} {x + w} {y + rt} L{x + w} {y + top + 20} Z', ftop)
            + P(f'M{x} {y + top} L{x + w} {y + top} L{x + w} {y + h - r} Q{x + w} {y + h} {x + w - r} {y + h} L{x + r} {y + h} Q{x} {y + h} {x} {y + h - r} Z', ffront))

def band(x, y, w, h, fill, r=40, left=True):
    """Shadow bevel band on one vertical edge of a face."""
    if left:
        return P(f'M{x + w} {y} L{x} {y} L{x} {y + h - r} Q{x} {y + h} {x + r} {y + h} L{x + w} {y + h} Z', fill)
    return P(f'M{x} {y} L{x + w} {y} L{x + w} {y + h - r} Q{x + w} {y + h} {x + w - r} {y + h} L{x} {y + h} Z', fill)

def locker():
    W, H = 556, 992
    F, D, T = '#749A9F', '#5F7784', '#91C2C0'
    x, y, w, h = 88, 50, 380, 910
    b = topped(x, y, w, h, 96, T, F, r=48, rt=56)
    b += band(x, y + 96, 50, h - 96, D, 48)
    dx, dy, dw, dh = x + 84, y + 150, w - 124, h - 210
    b += R(dx, dy, dw, dh, F, 30)
    for i in range(3):
        b += R(dx + 60, dy + 60 + i * 50, dw - 120, 22, D, 11)
    b += R(dx + 34, dy + dh * 0.47, 30, 130, D, 15)
    return svg(W, H, f'<g id="locker">\n{b}\n</g>')
FRONTS['locker'] = locker

def wrench(cx, cy, sc, fill, dx=0, dy=0):
    d = ('M-127.8 -22 L127.8 -22 A66 66 0 0 1 250.7 -26 L184 -26 L184 26 L250.7 26 A66 66 0 0 1 127.8 22 '
         'L-127.8 22 A66 66 0 0 1 -250.7 26 L-184 26 L-184 -26 L-250.7 -26 A66 66 0 0 1 -127.8 -22 Z')
    sx = 1.0
    toks = re.findall(r'[A-Za-z]|-?[\d.]+', d); out = []; cmd = None; k = 0
    for t in toks:
        if t.isalpha(): cmd = t; k = 0; out.append(t); continue
        v = float(t)
        if cmd == 'A':  # rx ry rot large sweep x y
            v = v * sx if k in (0, 5) else v * sc if k in (1, 6) else v
            v = v + (cx + dx) if k == 5 else v + (cy + dy) if k == 6 else v
            k = (k + 1) % 7
        else:
            v = v * sx + cx + dx if k % 2 == 0 else v * sc + cy + dy
            k += 1
        out.append(f'{v:.1f}' if not (cmd == 'A' and (k - 1) % 7 in (2, 3, 4)) else t)
    return f'<path d="{" ".join(out)}" fill="{fill}" {S}/>'

def toolbox():
    W, H = 864, 912
    LID, LID_T, BODY, BODY_D, MET, MET_D = '#7D3E67', '#9C5D7B', '#EE9F60', '#B66769', '#B4BCBC', '#8D898E'
    x, w = 70, 724
    b = R(x, 520, w, 330, BODY, 44)
    b += band(x, 520, 120, 330, BODY_D, 44)
    b += topped(x, 200, w, 350, 190, LID_T, LID, r=30, rt=90)
    b += band(x, 390, 120, 160, '#60284D', 30)
    cx, cy = x + w / 2 + 10, 296
    b += f'<g id="wrench">{wrench(cx, cy, 0.9, MET_D, 0, 16).replace(S, "")}{wrench(cx, cy, 0.9, MET)}</g>'
    for lx, lw in ((x + 160, 70), (x + w / 2 - 50, 110), (x + w - 190, 70)):
        b += R(lx, 500, lw, 120, BODY, 12)
        b += R(lx + 12, 575, lw - 24, 30, BODY_D, 8)
    return svg(W, H, f'<g id="toolbox">\n{b}\n</g>')
FRONTS['toolbox'] = toolbox

def crate(x, y, s, top, frame, frame_d, panel, panel_d, show_top=True):
    out = ''
    if show_top:
        out += P(f'M{x} {y} L{x + 26} {y - top + 18} Q{x + 34} {y - top} {x + 56} {y - top} L{x + s - 56} {y - top} '
                 f'Q{x + s - 34} {y - top} {x + s - 26} {y - top + 18} L{x + s} {y} Z', frame)
        out += P(f'M{x + 70} {y - 18} L{x + 84} {y - top + 26} L{x + s - 84} {y - top + 26} L{x + s - 70} {y - 18} Z', panel_d)
    out += R(x, y, s, s, frame, 34)
    out += band(x, y + 8, 46, s - 8, frame_d, 34)
    i = 74
    out += R(x + i, y + i, s - 2 * i, s - 2 * i, panel, 10)
    out += P(f'M{x + i} {y + i + 10} Q{x + i} {y + i} {x + i + 10} {y + i} L{x + s - i} {y + i} L{x + s - i - 30} {y + i + 30} '
             f'L{x + i + 30} {y + i + 30} L{x + i + 30} {y + s - i - 30} L{x + i} {y + s - i} Z', panel_d)
    return out

def crate_stack():
    W, H = 1128, 984
    s, top = 420, 120
    x0, yb = (W - 2 * s) // 2, H - 24 - s
    b = '<g id="crate_left">' + crate(x0, yb, s, top, '#F1D7BC', '#CAA29C', '#F0C494', '#CF977C') + '</g>\n'
    b += '<g id="crate_right">' + crate(x0 + s, yb, s, top, '#F0A160', '#CF8962', '#F0A160', '#CF8962') + '</g>\n'
    b += '<g id="crate_top">' + crate(x0 + s // 2, yb - s, s, top, '#F1D7BC', '#CAA29C', '#F0C494', '#CF977C') + '</g>'
    return svg(W, H, f'<g id="crate_stack">\n{b}\n</g>')
FRONTS['crate_stack'] = crate_stack

def water_cooler():
    W, H = 544, 988
    CR, CR_D, ALC, TRAY, TAPW = '#F1D4BA', '#C59F9A', '#B17781', '#9A9498', '#E4E8DE'
    x, w, y = 62, 420, 500
    b = topped(x, y, w, H - 24 - y, 70, '#F7E2CC', CR, r=40, rt=40)
    b += band(x + w - 64, y + 70, 64, H - 24 - y - 70, CR_D, 40, left=False)
    for i in range(3):
        b += L(x + w - 50, 840 + i * 26, x + w - 16, 840 + i * 26, 9, '#A97F86')
    ax, ay, aw, ah = x + 46, 620, w - 64 - 92, 230
    b += R(ax, ay, aw, ah, ALC, 26)
    b += R(ax + 16, ay + ah - 52, aw - 32, 36, TRAY, 10)
    for tx, cap in ((ax + aw * 0.3, '#E55571'), (ax + aw * 0.7, '#8DA7C7')):
        b += R(tx - 26, ay - 4, 52, 34, cap, 12)
        b += R(tx - 20, ay + 26, 40, 70, TAPW, 12)
        b += L(tx, ay + 96, tx, ay + 124, 10)
    # bottle: reuse the traced (round, view-independent) bottle from the orig, clipped above the body
    orig = open('water_cooler_orig.svg').read()
    bottle = '\n'.join(paths_of(orig))
    b += E(x + w / 2, y + 22, 120, 30, TRAY)
    defs = f'<clipPath id="bottleClip"><rect x="0" y="0" width="{W}" height="{y + 4}"/></clipPath>'
    b += f'<g id="bottle" clip-path="url(#bottleClip)"><g transform="translate({x + w / 2 - 270} {y - 476})">\n{bottle}\n</g></g>'
    return svg(W, H, f'<g id="water_cooler">\n{b}\n</g>', defs)
FRONTS['water_cooler'] = water_cooler

def monitor(cx, y, w, h, rot):
    FR, FR_L, GL, GLARE = '#95A0A7', '#B4BEC3', '#544D67', '#716F84'
    g = f'<g transform="rotate({rot} {cx} {y + h})">'
    g += R(cx - 18, y + h - 4, 36, 54, '#7F8A93', 6) + R(cx - 70, y + h + 44, 140, 26, FR, 13)
    g += R(cx - w / 2, y, w, h, FR, 30)
    g += R(cx - w / 2 + 10, y + 8, w - 20, 22, FR_L, 11, 'stroke-width="0"')
    g += '</g>'
    gx, gy, gw, gh = cx - w / 2 + 28, y + 28, w - 56, h - 56
    glass = f'<g transform="rotate({rot} {cx} {y + h})">' + R(gx, gy, gw, gh, GL, 16)
    glass += P(f'M{gx + 24} {gy + 70} Q{gx + 26} {gy + 24} {gx + 70} {gy + 22}', 'none', f'stroke="{GLARE}" stroke-width="14"').replace(f'stroke="{OL}" stroke-width="{SW}" ', '')
    glass += '</g>'
    clip = f'<clipPath id="glass{int(cx)}"><rect transform="rotate({rot} {cx} {y + h})" x="{gx + 7}" y="{gy + 7}" width="{gw - 14}" height="{gh - 14}" rx="12"/></clipPath>'
    on = (f'<g clip-path="url(#glass{int(cx)})"><g transform="rotate({rot} {cx} {y + h})"><rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#8EE3C2"/>'
          f'<g filter="url(#feedBlur)" fill="#5BAE97"><rect x="{gx + gw * 0.12}" y="{gy + gh * 0.55}" width="{gw * 0.3}" height="{gh * 0.22}"/>'
          f'<rect x="{gx + gw * 0.5}" y="{gy + gh * 0.35}" width="{gw * 0.22}" height="{gh * 0.42}"/>'
          f'<rect x="{gx}" y="{gy + gh * 0.8}" width="{gw}" height="{gh * 0.2}" fill="#6CC2A6"/></g>'
          f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh * 0.18}" fill="#B9F4DB" opacity="0.6" filter="url(#feedBlur)"/></g></g>')
    return g, glass, clip, on

def security_desk():
    W, H = 1216, 924
    TOP, TOP_L, FRONT, DARK, GAP = '#719C9E', '#8DBFBF', '#719C9E', '#607684', '#4C5B6F'
    b = ''
    x, w = 70, 1076
    ty = 470
    b += P(f'M{x} {ty + 90} L{x + 30} {ty + 10} Q{x + 34} {ty} {x + 50} {ty} L{x + w - 50} {ty} Q{x + w - 34} {ty} {x + w - 30} {ty + 10} L{x + w} {ty + 90} Z', TOP)
    mons = [monitor(cx, 226, 250, 214, rot) for cx, rot in ((222, -7), (478, -2), (738, 2), (994, 7))]
    frames = ''.join(m[0] for m in mons)
    b += R(x, ty + 90, w, 56, DARK, 16)
    b += L(x + 24, ty + 92, x + w - 24, ty + 92, 10, TOP_L)
    py = ty + 146; ph = H - 24 - py
    b += R(x + 30, py, 250, ph, FRONT, 26) + band(x + 30, py, 54, ph, DARK, 26)
    b += R(x + 280, py, 470, ph * 0.62, GAP, 0)
    b += R(x + 750, py, w - 780, ph, FRONT, 26)
    b += band(x + 750, py, 54, ph, DARK, 26)
    for i in range(2):
        dy = py + 30 + i * (ph - 50) / 2
        b += R(x + 820, dy, w - 870 - 30, (ph - 90) / 2, FRONT, 14)
        b += L(x + 820 + (w - 900) / 2 - 40, dy + 40, x + 820 + (w - 900) / 2 + 40, dy + 40, 14)
    body = b + '\n' + frames
    off = ''.join(m[1] for m in mons)
    clips = ''.join(m[2] for m in mons)
    on = ''.join(m[3] for m in mons)
    defs = (clips +
            '<filter id="feedBlur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>')
    inner = (f'<g id="body">\n{body}\n</g>\n<g id="screens_off">\n{off}\n</g>\n'
             f'<g id="screens_on">\n{on}\n</g>')
    return svg(W, H, f'<g id="security_desk">\n{inner}\n</g>', defs)
FRONTS['security_desk'] = security_desk

def med_scanner():
    W, H = 1036, 1000
    orig = open('med_scanner_orig.svg').read()
    base = orig.split('<g id="base">', 1)[1].split('</g>', 1)[0]
    cx, cy, a = 516, 664, 482
    T, T_L, T_D = '#739C9E', '#92C4C1', '#5F7583'
    xo = a - 40; xi = xo - 110
    def arch_d(dy=0):
        return (f'M{cx - xo} {cy + 20 + dy} L{cx - xo} {352 + dy} A{xo} 300 0 0 1 {cx + xo} {352 + dy} L{cx + xo} {cy + 20 + dy} '
                f'L{cx + xi} {cy + 20 + dy} L{cx + xi} {402 + dy} A{xi} 230 0 0 0 {cx - xi} {402 + dy} L{cx - xi} {cy + 20 + dy} Z')
    arch = P(arch_d(-26), T_L)
    arch += P(arch_d(), T)
    hl = f'M{cx - xo + 36} {cy} L{cx - xo + 36} 352 A{xo - 36} 264 0 0 1 {cx} 88'
    arch += f'<path d="{hl}" fill="none" stroke="{T_L}" stroke-width="24" stroke-linecap="round"/>'
    arch += f'<path d="M{cx + xo - 30} {cy + 4} L{cx + xo - 30} 352 A{xo - 30} 270 0 0 0 {cx + xo - 150} 132" fill="none" stroke="{T_D}" stroke-width="44" stroke-linecap="round"/>'
    arch += P(arch_d(), 'none')
    rings = ''
    for ry_c in (330, 500, 660):
        rings += f'<ellipse cx="{cx}" cy="{ry_c}" rx="300" ry="78" fill="none" stroke="#3E9E87" stroke-width="44"/>'
        rings += f'<ellipse cx="{cx}" cy="{ry_c}" rx="300" ry="78" fill="none" stroke="#9EF8D2" stroke-width="24"/>'
    defs = ('<filter id="ringGlowF" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>'
            '<radialGradient id="scanLightF"><stop offset="0" stop-color="#C8F5D6" stop-opacity="0.45"/>'
            '<stop offset="0.75" stop-color="#C8F5D6" stop-opacity="0.3"/><stop offset="1" stop-color="#C8F5D6" stop-opacity="0"/></radialGradient>')
    ring = (f'<ellipse id="scan_light" cx="{cx}" cy="{cy - 10}" rx="344" ry="186" fill="url(#scanLightF)"/>\n'
            f'<g id="scan_ring_glow" filter="url(#ringGlowF)" opacity="0.7">{rings}</g>\n<g id="scan_ring_core">{rings}</g>')
    inner = (f'<g id="base">{base}</g>\n<g id="arch">\n{arch}\n</g>\n'
             f'<g id="scan_ring" data-pivot="{cx},500">\n{ring}\n</g>')
    return svg(W, H, inner, defs)
FRONTS['med_scanner'] = med_scanner

def symmetric(n):
    """Round props: the sheet view already equals the room camera view (rotationally symmetric), so the
    front version keeps the traced artwork and only marks the view."""
    def f():
        return open(f'{n}_orig.svg').read().replace('<svg ', '<svg data-view="front (round prop: same artwork as orig)" ', 1)
    return f
for _n in ('plant', 'cactus', 'floor_lamp', 'mop_bucket'):
    FRONTS[_n] = symmetric(_n)

if __name__ == '__main__':
    import json
    for n in (sys.argv[1:] or FRONTS):
        s = FRONTS[n](); open(f'{n}_front.svg', 'w').write(s)
        Image.fromarray(render(s)).save(f'/tmp/claude-0/{n}_front.png')
        print(n, len(s) // 1024, 'KB')
