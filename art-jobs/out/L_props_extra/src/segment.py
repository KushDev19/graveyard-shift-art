"""Key the magenta background of sheet 38 and list object bboxes (source px)."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
SRC = '../../../raw_originals/38_PROPS_EXTRA.png'
a = np.asarray(Image.open(SRC).convert('RGB')).astype(np.int16)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
bg = (r > 200) & (b > 200) & (g < 60)
fg = ~bg
small = fg[::4, ::4]
small = ndi.binary_closing(small, iterations=6)
lab, n = ndi.label(small)
objs = []
for i, sl in enumerate(ndi.find_objects(lab)):
    area = (lab[sl] == i + 1).sum()
    if area < 400: continue
    y0, y1, x0, x1 = sl[0].start*4, sl[0].stop*4, sl[1].start*4, sl[1].stop*4
    objs.append(dict(x=x0, y=y0, w=x1-x0, h=y1-y0, area=int(area)))
objs.sort(key=lambda o: (round(o['y']/800), o['x']))
for o in objs: print(o)
json.dump(objs, open('src/bboxes_raw.json', 'w'), indent=1)
