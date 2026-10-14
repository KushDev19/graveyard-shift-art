"""23_LOGO.png -> layered logo.svg (glow, stripe, moon, 14 letters, helmet dot) + logo_mono_cream.svg."""
import pathlib, sys, json
import numpy as np, cv2
from scipy import ndimage as ndi
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, key
from tracer import trace_layer, mask_path, palette, svg_doc, hexc

OUT = pathlib.Path(__file__).resolve().parents[1]
S = 2  # work at half resolution, write source coordinates
img_full = load("23_LOGO.png")
H, W = img_full.shape[:2]
a_full, fg_full, plate = key(img_full)
img = cv2.resize(fg_full, (W // S, H // S), interpolation=cv2.INTER_AREA)
alpha = cv2.resize(a_full, (W // S, H // S), interpolation=cv2.INTER_AREA)
h, w = alpha.shape
yy, xx = np.mgrid[:h, :w] * S  # source coords per work pixel
raw = cv2.resize(img_full, (W // S, H // S), interpolation=cv2.INTER_AREA)
raw_gex = raw[..., 1] - np.maximum(raw[..., 0], raw[..., 2])
solid = (alpha > 0.55) & (raw_gex < 22)  # narrow green slivers between letters stay holes
solid = cv2.morphologyEx(solid.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
R, G, B = img[..., 0], img[..., 1], img[..., 2]
lum = img @ np.array([0.3, 0.59, 0.11])
ker = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))

# --- helmet dot: glass circle + antenna + cap + collar (source px, measured on grid crops)
def circ(cx, cy, r):
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
helmet = circ(2905, 1432, 262) | circ(2873, 1135, 58) | ((abs(xx - 2875) < 30) & (yy > 1150) & (yy < 1230))
helmet |= (xx > 2700) & (xx < 3110) & (yy > 1585) & (yy < 1680)
helmet &= solid

# --- racing stripe: saturated coral/amber, outside the helmet
stripe = solid & (R > 170) & (B < 150) & (R - B > 70) & ~cv2.dilate(helmet.astype(np.uint8), ker(6)).astype(bool)
stripe = cv2.morphologyEx(stripe.astype(np.uint8), cv2.MORPH_OPEN, ker(2)).astype(bool)
n, lab, st, _ = cv2.connectedComponentsWithStats(stripe.astype(np.uint8))
stripe = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 2000])

# --- letter faces: cream components
cream = solid & (lum > 200) & (R - B < 60) & ~helmet & ~stripe
cream = cv2.morphologyEx(cream.astype(np.uint8), cv2.MORPH_OPEN, ker(2))
n, lab, st, cen = cv2.connectedComponentsWithStats(cream)
faces = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 4000]
moon_box = (xx > 4640) & (yy < 1230)
moonface = [i for i in faces if cen[i][0] * S > 4870 and cen[i][1] * S < 900]
faces = [i for i in faces if i not in moonface]
rows = sorted(faces, key=lambda i: (cen[i][1] * S > 1250, cen[i][0]))
NAMES = ["G", "R", "A", "V", "E", "Y", "A2", "R2", "D", "S", "H", "I", "F", "T"]
print("faces found", len(rows), [(int(cen[i][0] * S), int(cen[i][1] * S)) for i in rows])
assert len(rows) == 14, "expected 14 letter faces"
facelab = np.zeros((h, w), np.int32)
for k, i in enumerate(rows):
    facelab[lab == i] = k + 1
dist, (iy, ix) = ndi.distance_transform_edt(facelab == 0, return_indices=True)
near = facelab[iy, ix]  # nearest face id for every pixel

# --- moon (behind the D): crescent + rod + ornament region, minus pixels that belong to the D's outline
moon = solid & moon_box & ~stripe & ~((near == 9) & (dist * S < 70))
moon &= ~(xx < 4655) & ~cv2.dilate(stripe.astype(np.uint8), ker(1)).astype(bool)
moon &= ~(cv2.dilate(stripe.astype(np.uint8), ker(6)).astype(bool) & (lum > 90))  # rod over the stripe: dark core only
_, ml = cv2.connectedComponents(moon.astype(np.uint8))
keep = np.unique(ml[np.isin(lab, moonface)]); keep = keep[keep > 0]
moon = np.isin(ml, keep)
letters_sil = solid & ~cv2.dilate(stripe.astype(np.uint8), ker(2)).astype(bool) & ~moon & (dist * S < 320)
letters_sil = cv2.morphologyEx(letters_sil.astype(np.uint8), cv2.MORPH_OPEN, ker(3)).astype(bool)
# helmet core = helmet pixels that are not the surrounding plum (the letters' base supplies the plum)
plum_ref = np.median(img[letters_sil & ~helmet & (lum < 70)], 0)
helmet = helmet & (np.abs(img - plum_ref).sum(-1) > 40) & ~cv2.dilate((facelab > 0).astype(np.uint8), ker(9)).astype(bool)
helmet = ndi.binary_fill_holes(cv2.morphologyEx(helmet.astype(np.uint8), cv2.MORPH_CLOSE, ker(4)))
helmet = cv2.dilate(helmet.astype(np.uint8), ker(1)).astype(bool) & solid
# --- glow: soft cream halo around letters + moon (measured from the keyed alpha)
core = (letters_sil | moon).astype(np.uint8)
dout = cv2.distanceTransform(1 - core, cv2.DIST_L2, 5) * S
ring_a = []
edges = list(range(0, 61, 5))
for d0, d1 in zip(edges[:-1], edges[1:]):
    sel = (dout > d0) & (dout <= d1) & ~stripe
    ring_a.append(float(np.median(alpha[sel])) if sel.any() else 0)
print("glow alpha by ring", [round(v, 3) for v in ring_a])
glow_rgb = np.array([244, 230, 200])  # cream glow; the keyed halo colour is green-contaminated

parts = []
# glow as stacked rings: outermost first; cumulative alpha 1-prod(1-o) must hit ring_a
glow = []
prev = 0.0
for d1, target in reversed(list(zip(edges[1:], ring_a))):
    o = 0 if target <= prev else 1 - (1 - target) / (1 - prev)
    prev = max(prev, target)
    if o > 0.01:
        m = cv2.dilate(core, ker(max(1, int(d1 / S)))).astype(bool)
        glow.append(f'<path fill="{hexc(glow_rgb)}" fill-opacity="{o:.3f}" d="{mask_path(m, S, 1.2)}"/>')
parts.append('<g id="glow">' + "".join(glow) + "</g>")

# the stripe is the bottom layer: let it run a few px under letters/moon so no green gap shows at the seams
stripe_draw = cv2.dilate(stripe.astype(np.uint8), ker(5)).astype(bool) & solid
sp, _, _ = trace_layer(img, stripe_draw, 3, S, eps=1.0, base="largest")
# stripe has no outline: drop the base silhouette path and recolour by bands
parts.append('<g id="racing_stripe">' + "".join(sp) + "</g>")
moon_core = moon & (raw_gex < 0) & (alpha > 0.97)  # palette from clean pixels only (no green-tinted edge colours)
cen_m, rgb_m = palette(img, moon_core, 3)
mp, _, _ = trace_layer(img, moon, 3, S, eps=0.8, cen=cen_m, rgb=rgb_m, base="largest")
parts.append('<g id="moon">' + "".join(mp) + "</g>")

# letters share one palette; helmet area is covered by the letter base (no hole under the dot)
cen_l, rgb_l = palette(img, letters_sil & ~helmet, 6)
lg = []
letter_masks = {}
for k, nm in enumerate(NAMES):
    m = letters_sil & (near == k + 1)
    letter_masks[nm] = m
    paths, _, _ = trace_layer(img, m & ~helmet, 6, S, cen=cen_l, rgb=rgb_l, eps=0.8)
    # base overlaps neighbours by 2 work px so adjacent letters never show an antialiasing seam
    grown = cv2.dilate((m & ~helmet).astype(np.uint8), ker(4 if nm == "D" else 2)).astype(bool) & (letters_sil | moon | helmet)
    paths[0] = paths[0].split('d="')[0] + f'd="{mask_path(grown, S, 0.8)}"/>'
    if (m & helmet).any():  # fill under the helmet with the base colour
        base = paths[0].split('d="')[0]
        paths.insert(1, base + f'd="{mask_path(m & helmet, S, 0.8)}"/>')
    lg.append(f'<g id="letter_{nm}" data-char="{nm[0]}">' + "".join(paths) + "</g>")
parts.append('<g id="letters">' + "\n".join(lg) + "</g>")
cen_h, rgb_h = palette(img, helmet, 16)
plum_i = int(np.argmin(((rgb_h - rgb_l[np.argmin(rgb_l @ [0.3, 0.59, 0.11])]) ** 2).sum(1)))
hp, _, _ = trace_layer(img, helmet, 16, S, eps=0.7, smooth=1.5, cen=cen_h, rgb=rgb_h, base=plum_i)
parts.append('<g id="helmet_dot" data-pivot="2905,1660">' + "".join(hp) + "</g>")
title = "<title>GRAVEYARD SHIFT logo</title>"
(OUT / "logo.svg").write_text(svg_doc(W, H, title + "\n".join(parts)))

# --- one-colour cream: faces + extrusion knocked apart by the outline gap
facemask = (facelab > 0) & letters_sil
body = (letters_sil | helmet | moon)
gap = cv2.dilate(facemask.astype(np.uint8), ker(int(26 / S))).astype(bool) & ~facemask
hd = cv2.dilate(helmet.astype(np.uint8), ker(9)).astype(bool)
mono = (facemask | (body & ~gap)) & ~hd
mono |= helmet & (lum > 100)  # helmet: glass rim, visor, highlights, collar, antenna read as cream  # helmet: glass rim + visor + highlights read as cream
mono = cv2.morphologyEx(mono.astype(np.uint8), cv2.MORPH_OPEN, ker(2)).astype(bool)
(OUT / "logo_mono_cream.svg").write_text(svg_doc(W, H, "<title>GRAVEYARD SHIFT logo, one colour</title>"
    f'<path fill="#F4E6C8" fill-rule="evenodd" d="{mask_path(mono, S, 0.9)}"/>'))
json.dump({"glow_alpha": ring_a}, open(OUT / "src" / "_logo_meta.json", "w"))
