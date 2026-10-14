"""Step 2: trace objects and shell to layered SVG, export PNGs, write check images and MAE scores.
Usage: python build_room.py galley [only_file_substring]"""
import json
import sys
from collections import OrderedDict

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import rooms
from tracelib import (OUT, delight, quantize, render_chrome, crop_rgba, composite, directional_fill, load, mae, render, segment, svg_doc,
                      trace_rgba, vfill)

CHECK = OUT / "check"


def side_by_side(orig, comp, box, name, onion_rgba=None):
    x, y, w, h = box
    p = 24
    x0, y0 = max(x - p, 0), max(y - p, 0)
    x1, y1 = min(x + w + p, orig.shape[1]), min(y + h + p, orig.shape[0])
    a, b = orig[y0:y1, x0:x1], comp[y0:y1, x0:x1]
    sc = min(1.0, 900 / max(a.shape[1], 1), 900 / max(a.shape[0], 1))
    size = (max(int(a.shape[1] * sc), 1), max(int(a.shape[0] * sc), 1))
    gap = np.full((size[1], 8, 3), 255, np.uint8)
    A = np.array(Image.fromarray(a).resize(size, Image.LANCZOS))
    B = np.array(Image.fromarray(b).resize(size, Image.LANCZOS))
    Image.fromarray(np.hstack([A, gap, B])).save(CHECK / f"{name}_side_by_side.png")
    if onion_rgba is not None:
        on = orig.astype(np.float32).copy()
        h2, w2 = onion_rgba.shape[:2]
        al = onion_rgba[..., 3:4] / 255.0 * 0.5
        on[y:y + h2, x:x + w2] = on[y:y + h2, x:x + w2] * (1 - al) + onion_rgba[..., :3] * al
        O = on[y0:y1, x0:x1].clip(0, 255).astype(np.uint8)
        Image.fromarray(O).resize(size, Image.LANCZOS).save(CHECK / f"{name}_onion.png")


def trace_piece(img, mask, ox, oy, pid, quant=24, **kw):
    rgba, (x, y, w, h) = crop_rgba(img, mask)
    if quant:
        m = rgba[..., 3] > 0
        rgba[..., :3] = quantize(img[y:y + h, x:x + w], m, quant)
        rgba[..., :3][~m] = 0
        kw = dict(dict(color_precision=8, layer_difference=1, filter_speckle=8), **kw)
    paths = trace_rgba(rgba, **kw)
    m = rgba[..., 3] > 0
    clip = ""
    if (ndi.binary_fill_holes(m) & ~m).sum() > 200:  # stacked tracing cannot cut holes: clip to the mask
        cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        d = "".join("M" + " ".join(f"{p[0]} {p[1]}" for p in cv2.approxPolyDP(c, 1.0, True).reshape(-1, 2)) + "Z"
                    for c in cs if len(c) > 2)
        paths = (f'<clipPath id="clip_{pid}"><path d="{d}" clip-rule="evenodd"/></clipPath>\n'
                 f'<g clip-path="url(#clip_{pid})">\n{paths}\n</g>')
    return f'<g id="{pid}" transform="translate({x - ox},{y - oy})">\n{paths}\n</g>'


