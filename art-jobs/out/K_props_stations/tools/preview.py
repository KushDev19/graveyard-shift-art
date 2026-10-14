"""PREVIEW.png: every export, labeled, on cream."""
from PIL import Image, ImageDraw, ImageFont

OUT = __file__.rsplit('/tools/', 1)[0]
ROWS = [
    ('station_keypad', ['idle', 'highlight', 'done']),
    ('station_switchboard', ['idle', 'highlight', 'done']),
    ('station_tape', ['idle', 'highlight', 'done']),
    ('station_scope', ['idle', 'highlight', 'done']),
    ('timeclock', ['idle', 'ready']),
]
CELL = 250


def font(sz):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def thumb(path):
    im = Image.open(path).convert('RGBA')
    im.thumbnail((CELL - 20, CELL - 40))
    return im


def main():
    cells = []
    for name, states in ROWS:
        row = [(f'{name}_orig_{s}', f'png/{name}_orig_{s}.png') for s in states]
        row += [(f'{name}_front_{s}', f'png/{name}_front_{s}.png') for s in states]
        cells.append(row)
    cells.append([('vent_orig closed', 'png/vent_orig_closed.png'), ('vent_orig open', 'png/vent_orig_open.png'),
                  ('vent_frame_orig', 'png/vent_frame_orig.png'), ('vent_front closed', 'png/vent_front_closed.png'),
                  ('vent_front open', 'png/vent_front_open.png'), ('vent_frame_front', 'png/vent_frame_front.png')])
    cells.append([('table_clutter_orig', 'png/table_clutter_orig.png'), ('table_clutter_front', 'png/table_clutter_front.png')])
    cols = max(len(r) for r in cells)
    W, H = cols * CELL + 40, len(cells) * CELL + 110
    o = Image.new('RGB', (W, H), (0xF4, 0xE6, 0xC8))
    d = ImageDraw.Draw(o)
    d.text((20, 18), 'JOB K  task stations + ship props   (left: *_orig as drawn, right: *_front re-projected)', fill=(0x2A, 0x1E, 0x35), font=font(26))
    f = font(13)
    for r, row in enumerate(cells):
        for c, (label, p) in enumerate(row):
            x, y = 20 + c * CELL, 80 + r * CELL
            t = thumb(f'{OUT}/{p}')
            o.paste(t, (x + (CELL - t.width) // 2, y + (CELL - 30 - t.height) // 2), t)
            d.text((x + 6, y + CELL - 28), label, fill=(0x2A, 0x1E, 0x35), font=f)
        if len(row) == 6:
            d.line([(20 + 3 * CELL - 4, 80 + r * CELL + 10), (20 + 3 * CELL - 4, 80 + (r + 1) * CELL - 10)], fill=(0x3D, 0x2A, 0x4F), width=2)
        elif len(row) == 4:
            d.line([(20 + 2 * CELL - 4, 80 + r * CELL + 10), (20 + 2 * CELL - 4, 80 + (r + 1) * CELL - 10)], fill=(0x3D, 0x2A, 0x4F), width=2)
    o.save(f'{OUT}/PREVIEW.png')
    print(o.size)


if __name__ == '__main__':
    main()
