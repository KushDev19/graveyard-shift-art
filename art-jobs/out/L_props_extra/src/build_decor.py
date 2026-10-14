"""Trace the simple decor props of sheet 38 into *_orig.svg (one named group each)."""
import sys, json
from common import *
TRACE = dict(color_precision=8, layer_difference=1, filter_speckle=10, mode='spline')
K = dict(plant=14, crate_stack=12, water_cooler=16, locker=12, toolbox=14, mop_bucket=14, cactus=16)
EXTRA = dict(water_cooler=[(229, 85, 113), (141, 167, 199)])
res = json.load(open('src/mae.json')) if len(sys.argv) > 1 else {}
for n in (sys.argv[1:] or K):
    q = prep(n, K[n], extra=EXTRA.get(n, ()))
    svg = wrap(n, group(n, trace(q, **TRACE)))
    open(f'{n}_orig.svg', 'w').write(svg)
    res[n] = round(checks(n, svg), 2)
    print(n, res[n], len(svg) // 1024, 'KB')
json.dump(res, open('src/mae.json', 'w'), indent=1)
