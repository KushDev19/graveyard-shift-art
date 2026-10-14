import sys, numpy as np
from PIL import Image
from tracelib import OUT
room = sys.argv[1]
m = np.load(f"masks_{room}.npz")
acc = np.zeros(m[m.files[0]].shape + (3,), np.uint8)
rng = np.random.default_rng(5)
for k in m.files:
    acc[m[k]] = rng.integers(90, 255, 3)
Image.fromarray(acc).resize((1376, 768)).save(OUT / "check" / f"{room}_maskmap.png")
