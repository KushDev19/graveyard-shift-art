"""Outline alignment: mean / 95th-percentile distance (source px) from each rendered outline pixel to the
nearest outline pixel of the original, and the reverse (idle / single-state drawings)."""
import re, json, numpy as np, cv2
from kcommon import load, crop, STATIONS, SHIP, main_mask
from svgcheck import render_rgba
from trace import outline_mask

OUT = __file__.rsplit('/tools/', 1)[0]
ITEMS = [(n + '_orig', '14', STATIONS[n][0]) for n in STATIONS] + [('timeclock_orig', '15', SHIP['timeclock_idle']),
         ('table_clutter_orig', '15', SHIP['table_clutter'])]
res = {}
for name, sheet, box in ITEMS:
    im = load(sheet)
    text = open(f'{OUT}/{name}.svg').read()
    x, y, w, h = map(int, re.search(r'viewBox="([-\d]+) ([-\d]+) (\d+) (\d+)"', text).groups())
    src = im[y:y + h, x:x + w]
    r = render_rgba(text, w, h); a = r[..., 3:] / 255
    comp = (r[..., :3] * a + src * (1 - a)).astype(np.uint8)
    m = main_mask(src)
    o_src = outline_mask(src, m); o_svg = outline_mask(comp, m | (a[..., 0] > 0.5))
    dt = cv2.distanceTransform((~o_src).astype(np.uint8), cv2.DIST_L2, 5)
    d = dt[o_svg]
    d2 = cv2.distanceTransform((~o_svg).astype(np.uint8), cv2.DIST_L2, 5)[o_src]  # original outline missed by the SVG
    res[name] = {'svg_to_orig_mean_px': round(float(d.mean()), 2), 'svg_to_orig_p95_px': round(float(np.percentile(d, 95)), 1),
                 'orig_to_svg_mean_px': round(float(d2.mean()), 2), 'orig_to_svg_p95_px': round(float(np.percentile(d2, 95)), 1)}
    print(name, res[name])
json.dump(res, open(f'{OUT}/tools/log_outline.json', 'w'), indent=1)
