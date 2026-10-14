"""Fit the podium top ellipse on screens 28/29/33/34 (snaps a hand estimate onto the dark rim line)."""
import json, pathlib, sys
import numpy as np, cv2
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load

OUT = pathlib.Path(__file__).resolve().parents[1]
EST = {  # cx, cy, a, b (source px), measured on grid crops
    "28_SCREEN_REVEAL_CREW": (3150, 2085, 1770, 215),
    "29_SCREEN_REVEAL_IMPOSTOR": (2050, 3500, 1695, 218),
    "33_SCREEN_WIN_CREW": (2752, 2525, 1543, 207),
    "34_SCREEN_WIN_IMPOSTOR": (2747, 2527, 1537, 197),
}
t = np.linspace(0, 2 * np.pi, 720, endpoint=False)


def score(L, p):
    cx, cy, a, b = p
    x = (cx + a * np.cos(t)).astype(int); y = (cy + b * np.sin(t)).astype(int)
    ok = (x >= 0) & (y >= 0) & (x < L.shape[1]) & (y < L.shape[0])
    return L[y[ok], x[ok]].mean()


res = {}
for name, p in EST.items():
    img = load(name + ".png")
    L = cv2.GaussianBlur(img.mean(2), (0, 0), 3)
    p = list(map(float, p))
    for step in (24, 12, 6, 3, 1):
        improved = True
        while improved:
            improved = False
            for i in range(4):
                for d in (-step, step):
                    q = p.copy(); q[i] += d
                    if score(L, q) < score(L, p):
                        p, improved = q, True
    cx, cy, a, b = [round(v) for v in p]
    res[name] = (cx, cy, a, b, round(float(score(L, p)), 1))
    print(name, res[name])
    dbg = img.astype(np.uint8)[..., ::-1].copy()
    cv2.ellipse(dbg, (cx, cy), (a, b), 0, 0, 360, (0, 255, 0), 8)
    cv2.line(dbg, (cx - int(a * .8), cy), (cx + int(a * .8), cy), (255, 255, 0), 8)
    cv2.imwrite(str(OUT / "check" / f"podium_{name[:2]}.jpg"), cv2.resize(dbg, None, fx=.25, fy=.25))
json.dump(res, open(OUT / "src" / "podiums_fit.json", "w"))
