"""Med scanner: split arch / base on the idle sprite and model the base ellipses for repainting under the arch."""
from common import *
n = 'med_scanner'
q = prep(n, 14); rgb = q[..., :3].astype(int); obj = q[..., 3] > 0
H, W = obj.shape
def is_(c): return (np.abs(rgb - np.array(c)).sum(-1) < 4) & obj
OUT, TEAL_D, TEAL, TEAL_L = (81, 23, 74), (95, 117, 131), (115, 156, 158), (146, 196, 193)
SIDE, CREAM, CREAM_L = (208, 170, 165), (240, 214, 188), (251, 232, 209)
teal = is_(TEAL_D) | is_(TEAL) | is_(TEAL_L)
lab, k = ndi.label(teal); s = ndi.sum(teal, lab, range(1, k + 1))
order = list(np.argsort(-s)[:4] + 1)
objs = ndi.find_objects(lab)
ring_id = max(order, key=lambda i: objs[i - 1][0].start)          # lowest-starting big component = base ring
arch_core = np.isin(lab, [i for i in order if i != ring_id])
ring = lab == ring_id
arch = ndi.binary_fill_holes(ndi.binary_closing(arch_core | (ndi.binary_dilation(arch_core, iterations=16) & is_(OUT) & ~ndi.binary_dilation(ring, iterations=3)), iterations=4))
arch &= obj

def fit_ellipse(pts):
    x, y = pts[:, 1].astype(float), pts[:, 0].astype(float)
    A = np.stack([x * x, y * y, x, y], 1); sol = np.linalg.lstsq(A, np.ones_like(x), rcond=None)[0]
    a, c, d, e = sol; cx, cy = -d / (2 * a), -e / (2 * c); f = 1 + a * cx * cx + c * cy * cy
    return cx, cy, np.sqrt(f / a), np.sqrt(f / c)

def contour(m):
    return np.argwhere(m & ~ndi.binary_erosion(m))

far = ~ndi.binary_dilation(arch, iterations=20)
def nr(e, pts):
    cx, cy, a, b = e; return np.sqrt(((pts[:, 1] - cx) / a) ** 2 + ((pts[:, 0] - cy) / b) ** 2)
cr = contour(ring); cr = cr[far[tuple(cr.T)]]
e0 = fit_ellipse(cr)
e_ring_out = fit_ellipse(cr[nr(e0, cr) > 1]); e_ring_in = fit_ellipse(cr[nr(e0, cr) < 1])
creams = is_(CREAM) | is_(CREAM_L)
lab2, _ = ndi.label(creams); objs2 = ndi.find_objects(lab2)
cc = np.vstack([contour(lab2 == i + 1) for i, o in enumerate(objs2) if (lab2[o] == i + 1).sum() > 2000])
cc = cc[far[tuple(cc.T)]]; cc = cc[nr(e_ring_out, cc) > 1.12]
e_top = fit_ellipse(cc)
bottom_y = np.where(obj.any(1))[0].max()
print('ring_out', np.round(e_ring_out, 1)); print('ring_in', np.round(e_ring_in, 1)); print('top', np.round(e_top, 1)); print('bottom', bottom_y)

def model():
    """Raster model of the base (colours as in the painting) for filling hidden pixels."""
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    def inside(e, grow=0.0, dy=0.0):
        cx, cy, a, b = e; return ((xx - cx) / (a + grow)) ** 2 + ((yy - cy - dy) / (b + grow)) ** 2 <= 1
    cx, cy, a, b = e_top; t = bottom_y - (cy + b) - 14
    img = np.zeros((H, W, 3), np.uint8)
    sil = inside(e_top, 14) | inside(e_top, 7, t) | ((np.abs(xx - cx) <= a + 14) & (yy >= cy) & (yy <= cy + t))
    img[sil] = OUT
    side = inside(e_top, 0, t - 1) | ((np.abs(xx - cx) <= a) & (yy >= cy) & (yy <= cy + t))
    img[side & sil] = SIDE
    img[inside(e_top, 14)] = OUT; img[inside(e_top)] = CREAM
    img[inside(e_ring_out, 14)] = OUT; img[inside(e_ring_out)] = TEAL
    img[inside(e_ring_in, 0)] = OUT; img[inside(e_ring_in, -14)] = CREAM
    return img, sil
