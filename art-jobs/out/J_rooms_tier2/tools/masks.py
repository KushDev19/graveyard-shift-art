"""Stage 1: object masks -> work/<room>_masks.npz and an overlay PNG to eyeball."""
import sys, numpy as np
from PIL import Image
from jlib import *
from rooms import ROOMS

def build(room):
    spec = ROOMS[room]; img = load(spec['src']); outl = outline_mask(img)
    taken = np.zeros(img.shape[:2], bool); masks = {}
    for o in spec['objects']:
        reg = poly_mask(img.shape, sc(o['region']))
        ex = taken.copy()
        for e in o.get('excl', []):
            ex |= poly_mask(img.shape, sc(e))
        add = None
        for a in o.get('add', []):
            add = poly_mask(img.shape, sc(a)) | (add if add is not None else False)
        m = object_mask(img, outl, reg, ex, keep_frac=o.get('keep', 0.02), add=add, wall_tol=o.get('wall_tol', 0))
        masks[o['id']] = m; taken |= m
    (OUT / 'work').mkdir(exist_ok=True)
    np.savez_compressed(OUT / 'work' / f'{room}_masks.npz', **masks)
    ov = img.astype(float) * 0.45
    rng = np.random.default_rng(3)
    for k, m in masks.items():
        c = rng.integers(80, 255, 3)
        ov[m] = img[m] * 0.5 + c * 0.5
    Image.fromarray(ov.astype(np.uint8)).resize((2000, round(img.shape[0] / K))).save(OUT / 'work' / f'{room}_masks.png')

if __name__ == '__main__':
    for r in sys.argv[1:]:
        build(r)
