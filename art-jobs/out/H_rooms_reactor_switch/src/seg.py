"""Segmentation helpers: rasterise rough shapes (source px), refine with GrabCut at work scale."""
import numpy as np, cv2

WS = 2  # work scale divisor (trace at half source resolution)


def raster(shapes, H, W, s=WS):
    """shapes: list of ('poly', pts) | ('ell', cx, cy, rx, ry) | ('rect', x0, y0, x1, y1) | ('sub', shape)"""
    m = np.zeros((H, W), np.uint8)
    for sh in shapes:
        val = 255
        if sh[0] == 'sub':
            sh, val = sh[1], 0
        if sh[0] == 'poly':
            cv2.fillPoly(m, [np.round(np.array(sh[1], float) / s).astype(np.int32)], val)
        elif sh[0] == 'ell':
            cv2.ellipse(m, (round(sh[1] / s), round(sh[2] / s)), (round(sh[3] / s), round(sh[4] / s)), 0, 0, 360, val, -1)
        elif sh[0] == 'line':
            cv2.polylines(m, [np.round(np.array(sh[1], float) / s).astype(np.int32)], False, val, max(1, round(sh[2] / s)))
            for p in sh[1]:
                cv2.circle(m, (round(p[0] / s), round(p[1] / s)), round(sh[2] / s / 2), val, -1)
        elif sh[0] == 'rect':
            cv2.rectangle(m, (round(sh[1] / s), round(sh[2] / s)), (round(sh[3] / s), round(sh[4] / s)), val, -1)
    return m > 0


def grabcut(img, region, margin=14, sure=10, iters=5):
    """img: HxWx3 uint8 RGB at work scale; region: bool mask (generous). Returns refined bool mask."""
    H, W = region.shape
    ys, xs = np.nonzero(region)
    x0, x1 = max(xs.min() - margin * 2, 0), min(xs.max() + margin * 2 + 1, W)
    y0, y1 = max(ys.min() - margin * 2, 0), min(ys.max() + margin * 2 + 1, H)
    r = region[y0:y1, x0:x1].astype(np.uint8)
    k = lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * n + 1, 2 * n + 1))
    gm = np.full(r.shape, cv2.GC_BGD, np.uint8)
    gm[cv2.dilate(r, k(margin)) > 0] = cv2.GC_PR_BGD
    gm[r > 0] = cv2.GC_PR_FGD
    if sure:
        gm[cv2.erode(r, k(sure)) > 0] = cv2.GC_FGD
    bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
    crop = np.ascontiguousarray(img[y0:y1, x0:x1, ::-1])
    cv2.grabCut(crop, gm, None, bgd, fgd, iters, cv2.GC_INIT_WITH_MASK)
    out = np.zeros((H, W), bool)
    out[y0:y1, x0:x1] = (gm == cv2.GC_FGD) | (gm == cv2.GC_PR_FGD)
    return out


def clean(m, close=2, min_area=40):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * close + 1, 2 * close + 1))
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, k)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= min_area
    m = keep[lab]
    # fill small holes (enclosed bg specks)
    inv = (~m).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    small = np.zeros(n, bool)
    small[1:] = st[1:, cv2.CC_STAT_AREA] < min_area
    return m | small[lab]


def hsv(img):
    h = cv2.cvtColor(img, cv2.COLOR_RGB2HSV_FULL).astype(np.int32)
    return h[..., 0] * 360 // 256, h[..., 1] / 255.0, h[..., 2] / 255.0


def warm(img):
    """True for pipe/cable/prop colours (cream, mauve, plum outline, wood); False for teal/blue walls and floor."""
    h, s, v = hsv(img)
    cool = (h >= 150) & (h <= 250) & (s > 0.12)
    return ~cool


def grabcut_init(img, region, fg, iters=4):
    """GrabCut seeded with a colour guess: fg -> probable fg, rest of region -> probable bg."""
    H, W = region.shape
    ys, xs = np.nonzero(region)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    gm = np.full((y1 - y0, x1 - x0), cv2.GC_BGD, np.uint8)
    gm[region[y0:y1, x0:x1]] = cv2.GC_PR_BGD
    gm[fg[y0:y1, x0:x1]] = cv2.GC_PR_FGD
    bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(np.ascontiguousarray(img[y0:y1, x0:x1, ::-1]), gm, None, bgd, fgd, iters, cv2.GC_INIT_WITH_MASK)
    out = np.zeros((H, W), bool)
    out[y0:y1, x0:x1] = (gm == cv2.GC_FGD) | (gm == cv2.GC_PR_FGD)
    return out


def steam(img, region, ow=10):
    """Light grey puff + its dark outline."""
    h, s, v = hsv(img)
    light = region & (v > 0.55) & (s < 0.3) & ~((h > 12) & (h < 55) & (s > 0.12))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))
    near = cv2.dilate(light.astype(np.uint8), k) > 0
    m = light | (near & region & (v < 0.3))
    return m
