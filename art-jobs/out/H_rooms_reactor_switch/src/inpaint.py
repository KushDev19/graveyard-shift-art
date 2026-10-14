"""Repaint the shell behind removed objects, zone by zone (so walls never bleed into floor)."""
import numpy as np, cv2, seg


def period_x(img, band, known):
    ys, xs = np.nonzero(band & known)
    y0, y1 = ys.min(), ys.max()
    row = img[(y0 + y1) // 2].astype(float).mean(1)
    ok = (band & known)[(y0 + y1) // 2]
    best, bp = 1e9, 40
    for p in range(20, 200):
        a, b = ok[:-p], ok[p:]
        sel = a & b
        if sel.sum() < 200:
            continue
        e = np.abs(row[:-p][sel] - row[p:][sel]).mean()
        if e < best:
            best, bp = e, p
    return bp


def telea(img, hole, zone, r=6):
    """Fill hole∩zone using only known pixels from the zone."""
    tgt = hole & zone
    if not tgt.any():
        return img
    ys, xs = np.nonzero(tgt)
    m = 40
    y0, y1, x0, x1 = max(ys.min() - m, 0), ys.max() + m + 1, max(xs.min() - m, 0), xs.max() + m + 1
    sub = img[y0:y1, x0:x1].copy()
    msk = (hole | ~zone)[y0:y1, x0:x1].astype(np.uint8)
    # coarse-to-fine for big holes: inpaint at 1/4 then refine
    coarse = pushpull(sub, msk == 0)
    pre = sub.copy()
    pre[msk > 0] = coarse[msk > 0]
    # fine pass only near the hole border (known pixels within 12px)
    inner = cv2.erode(msk, np.ones((25, 25), np.uint8))
    fine_mask = (msk > 0) & ~(inner > 0)
    fine = cv2.inpaint(np.where(inner[..., None] > 0, pre, sub).astype(np.uint8), fine_mask.astype(np.uint8), r, cv2.INPAINT_TELEA)
    res = np.where(inner[..., None] > 0, pre, fine)
    out = img.copy()
    t = tgt[y0:y1, x0:x1]
    out[y0:y1, x0:x1][t] = res[t]
    return out


def period_vec(img, zone, known, u):
    ys, xs = np.nonzero(zone & known)
    g = img.astype(float).mean(2)
    best, bp = 1e9, 40
    for p in range(20, 200):
        yy, xx = np.round(ys + p * u[1]).astype(int), np.round(xs + p * u[0]).astype(int)
        ok = (yy >= 0) & (yy < g.shape[0]) & (xx >= 0) & (xx < g.shape[1])
        ok[ok] = (zone & known)[yy[ok], xx[ok]]
        if ok.sum() < 300:
            continue
        e = np.abs(g[ys[ok], xs[ok]] - g[yy[ok], xx[ok]]).mean()
        if e < best:
            best, bp = e, p
    return bp


def periodic(img, hole, zone, u=(1.0, 0.0)):
    known = ~hole
    u = np.array(u, float) / np.hypot(*u)
    p = period_x(img, zone, known) if u[1] == 0 else period_vec(img, zone, known, u)
    out = img.copy()
    ys, xs = np.nonzero(hole & zone)
    H, W = img.shape[:2]
    todo = np.ones(len(ys), bool)
    for k in [1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, -9, 10, -10, 12, -12, 14, -14]:
        xx = np.round(xs + k * p * u[0]).astype(int)
        yy = np.round(ys + k * p * u[1]).astype(int)
        ok = todo & (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
        ok[ok] = (zone & known)[yy[ok], xx[ok]]
        out[ys[ok], xs[ok]] = img[yy[ok], xx[ok]]
        todo &= ~ok
    left = np.zeros(hole.shape, bool)
    left[ys[todo], xs[todo]] = True
    return out, p, left


def repaint(img, hole, zones, H, W):
    """zones: list of (name, shapes, method). Pixel belongs to the first zone that contains it."""
    taken = np.zeros(hole.shape, bool)
    out = img.copy()
    for name, shapes, method in zones:
        z = (seg.raster(shapes, H, W) if shapes else np.ones(hole.shape, bool)) & ~taken
        taken |= z
        if method == 'periodic' or (isinstance(method, tuple) and method[0] == 'periodic'):
            out, p, left = periodic(out, hole, z, *(method[1:] if isinstance(method, tuple) else ()))
            if left.any():
                out = telea(out, left, z)
        else:
            out = telea(out, hole, z)
    return out


def pushpull(img, known):
    """Smooth membrane-like fill of unknown pixels from a known-pixel pyramid."""
    c = img.astype(np.float32) * known[..., None]
    wgt = known.astype(np.float32)
    pyr = [(c, wgt)]
    while min(c.shape[:2]) > 4:
        c = cv2.resize(c, (c.shape[1] // 2 + 1, c.shape[0] // 2 + 1), interpolation=cv2.INTER_AREA)
        wgt = cv2.resize(wgt, (wgt.shape[1] // 2 + 1, wgt.shape[0] // 2 + 1), interpolation=cv2.INTER_AREA)
        pyr.append((c, wgt))
    c, wgt = pyr[-1]
    est = c / np.maximum(wgt, 1e-6)[..., None]
    for c, wgt in reversed(pyr[:-1]):
        up = cv2.resize(est, (c.shape[1], c.shape[0]), interpolation=cv2.INTER_LINEAR)
        up = cv2.GaussianBlur(up, (5, 5), 0)
        a = np.clip(wgt * 4, 0, 1)[..., None]
        est = (c / np.maximum(wgt, 1e-6)[..., None]) * a + up * (1 - a)
    return np.clip(est, 0, 255).astype(np.uint8)
