"""Split the reactor core mask into housing / sphere / cage (work scale)."""
import numpy as np, cv2, seg


def split(img, core):
    h, s, v = seg.hsv(img)
    cream = core & (s < 0.4) & (v > 0.72) & (h >= 15) & (h <= 65)
    lim = seg.raster([('ell', 2742, 1110, 745, 745)], *core.shape)
    cream &= lim
    n, lab, st, _ = cv2.connectedComponentsWithStats(cream.astype(np.uint8), 8)
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    glass = core & lim & (s > 0.35) & (v > 0.7) & ((h < 45) | (h > 300))
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats((cream | glass).astype(np.uint8), 4)
    big2 = 1 + np.argmax(st2[1:, cv2.CC_STAT_AREA])
    pts = np.column_stack(np.nonzero(lab2 == big2)[::-1]).astype(np.int32)
    hull = np.zeros(core.shape, np.uint8)
    cv2.fillPoly(hull, [cv2.convexHull(pts)], 1)
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    disc = cv2.dilate(hull, k(9)) > 0          # include the rim's outer outline
    cage_c = lab == big
    near = cv2.dilate(cage_c.astype(np.uint8), k(11)) > 0
    cage = cage_c | (near & disc & (v < 0.45))
    cage = cage | (disc & ~(cv2.erode(disc.astype(np.uint8), k(12)) > 0))  # rim outline ring
    cage = seg.clean(cage, 1, 30) & disc
    sphere = disc & ~cage
    housing = core & ~disc
    return housing, disc, cage, sphere
