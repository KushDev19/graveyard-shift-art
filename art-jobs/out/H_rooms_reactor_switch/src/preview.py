"""PREVIEW.png: both rebuilt rooms + every exported piece, labelled, on cream."""
import json, glob, pathlib
from PIL import Image, ImageDraw, ImageFont
OUT = pathlib.Path(__file__).resolve().parent.parent
try:
    F = ImageFont.truetype('DejaVuSans-Bold.ttf', 14); FB = ImageFont.truetype('DejaVuSans-Bold.ttf', 26)
except OSError:
    F = FB = ImageFont.load_default()
CREAM, INK = (244, 230, 200), (42, 30, 53)
W = 2400
tiles = []
for room in ('reactor', 'switchboard'):
    man = json.load(open(OUT / f'{room}.json'))
    for o in man['objects']:
        tiles.append((f'{room}/{o["id"]}  MAE {o["mae"]}', OUT / 'png' / pathlib.Path(o['file']).name.replace('.svg', '.png')))
        for k, f in o.get('layers', {}).items():
            tiles.append((f'  layer: {k}', OUT / 'png' / pathlib.Path(f).name.replace('.svg', '.png')))
    for k, s in man.get('sprites', {}).items():
        tiles.append((f'{room}/{k} (sprite)', OUT / s['file'].replace('objects/', 'png/').replace('.svg', '.png')))
cell, cols = 290, 8
rows = (len(tiles) + cols - 1) // cols
top = 60 + 2 * (W // 2 * 1536 // 2754) // 1
im = Image.new('RGB', (W, 60 + (W // 2 - 20) * 1536 // 2754 + 60 + rows * (cell + 40) + 20), CREAM)
d = ImageDraw.Draw(im)
d.text((20, 15), 'Job H: Reactor + Switchboard, rebuilt from layered SVG (shell + objects composite)', fill=INK, font=FB)
for i, room in enumerate(('reactor', 'switchboard')):
    c = Image.open(OUT / 'check' / f'{room}_composite.png').convert('RGB')
    c = c.resize((W // 2 - 20, (W // 2 - 20) * c.height // c.width))
    im.paste(c, (10 + i * W // 2, 60))
y0 = 60 + (W // 2 - 20) * 1536 // 2754 + 40
for n, (label, f) in enumerate(tiles):
    x, y = 10 + (n % cols) * (cell + 10), y0 + (n // cols) * (cell + 40)
    t = Image.open(f).convert('RGBA')
    t.thumbnail((cell, cell - 10))
    bg = Image.new('RGBA', (cell, cell - 10), (120, 146, 150, 255))  # teal swatch so cream pieces read
    bg.alpha_composite(t, ((cell - t.width) // 2, (cell - 10 - t.height) // 2))
    im.paste(bg.convert('RGB'), (x, y))
    d.text((x, y + cell - 8), label[:38], fill=INK, font=F)
im.save(OUT / 'PREVIEW.png', optimize=True)
print(im.size, len(tiles))