def build_objects(cfg, img, masks, only=None):
    files = OrderedDict()
    for o in cfg["objects"]:
        files.setdefault(o["file"], []).append(o)
    results = {}
    imgb = img
    for f, objs in files.items():
        if only and only not in f:
            continue
        union = np.zeros(img.shape[:2], bool)
        for o in objs:
            union |= masks[o["id"]]
        ys, xs = np.where(union)
        x0, y0 = int(xs.min()) - 2, int(ys.min()) - 2
        w, h = int(xs.max()) + 3 - x0, int(ys.max()) + 3 - y0
        body = []
        for o in objs:
            m = masks[o["id"]]
            src = imgb
            if o.get("erase"):  # paint out parts that become separate SVGs (e.g. clock hands)
                from tracelib import poly_mask
                src = img.copy()
                for e in o["erase"]:
                    hole = poly_mask(img.shape, e["poly"]) & (img[..., 1] < 150) & m
                    hole = ndi.binary_dilation(hole, iterations=3) & m
                    known = m & ~hole
                    src = vfill(src, hole, known=known) if e["fill"] == "v" else directional_fill(src, hole, known=known)
            body.append(trace_piece(src, m, x0, y0, o["id"], **o.get("trace", {})))
            for p in o.get("parts", []):
                pm = segment(img, p["poly"], ~m, cfg.get("barrier", 55), p.get("mode", "flood"))
                body.append(trace_piece(imgb, pm, x0, y0, p["id"], **o.get("trace", {})))
        stem = f.split("/")[-1][:-4]
        extra = ""
        if objs[0].get("pivot"):
            extra = f' data-pivot="{objs[0]["pivot"][0] - x0},{objs[0]["pivot"][1] - y0}"'
        svg = svg_doc(w, h, f'<g id="{stem}"{extra}>\n' + "\n".join(body) + "\n</g>")
        path = OUT / f
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg)
        full = render(svg, w)
        Image.fromarray(render(svg, max(w // 2, 1))).save(path.with_suffix(".png"))
        comp = composite(img, full, x0, y0)
        score = mae(img, comp, union)
        side_by_side(img, comp, (x0, y0, w, h), stem, full)
        results[stem] = dict(file=f, x=x0, y=y0, w=w, h=h, mae=round(score, 2), kb=round(len(svg) / 1024, 1),
                             ids=[o["id"] for o in objs])
        print(f"{stem:32s} MAE {score:5.2f}  {len(svg) / 1024:7.1f} KB")
    return results


def repaint_shell(cfg, img, masks):
    hole_all = np.zeros(img.shape[:2], bool)
    grown = {}
    for o in cfg["objects"]:
        grown[o["id"]] = ndi.binary_dilation(masks[o["id"]], iterations=8)
        hole_all |= grown[o["id"]]
    out = img.copy()
    remaining = hole_all.copy()
    for o in reversed(cfg["objects"]):  # back objects first
        hole = grown[o["id"]] & remaining
        if not hole.any():
            continue
        known = ~remaining
        if o.get("fill", "h") == "v":
            out = vfill(out, hole, known=known, side=o.get("side", "both"))
        else:
            out = directional_fill(out, hole, known=known, side=o.get("side", "both"))
        remaining &= ~hole
    for r in cfg.get("repaint", []):  # hand-specified flat repaints, e.g. a doorway behind sliding leaves
        from tracelib import poly_mask
        pm = poly_mask(img.shape, r["poly"])
        out[pm] = r["color"]
    return out, hole_all


def build_shell(cfg, img, masks):
    filled, hole = repaint_shell(cfg, img, masks)
    Image.fromarray(filled).resize((1376, 768)).save(CHECK / f"{cfg['room']}_shell_repaint.png")
    H, W = img.shape[:2]
    half = np.array(Image.fromarray(filled).resize((W // 2, H // 2), Image.LANCZOS))
    half = delight(half)
    Image.fromarray(half).resize((1376, 768)).save(CHECK / f"{cfg['room']}_shell_flat.png")
    rgba = np.dstack([half, np.full(half.shape[:2], 255, np.uint8)])
    groups = [f'<g id="base" transform="scale(2)">\n{trace_rgba(rgba, filter_speckle=9, color_precision=6, layer_difference=20)}\n</g>']
    claimed = np.zeros(img.shape[:2], bool)
    for p in cfg.get("shell_parts", []):
        pm = segment(img, p["poly"], claimed, cfg.get("barrier", 55), p.get("mode", "flood"))
        claimed |= pm
        groups.append(trace_piece(filled, pm, 0, 0, p["id"], quant=p.get("quant", 24), filter_speckle=p.get("speckle", 8)))
    stem = f"{cfg['room']}_shell"
    svg = svg_doc(W, H, f'<g id="{stem}">\n' + "\n".join(groups) + "\n</g>")
    (OUT / f"{stem}.svg").write_text(svg)
    full = render(svg, W)[..., :3]
    Image.fromarray(render(svg, W // 2)).save(OUT / f"{stem}.png")
    score = mae(img, full, ~hole)
    side_by_side(img, full, (0, 0, W, H), stem)
    print(f"{stem:32s} MAE {score:5.2f}  {len(svg) / 1024:7.1f} KB (outside object holes)")
    return dict(file=f"{stem}.svg", mae=round(score, 2), kb=round(len(svg) / 1024, 1)), full


def compose(cfg, img, scores):
    """Inline every layer into <room>_room.svg (preview / single-image use) and score the whole room."""
    import re
    H, W = img.shape[:2]
    shell = (OUT / f"{cfg['room']}_shell.svg").read_text()
    inner = [re.search(r"<svg[^>]*>\n(.*)</svg>", shell, re.S).group(1)]
    lights = OUT / f"{cfg['room']}_lights.svg"
    light_inner = re.search(r"<svg[^>]*>\n(.*)</svg>", lights.read_text(), re.S).group(1) if lights.exists() else ""
    light_inner = re.sub(r"<defs>.*?</defs>", "", light_inner, flags=re.S)  # same defs as the shell
    files = []
    for o in cfg["objects"]:
        if o["file"] not in files:
            files.append(o["file"])
    order = sorted(files, key=lambda f: (0 if any(o.get("wall") or o.get("floor") for o in cfg["objects"] if o["file"] == f) else 1,
                                         scores[f.split("/")[-1][:-4]]["y"] + scores[f.split("/")[-1][:-4]]["h"]))
    wall = [f for f in order if any(o.get("wall") for o in cfg["objects"] if o["file"] == f)]
    order = wall + [f for f in order if f not in wall]
    for f in order:
        if f == (order[len(wall)] if len(order) > len(wall) else None):
            inner.append(light_inner)
        sc = scores[f.split("/")[-1][:-4]]
        t = (OUT / f).read_text()
        inner.append(f'<g transform="translate({sc['x']},{sc['y']})">' + re.search(r"<svg[^>]*>\n(.*)</svg>", t, re.S).group(1) + "</g>")
    for f, anchor in cfg.get("overlays", []):  # separate moving parts (clock hands) placed like their base object
        if (OUT / f).exists():
            sc = scores[anchor]
            t = (OUT / f).read_text()
            inner.append(f'<g transform="translate({sc['x']},{sc['y']})">' + re.search(r"<svg[^>]*>\n(.*)</svg>", t, re.S).group(1) + "</g>")
    svg = svg_doc(W, H, f'<g id="{cfg["room"]}_room">\n' + "\n".join(inner) + "\n</g>")
    (OUT / "build" / f"{cfg['room']}_room_full.svg").write_text(svg)  # inline composite, kept out of deliverables (> 1.5 MB)
    full = render_chrome(svg, W)[..., :3]
    Image.fromarray(full).resize((W // 2, H // 2), Image.LANCZOS).save(OUT / f"{cfg['room']}_room.png")
    score = mae(img, full, np.ones(img.shape[:2], bool))
    q = (W // 4, H // 4)
    A = np.array(Image.fromarray(img).resize(q, Image.LANCZOS)); B = np.array(Image.fromarray(full).resize(q, Image.LANCZOS))
    Image.fromarray(np.vstack([A, np.full((8, q[0], 3), 255, np.uint8), B])).save(CHECK / f"{cfg['room']}_room_side_by_side.png")
    on = (A.astype(np.float32) * 0.5 + B * 0.5).astype(np.uint8)
    Image.fromarray(on).save(CHECK / f"{cfg['room']}_room_onion.png")
    print(f"{cfg['room']}_room MAE {score:5.2f}  {len(svg) / 1024:7.1f} KB")
    return dict(file=f"{cfg['room']}_room.svg", mae=round(score, 2), kb=round(len(svg) / 1024, 1))


def main():
    cfg = getattr(rooms, sys.argv[1].upper())
    only = sys.argv[2] if len(sys.argv) > 2 else None
    img = load(cfg["source"])
    masks = dict(np.load(OUT / "build" / f"masks_{cfg['room']}.npz"))
    CHECK.mkdir(exist_ok=True)
    scores_path = OUT / "build" / f"scores_{cfg['room']}.json"
    scores = json.loads(scores_path.read_text()) if scores_path.exists() else {}
    if only not in ("shell", "compose"):
        scores.update(build_objects(cfg, img, masks, only))
    if only in (None, "shell"):
        scores["shell"], _ = build_shell(cfg, img, masks)
        scores_path.write_text(json.dumps(scores, indent=1))
    if only in (None, "shell"):
        import subprocess
        subprocess.run([sys.executable, str(OUT / "build" / "light_fit.py"), cfg["room"]], check=True)
    if only in (None, "shell", "compose"):
        scores["room"] = compose(cfg, img, scores)
    scores_path.write_text(json.dumps(scores, indent=1))


if __name__ == "__main__":
    main()
