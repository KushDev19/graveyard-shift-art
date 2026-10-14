"""Stage 4: PREVIEW.png (labeled, cream background): each room composite + its object sheet + lights/mist."""
import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
from jlib import OUT

F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f_big, f_sm = ImageFont.truetype(F, 34), ImageFont.truetype(F, 15)
CREAM, PLUM = (244, 230, 200), (42, 30, 53)
rooms = ['sickbay', 'hydroponics', 'cargo']
WIDTH = 2200
blocks = []
for r in rooms:
    man = json.load(open(OUT / r / f'{r}.json'))
    comp = Image.open(OUT / r / f'{r}_composite.png').convert('RGB')
    comp = comp.resize((1300, round(comp.height * 1300 / comp.width)))
    shell = Image.open(OUT / r / 'png' / f'{r}_shell.png').convert('RGBA')
    shell = shell.resize((600, round(shell.height * 600 / shell.width)))
    lights = Image.open(OUT / r / 'png' / f'{r}_lights.png').convert('RGBA').resize(shell.size)
    sl = Image.new('RGB', shell.size, (20, 18, 30)); sl.paste(lights, (0, 0), lights)
    if (OUT / r / 'png' / f'{r}_mist.png').exists():
        mi = Image.open(OUT / r / 'png' / f'{r}_mist.png').convert('RGBA').resize(shell.size); sl.paste(mi, (0, 0), mi)
    # object sheet
    cells, cw, ch = [], 210, 200
    for e in man['objects']:
        im = Image.open(OUT / r / e['png']).convert('RGBA'); im.thumbnail((cw - 10, ch - 34))
        c = Image.new('RGB', (cw, ch), CREAM); c.paste(im, ((cw - im.width) // 2, 4 + (ch - 34 - im.height) // 2), im)
        ImageDraw.Draw(c).text((cw // 2, ch - 16), e['id'], font=f_sm, fill=PLUM, anchor='mm')
        cells.append(c)
    cols = WIDTH // cw
    sheet = Image.new('RGB', (WIDTH, ch * ((len(cells) + cols - 1) // cols)), CREAM)
    for i, c in enumerate(cells):
        sheet.paste(c, ((i % cols) * cw, (i // cols) * ch))
    hgt = 60 + comp.height + 20 + sheet.height + 30
    b = Image.new('RGB', (WIDTH, hgt), CREAM); d = ImageDraw.Draw(b)
    d.text((20, 12), f'{r.upper()}  composite (shell + lights + objects)', font=f_big, fill=PLUM)
    b.paste(comp, (20, 60))
    b.paste(shell, (1340, 60), shell); d.text((1340, 60 + shell.height + 4), 'shell only', font=f_sm, fill=PLUM)
    y2 = 60 + shell.height + 26
    if y2 + sl.height < 60 + comp.height + 20:
        b.paste(sl, (1340, y2)); d.text((1340, y2 + sl.height + 4), 'lights' + (' + mist' if 'mist' in man else '') + ' layer (ADD)', font=f_sm, fill=PLUM)
    b.paste(sheet, (0, 60 + comp.height + 20))
    blocks.append(b)
out = Image.new('RGB', (WIDTH, sum(b.height for b in blocks)), CREAM)
y = 0
for b in blocks:
    out.paste(b, (0, y)); y += b.height
out.save(OUT / 'PREVIEW.png', optimize=True)
print(out.size)
