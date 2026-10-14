"""Step 1: segment objects, save masks (npz) and a colored debug overlay."""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rooms
from tracelib import load, segment, OUT, font

def run(cfg):
    img = load(cfg["source"])
    claimed = np.zeros(img.shape[:2], bool)
    masks = {}
    for o in cfg["objects"]:
        m = segment(img, o["poly"], claimed, cfg.get("barrier", 55), o.get("mode", "flood"),
                    o.get("core", 0), o.get("grow", 0), o.get("keep_largest", False), o.get("add"), o.get("open_r", 7))
        masks[o["id"]] = m
        claimed |= m
    np.savez_compressed(OUT / "build" / f"masks_{cfg['room']}.npz", **masks)
    small = Image.fromarray(img).resize((1376, 768))
    ov = np.array(small).astype(float) * 0.25
    base = np.array(small).astype(float)
    rng = np.random.default_rng(3)
    d_lbl = []
    for k, m in masks.items():
        ms = np.array(Image.fromarray((m * 255).astype(np.uint8)).resize((1376, 768))) > 127
        c = rng.integers(60, 255, 3)
        ov[ms] = base[ms] * 0.8 + c * 0.2
        ys, xs = np.where(ms)
        if len(xs):
            d_lbl.append((k, xs.min(), ys.min()))
    im = Image.fromarray(ov.astype(np.uint8))
    d = ImageDraw.Draw(im)
    for k, x, y in d_lbl:
        d.text((x + 2, y + 1), k, fill=(255, 255, 255), font=font(11), stroke_width=2, stroke_fill=(0, 0, 0))
    (OUT / "check").mkdir(exist_ok=True)
    im.save(OUT / "check" / f"{cfg['room']}_segments.png")

if __name__ == "__main__":
    run(getattr(rooms, sys.argv[1].upper()))
