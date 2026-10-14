"""Color-region tracer: k-means palette -> majority-cleaned label map -> smoothed SVG paths.
All coordinates are written in SOURCE pixels (work scale is multiplied back)."""
import numpy as np, cv2


def palette(img, mask, k, seed=1, sample=250000):
    px = img[mask].reshape(-1, 3).astype(np.float32)
    rng = np.random.default_rng(seed)
    if len(px) > sample:
        px = px[rng.choice(len(px), sample, replace=False)]
    lab = cv2.cvtColor(px[None] / 255.0, cv2.COLOR_RGB2Lab)[0]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
    _, lbl, cen = cv2.kmeans(lab, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    rgb = np.array([px[lbl[:, 0] == i].mean(0) if (lbl[:, 0] == i).any() else [0, 0, 0] for i in range(k)])
    return cen, rgb


def assign(img, mask, cen, smooth=2):
    lab = cv2.cvtColor(img.astype(np.float32) / 255.0, cv2.COLOR_RGB2Lab)
    if smooth:
        lab = cv2.GaussianBlur(lab, (0, 0), smooth)
    d = ((lab[..., None, :] - cen[None, None]) ** 2).sum(-1)
    lbl = d.argmin(-1).astype(np.int32)
    lbl[~mask] = -1
    return lbl


def majority(lbl, k, mask, r=2):
    """Mode filter to kill speckles (box radius r)."""
    best = np.zeros(lbl.shape, np.float32); out = lbl.copy()
    for i in range(k):
        v = cv2.boxFilter((lbl == i).astype(np.float32), -1, (2 * r + 1, 2 * r + 1))
        upd = v > best; best[upd] = v[upd]; out[upd] = i
    out[~mask] = -1
    return out


def _fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def mask_path(m, scale, eps=0.9, min_area=6):
    """Contours (outer + holes) of a binary mask -> one path string using midpoint-quadratic smoothing."""
    cs, hier = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    parts = []
    for c in cs:
        if abs(cv2.contourArea(c)) < min_area:
            continue
        p = cv2.approxPolyDP(c, eps, True)[:, 0].astype(np.float64) + 0.5
        if len(p) < 3:
            continue
        p *= scale
        mids = (p + np.roll(p, -1, 0)) / 2
        seg = [f"M{_fmt(mids[-1][0])} {_fmt(mids[-1][1])}"]
        for v, mpt in zip(p, mids):
            seg.append(f"Q{_fmt(v[0])} {_fmt(v[1])} {_fmt(mpt[0])} {_fmt(mpt[1])}")
        parts.append("".join(seg) + "Z")
    return "".join(parts)


def hexc(c):
    return "#%02X%02X%02X" % tuple(int(round(min(max(x, 0), 255))) for x in c)


def trace_layer(img, mask, k, scale, base=None, eps=0.9, smooth=2, maj=2, seed=1, cen=None, rgb=None,
                dil=1, skip_base_color=True):
    """Return list of SVG <path> strings: base silhouette (darkest colour) + colour regions on top."""
    if cen is None:
        cen, rgb = palette(img, mask, k, seed)
    lbl = majority(assign(img, mask, cen, smooth), len(cen), mask, maj)
    lum = rgb @ [0.3, 0.59, 0.11]
    areas = [(lbl == i).sum() for i in range(len(cen))]
    dark = int(np.argmin(lum)) if base is None else int(np.argmax(areas)) if base == "largest" else base
    out = [f'<path fill="{hexc(rgb[dark])}" d="{mask_path(mask, scale, eps)}"/>']
    ker = np.ones((2 * dil + 1, 2 * dil + 1), np.uint8)
    for i in np.argsort(areas)[::-1]:
        if (i == dark and skip_base_color) or areas[i] == 0:
            continue
        m = (lbl == i)
        if dil:
            m = cv2.dilate(m.astype(np.uint8), ker).astype(bool) & mask
        d = mask_path(m, scale, eps)
        if d:
            out.append(f'<path fill="{hexc(rgb[i])}" d="{d}"/>')
    return out, lbl, (cen, rgb)


def svg_doc(w, h, body, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"{extra}>\n'
            + body + "\n</svg>\n")
