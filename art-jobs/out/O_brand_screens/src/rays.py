"""Burst rays of screens 30/31 -> <screen>_rays.svg (backing + spinnable ray group) and <screen>_fg.png
(everything in front of the rays, transparent elsewhere)."""
import json, pathlib, sys, io
import numpy as np, cv2, cairosvg
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load
from tracer import hexc

OUT = pathlib.Path(__file__).resolve().parents[1]
CFG = {  # centre found by polar-consistency search (rays_probe.py); r range that no foreground occludes
    "30_SCREEN_SPLASH_EMERGENCY": dict(c=(1378, 1530), rmin=150, rmax=1300, finite=False),
    "31_SCREEN_SPLASH_BODY": dict(c=(1416, 1536), rmin=120, rmax=950, finite=True),
}
NA = 4320
meta = {}
FLOOR = {"31_SCREEN_SPLASH_BODY": [(1763, 3072), (2610, 2370), (5504, 2370), (5504, 3072)]}


def ray_length(apex, l_end, r_end, cfg):
    """Walk out along the ray axis: a visible flat end (ray -> backing) keeps its length; rays that run off
    the image or under foreground are treated as endless (5200 px from the pivot)."""
    if not cfg["finite"]:  # 30: every ray runs off the frame or under the comic panel
        return 5200.0
    c = np.array(cfg["c"], float); mid = (l_end + r_end) / 2
    d = (mid - apex) / np.linalg.norm(mid - apex)
    off = 0
    for r in np.arange(cfg["rmax"] - 50, 5200, 6.0):
        x, y = apex + d * (r - np.dot(apex - c, d))
        if not (0 <= x < W and 0 <= y < H):
            return 5200.0
        v = IMG[int(y), int(x)]
        if v @ [0.3, 0.59, 0.11] < 110:
            off += 1
            if off >= 4:
                if np.abs(v - BG).sum() < 45 and not FLOORM[int(y), int(x)]:
                    return float(r - 18)
                return 5200.0 if not FLOORM[int(y), int(x)] else float(r + 600)
        else:
            off = 0
    return 5200.0
