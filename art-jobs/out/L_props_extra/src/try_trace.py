import sys, numpy as np, time
from common import *
n = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 14
c = crop(n); q = prep(n, k)
t = time.time(); s = trace(q, color_precision=8, layer_difference=1, filter_speckle=10, mode='spline')
print('trace', round(time.time() - t, 1), 's', len(s) // 1024, 'KB', len(paths_of(s)), 'paths')
open(f'/tmp/claude-0/{n}_try.svg', 'w').write(s)
m, comp, r = mae(n, s); print('MAE', round(m, 2))
from PIL import Image
Image.fromarray(np.hstack([c, comp])).save(f'/tmp/claude-0/{n}_sbs.png')
