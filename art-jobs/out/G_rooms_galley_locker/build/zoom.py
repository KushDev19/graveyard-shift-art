"""Debug zoom: crop (quarter coords) at given scale with a 10-q grid and mask outlines in magenta."""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from tracelib import load, font
room, src, x0, y0, x1, y1, out = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7]), sys.argv[7]
s = float(sys.argv[8]) if len(sys.argv) > 8 else 2
img = load(src)
crop = img[y0*4:y1*4, x0*4:x1*4].copy()
try:
    m = np.load(f"masks_{room}.npz")
    for k in m.files:
        mm = m[k][y0*4:y1*4, x0*4:x1*4]
        if mm.any():
            e = mm & ~ndi.binary_erosion(mm, iterations=3)
            crop[e] = (255, 0, 255)
except FileNotFoundError:
    pass
im = Image.fromarray(crop).resize((int((x1-x0)*s), int((y1-y0)*s)))
d = ImageDraw.Draw(im)
for x in range((x0+9)//10*10, x1, 10):
    d.line([((x-x0)*s, 0), ((x-x0)*s, im.height)], fill=(255,255,0) if x % 50 == 0 else (90,90,90))
    if x % 50 == 0: d.text(((x-x0)*s+2, 2), str(x), fill=(255,255,0), font=font(12))
for y in range((y0+9)//10*10, y1, 10):
    d.line([(0, (y-y0)*s), (im.width, (y-y0)*s)], fill=(255,255,0) if y % 50 == 0 else (90,90,90))
    if y % 50 == 0: d.text((2, (y-y0)*s+2), str(y), fill=(255,255,0), font=font(12))
im.save(out)
