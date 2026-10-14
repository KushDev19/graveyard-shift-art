"""Step 4: special parts (clock hands, sliding door), manifest JSON + debug overlay, Chromium PNG exports.
Usage: python finalize.py galley|locker"""
import json
import re
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

import rooms
from tracelib import OUT, composite, font, load, mae, render, render_chrome, svg_doc

CHECK = OUT / "check"
PLUM = "#3B1F3D"

EXTRA = {
    "galley": dict(
        walkable=[(155, 336), (1220, 336), (1262, 470), (1348, 700), (800, 700), (800, 744), (584, 744), (584, 700),
                  (28, 700), (112, 470)],
        doors=[dict(id="left", side="left", box=[(50, 226), (114, 608)]),
               dict(id="right", side="right", box=[(1260, 226), (1326, 608)]),
               dict(id="bottom", side="bottom", box=[(584, 700), (800, 746)])],
        anchors=dict(emergency_pedestal=(688, 438),
                     seats=[(487, 428), (588, 428), (787, 428), (887, 428), (350, 520), (1026, 520),
                            (480, 600), (583, 600), (792, 600), (897, 600)],
                     vents=[(230, 640), (1150, 640)]),
        depth={"table": 60, "coffee_counter": 34, "vending_machine": 30, "fridge": 30, "plant_1": 18, "plant_2": 18},
        default_depth=12, no_collision=["lamp", "cork_board"],
        light_radius=dict(light_lamp=520, light_vending=420, light_door=380)),
    "locker": dict(
        walkable=[(155, 336), (1220, 336), (1262, 470), (1348, 700), (800, 700), (800, 744), (584, 744), (584, 700),
                  (28, 700), (112, 470)],
        doors=[dict(id="bulkhead", side="back", box=[(243, 122), (461, 345)]),
               dict(id="bottom", side="bottom", box=[(584, 700), (800, 746)])],
        anchors=dict(timeclock_alcove=(1108, 330), vents=[(300, 662)],
                     seats=[(420, 496), (495, 496), (570, 496), (805, 496), (880, 496), (955, 496), (140, 440),
                            (125, 482), (110, 524), (688, 600)]),
        depth={"lockers": 18, "coffee_counter": 30, "water_cooler": 26, "bench_left": 30, "bench_right": 30,
               "bench_side": 60, "locker_04": 18, "locker_06": 18, "locker_04_door": 20},
        default_depth=14, no_collision=["lamp", "cork_board", "clock", "beacon", "door_frame", "door_leaf", "rug"],
        light_radius=dict(light_lamp=520, light_beacon=300, light_alcove=360)),
}


def q(p):
    return [int(p[0] * 4), int(p[1] * 4)]


def hull_poly(mask, depth_px):
    ys, xs = np.where(mask)
    bottom = ys.max()
    band = mask & (np.arange(mask.shape[0])[:, None] >= bottom - depth_px)
    pts = np.column_stack(np.where(band)[::-1]).astype(np.int32)
    hull = cv2.convexHull(pts)
    hull = cv2.approxPolyDP(hull, 6, True).reshape(-1, 2)
    return [[int(x), int(y)] for x, y in hull], int(bottom)


