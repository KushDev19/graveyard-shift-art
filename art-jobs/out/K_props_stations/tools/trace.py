"""Color-layer tracer for Job K: quantize a painted sprite, trace stacked flat-color layers to SVG paths."""
import numpy as np, cv2


def smooth(img):
    out = img
    for _ in range(2):
        out = cv2.bilateralFilter(out, 9, 28, 7)
    return cv2.pyrMeanShiftFiltering(out, 7, 12)


def quantize(img, mask, k, seed=1):
    """K-means in Lab over masked pixels. Returns label image (-1 outside) and RGB centers (median of members)."""
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    idx = np.flatnonzero(mask.ravel())
    rng = np.random.default_rng(seed)
    sample = lab[rng.choice(idx, min(len(idx), 120000), replace=False)]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
    _, _, cen = cv2.kmeans(sample, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    d = ((lab[idx, None, :] - cen[None]) ** 2).sum(2)
    lbl = np.full(mask.size, -1, np.int32)
    lbl[idx] = d.argmin(1)
    return lbl.reshape(mask.shape)


def majority(lbl, k, mask, r=5, passes=2):
    """Mode filter: removes speckles and smooths color boundaries."""
    for _ in range(passes):
        votes = np.stack([cv2.blur((lbl == i).astype(np.float32), (r, r)) for i in range(k)], 0)
        new = votes.argmax(0).astype(np.int32)
        lbl = np.where(mask, new, -1)
    return lbl


def remove_small(lbl, k, mask, min_area):
    """Merge tiny islands into the surrounding label."""
    for i in range(k):
        m = (lbl == i).astype(np.uint8)
        n, cc, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
        for j in range(1, n):
            if st[j, 4] < min_area:
                isl = cc == j
                ring = cv2.dilate(isl.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~isl & mask
                if ring.any():
                    vals = lbl[ring]; vals = vals[vals >= 0]
                    if len(vals):
                        lbl[isl] = np.bincount(vals).argmax()
    return lbl


def contour_path(mask, eps=1.3, ox=0.0, oy=0.0, min_area=12, blur=2.2):
    """Trace a binary mask to an SVG path 'd' (evenodd), Catmull-Rom smoothed cubic curves."""
    m = mask.astype(np.uint8)
    # trace at 2x so the curve sits on pixel edges, then scale back
    m2 = cv2.resize(m.astype(np.float32), (m.shape[1] * 2, m.shape[0] * 2), interpolation=cv2.INTER_LINEAR)
    m2 = (cv2.GaussianBlur(m2, (0, 0), blur) > 0.5).astype(np.uint8)
    cs, _ = cv2.findContours(m2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    parts = []
    for c in cs:
        if abs(cv2.contourArea(c)) < min_area * 4:
            continue
        p = cv2.approxPolyDP(c, eps * 2, True)[:, 0, :].astype(np.float64) / 2.0 + [ox - 0.25, oy - 0.25]
        if len(p) < 3:
            continue
        parts.append(catmull(p))
    return ''.join(parts)


def catmull(p, t=0.5):
    n = len(p)
    f = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')
    s = [f'M{f(p[0][0])} {f(p[0][1])}']
    if n < 4:
        s += [f'L{f(x)} {f(y)}' for x, y in p[1:]]
        return ''.join(s) + 'Z'
    for i in range(n):
        p0, p1, p2, p3 = p[i - 1], p[i], p[(i + 1) % n], p[(i + 2) % n]
        # keep sharp corners straight
        a = p1 - p0; b = p2 - p1; c = p3 - p2
        def ang(u, v):
            nu, nv = np.linalg.norm(u), np.linalg.norm(v)
            return 0 if nu * nv == 0 else np.dot(u, v) / (nu * nv)
        if ang(a, b) < 0.2 or ang(b, c) < 0.2:
            s.append(f'L{f(p2[0])} {f(p2[1])}')
            continue
        seg = np.linalg.norm(b)
        t1 = p2 - p0; t1 = t1 / (np.linalg.norm(t1) or 1)
        t2 = p3 - p1; t2 = t2 / (np.linalg.norm(t2) or 1)
        c1 = p1 + t1 * seg * 0.33
        c2 = p2 - t2 * seg * 0.33
        s.append(f'C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}')
    return ''.join(s) + 'Z'


def hexc(rgb):
    return '#%02X%02X%02X' % tuple(int(v) for v in rgb)


def merge_close(lbl, k, img, de):
    """Merge clusters whose mean colors are within de (CIELAB) of each other: flattens soft painted gradients."""
    lab = cv2.cvtColor(img.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
    means = {i: lab[lbl == i].mean(0) for i in range(k) if (lbl == i).any()}
    cnt = {i: (lbl == i).sum() for i in means}
    changed = True
    while changed:
        changed = False
        ids = sorted(means, key=lambda i: -cnt[i])
        for a in ids:
            for b in ids:
                if a != b and b in means and a in means and np.linalg.norm(means[a] - means[b]) < de:
                    lbl[lbl == b] = a
                    means[a] = (means[a] * cnt[a] + means[b] * cnt[b]) / (cnt[a] + cnt[b]); cnt[a] += cnt[b]
                    del means[b], cnt[b]; changed = True
    return lbl


def outline_mask(img, mask, t=78):
    lum = cv2.GaussianBlur(img.astype(np.float32), (0, 0), 0.8) @ np.float32([0.3, 0.59, 0.11])
    lmax = cv2.dilate(lum, np.ones((15, 15), np.uint8))
    o = (((lum < t) | ((lum < 118) & (lum < 0.55 * lmax))) & mask).astype(np.uint8)
    n, cc, st, _ = cv2.connectedComponentsWithStats(o)
    for j in range(1, n):
        if st[j, 4] < 30:
            o[cc == j] = 0
    return o.astype(bool)


def grow_labels(lbl, k, mask, r=5):
    """Fill unlabeled pixels inside mask from neighboring labels."""
    for _ in range(60):
        todo = (lbl < 0) & mask
        if not todo.any():
            break
        votes = np.stack([cv2.blur((lbl == i).astype(np.float32), (r, r)) for i in range(k)], 0)
        best = votes.argmax(0); has = votes.max(0) > 0
        upd = todo & has
        lbl = np.where(upd, best, lbl)
    return lbl


def trace_layers(img, mask, k=20, ox=0, oy=0, eps=1.1, min_island=400, outline_t=78, merge_de=6.0, fill_blur=3.2):
    """Return list of (hex, d) stacked layers whose painter's-order composite reproduces img inside mask.
    Fill colors are clustered without the outline pixels and grown underneath them; layers are ordered by
    area and stacked (each layer = its cluster plus all later ones) so there are never gaps; the plum
    outline is traced separately from a luminance threshold and drawn on top."""
    out = outline_mask(img, mask, outline_t)
    fillm = mask & ~out
    sm = smooth(img)
    lbl = quantize(sm, fillm, k)
    lbl = merge_close(lbl, k, sm, merge_de)
    lbl = majority(lbl, k, fillm, r=9, passes=3)
    lbl = grow_labels(lbl, k, mask)
    lbl = remove_small(lbl, k, mask, min_island)
    cols, areas = [], []
    for i in range(k):
        sel = (lbl == i) & fillm
        areas.append(sel.sum())
        cols.append(np.median(img[sel], 0) if sel.any() else np.zeros(3))
    order = [i for i in np.argsort(-np.array(areas)) if areas[i] > 0]
    lut = np.full(k, -1); lut[order] = np.arange(len(order))
    rk = np.where(lbl >= 0, lut[np.maximum(lbl, 0)], -1)
    layers = []
    for r, c in enumerate(order):
        m = (rk >= r) if r else mask
        r_, g_, b_ = cols[c]
        if g_ - max(r_, b_) > 30 and 120 + 60 * (b_ - r_) / max(g_ - min(r_, b_), 1) < 147:
            continue  # green-screen fringe (hue near 120), never part of the art; seafoam (hue ~160) is kept
        d = contour_path(m, eps, ox, oy, blur=fill_blur)
        if d:
            layers.append((hexc(cols[c]), d))
    if out.any():
        ol = quantize(img, out, 3)
        ol = merge_close(ol, 3, img, 12.0)
        ol = grow_labels(majority(ol, 3, out, r=5, passes=1), 3, out)
        ids = sorted(set(ol[out].tolist()), key=lambda i: -(ol == i).sum())
        for r, i in enumerate(ids):
            m = out if r == 0 else np.isin(ol, ids[r:]) & out
            if r and (ol == i).sum() < 200:
                continue
            layers.append((hexc(np.median(img[(ol == i) & out], 0)), contour_path(m, eps, ox, oy, blur=1.2)))
    return layers, lbl, out
