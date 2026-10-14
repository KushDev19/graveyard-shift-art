"""26_ARCADE_HD.png -> arcade.svg (cabinet, marquee, screen, coin_door, controls) + standalone screen/marquee SVGs."""
import pathlib, sys
import numpy as np, cv2
from scipy import ndimage as ndi
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, key
from tracer import trace_layer, mask_path, palette, svg_doc, hexc

OUT = pathlib.Path(__file__).resolve().parents[1]
DEBUG = "--debug" in sys.argv
S = 2
img_full = load("26_ARCADE_HD.png")
H, W = img_full.shape[:2]
a_full, fg_full, _ = key(img_full)
img = cv2.resize(fg_full, (W // S, H // S), interpolation=cv2.INTER_AREA)
raw = cv2.resize(img_full, (W // S, H // S), interpolation=cv2.INTER_AREA)
alpha = cv2.resize(a_full, (W // S, H // S), interpolation=cv2.INTER_AREA)
h, w = alpha.shape
raw_gex = raw[..., 1] - np.maximum(raw[..., 0], raw[..., 2])
solid = (alpha > 0.5) & (raw_gex < 25)
solid = ndi.binary_fill_holes(cv2.morphologyEx(solid.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)))
n, lab, st, _ = cv2.connectedComponentsWithStats(solid.astype(np.uint8))
solid = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 400])
lum = img @ np.array([0.3, 0.59, 0.11])
ker = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
yy, xx = np.mgrid[:h, :w] * S


def seed_region(sx, sy, dark=55, hull=True):
    """Non-outline component containing a seed (source px), optionally its convex hull."""
    m = (solid & (lum > dark)).astype(np.uint8)
    _, l = cv2.connectedComponents(m, connectivity=4)
    r = l == l[sy // S, sx // S]
    if hull:
        cs, _ = cv2.findContours(r.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hm = np.zeros_like(m); cv2.fillPoly(hm, [cv2.convexHull(np.vstack(cs))], 1)
        r = hm.astype(bool)
    return r & solid


marquee = seed_region(2226, 615)
screen = seed_region(1908, 1484)
coin = (xx > 2262) & (xx < 2740) & (yy > 3000) & (yy < 3690) & solid
# buttons: saturated warm blobs on the deck + outline ring; joystick: ball, stem, base
deck = (xx > 1700) & (xx < 3100) & (yy > 2240) & (yy < 2620)
warm = deck & (img[..., 0] > 150) & (img[..., 0] - img[..., 2] > 60)
warm = cv2.morphologyEx(warm.astype(np.uint8), cv2.MORPH_OPEN, ker(2))
nb, lb, sb, cb = cv2.connectedComponentsWithStats(warm)
controls = np.isin(lb, [i for i in range(1, nb) if sb[i, cv2.CC_STAT_AREA] > 150]).astype(np.uint8)
controls = cv2.dilate(controls, ker(9)).astype(bool)
stick = ((abs(xx - 1893) < 24) & (yy > 2330) & (yy < 2510)) | ((((xx - 1893) / 105.0) ** 2 + ((yy - 2522) / 48.0) ** 2) <= 1)
controls |= cv2.dilate(stick.astype(np.uint8), ker(5)).astype(bool)
controls &= solid
if DEBUG:
    dbg = (raw * 0.5).astype(np.uint8)
    for m, c in ((marquee, (255, 255, 0)), (screen, (0, 255, 255)), (coin, (255, 0, 255)), (controls, (255, 128, 0))):
        dbg[m] = (dbg[m] * 0.4 + np.array(c) * 0.6).astype(np.uint8)
    cv2.imwrite("/tmp/claude-0/-home-user-graveyard-shift-art/ae10c658-2c2d-5610-85c5-6653551e0c49/scratchpad/arc_dbg.jpg",
                cv2.resize(dbg[..., ::-1], (1000, 1000)))
    sys.exit()

# cabinet: repaint what the upper layers cover (controls/coin door inpainted, screen = CRT-off glass, marquee = plum)
cab_img = img.copy()
hole = (cv2.dilate((controls | coin).astype(np.uint8), ker(2)) > 0) & solid
cab_img = cv2.inpaint(np.clip(cab_img, 0, 255).astype(np.uint8), hole.astype(np.uint8), 12, cv2.INPAINT_TELEA).astype(np.float32)
cab_img = cv2.pyrMeanShiftFiltering(np.clip(cab_img, 0, 255).astype(np.uint8), 10, 10).astype(np.float32)  # flatten paint noise
cab_img[screen] = (34, 26, 52)
cab_img[marquee] = (61, 42, 79)
parts = []
cp, _, (cen, rgb) = trace_layer(cab_img, solid, 16, S, eps=0.8, smooth=2, maj=4)
parts.append('<g id="cabinet">' + "".join(cp) + "</g>")
mp, _, _ = trace_layer(img, marquee, 10, S, eps=0.8, dil=1)
parts.append('<g id="marquee" data-note="blank: put the title here">' + "".join(mp) + "</g>")
sp, _, _ = trace_layer(img, screen, 24, S, eps=0.7, smooth=1.5)
parts.append('<g id="screen" data-note="screen content, swap or animate">' + "".join(sp) + "</g>")
kp, _, _ = trace_layer(img, coin, 8, S, eps=0.7)
parts.append('<g id="coin_door">' + "".join(kp) + "</g>")
bp, _, _ = trace_layer(img, controls, 10, S, eps=0.6, smooth=1)
parts.append('<g id="controls" data-pivot="1893,2522">' + "".join(bp) + "</g>")
(OUT / "arcade.svg").write_text(svg_doc(W, H, "<title>GRAVEYARD SHIFT arcade cabinet HD</title>\n" + "\n".join(parts)))


def crop_svg(name, m, body, title):
    ys, xs = np.nonzero(m)
    x0, y0 = xs.min() * S - 4, ys.min() * S - 4
    x1, y1 = (xs.max() + 1) * S + 4, (ys.max() + 1) * S + 4
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" '
           f'width="{x1 - x0}" height="{y1 - y0}" data-origin="{x0},{y0}"><title>{title}</title>\n{body}\n</svg>\n')
    (OUT / name).write_text(doc)
    return x0, y0, x1, y1


print("screen", crop_svg("arcade_screen.svg", screen, "".join(sp), "arcade screen content (place at data-origin)"))
print("marquee", crop_svg("arcade_marquee_blank.svg", marquee, "".join(mp), "arcade marquee, blank"))
