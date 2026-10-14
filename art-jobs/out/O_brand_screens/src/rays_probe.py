import sys, numpy as np, cv2, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load
name, cx, cy, r0, r1 = sys.argv[1], *map(float, sys.argv[2:6])
img = load(name + ".png")
small = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2), interpolation=cv2.INTER_AREA)
def polar(c, n=2880, rs=None):
    th = np.linspace(-np.pi, np.pi, n, endpoint=False)
    rs = np.linspace(r0, r1, 120) if rs is None else rs
    X = (c[0] + np.outer(rs, np.cos(th))) / 2; Y = (c[1] + np.outer(rs, np.sin(th))) / 2
    return cv2.remap(small, X.astype(np.float32), Y.astype(np.float32), cv2.INTER_LINEAR, borderValue=(-1, -1, -1))
def score(c):
    p = polar(c, 1440)
    sat = p.max(-1) - p.min(-1)  # rays are saturated/light, background plum is dark & dull
    ray = (p[..., 0] > 150).astype(np.float32)
    valid = p[..., 0] >= 0
    v = np.where(valid, ray, np.nan)
    return np.nanmean(np.nanvar(v, 0))
best = (cx, cy); bs = score(best)
for step in (64, 32, 16, 8, 4):
    imp = True
    while imp:
        imp = False
        for dx, dy in ((step, 0), (-step, 0), (0, step), (0, -step)):
            c = (best[0] + dx, best[1] + dy); s = score(c)
            if s < bs: best, bs, imp = c, s, True
print("center", best, "score", round(float(bs), 4))
p = polar(best, 2880, np.linspace(0, r1, 400))
cv2.imwrite(sys.argv[6], cv2.resize(np.clip(p, 0, 255).astype(np.uint8)[..., ::-1], (1440, 400)))
