"""PREVIEW.png: both composites + every layer (half-scale PNG) labeled on cream."""
import json, pathlib
from PIL import Image, ImageDraw, ImageFont
OUT = pathlib.Path(__file__).resolve().parent.parent
F = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)
CREAM, PLUM = (244, 230, 200), (42, 30, 53)
W = 2400
tiles = []
for room in ['radio', 'bridge']:
    man = json.loads((OUT / room / f'{room}.json').read_text())
    tiles.append(('__room__', room, Image.open(OUT / room / f'{room}_composite.png')))
    items = [('space', man['background'])] + [(e['id'], e) for e in man.get('background_children', []) + man['objects'] + man['children']]
    for name, e in items:
        im = Image.open(OUT / room / pathlib.Path(e['file']).with_suffix('.png')).convert('RGBA')
        tiles.append((f'{room}_{name}', e.get('parent', ''), im))
    tiles.append((f'{room}_shell', '', Image.open(OUT / room / f'{room}_shell.png').convert('RGBA')))
    if (OUT / room / f'{room}_light_pools.png').exists():
        tiles.append((f'{room}_light_pools', 'screen, always on', Image.open(OUT / room / f'{room}_light_pools.png').convert('RGBA')))
    tiles.append((f'{room}_lights_glow', 'effect layer', Image.open(OUT / room / f'{room}_lights_glow.png').convert('RGBA')))
rows, cur, x, rowh = [], [], 0, 0
cell = 270
canvas_parts = []
y = 70
pos = []
for name, sub, im in tiles:
    if name == '__room__':
        if x:
            y += rowh + 50
            x, rowh = 0, 0
        r = im.copy()
        r.thumbnail((W - 40, 900))
        pos.append((20, y, r, f'{sub.upper()} composite (shell + layers, MAE-checked)', ''))
        y += r.height + 60
        continue
    r = im.copy()
    if name.endswith(('_shell', '_lights_glow', '_light_pools', '_space')):
        r.thumbnail((560, 320))
    else:
        r.thumbnail((cell, cell))
    if x + r.width + 20 > W:
        y += rowh + 50
        x, rowh = 0, 0
    pos.append((x + 20, y, r, name, sub))
    x += max(r.width, 300) + 30
    rowh = max(rowh, r.height)
H = y + rowh + 60
can = Image.new('RGB', (W, H), CREAM)
d = ImageDraw.Draw(can)
d.text((20, 15), 'Job I  -  Radio Room + Bridge  (layered SVG, labels = file ids)', fill=PLUM, font=F(34))
for px, py, r, name, sub in pos:
    if name.endswith(('_lights_glow', '_light_pools')):
        bg = Image.new('RGB', r.size, (27, 24, 48))
        bg.paste(r, (0, 0), r)
        can.paste(bg, (px, py))
    elif r.mode == 'RGBA':
        can.paste(r, (px, py), r)
    else:
        can.paste(r, (px, py))
    d.text((px, py + r.height + 4), name + (f'  [{sub}]' if sub else ''), fill=PLUM, font=F(17))
can.save(OUT / 'PREVIEW.png', optimize=True)
print(can.size)
