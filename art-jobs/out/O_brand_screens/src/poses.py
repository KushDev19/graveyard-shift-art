"""Key the green off the 04A-04E pose sheets into one transparent PNG per pose."""
import json, pathlib, sys
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, key

OUT = pathlib.Path(__file__).resolve().parents[1] / "poses"
SHEETS = {
    "04A_POSES_REVEAL.png": ["reveal_hands_on_hips", "reveal_arms_crossed_smug"],
    "04B_POSES_MEETING.png": ["meeting_point_accuse", "meeting_shrug"],
    "04C_POSES_WIN.png": ["win_jump_cheer", "win_wave"],
    "04D_POSES_FALLEN_GHOST.png": ["fallen_headless", "ghost_halo"],
    "04E_POSES_EJECT_SNEAK.png": ["eject_tumble", "sneak_tiptoe"],
}
PAD = 24
meta = {}
for sheet, names in SHEETS.items():
    img = load(sheet)
    a, fg, _ = key(img)
    a[a < 0.04] = 0
    # drop specks: keep components with real mass
    n, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] > 150
    solid = keep[lab]
    near = cv2.dilate(solid.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
    a = np.where(near, a, 0)
    # split left/right at the emptiest column in the middle third
    col = a.sum(0); w = a.shape[1]
    mid = w // 3 + int(np.argmin(cv2.blur(col[None], (1, 101))[0, w // 3: 2 * w // 3]))
    for name, (x0, x1) in zip(names, ((0, mid), (mid, w))):
        sub = a[:, x0:x1]
        ys, xs = np.nonzero(sub > 0.02)
        bx0, bx1 = max(xs.min() - PAD, 0) + x0, min(xs.max() + PAD, x1 - x0) + x0
        by0, by1 = max(ys.min() - PAD, 0), min(ys.max() + PAD, a.shape[0])
        f = fg[by0:by1, bx0:bx1].copy(); al = a[by0:by1, bx0:bx1].copy()
        # despill: grey/plum art never has green above max(R,B); the mint ghost helmet keeps a little
        k = 26 if name == "ghost_halo" else 3
        f[..., 1] = np.minimum(f[..., 1], np.maximum(f[..., 0], f[..., 2]) + k)
        # firm up the alpha in Gemini's smeared spots, keep antialiased edges
        al = cv2.medianBlur((al * 255).astype(np.uint8), 5) / 255.0
        al = np.clip((al - 0.12) / 0.76, 0, 1)
        f[al == 0] = 0
        rgba = np.dstack([f, al * 255]).round().astype(np.uint8)
        # x-limit the crop to this pose's half
        rgba[:, : max(0, x0 - bx0)] = 0
        im = Image.fromarray(rgba, "RGBA")
        im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)  # half source scale
        im.save(OUT / f"pose_{name}.png", optimize=True)
        meta[name] = {"sheet": f"raw_originals/{sheet}", "x": int(bx0), "y": int(by0),
                      "w": int(bx1 - bx0), "h": int(by1 - by0), "png_scale": 0.5}
        print(name, meta[name])
(OUT / "poses.json").write_text(json.dumps(meta, indent=1))
