"""Measure each 45N character's helmet interior (dark glass) so items map onto the puppet dome."""
import json
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
from lib import ROOT, OUT
A = np.asarray(Image.open(ROOT / 'raw_originals/45N_COS_VISORS_DECALS.png').convert('RGB')).astype(int)
CHARS = {'aviator_s1': (34, 91, 870, 1485), 'aviator_s2': (870, 91, 1711, 1485), 'heart_s': (1749, 91, 2622, 1485),
         'star_f': (2834, 91, 3666, 1485), 'led_s': (3731, 91, 4554, 1485), 'led_f': (4545, 91, 5377, 1485),
         'tag_s': (49, 1587, 870, 2999), 'tag_f': (870, 1587, 1705, 2999), 'bolt_s': (1847, 1587, 2697, 2999),
         'smiley_f': (2765, 1587, 3635, 2997), 'flames_s': (3730, 1587, 4569, 2998), 'flames_f': (4564, 1587, 5400, 2985)}
if __name__ == '__main__':
    res = {}
    for k, (x0, y0, x1, y1) in CHARS.items():
        a = A[y0:y1, x0:x1]
        m = np.abs(a - [47, 31, 70]).sum(2) < 30
        m = ndi.binary_opening(m, iterations=12)
        lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); i = np.argmax(sz) + 1
        m = ndi.binary_fill_holes(ndi.binary_closing(lab == i, iterations=20))
        ys, xs = np.where(m)
        # x extent at the widest row gives centre and rx; top gives cy - ry (ry = rx * 185/196 like the puppet)
        cx = (xs.min() + xs.max()) / 2 + x0; rx = (xs.max() - xs.min()) / 2
        top = ys.min() + y0
        res[k] = {'cx': cx, 'rx': rx, 'top': int(top), 'bottom': int(ys.max() + y0), 'cy': top + rx * 185 / 196}
        print(k, {kk: round(v) for kk, v in res[k].items()})
    (OUT / 'build' / 'domes.json').write_text(json.dumps(res, indent=1))