for name, cfg in CFG.items():
    img = load(name + ".png"); H, W = img.shape[:2]
    cx, cy = cfg["c"]
    IMG = img
    FLOORM = np.zeros((H, W), np.uint8)
    if name in FLOOR:
        cv2.fillPoly(FLOORM, [np.array(FLOOR[name], np.int32)], 1)
    FLOORM = FLOORM.astype(bool)
    th = np.linspace(-np.pi, np.pi, NA, endpoint=False)
    rs = np.arange(cfg["rmin"], cfg["rmax"], 2.0)
    X = cx + np.outer(rs, np.cos(th)); Y = cy + np.outer(rs, np.sin(th))
    P = cv2.remap(img, X.astype(np.float32), Y.astype(np.float32), cv2.INTER_LINEAR)
    lum = P @ np.array([0.3, 0.59, 0.11])
    ray = lum > 110  # rays are coral/amber/cream, backing is dark plum
    ray = ndi.binary_opening(ray, np.ones((3, 3)))
    bgc = np.median(P[~ray & (lum < 90)], 0)
    BG = bgc
    # backing radial darkening (30 has a dark centre): median backing colour per radius band
    lab, n = ndi.label(ray, structure=np.ones((3, 3)))
    # merge labels that wrap around -pi/pi
    for i in range(len(rs)):
        a, b = lab[i, 0], lab[i, -1]
        if a and b and a != b:
            lab[lab == b] = a
    rays = []
    for k in range(1, n + 1):
        m = lab == k
        if m.sum() < 400:
            continue
        rows = np.nonzero(m.any(1))[0]
        if len(rows) < 20:
            continue
        L, R = [], []
        for i in rows[3:]:
            cols = np.nonzero(m[i])[0]
            if cols.max() - cols.min() > NA / 2:  # wrapped
                cols = np.where(cols < NA / 2, cols + NA, cols)
            t0, t1 = th[0] + (cols.min() - 0.5) * 2 * np.pi / NA, th[0] + (cols.max() + 0.5) * 2 * np.pi / NA
            L.append((cx + rs[i] * np.cos(t0), cy + rs[i] * np.sin(t0)))
            R.append((cx + rs[i] * np.cos(t1), cy + rs[i] * np.sin(t1)))
        L, R = np.array(L), np.array(R)
        fl = cv2.fitLine(L.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        fr = cv2.fitLine(R.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        # apex = intersection of the two edge lines
        A = np.array([[fl[0], -fr[0]], [fl[1], -fr[1]]])
        try:
            s, _ = np.linalg.solve(A, [fr[2] - fl[2], fr[3] - fl[3]])
            apex = np.array([fl[2] + s * fl[0], fl[3] + s * fl[1]])
        except np.linalg.LinAlgError:
            apex = np.array([cx, cy])
        if np.hypot(*(apex - (cx, cy))) > rs[rows[0]] + 200:  # bad fit: fall back to tip on the centre line
            apex = (L[0] + R[0]) / 2
        far = ray_length(apex, L[-1], R[-1], cfg)
        def far_pt(f):
            d = np.array([f[0], f[1]]); p0 = np.array([f[2], f[3]])
            if np.dot(d, p0 - (cx, cy)) < 0: d = -d
            return p0 + d * (far - np.dot(p0 - (cx, cy), d))
        col = np.median(P[m], 0)
        rays.append((apex, far_pt(fl), far_pt(fr), col, float(np.degrees(np.arctan2(*(far_pt(fl) + far_pt(fr) - 2 * np.array([cx, cy]))[::-1])))))
    rays.sort(key=lambda r: r[4])
    # snap colours to the few painted ones
    cols = np.array([r[3] for r in rays], np.float32)
    k = 3
    _, lbl, cen = cv2.kmeans(cols, k, None, (cv2.TERM_CRITERIA_EPS, 20, 0.5), 5, cv2.KMEANS_PP_CENTERS)
    paths = []
    for (ap, fl, fr, _, ang), li in zip(rays, lbl[:, 0]):
        paths.append(f'<path fill="{hexc(cen[li])}" d="M{ap[0]:.1f} {ap[1]:.1f}L{fl[0]:.1f} {fl[1]:.1f}L{fr[0]:.1f} {fr[1]:.1f}Z"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
           f'<title>{name.lower()} burst rays</title>\n'
           f'<rect id="backing" width="{W}" height="{H}" fill="{hexc(bgc)}"/>\n'
           f'<g id="rays" data-pivot="{cx},{cy}">' + "".join(paths) + "</g>\n</svg>\n")
    sp = OUT / "screens" / f"{name[:2]}_rays.svg"
    sp.write_text(svg)
    ren = np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(url=str(sp), output_width=W, output_height=H))).convert("RGB")).astype(np.float32)
    # foreground = what the rays model cannot explain
    d = cv2.GaussianBlur(np.abs(ren - img).sum(-1), (0, 0), 3)
    fg = (d > 90).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    fg = ndi.binary_fill_holes(fg)
    lab2, n2 = ndi.label(fg)
    sizes = ndi.sum(fg, lab2, range(1, n2 + 1))
    fg = np.isin(lab2, 1 + np.nonzero(sizes > 60000)[0])
    fg |= FLOORM
    if name.startswith("30"):  # keep the comic panel's plum frame with the panel
        big = cv2.dilate(fg.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))).astype(bool)
        fg = big
    alpha = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.5)
    rgba = np.dstack([img, alpha * 255]).astype(np.uint8)
    for w in (1920, 3840):
        Image.fromarray(rgba, "RGBA").resize((w, round(H * w / W)), Image.LANCZOS).save(
            OUT / "screens" / f"{name.lower()}_fg_{w}.webp", "WEBP", quality=85, method=6)
        rmask = np.zeros((H, W), bool); rmask[:] = True; rmask[fg] = False
    mae = float(np.abs(cv2.resize(ren, (W // 4, H // 4), interpolation=cv2.INTER_AREA) - cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA))[cv2.resize(rmask.astype(np.uint8), (W // 4, H // 4)) > 0].mean())
    meta[name[:2]] = {"rays_svg": f"screens/{sp.name}", "pivot": [cx, cy], "ray_count": len(rays), "mae_ray_area": round(mae, 2),
                      "fg": [f"screens/{name.lower()}_fg_{w}.webp" for w in (1920, 3840)]}
    print(name, len(rays), "rays, MAE over ray area", round(mae, 2))
    side = np.concatenate([img, ren], 1).astype(np.uint8)
    Image.fromarray(side).resize((1800, int(1800 * H / (2 * W)))).save(OUT / "check" / f"rays_{name[:2]}_side_by_side.png")
    on = (img * 0.5 + ren * 0.5).astype(np.uint8)
    Image.fromarray(on).resize((1200, int(1200 * H / W))).save(OUT / "check" / f"rays_{name[:2]}_onion.png")
    dbg = img.copy(); dbg[~fg] *= 0.35
    Image.fromarray(dbg.astype(np.uint8)).resize((900, int(900 * H / W))).save(OUT / "check" / f"rays_{name[:2]}_fgmask.png")
json.dump(meta, open(OUT / "src" / "_rays_meta.json", "w"), indent=1)
