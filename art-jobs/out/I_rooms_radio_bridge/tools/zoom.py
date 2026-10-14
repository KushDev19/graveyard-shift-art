"""Montage of original|composite crops: python zoom.py room out.png x0,y0,x1,y1 ..."""
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
room, out = sys.argv[1], sys.argv[2]
src = {'radio': '08_ROOM_RADIO.png', 'bridge': '09_ROOM_BRIDGE.png'}[room]
o = Image.open(f'../../../raw_originals/{src}').convert('RGB')
c = Image.open(f'{room}/{room}_composite.png').convert('RGB').resize(o.size)
rows = []
for box in sys.argv[3:]:
    b = tuple(int(v) for v in box.split(','))
    a, z = o.crop(b), c.crop(b)
    s = 380 / a.height
    a, z = a.resize((int(a.width * s), 380)), z.resize((int(a.width * s), 380))
    rows.append(np.hstack([np.array(a), np.full((380, 6, 3), 255, np.uint8), np.array(z)]))
W = max(r.shape[1] for r in rows)
rows = [np.pad(r, ((0, 6), (0, W - r.shape[1]), (0, 0))) for r in rows]
Image.fromarray(np.vstack(rows)).save(out)
