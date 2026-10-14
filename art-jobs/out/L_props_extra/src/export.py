"""PNG exports (half source scale), standalone animation/state layer SVGs, PREVIEW.png."""
import os, glob
from PIL import ImageDraw, ImageFont
from common import *
os.makedirs('png', exist_ok=True); os.makedirs('layers', exist_ok=True)
HIDE = {'med_scanner': ('scan_ring', 'idle'), 'security_desk': ('screens_on', 'off'), 'floor_lamp': ('glow', 'off')}

def hide(s, gid):
    return s.replace(f'<g id="{gid}"', f'<g id="{gid}" display="none"', 1)

def size(s):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s); return int(float(m.group(1))), int(float(m.group(2)))

def save_png(s, path):
    w, h = size(s); Image.fromarray(render(s, w // 2, h // 2)).save(path)

def layer_only(s, gid):
    """Standalone SVG with the same viewBox containing only <defs> and the given group."""
    head = s.split('>', 1)[0] + '>'
    defs = re.search(r'<defs>.*?</defs>', s, re.S)
    start = s.index(f'<g id="{gid}"'); depth = 0; i = start
    for m in re.finditer(r'<g[ >]|</g>', s[start:]):
        depth += 1 if m.group().startswith('<g') else -1
        if depth == 0: end = start + m.end(); break
    return head + '\n' + (defs.group() + '\n' if defs else '') + s[start:end] + '\n</svg>\n'

files = sorted(glob.glob('*_orig.svg') + glob.glob('*_front.svg'))
for f in files:
    s = open(f).read(); base = f[:-4]
    save_png(s, f'png/{base}.png')
    n = base.rsplit('_', 1)[0]
    if n in HIDE:
        gid, st = HIDE[n]
        save_png(hide(s, gid), f'png/{base}_{st}.png')
        lay = layer_only(s, gid)
        open(f'layers/{n}_{gid}_{base.rsplit("_", 1)[1]}.svg', 'w').write(lay)
    print(f, len(s) // 1024, 'KB')

# PREVIEW
NAMES10 = ['med_scanner', 'security_desk', 'plant', 'floor_lamp', 'crate_stack', 'water_cooler', 'locker', 'toolbox', 'mop_bucket', 'cactus']
def font(sz):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
F1, F2 = font(30), font(20)
TH = 300; CREAM = (244, 230, 200); INK = (42, 30, 53)
tiles = []
for n in NAMES10:
    ims, caps = [], []
    for v in ('orig', 'front'):
        ims.append(Image.open(f'png/{n}_{v}.png')); caps.append(v)
        if n in HIDE:
            ims.append(Image.open(f'png/{n}_{v}_{HIDE[n][1]}.png')); caps.append(f'{v} ({HIDE[n][1]})')
    ims = [i.resize((max(1, int(i.width * TH / i.height)), TH), Image.LANCZOS) for i in ims]
    w = sum(i.width for i in ims) + 24 * (len(ims) - 1) + 40
    t = Image.new('RGB', (w, TH + 110), CREAM); d = ImageDraw.Draw(t)
    d.text((20, 8), n, font=F1, fill=INK); x = 20
    for i, c in zip(ims, caps):
        t.paste(i, (x, 52), i); d.text((x, TH + 64), c, font=F2, fill=(61, 42, 79)); x += i.width + 24
    tiles.append(t)
W = 2600; rows = []; row = []; x = 0
for t in tiles:
    if x + t.width > W and row: rows.append(row); row = []; x = 0
    row.append(t); x += t.width + 20
rows.append(row)
H = 90 + sum(max(t.height for t in r) + 20 for r in rows)
out = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(out)
d.text((20, 20), 'GRAVEYARD SHIFT  Job L: extra props (sheet 38)  orig = traced from sheet, front = room camera', font=F1, fill=INK)
y = 80
for r in rows:
    x = 20
    for t in r: out.paste(t, (x, y)); x += t.width + 20
    y += max(t.height for t in r) + 20
out.save('PREVIEW.png'); print('preview', out.size)
