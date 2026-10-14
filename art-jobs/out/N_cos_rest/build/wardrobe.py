"""Compose the puppet wearing each cosmetic (side + front, 3 crew colours) -> wardrobe_preview.png, PREVIEW.png."""
import json, re, sys, colorsys
from lib import ROOT, OUT, page

PUP = (ROOT / 'frontend/public/assets/ship/crew/crew_puppet.svg').read_text()
COS = json.loads((OUT / 'cosmetics.json').read_text())['items']
SIDE = ['leg_back', 'arm_back', 'leg_front', 'backpack', 'body', 'stripe', 'dome', 'visor_glow', 'visor',
        'glass_highlight', 'collar', 'antenna', 'arm_front']
FRONT = ['f_leg_l', 'f_leg_r', 'f_body', 'f_stripe', 'f_dome', 'f_visor_glow', 'f_visor', 'f_collar', 'f_antenna', 'f_arm_l', 'f_arm_r']
COLORS = {'tomato': '#E4483C', 'sky': '#6EC3F0', 'lime': '#A6D64A', 'cobalt': '#3F5FD9', 'mint': '#6FD6B0', 'mustard': '#E9C046', 'grape': '#8E5AC8'}


def tone(hx, f):
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, min(.95, l * f), s)
    return '#%02x%02x%02x' % tuple(round(v * 255) for v in (r, g, b))


def style(hx):
    return f'--suit:{hx};--suit-shade:{tone(hx,.78)};--suit-back:{tone(hx,.64)};--suit-light:{tone(hx,1.16)}'


def group_span(s, gid):
    m = re.search(r'<g id="%s"[^>]*>' % gid, s); i = m.start(); depth = 0
    for t in re.finditer(r'<g\b|</g>', s[i:]):
        depth += 1 if t.group() == '<g' else -1
        if depth == 0: return i, i + t.end()


def set_display(s, gid, show):
    m = re.search(r'<g id="%s"([^>]*)>' % gid, s)
    attrs = re.sub(r'\s*display="none"', '', m.group(1)) + ('' if show else ' display="none"')
    return s[:m.start()] + f'<g id="{gid}"{attrs}>' + s[m.end():]


def cos_inner(fname):
    t = (OUT / fname).read_text()
    return re.sub(r'^<svg[^>]*>|</svg>\s*$', '', t.strip())


def puppet(view, color, items=()):
    s = PUP
    for g in SIDE: s = set_display(s, g, view == 'side')
    for g in FRONT: s = set_display(s, g, view == 'front')
    for it in items:
        if not it[view]: continue
        for g in it['replaces'][view]: s = set_display(s, g, False)
        a, b = group_span(s, it['z'][view])
        s = s[:b] + f'\n<g class="cos-{it["id"]}">{cos_inner(it[view]["file"])}</g>' + s[b:]
    s = re.sub(r'<svg [^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -70 660 880" style="{style(COLORS[color])}">', s, 1)
    return s


def sheet(png, cells, cols, cw, ch, title, label_h=26):
    """cells: list of (label, [svg markup ...])"""
    html = ['<html><head><link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600&display=swap" rel="stylesheet">'
            '<style>body{margin:0;background:#F4E6C8;font-family:"Space Grotesk",sans-serif;color:#2A1E35}'
            f'.g{{display:grid;grid-template-columns:repeat({cols},auto);gap:10px;padding:14px}}'
            '.c{background:#EAD9B6;border:3px solid #2A1E35;border-radius:12px;padding:4px 6px}'
            f'.c b{{display:block;font-size:17px;height:{label_h}px}}.r{{display:flex}}'
            f'.r svg{{width:{cw}px;height:{ch}px}}h1{{margin:14px 14px 0;font-size:26px}}</style></head><body>'
            f'<h1>{title}</h1><div class="g">']
    for label, svgs in cells:
        html.append(f'<div class="c"><b>{label}</b><div class="r">{"".join(svgs)}</div></div>')
    html.append('</div></body></html>')
    p = page(); p.set_viewport_size({'width': 800, 'height': 600})
    p.set_content(''.join(html)); p.wait_for_timeout(400)
    p.screenshot(path=str(png), full_page=True)


if __name__ == '__main__':
    only = sys.argv[1:]
    items = [it for it in COS if not only or any(o in it['id'] for o in only)]
    cells = []
    for it in items:
        svgs = [puppet('side', c, [it]) for c in ('tomato', 'cobalt', 'mint')]
        if it['front']: svgs += [puppet('front', c, [it]) for c in ('tomato', 'cobalt', 'mint')]
        cells.append((it['id'], svgs))
    out = OUT / ('wardrobe_preview.png' if not only else 'build/_wip.png')
    sheet(out, cells, 2 if not only else 2, 96, 128, 'Job N wardrobe: every item on the puppet, side + front, 3 crew colours')
    print(out)
