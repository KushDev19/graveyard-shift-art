"""Shared helpers for Job O: green keying, background plates, MAE and check images."""
import numpy as np
import cv2
from PIL import Image

ROOT = __import__("pathlib").Path(__file__).resolve().parents[4]
RAW = ROOT / "raw_originals"


def load(name):
    return np.asarray(Image.open(RAW / name).convert("RGB")).astype(np.float32)


def gex(img):
    return img[..., 1] - np.maximum(img[..., 0], img[..., 2])


def bg_plate(img, thresh=80, scale=8, sigma=12):
    """Estimate the (uneven) green background everywhere, including behind the subject."""
    h, w = img.shape[:2]
    m = (gex(img) > thresh).astype(np.float32)
    small = cv2.resize(img * m[..., None], (w // scale, h // scale), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (w // scale, h // scale), interpolation=cv2.INTER_AREA)
    for s in (sigma, sigma * 3, sigma * 9):
        num = cv2.GaussianBlur(small, (0, 0), s)
        den = cv2.GaussianBlur(ms, (0, 0), s)[..., None]
        est = num / np.maximum(den, 1e-4)
        if s == sigma:
            out = est.copy(); ok = den[..., 0] > 0.05
        else:
            fill = (~ok) & (den[..., 0] > 0.02)
            out[fill] = est[fill]; ok |= fill
    return cv2.resize(out, (w, h), interpolation=cv2.INTER_LINEAR)


def key(img, plate=None, solid=12):
    """Return (alpha 0..1, unmixed RGB, plate). Alpha from green excess relative to the local plate."""
    if plate is None:
        plate = bg_plate(img)
    g = gex(img)
    gb = np.maximum(gex(plate), 60)
    a = np.clip((gb - g) / (gb - solid), 0, 1)
    a[g <= solid] = 1
    am = np.maximum(a, 1e-3)[..., None]
    fg = (img - (1 - am) * plate) / am
    fg = np.clip(fg, 0, 255)
    # despill: green may not exceed max(R,B)+small where partly transparent
    lim = np.maximum(fg[..., 0], fg[..., 2]) + 18
    edge = a < 0.98
    fg[..., 1] = np.where(edge, np.minimum(fg[..., 1], lim), fg[..., 1])
    return a, fg, plate


def mae(svg_rgba, orig, plate, bbox, down=4):
    """Composite SVG render over the background plate, MAE vs original inside bbox at 1/down scale."""
    x0, y0, x1, y1 = bbox
    a = svg_rgba[y0:y1, x0:x1, 3:4] / 255.0
    comp = svg_rgba[y0:y1, x0:x1, :3] * a + plate[y0:y1, x0:x1] * (1 - a)
    o = orig[y0:y1, x0:x1]
    sz = ((x1 - x0) // down, (y1 - y0) // down)
    c = cv2.resize(comp.astype(np.float32), sz, interpolation=cv2.INTER_AREA)
    o = cv2.resize(o.astype(np.float32), sz, interpolation=cv2.INTER_AREA)
    return float(np.abs(c - o).mean()), comp


def checks(name, comp, orig_crop, outdir, maxw=1800):
    o = orig_crop.astype(np.uint8); c = np.clip(comp, 0, 255).astype(np.uint8)
    sbs = np.concatenate([o, c], 1)
    onion = (o.astype(np.float32) * 0.5 + c * 0.5).astype(np.uint8)
    for tag, im in (("side_by_side", sbs), ("onion", onion)):
        p = Image.fromarray(im)
        if p.width > maxw:
            p = p.resize((maxw, int(p.height * maxw / p.width)), Image.LANCZOS)
        p.save(outdir / f"{name}_{tag}.png")
