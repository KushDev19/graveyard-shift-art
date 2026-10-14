"""Cut Gemini pose sheets (two poses on flat green) into transparent pose PNGs.

For each pose writes, into frontend/public/assets/ship/crew/poses/:
  pose_<name>.png        full art (grey suit)
  pose_<name>_suit.png   only the neutral-grey suit pixels, normalized to white -> multiply-tint with the player color
  pose_<name>_fixed.png  everything else (outlines, helmet, visor, stripes, highlights)
Usage: py -3.12 key_poses.py <sheet image> <left name> <right name> [...more triples]"""
import sys

import numpy as np
from PIL import Image

from svgtools import ROOT, WORK

OUT = ROOT / "frontend/public/assets/ship/crew/poses"
MAX_H = 1200  # output height cap (in-game poses are shown far smaller)


def shift_max(m, r, axis):
    out = m.copy()
    for d in range(1, r + 1):
        out |= np.roll(m, d, axis) | np.roll(m, -d, axis)
    return out


def dilate(m, r):
    return shift_max(shift_max(m, r, 0), r, 1)


def erode(m, r):
    return ~dilate(~m, r)


def majority(m, r):
    """True where more than half of the (2r+1)^2 neighbourhood is True (integral-image box filter)."""
    k = 2 * r + 1
    p = np.pad(m.astype(np.int32), r + 1, mode="edge")
    s = p.cumsum(0).cumsum(1)
    box = s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k]
    return box[:m.shape[0], :m.shape[1]] * 2 > k * k


def key(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gdom = g - np.maximum(r, b)
    alpha = np.clip((70 - gdom) / 50, 0, 1)
    edge = (alpha < 0.98) & (g > np.maximum(r, b))
    a[..., 1] = np.where(edge, np.maximum(r, b), g)  # despill only at the soft edge (keeps seafoam visors)
    solid = alpha > 0.5
    solid = dilate(erode(solid, 2), 2)  # drop specks
    alpha = np.where(solid | (alpha > 0.9), alpha, 0)
    alpha = np.clip((alpha - 0.3) / 0.55, 0, 1)  # firm edges; drops blur/smudge residue
    return a, alpha


def split_columns(alpha):
    cols = (alpha > 0.5).sum(axis=0) > 3
    w = len(cols)
    best, run_start, best_mid = 0, None, w // 2
    for x in range(int(w * 0.3), int(w * 0.75)):
        if not cols[x]:
            run_start = x if run_start is None else run_start
            if x - run_start > best:
                best, best_mid = x - run_start, (x + run_start) // 2
        else:
            run_start = None
    return best_mid


def crop_pose(a, alpha, x0, x1, pad=16):
    sub = alpha[:, x0:x1] > 0.5
    ys, xs = np.nonzero(sub)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, alpha.shape[0])
    cx0, cx1 = max(xs.min() - pad + x0, 0), min(xs.max() + pad + x0, alpha.shape[1])
    rgba = np.dstack([a[y0:y1, cx0:cx1], alpha[y0:y1, cx0:cx1] * 255]).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    if im.height > MAX_H:
        im = im.resize((round(im.width * MAX_H / im.height), MAX_H), Image.LANCZOS)
    return im


def split_suit(im):
    a = np.asarray(im).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3] / 255
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    val = mx / 255
    # hue in degrees (only meaningful when saturated): AI greys lean purple, so accept a little purple tint
    r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = (np.degrees(np.arctan2(np.sqrt(3) * (g_ - b_), 2 * r_ - g_ - b_)) + 360) % 360
    purple_grey = (sat < 0.17) & (hue > 215) & (hue < 330)
    suit = ((sat < 0.08) | purple_grey) & (val > 0.38) & (al > 0.5)
    suit = majority(suit, 3)  # kill JPEG speckles
    # glass highlights are light & unsaturated too: drop the ones sitting inside the dark dome
    dark = (val < 0.33) & (al > 0.5)
    core = erode(dark, 7)
    suit &= ~dilate(core, 25)
    suit_rgba = a.copy()
    lum = rgb.mean(axis=2)
    ref = np.percentile(lum[suit], 92) if suit.any() else 255
    suit_rgba[..., :3] = np.clip(rgb * (255 / max(ref, 1)), 0, 255)
    suit_rgba[..., 3] = np.where(suit, a[..., 3], 0)
    fixed = a.copy()
    fixed[..., 3] = np.where(suit, 0, a[..., 3])
    return (Image.fromarray(suit_rgba.astype(np.uint8), "RGBA"),
            Image.fromarray(fixed.astype(np.uint8), "RGBA"))


def tinted(suit, fixed, color):
    c = np.array([int(color[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    s = np.asarray(suit).astype(np.float32)
    s[..., :3] *= c
    base = Image.fromarray(s.astype(np.uint8), "RGBA")
    base.alpha_composite(fixed)
    return base


def main(args):
    OUT.mkdir(parents=True, exist_ok=True)
    previews = []
    for i in range(0, len(args), 3):
        src, left, right = args[i:i + 3]
        a, alpha = key(Image.open(src))
        mid = split_columns(alpha)
        for name, (x0, x1) in ((left, (0, mid)), (right, (mid, alpha.shape[1]))):
            im = crop_pose(a, alpha, x0, x1)
            suit, fixed = split_suit(im)
            im.save(OUT / f"pose_{name}.png")
            suit.save(OUT / f"pose_{name}_suit.png")
            fixed.save(OUT / f"pose_{name}_fixed.png")
            previews.append((name, im, suit, fixed))
            print(name, im.size)
    # preview: each pose in grey + 3 crew colors on cream
    cell = 260
    sheet = Image.new("RGB", (cell * 4, cell * len(previews)), (244, 230, 200))
    for row, (name, im, suit, fixed) in enumerate(previews):
        for col, c in enumerate([None, "#E4483C", "#6FD6B0", "#3F5FD9"]):
            t = im if c is None else tinted(suit, fixed, c)
            t = t.copy()
            t.thumbnail((cell - 10, cell - 10))
            sheet.paste(t, (col * cell + (cell - t.width) // 2, row * cell + (cell - t.height) // 2), t)
    sheet.save(WORK / "poses_keyed_preview.png")


if __name__ == "__main__":
    main(sys.argv[1:])