def clock_hands(cfg, scores):
    sc = scores["locker_clock"]
    ox, oy, w, h = sc["x"], sc["y"], sc["w"], sc["h"]
    cx, cy = 688 * 4 - ox, 98.5 * 4 - oy
    piv = f'data-pivot="{cx:g},{cy:g}"'
    hub = f'<circle cx="{cx:g}" cy="{cy:g}" r="17" fill="{PLUM}"/><circle cx="{cx:g}" cy="{cy:g}" r="7.5" fill="#8C7C8E"/>'
    # minute hand points to 12, hour hand to 3 (as painted); code rotates them about data-pivot
    minute = (f'<path d="M{cx - 5:g} {cy:g} V{cy - 74:g} H{cx - 15:g} L{cx:g} {cy - 120:g} L{cx + 15:g} {cy - 74:g} '
              f'H{cx + 5:g} V{cy:g} Z" fill="{PLUM}" stroke="{PLUM}" stroke-width="2" stroke-linejoin="round"/>')
    hour = (f'<path d="M{cx:g} {cy - 5:g} H{cx + 70:g} V{cy - 15:g} L{cx + 105:g} {cy:g} L{cx + 70:g} {cy + 15:g} '
            f'V{cy + 5:g} H{cx:g} Z" fill="{PLUM}" stroke="{PLUM}" stroke-width="2" stroke-linejoin="round"/>')
    (OUT / "objects/locker_clock_hand_hour.svg").write_text(
        svg_doc(w, h, f'<g id="clock_hand_hour" {piv}>{hour}</g>'))
    (OUT / "objects/locker_clock_hand_minute.svg").write_text(
        svg_doc(w, h, f'<g id="clock_hand_minute" {piv}>{minute}{hub}</g>'))
    face = (OUT / "objects/locker_clock.svg").read_text()
    inner = re.search(r"<svg[^>]*>\n(.*)</svg>", face, re.S).group(1)
    full = svg_doc(w, h, inner + f"<g>{hour}</g><g>{minute}{hub}</g>")
    img = load(cfg["source"])
    comp = composite(img, render(full, w), ox, oy)
    m = np.load(OUT / "build/masks_locker.npz")["clock"]
    s = mae(img, comp, m)
    for k in ("hour", "minute"):
        Image.fromarray(render((OUT / f"objects/locker_clock_hand_{k}.svg").read_text(), w // 2)).save(
            OUT / f"objects/locker_clock_hand_{k}.png")
    a = img[oy:oy + h, ox:ox + w]
    b = comp[oy:oy + h, ox:ox + w]
    Image.fromarray(np.hstack([a, np.full((h, 8, 3), 255, np.uint8), b])).save(CHECK / "locker_clock_assembled_side_by_side.png")
    print(f"clock face+hands MAE {s:.2f}")
    return round(s, 2)


def door_states(cfg, scores):
    fr = scores["locker_door_frame"]
    ox, oy, w, h = fr["x"], fr["y"], fr["w"], fr["h"]
    x0, y0, x1, y1 = 272 * 4 - ox, 175 * 4 - oy, 434 * 4 - ox, 334 * 4 - oy
    def inner(name):
        t = (OUT / f"objects/{name}.svg").read_text()
        return re.search(r"<svg[^>]*>\n(.*)</svg>", t, re.S).group(1)
    L, R = scores["locker_door_leaf_left"], scores["locker_door_leaf_right"]
    clip = f'<clipPath id="opening"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>'
    doorway = f'<rect id="doorway" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#2E1E34"/>'
    for state, slide in (("closed", 0), ("open", 1)):
        lx = L["x"] - ox - slide * L["w"]
        rx = R["x"] - ox + slide * R["w"]
        body = (f'<defs>{clip}</defs>{doorway}<g id="leaves" clip-path="url(#opening)">'
                f'<g transform="translate({lx},{L["y"] - oy})" data-slide="-{L["w"]}">{inner("locker_door_leaf_left")}</g>'
                f'<g transform="translate({rx},{R["y"] - oy})" data-slide="{R["w"]}">{inner("locker_door_leaf_right")}</g></g>'
                f'{inner("locker_door_frame")}')
        svg = svg_doc(w, h, f'<g id="locker_door_{state}">{body}</g>')
        (OUT / f"objects/locker_door_{state}.svg").write_text(svg)
        Image.fromarray(render(svg, w // 2)).save(OUT / f"objects/locker_door_{state}.png")


def manifest(cfg, scores, ex):
    masks = np.load(OUT / f"build/masks_{cfg['room']}.npz")
    room = cfg["room"]
    objs = []
    done = set()
    for o in cfg["objects"]:
        f = o["file"]
        stem = f.split("/")[-1][:-4]
        if f in done:
            continue
        done.add(f)
        sc = scores[stem]
        ids = [p["id"] for p in cfg["objects"] if p["file"] == f]
        m = np.zeros(masks[ids[0]].shape, bool)
        for i in ids:
            m |= masks[i]
        layer = "wall" if o.get("wall") else "floor" if o.get("floor") else "sorted"
        entry = dict(id=stem.replace(f"{room}_", ""), file=f, x=sc["x"], y=sc["y"], w=sc["w"], h=sc["h"], layer=layer)
        key = next((k for k in ex["depth"] if entry["id"].startswith(k)), None)
        poly, bottom = hull_poly(m, ex["depth"].get(key, ex["default_depth"]) * 4)
        entry["sortY"] = 0 if layer != "sorted" else bottom
        if not any(entry["id"].startswith(n) for n in ex["no_collision"]):
            entry["collision"] = poly
        objs.append(entry)
    lights = []
    for s in cfg["lights"]:
        r = next((v for k, v in ex["light_radius"].items() if s["id"].startswith(k)), 400)
        lights.append(dict(id=s["id"], group=s["id"], x=s["x"] * 4, y=s["y"] * 4, radius=r, color="#F5A54A"))
    anchors = {}
    for k, v in ex["anchors"].items():
        anchors[k] = q(v) if isinstance(v, tuple) else [q(p) for p in v]
    data = dict(room=room, source=f"raw_originals/{cfg['source']}", size=[5504, 3072],
                shell=f"{room}_shell.svg", lights_layer=f"{room}_lights.svg",
                draw_order=["shell", "objects with layer=wall", "lights_layer (flicker its groups)",
                            "objects with layer=floor", "objects with layer=sorted and players, by sortY"],
                objects=objs, walkable=[q(p) for p in ex["walkable"]],
                doors=[dict(id=d["id"], side=d["side"], x=d["box"][0][0] * 4, y=d["box"][0][1] * 4,
                            w=(d["box"][1][0] - d["box"][0][0]) * 4, h=(d["box"][1][1] - d["box"][0][1]) * 4)
                       for d in ex["doors"]],
                anchors=anchors, lights=lights)
    if room == "locker":
        fr = next(o for o in objs if o["id"] == "door_frame")
        data["sliding_door"] = dict(closed="objects/locker_door_closed.svg", open="objects/locker_door_open.svg",
                                    leaves=["door_leaf_left", "door_leaf_right"],
                                    slide_px={"door_leaf_left": -scores["locker_door_leaf_left"]["w"],
                                              "door_leaf_right": scores["locker_door_leaf_right"]["w"]},
                                    clip=[272 * 4, 175 * 4, 162 * 4, 159 * 4], note="leaves draw under door_frame, clipped to clip rect")
        data["clock_hands"] = dict(hour="objects/locker_clock_hand_hour.svg", minute="objects/locker_clock_hand_minute.svg",
                                   x=scores["locker_clock"]["x"], y=scores["locker_clock"]["y"], pivot=q((688, 98.5)),
                                   painted_time="3:00")
    (OUT / f"{room}.json").write_text(json.dumps(data, indent=1))
    # debug overlay at half scale
    im = Image.open(OUT / f"{room}_room.png").convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    h2 = lambda pts: [(x / 2, y / 2) for x, y in pts]
    d.polygon(h2(data["walkable"]), fill=(60, 220, 90, 60), outline=(60, 220, 90, 255))
    for o in objs:
        if "collision" in o:
            d.polygon(h2(o["collision"]), fill=(230, 40, 40, 80), outline=(230, 40, 40, 255))
        if o["sortY"]:
            d.line([(o["x"] / 2, o["sortY"] / 2), ((o["x"] + o["w"]) / 2, o["sortY"] / 2)], fill=(40, 90, 255, 255), width=3)
    for dd in data["doors"]:
        d.rectangle([dd["x"] / 2, dd["y"] / 2, (dd["x"] + dd["w"]) / 2, (dd["y"] + dd["h"]) / 2], outline=(255, 255, 255, 255), width=3)
        d.text((dd["x"] / 2 + 4, dd["y"] / 2 + 4), "door:" + dd["id"], fill=(255, 255, 255), font=font(22))
    for k, v in anchors.items():
        for p in (v if isinstance(v[0], list) else [v]):
            d.ellipse([p[0] / 2 - 9, p[1] / 2 - 9, p[0] / 2 + 9, p[1] / 2 + 9], fill=(255, 220, 0, 255), outline=(0, 0, 0))
        p0 = v if not isinstance(v[0], list) else v[0]
        d.text((p0[0] / 2 + 12, p0[1] / 2 - 10), k, fill=(255, 220, 0), font=font(22), stroke_width=2, stroke_fill=(0, 0, 0))
    for l in lights:
        d.ellipse([l["x"] / 2 - l["radius"] / 2, l["y"] / 2 - l["radius"] / 2, l["x"] / 2 + l["radius"] / 2,
                   l["y"] / 2 + l["radius"] / 2], outline=(255, 170, 60, 200), width=2)
    im.save(CHECK / f"{room}_manifest_debug.png")


def exports(cfg):
    room = cfg["room"]
    for name in (f"{room}_shell", f"{room}_lights"):
        svg = (OUT / f"{name}.svg").read_text()
        Image.fromarray(render_chrome(svg, 2752)).save(OUT / f"{name}.png")


def main():
    cfg = getattr(rooms, sys.argv[1].upper())
    ex = EXTRA[cfg["room"]]
    scores = json.loads((OUT / f"build/scores_{cfg['room']}.json").read_text())
    if cfg["room"] == "locker":
        scores["clock_assembled_mae"] = clock_hands(cfg, scores)
        door_states(cfg, scores)
        (OUT / f"build/scores_{cfg['room']}.json").write_text(json.dumps(scores, indent=1))
    exports(cfg)
    manifest(cfg, scores, ex)


if __name__ == "__main__":
    main()
