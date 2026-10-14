"""Step 3: fit the painted soft light (lamp cones, glow pools) and soft shade as blurred SVG blobs.
Positive residual -> <room>_lights.svg (one group per light source, flicker-able).
Negative residual -> group "shade" appended to <room>_shell.svg.
Usage: python light_fit.py galley"""
import re
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import rooms
from tracelib import OUT, load, render, svg_doc

S = 4          # fit scale (1/4 source)
SIG = 3.0      # blur sigma at fit scale -> 12 px in source space
LEVELS = [4, 8, 13, 19, 27, 37, 50, 66, 85, 110]


def fit_blobs(O, P, valid, sign):
    blobs = []
    d = cv2.GaussianBlur(O - P, (0, 0), 1.5).mean(2) * sign
    for t in LEVELS:
        M = (d > t) & valid
        M = ndi.binary_opening(M, iterations=1)
        lab, n = ndi.label(M)
        for i in range(1, n + 1):
            comp = lab == i
            if comp.sum() < 30:
                continue
            m = cv2.GaussianBlur(comp.astype(np.float32), (0, 0), SIG)
            w = (m > 0.02) & valid
            mw, Pw, Ow = m[w][:, None], P[w], O[w]
            a = 0.5
            for _ in range(4):
                C = (mw * (Ow - Pw + a * mw * Pw)).sum(0) / max((a * mw * mw).sum(), 1e-6)
                C = C.clip(0, 255)
                diff = C[None] - Pw
                a = float((mw * diff * (Ow - Pw)).sum() / max((mw * mw * diff * diff).sum(), 1e-6))
                a = min(max(a, 0.04), 0.95)
            P = P + a * m[..., None] * (C[None, None] - P)
            cs, _ = cv2.findContours(comp.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            ys, xs = np.where(comp)
            blobs.append(dict(level=t, C=C, a=a, contours=[cv2.approxPolyDP(c, 1.0, True) for c in cs],
                              cx=xs.mean() * S, cy=ys.mean() * S))
            d = cv2.GaussianBlur(O - P, (0, 0), 1.5).mean(2) * sign
    return blobs, P


def path_of(b):
    parts = []
    for c in b["contours"]:
        pts = (c.reshape(-1, 2) * S + S / 2).round().astype(int)
        if len(pts) < 3:
            continue
        parts.append("M" + " ".join(f"{x} {y}" for x, y in pts) + "Z")
    col = "#%02X%02X%02X" % tuple(int(v) for v in b["C"])
    return f'<path d="{"".join(parts)}" fill="{col}" fill-opacity="{b["a"]:.2f}" filter="url(#soft)"/>'


def filt(W, H, interior=None):
    clip = ""
    if interior:
        d = "M" + " ".join(f"{x * 4} {y * 4}" for x, y in interior) + "Z"
        clip = f'<clipPath id="interior"><path d="{d}"/></clipPath>'
    return (f'<defs><filter id="soft" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<feGaussianBlur stdDeviation="{SIG * S:g}"/></filter>{clip}</defs>')


def main():
    cfg = getattr(rooms, sys.argv[1].upper())
    room = cfg["room"]
    img = load(cfg["source"])
    H, W = img.shape[:2]
    shell_path = OUT / f"{room}_shell.svg"
    shell = shell_path.read_text()
    shell = re.sub(r'\n<defs><filter id="soft".*?</defs>|\n<g id="shade"[^>]*>.*?</g>(?=\n</g>\n</svg>)', "", shell, flags=re.S)
    # base = flat shell + wall-mounted objects (lamps, boards); lights are drawn above those
    import json
    scores = json.loads((OUT / "build" / f"scores_{room}.json").read_text())
    wall_ids = {o["id"] for o in cfg["objects"] if o.get("wall")}
    wall_files = []
    for o in cfg["objects"]:
        if o.get("wall") and o["file"] not in wall_files:
            wall_files.append(o["file"])
    extra = ""
    for f in wall_files:
        sc = scores[f.split("/")[-1][:-4]]
        t = (OUT / f).read_text()
        extra += f'<g transform="translate({sc["x"]},{sc["y"]})">' + re.search(r"<svg[^>]*>\n(.*)</svg>", t, re.S).group(1) + "</g>"
    base = render(shell.replace("\n</svg>", extra + "\n</svg>"), W // S)[..., :3].astype(np.float32)
    O = np.array(Image.fromarray(img).resize((W // S, H // S), Image.BOX)).astype(np.float32)
    masks = np.load(OUT / "build" / f"masks_{room}.npz")
    hole = np.zeros(img.shape[:2], bool)
    for k in masks.files:
        if k not in wall_ids:
            hole |= masks[k]
    hole8 = np.array(Image.fromarray((hole * 255).astype(np.uint8)).resize((W // S, H // S), Image.BOX)) > 60
    valid = ~ndi.binary_dilation(hole8, iterations=1)
    for poly in cfg.get("no_light", []):  # e.g. porthole glass: keep its own colors
        from tracelib import poly_mask
        pm = poly_mask((H, W), poly)
        valid &= ~(np.array(Image.fromarray((pm * 255).astype(np.uint8)).resize((W // S, H // S))) > 0)
    from tracelib import poly_mask
    inter = poly_mask((H // S, W // S), cfg["interior"], scale=4 / S)
    valid &= inter
    shade, P = fit_blobs(O, base, valid, -1)
    light, P = fit_blobs(O, P, valid, +1)
    print(f"{len(shade)} shade blobs, {len(light)} light blobs; fit MAE@1/8 {np.abs(O - P)[valid].mean():.2f}"
          f" (flat {np.abs(O - base)[valid].mean():.2f})")
    # shade -> shell
    sh = "\n".join(path_of(b) for b in shade)
    shell = shell.replace("\n</g>\n</svg>", f'\n<g id="shade" clip-path="url(#interior)">\n{sh}\n</g>\n</g>\n</svg>')
    shell = shell.replace(">\n<g id=", ">\n" + filt(W, H, cfg["interior"]) + "\n<g id=", 1)
    shell_path.write_text(shell)
    # light -> per-source groups
    srcs = cfg["lights"]
    groups = {s["id"]: [] for s in srcs}
    for b in light:
        dist = [((b["cx"] - s["x"] * 4) ** 2 + (0.5 * (b["cy"] - s["y"] * 4)) ** 2, s["id"]) for s in srcs]
        groups[min(dist)[1]].append(path_of(b))
    body = "\n".join(f'<g id="{k}">\n' + "\n".join(v) + "\n</g>" for k, v in groups.items() if v)
    (OUT / f"{room}_lights.svg").write_text(svg_doc(W, H, filt(W, H, cfg["interior"]) + f'\n<g id="{room}_lights" clip-path="url(#interior)">\n{body}\n</g>'))


if __name__ == "__main__":
    main()
