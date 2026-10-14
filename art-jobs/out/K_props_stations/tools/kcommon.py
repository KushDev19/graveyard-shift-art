"""Shared helpers for Job K: chroma key, object boxes, MAE."""
import numpy as np, cv2
from PIL import Image
ROOT = __file__.rsplit('/art-jobs/', 1)[0]
SRC = {'14': ROOT + '/raw_originals/14_PROPS_STATIONS.png', '15': ROOT + '/raw_originals/15_PROPS_SHIP.png'}

def load(sheet):
    return np.array(Image.open(SRC[sheet]).convert('RGB'))

def key_mask(img):
    """True where the pixel is NOT green screen."""
    r, g, b = [img[..., i].astype(int) for i in range(3)]
    green = (g > 150) & (g - r > 70) & (g - b > 70)
    return ~green

def alpha_matte(img):
    """Soft alpha: 0 on pure green, 1 on object; despilled colors."""
    r, g, b = [img[..., i].astype(float) for i in range(3)]
    spill = g - np.maximum(r, b)
    a = 1 - np.clip((spill - 25) / 120, 0, 1)
    return a

def mae(a_rgb, b_rgb, mask, factor=4):
    """Mean abs error over mask on a factor-x downscale (0..255)."""
    h, w = mask.shape
    hs, ws = h // factor, w // factor
    def ds(x):
        return cv2.resize(x.astype(np.float32), (ws, hs), interpolation=cv2.INTER_AREA)
    A, B, M = ds(a_rgb), ds(b_rgb), ds(mask.astype(np.float32)) > 0.5
    return float(np.abs(A - B).mean(axis=2)[M].mean())

# object boxes (x, y, w, h) in source pixels, padded later
STATIONS = {  # name: [idle, highlight, done]
    'station_keypad':      [(256, 31, 926, 995), (1601, 31, 925, 995), (2936, 31, 925, 995)],
    'station_switchboard': [(198, 1057, 998, 982), (1553, 1065, 998, 983), (2894, 1065, 999, 982)],
    'station_tape':        [(190, 2068, 1034, 993), (1535, 2070, 1035, 991), (2871, 2069, 1035, 992)],
    'station_scope':       [(195, 3116, 962, 956), (1547, 3116, 963, 956), (2901, 3102, 963, 970)],
}
SHIP = {
    'vent_closed': (223, 1242, 1087, 591), 'vent_open': (1646, 1087, 1135, 885),
    'timeclock_idle': (3101, 1053, 867, 967), 'timeclock_ready': (4354, 1053, 866, 967),
    'table_clutter': (4028, 110, 1223, 825),
}

def crop(img, box, pad=24):
    x, y, w, h = box
    return img[max(0, y - pad):y + h + pad, max(0, x - pad):x + w + pad], (max(0, x - pad), max(0, y - pad))

def align(ref, mov, search=60):
    """Integer shift (dx, dy) so that mov shifted by it best matches ref (by key masks)."""
    a = key_mask(ref).astype(np.float32); b = key_mask(mov).astype(np.float32)
    H = max(a.shape[0], b.shape[0]); W = max(a.shape[1], b.shape[1])
    A = np.zeros((H, W), np.float32); B = np.zeros((H, W), np.float32)
    A[:a.shape[0], :a.shape[1]] = a; B[:b.shape[0], :b.shape[1]] = b
    (dx, dy), _ = cv2.phaseCorrelate(B, A)
    return int(round(dx)), int(round(dy))

def main_mask(img, keep_frac=0.02):
    """Key mask limited to the central object (drops fragments of neighbours at the crop edges)."""
    m = cv2.morphologyEx(key_mask(img).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    g = cv2.dilate(m, np.ones((31, 31), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats(g)
    if n <= 2:
        return m.astype(bool)
    big = 1 + int(np.argmax(st[1:, 4]))
    return (m > 0) & (cc == big)
