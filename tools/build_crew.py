"""Builds crew assets from frontend/public/assets/ship/crew/crew_puppet.svg:
  - crew_parts.png/.json    Phaser atlas (JSON hash) of every puppet part
  - crew_rig.json           part offsets, pivots, tint flags and draw order (viewBox units)
Previews go to art/work/ (lineup_preview, parts_preview, rig_check). Poses: key_poses.py."""
import colorsys
import json

import numpy as np
from PIL import Image

from svgtools import ET, NS, ROOT, WORK, cells, contact_sheet, pack, render_rgba, screenshot, trim, variant

MASTER = ROOT / "frontend/public/assets/ship/crew/crew_puppet.svg"
OUT = ROOT / "frontend/public/assets/ship/crew"
CW, CH = 640, 800

SIDE = ["leg_back", "arm_back", "leg_front", "backpack", "body", "stripe", "dome", "visor_glow", "visor",
        "glass_highlight", "collar", "antenna", "arm_front"]
FRONT = ["f_leg_l", "f_leg_r", "f_body", "f_stripe", "f_collar", "f_dome", "f_visor_glow", "f_visor",
         "glass_highlight", "f_antenna", "f_arm_l", "f_arm_r"]
TINT = {"leg_back", "arm_back", "leg_front", "backpack", "body", "collar", "antenna", "arm_front", "ghost_tail",
        "f_leg_l", "f_leg_r", "f_body", "f_arm_l", "f_arm_r", "f_collar", "f_antenna", "fallen_suit"}
# Light-grey base for multiply tinting: suit lands at 0.89 x player color, highlights stay at full color.
WHITE_BASE = "--suit:#E2E2E2;--suit-shade:#B0B0B0;--suit-back:#939393;--suit-light:#FFFFFF;"

COLORS = {"tomato": "#E4483C", "tangerine": "#F28A2E", "mustard": "#E9C046", "lime": "#A6D64A",
          "mint": "#6FD6B0", "sky": "#6EC3F0", "cobalt": "#3F5FD9", "grape": "#8E5AC8",
          "bubblegum": "#F07BB5", "cream": "#F4E6C8"}


def v(show, **kw):
    return variant(MASTER, show, **kw)


def tone(hex_color, f):
    r, g, b = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, min(0.95, l * f), s)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def suit_style(c):
    return f"--suit:{c};--suit-shade:{tone(c, .78)};--suit-back:{tone(c, .64)};--suit-light:{tone(c, 1.16)};"


def tinted(svg, c, extra=""):
    return svg.replace("<svg ", f'<svg style="{suit_style(c)}{extra}" ', 1)


def build_lineup():
    side, front = v(SIDE), v(FRONT)
    impostor = v([p if p != "visor" else "visor_coral" for p in SIDE if p != "visor_glow"])
    ghost = v(["arm_back", "ghost_tail", "backpack", "body", "stripe", "dome", "visor_ghost",
               "glass_highlight", "collar", "antenna", "arm_front"])
    items = [(side, None, "grey side"), (front, None, "grey front"),
             (side, COLORS["tomato"], "tomato"), (front, COLORS["mint"], "mint"),
             (side, COLORS["mustard"], "mustard"), (impostor, COLORS["cobalt"], "cobalt impostor visor"),
             (front, COLORS["bubblegum"], "bubblegum"), (tinted(ghost, "#CDCCD4", "opacity:.6;"), None, "ghost")]
    svgs = [tinted(s, c) if c else s for s, c, _ in items]
    screenshot(svgs, 4, 320, 400, "#2B4A5E", labels=[l for _, _, l in items], out=WORK / "lineup_preview.png")


def build_parts():
    extra = ["ghost_tail", "visor_coral", "visor_ghost", "visor_blink", "visor_surprised",
             "f_leg_l", "f_leg_r", "f_body", "f_stripe", "f_collar", "f_dome", "f_visor_glow", "f_visor",
             "f_antenna", "f_arm_l", "f_arm_r", "fallen_suit", "fallen_fx", "fallen_helmet"]
    names = SIDE + [e for e in extra if e not in SIDE]
    svgs = [v([n], style=WHITE_BASE if n in TINT else "") for n in names]
    cols = 6
    img = render_rgba(svgs, cols, CW, CH)
    master = ET.parse(MASTER).getroot()
    pivots = {g.get("id"): g.get("data-pivot") for g in master.iter(f"{{{NS}}}g") if g.get("data-pivot")}
    parts, rig = {}, {}
    for name, cell in zip(names, cells(img, len(names), cols, CW, CH)):
        t, box = trim(cell)
        parts[name] = t
        pv = [int(p) for p in pivots[name].split(",")] if name in pivots else None
        rig[name] = {"x": box[0], "y": box[1], "w": t.width, "h": t.height, "pivot": pv, "tint": name in TINT}
    atlas, pos = pack(parts)
    atlas.save(OUT / "crew_parts.png")
    frames = {k: {"frame": {"x": x, "y": y, "w": w, "h": h}, "rotated": False, "trimmed": False,
                  "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "sourceSize": {"w": w, "h": h}}
              for k, (x, y, w, h) in pos.items()}
    (OUT / "crew_parts.json").write_text(json.dumps(
        {"frames": frames, "meta": {"image": "crew_parts.png", "size": {"w": atlas.width, "h": atlas.height}, "scale": "1"}},
        indent=1))
    (OUT / "crew_rig.json").write_text(json.dumps({
        "viewBox": [CW, CH],
        "note": "Side view faces right; mirror for left. Place each part at (x, y) in viewBox units; rotate around "
                "pivot. tint=true parts are drawn on a light-grey base: multiply-tint them with the player color.",
        "order": {"side": SIDE, "front": FRONT},
        "swaps": {"ghost": {"hide": ["leg_back", "leg_front"], "show": ["ghost_tail"], "visor": "visor_ghost"},
                  "impostorPartner": {"visor": "visor_coral"}, "blink": {"visor": "visor_blink"},
                  "surprised": {"visor": "visor_surprised"}},
        "colors": COLORS,
        "parts": rig}, indent=1))
    contact_sheet(parts, WORK / "parts_preview.png")
    return parts, rig


def rig_check(parts, rig, color="#E4483C"):
    """Re-assemble the side puppet from exported parts with a multiply tint, like Phaser would."""
    tint = np.array([int(color[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    canvas = Image.new("RGBA", (CW, CH), (43, 74, 94, 255))
    for name in SIDE:
        im = parts[name]
        if rig[name]["tint"]:
            a = np.asarray(im).astype(np.float32)
            a[..., :3] *= tint
            im = Image.fromarray(a.astype(np.uint8), "RGBA")
        canvas.alpha_composite(im, (rig[name]["x"], rig[name]["y"]))
    canvas.save(WORK / "rig_check.png")


if __name__ == "__main__":
    build_lineup()
    parts, rig = build_parts()
    rig_check(parts, rig)
    print("done:", len(parts), "parts")
