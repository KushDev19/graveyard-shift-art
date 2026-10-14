"""Job D generator: Tier 2 task panels, their moving parts, the minimap, JSON, debug images.
Run from repo root: python art-jobs/out/D_panels2_minimap/src/build.py"""
import json
import math
import pathlib

import cairosvg
from PIL import Image, ImageDraw

OUTDIR = pathlib.Path(__file__).resolve().parent.parent
PARTS = OUTDIR / "parts"
DEBUG = OUTDIR / "debug"

OUT = "#2A1E35"; IND = "#1B1830"; PLUM = "#3D2A4F"; PLUM_D = "#2E2040"
TEAL = "#2F6F73"; TEAL_D = "#245558"; TEAL_L = "#3E8589"
SEA = "#7FC8B8"; SEA_D = "#5FA898"; SEA_L = "#B6E6DA"
AMB = "#F5A54A"; AMB_D = "#D9832E"; AMB_L = "#FFD08A"
CREAM = "#F4E6C8"; CREAM_D = "#DEC79C"; CREAM_L = "#FFF6E3"
CORAL = "#E8574A"; CORAL_D = "#C2413A"; PINK = "#D9738C"
GLASS = "#4A3A5E"; GLASS_D = "#3A2C4C"
SW = 10  # uniform outline width at panel scale (2048 wide)

_uid = [0]


def uid(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


# ---------- primitives ----------
def rr(x, y, w, h, r, fill, stroke=OUT, sw=SW, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(r)}" fill="{fill}"{s}{extra}/>'


def circ(cx, cy, r, fill, stroke=OUT, sw=SW, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"{s}{extra}/>'


def line(x1, y1, x2, y2, stroke, sw, cap="round", extra=""):
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="{cap}"{extra}/>')


def bevel_rr(x, y, w, h, r, base, shade, depth, sw=SW):
    """Two-tone raised block: shade band along the bottom, one outline."""
    cid = uid("c")
    return (f'<clipPath id="{cid}">{rr(x, y, w, h, r, "#000", None)}</clipPath>'
            f'<g clip-path="url(#{cid})">{rr(x, y, w, h, r, shade, None)}'
            f'{rr(x, y - r, w, h - depth + r, r, base, None)}</g>'
            f'{rr(x, y, w, h, r, "none", OUT, sw)}')


def bevel_circ(cx, cy, r, base, shade, depth, sw=SW):
    cid = uid("c")
    return (f'<clipPath id="{cid}">{circ(cx, cy, r, "#000", None)}</clipPath>'
            f'<g clip-path="url(#{cid})">{circ(cx, cy, r, shade, None)}'
            f'{circ(cx, cy - depth, r, base, None)}</g>{circ(cx, cy, r, "none", OUT, sw)}')


def recess_rr(x, y, w, h, r, inner=PLUM, shadow=PLUM_D, lip=CREAM_D, lipw=14, sdepth=22):
    """Empty socket: lip ring, dark well, shadow band on the TOP inner edge (light from above)."""
    cid = uid("c")
    out = rr(x - lipw, y - lipw, w + 2 * lipw, h + 2 * lipw, r + lipw, lip) if lipw else ""
    return out + (f'<clipPath id="{cid}">{rr(x, y, w, h, r, "#000", None)}</clipPath>'
                  f'<g clip-path="url(#{cid})">{rr(x, y, w, h, r, shadow, None)}'
                  f'{rr(x, y + sdepth, w, h, r, inner, None)}</g>{rr(x, y, w, h, r, "none")}')


def recess_circ(cx, cy, r, inner=PLUM, shadow=PLUM_D, lip=CREAM_D, lipw=14, sdepth=None):
    sdepth = sdepth if sdepth is not None else max(8, r * 0.18)
    cid = uid("c")
    out = circ(cx, cy, r + lipw, lip) if lipw else ""
    return out + (f'<clipPath id="{cid}">{circ(cx, cy, r, "#000", None)}</clipPath>'
                  f'<g clip-path="url(#{cid})">{circ(cx, cy, r, shadow, None)}'
                  f'{circ(cx, cy + sdepth, r, inner, None)}</g>{circ(cx, cy, r, "none")}')


def screw(cx, cy, r=34, ang=35):
    a = math.radians(ang)
    dx, dy = math.cos(a) * r * 0.62, math.sin(a) * r * 0.62
    return (bevel_circ(cx, cy, r, CREAM_L, CREAM_D, r * 0.25)
            + line(cx - dx, cy - dy - 3, cx + dx, cy + dy - 3, OUT, 8))


def glass_hl(x, y, w, h, r):
    """Soft CRT glass highlight: two flat white streaks, low opacity."""
    return (rr(x + r, y + 30, w * 0.42, 20, 10, "#FFFFFF", None, extra=' opacity="0.10"')
            + rr(x + r + w * 0.46, y + 30, w * 0.07, 20, 10, "#FFFFFF", None, extra=' opacity="0.10"')
            + rr(x + 30, y + r + 10, 20, h * 0.22, 10, "#FFFFFF", None, extra=' opacity="0.06"'))


def glow(cx, cy, r, color, op=0.55):
    gid = uid("g")
    return (f'<radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="url(#{gid})"/>')


def svg_doc(w, h, body, gid=None):
    inner = f'<g id="{gid}">{body}</g>' if gid else body
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{inner}</svg>\n')


# ---------- shared panel frame (same construction language as Job C) ----------
W, H = 2048, 1536


def frame():
    s = []
    # bezel body: cream, two-tone (darker cream band along the bottom), plum outline
    s.append('<g id="bezel">' + bevel_rr(24, 24, 2000, 1488, 96, CREAM, CREAM_D, 46, 14) + "</g>")
    # racing stripe across the top, clipped to the bezel: cream / amber / coral
    cid = uid("c")
    st = [f'<clipPath id="{cid}">{rr(24, 24, 2000, 1488, 96, "#000", None)}</clipPath><g clip-path="url(#{cid})">']
    y = 146
    for col in (CREAM_L, AMB, CORAL):
        st.append(f'<rect x="0" y="{y}" width="{W}" height="26" fill="{col}"/>')
        y += 26
    st.append(line(0, 146, W, 146, OUT, 6, "butt") + line(0, 224, W, 224, OUT, 6, "butt"))
    st.append(line(0, 172, W, 172, OUT, 3, "butt") + line(0, 198, W, 198, OUT, 3, "butt"))
    st.append("</g>")
    s.append('<g id="racing_stripe">' + "".join(st) + "</g>")
    s.append('<g id="screws">' + "".join(screw(x, y) for x, y in
             ((96, 88), (1952, 88), (96, 1428), (1952, 1428))) + "</g>")
    # bottom details: vent slots (left), unlit power lamp socket (right)
    v = "".join(rr(196 + i * 52, 1418, 26, 62, 13, PLUM, OUT, 6) for i in range(5))
    s.append(f'<g id="vent">{v}</g>')
    s.append('<g id="power_lamp_socket">' + recess_circ(1848, 1450, 22, lipw=10) + "</g>")
    return "".join(s)


POWER_LAMP = {"id": "power_lamp", "shape": "circle", "cx": 1848, "cy": 1450, "r": 22,
              "part": "lamp_small_unlit / lamp_small_lit_amber"}


# ---------- panel: thrusters ----------
def panel_thrusters():
    s = [frame()]
    # CRT module
    s.append('<g id="crt">' + bevel_rr(140, 262, 1220, 1092, 64, CREAM_D, "#CDB488", 28))
    sx, sy, sw_, sh = 196, 314, 1108, 960
    s.append(recess_rr(sx, sy, sw_, sh, 48, inner=IND, shadow="#120F22", lipw=0, sdepth=18))
    s.append("</g>")
    cy = sy + sh / 2  # target line y = 794
    # blank edge ticks
    t = []
    for i in range(1, 12):
        yy = sy + i * sh / 12
        L = 34 if i == 6 else 20
        t.append(line(sx + 30, yy, sx + 30 + L, yy, SEA, 5, extra=' opacity="0.45"'))
        t.append(line(sx + sw_ - 30, yy, sx + sw_ - 30 - L, yy, SEA, 5, extra=' opacity="0.45"'))
    s.append('<g id="screen_ticks">' + "".join(t) + "</g>")
    # thruster nozzle diagram, side view, axis on the target line, pointing right
    nx = 300
    d = (f"M{nx},{cy - 120} H{nx + 190} Q{nx + 230},{cy - 120} {nx + 250},{cy - 60} "
         f"L{nx + 270},{cy - 46} Q{nx + 330},{cy - 140} {nx + 470},{cy - 190} V{cy + 190} "
         f"Q{nx + 330},{cy + 140} {nx + 270},{cy + 46} L{nx + 250},{cy + 60} "
         f"Q{nx + 230},{cy + 120} {nx + 190},{cy + 120} H{nx} Z")
    noz = [f'<path d="{d}" fill="{SEA}" fill-opacity="0.12" stroke="{SEA}" stroke-width="9" stroke-linejoin="round"/>']
    noz.append(line(nx + 60, cy - 120, nx + 60, cy + 120, SEA, 6))
    noz.append(line(nx + 130, cy - 120, nx + 130, cy + 120, SEA, 6))
    noz.append(rr(nx - 70, cy - 60, 70, 120, 10, "none", SEA, 8))
    noz.append(line(nx - 70, cy, nx - 140, cy, SEA, 8))
    s.append('<g id="nozzle_diagram">' + "".join(noz) + "</g>")
    # dashed amber target line across the screen
    s.append('<g id="target_line">' + line(sx + 80, cy, sx + sw_ - 80, cy, AMB, 10, "round",
             ' stroke-dasharray="34 30"') + "</g>")
    s.append(glass_hl(sx, sy, sw_, sh, 48))
    # slider module
    s.append('<g id="slider_module">' + bevel_rr(1420, 262, 484, 1092, 64, CREAM_D, "#CDB488", 28))
    tx, tw, ty, th = 1662 - 40, 80, 330, 928
    tk = []
    for i in range(11):
        yy = ty + 50 + i * (th - 100) / 10
        long_ = i in (0, 5, 10)
        L = 70 if long_ else 44
        col = AMB if i == 5 else OUT
        tk.append(line(tx - 40 - L, yy, tx - 40, yy, col, 10 if i == 5 else 7))
        tk.append(line(tx + tw + 40, yy, tx + tw + 40 + L, yy, col, 10 if i == 5 else 7))
    s.append("".join(tk))
    s.append(recess_rr(tx, ty, tw, th, 40, lipw=16, lip="#CDB488"))
    s.append("</g>")
    sockets = [
        {"id": "crt_screen", "shape": "rect", "x": sx, "y": sy, "w": sw_, "h": sh,
         "cx": sx + sw_ / 2, "cy": cy, "note": "area for thrust_marker; nozzle drawn on the left"},
        {"id": "target_line", "shape": "hline", "x1": sx + 80, "x2": sx + sw_ - 80, "y": cy},
        {"id": "thrust_marker_path", "shape": "vline", "x": 980, "y1": sy + 90, "y2": sy + sh - 90,
         "part": "thrust_marker", "note": "marker center x fixed, y moves; aligned when y == target_line.y"},
        {"id": "slider_track", "shape": "rect", "x": tx, "y": ty, "w": tw, "h": th,
         "cx": tx + tw / 2, "cy": ty + th / 2},
        {"id": "slider_knob_path", "shape": "vline", "x": tx + tw / 2, "y1": ty + 50, "y2": ty + th - 50,
         "part": "slider_knob", "note": "knob center travels between y1 and y2; amber tick at cy is the target"},
        POWER_LAMP,
    ]
    return "".join(s), sockets


# ---------- panel: gyro ----------
GYRO_C = (1024, 682)
GYRO_GROOVES = [(392, 38), (282, 150), (172, 262)]  # (radius, notch angle deg, clockwise from up)
GROOVE_W = 46


def panel_gyro():
    cx, cy = GYRO_C
    s = [frame()]
    s.append('<g id="dial">' + bevel_circ(cx, cy, 488, CREAM_D, "#CDB488", 26))
    s.append(recess_circ(cx, cy, 446, inner=IND, shadow="#120F22", lipw=0, sdepth=16))
    rim = []
    for i in range(48):
        a = math.radians(i * 7.5)
        r1, r2 = (414, 436) if i % 4 else (404, 436)
        rim.append(line(cx + r1 * math.sin(a), cy - r1 * math.cos(a), cx + r2 * math.sin(a),
                        cy - r2 * math.cos(a), CREAM, 5 if i % 4 else 7, extra=' opacity="0.35"'))
    s.append('<g id="rim_ticks">' + "".join(rim) + "</g>")
    notches = []
    for i, (r, ang) in enumerate(GYRO_GROOVES):
        # groove = dark ring with a darker top half-shadow, outlined both edges
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#5A4878" stroke-width="{GROOVE_W + 16}"/>')
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{OUT}" stroke-width="{GROOVE_W + 4}"/>')
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0E0B18" stroke-width="{GROOVE_W - 4}"/>')
        s.append(f'<circle cx="{cx}" cy="{cy + 7}" r="{r}" fill="none" stroke="{PLUM_D}" stroke-width="{GROOVE_W - 22}"/>')
        a = math.radians(ang)
        nxp, nyp = cx + r * math.sin(a), cy - r * math.cos(a)
        ro = r + GROOVE_W / 2 + 6
        # seafoam notch: bar across the groove plus a small wedge on the outer edge
        bx1, by1 = cx + (r - GROOVE_W / 2 + 4) * math.sin(a), cy - (r - GROOVE_W / 2 + 4) * math.cos(a)
        bx2, by2 = cx + (ro + 4) * math.sin(a), cy - (ro + 4) * math.cos(a)
        g = [line(bx1, by1, bx2, by2, OUT, 26), line(bx1, by1, bx2, by2, SEA, 14)]
        px, py = math.cos(a), math.sin(a)
        tip = (cx + (ro + 6) * math.sin(a), cy - (ro + 6) * math.cos(a))
        base = (cx + (ro + 44) * math.sin(a), cy - (ro + 44) * math.cos(a))
        g.append(f'<polygon points="{f(tip[0])},{f(tip[1])} {f(base[0] + 24 * px)},{f(base[1] + 24 * py)} '
                 f'{f(base[0] - 24 * px)},{f(base[1] - 24 * py)}" fill="{SEA}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>')
        s.append(f'<g id="notch_{i}">' + "".join(g) + "</g>")
        notches.append({"id": f"groove_{i}", "shape": "ring", "cx": cx, "cy": cy, "r": r, "width": GROOVE_W,
                        "notch_angle_deg": ang, "notch_x": round(nxp, 1), "notch_y": round(nyp, 1),
                        "part": "gyro_bead / gyro_bead_locked",
                        "note": "bead center at (cx + r*sin(a), cy - r*cos(a)), a clockwise from up; aligned when a == notch_angle_deg"})
    # center hub (static)
    s.append(bevel_circ(cx, cy, 62, TEAL_L, TEAL_D, 12) + circ(cx, cy - 6, 18, CREAM, OUT, 6))
    s.append("</g>")
    # button socket and two lamps
    bcx, bcy = 1024, 1300
    s.append('<g id="button_socket">' + recess_circ(bcx, bcy, 118, lipw=18) + "</g>")
    s.append('<g id="lamp_sockets">' + recess_circ(bcx - 250, bcy, 34, lipw=12)
             + recess_circ(bcx + 250, bcy, 34, lipw=12) + "</g>")
    # side decoration: three toggle switches left, vent grille right
    dec = []
    for i in range(3):
        yy = 520 + i * 170
        dec.append(rr(250, yy - 46, 120, 92, 22, PLUM, OUT, 8))
        dec.append(line(310, yy, 310, yy - 60, OUT, 30) + line(310, yy, 310, yy - 60, CREAM_D, 16))
        dec.append(circ(310, yy - 66, 20, CREAM_L, OUT, 7))
    for i in range(6):
        dec.append(rr(1690, 460 + i * 80, 140, 34, 17, PLUM, OUT, 7))
    s.append('<g id="side_details">' + "".join(dec) + "</g>")
    sockets = notches + [
        {"id": "dial_face", "shape": "circle", "cx": cx, "cy": cy, "r": 446},
        {"id": "button_big", "shape": "circle", "cx": bcx, "cy": bcy, "r": 118, "part": "btn_big_round_idle / _pressed"},
        {"id": "lamp_left", "shape": "circle", "cx": bcx - 250, "cy": bcy, "r": 34, "part": "lamp_small_*"},
        {"id": "lamp_right", "shape": "circle", "cx": bcx + 250, "cy": bcy, "r": 34, "part": "lamp_small_*"},
        POWER_LAMP,
    ]
    return "".join(s), sockets


# ---------- panel: memory ----------
MEM_X = [330, 572, 814]
MEM_BX = [1232, 1474, 1716]
MEM_Y = [524, 766, 1008]


def panel_memory():
    s = [frame()]
    s.append('<g id="crt">' + bevel_rr(140, 262, 870, 1012, 64, CREAM_D, "#CDB488", 28))
    sx, sy, sw_, sh = 196, 314, 758, 880
    s.append(recess_rr(sx, sy, sw_, sh, 48, inner=IND, shadow="#120F22", lipw=0, sdepth=18))
    grid = []
    for y in MEM_Y:
        for x in MEM_X:
            grid.append(recess_circ(x, y, 86, inner="#120E1F", shadow="#0B0916", lip=GLASS_D, lipw=12, sdepth=14))
    s.append('<g id="lamp_grid">' + "".join(grid) + "</g>")
    s.append(glass_hl(sx, sy, sw_, sh, 48) + "</g>")
    # teal metal plate
    s.append('<g id="button_plate">' + bevel_rr(1040, 262, 868, 1012, 64, TEAL, TEAL_D, 32))
    for x, y in ((1092, 314), (1856, 314), (1092, 1196), (1856, 1196)):
        s.append(circ(x, y, 18, TEAL_L, OUT, 6) + line(x - 10, y - 6, x + 10, y + 6, OUT, 5))
    for y in MEM_Y:
        for x in MEM_BX:
            s.append(recess_rr(x - 90, y - 90, 180, 180, 30, lip=TEAL_D, lipw=12))
    s.append("</g>")
    prog = []
    PX = [744, 884, 1024, 1164, 1304]
    for x in PX:
        prog.append(recess_circ(x, 1340, 30, lipw=12))
    s.append('<g id="progress_lamps">' + "".join(prog) + "</g>")
    sockets = []
    for j, y in enumerate(MEM_Y):
        for i, x in enumerate(MEM_X):
            sockets.append({"id": f"lamp_{j}{i}", "shape": "circle", "cx": x, "cy": y, "r": 86,
                            "part": "lamp_round_unlit / lamp_round_lit"})
    for j, y in enumerate(MEM_Y):
        for i, x in enumerate(MEM_BX):
            sockets.append({"id": f"button_{j}{i}", "shape": "rect", "x": x - 90, "y": y - 90, "w": 180, "h": 180,
                            "cx": x, "cy": y, "part": "btn_square_idle / _pressed / _correct / _wrong"})
    for k, x in enumerate(PX):
        sockets.append({"id": f"progress_{k}", "shape": "circle", "cx": x, "cy": 1340, "r": 30,
                        "part": "lamp_small_unlit / lamp_small_lit_seafoam"})
    sockets.append(POWER_LAMP)
    return "".join(s), sockets


# ---------- moving parts (drawn at 1:1 panel scale, centered in their viewBox) ----------
def part_slider_knob():
    w, h = 300, 170
    b = [bevel_rr(22, 26, 256, 118, 30, CREAM, CREAM_D, 26)]
    for x in (110, 150, 190):
        b.append(line(x, 50, x, 104, CREAM_D, 12) + line(x, 50, x, 104, OUT, 4, extra=' opacity="0"'))
    b.append(f'<polygon points="22,80 52,62 52,98" fill="{AMB}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>')
    b.append(f'<polygon points="278,80 248,62 248,98" fill="{AMB}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>')
    return w, h, "".join(b)


def part_thrust_marker():
    w, h = 560, 140
    b = [glow(280, 70, 90, SEA, 0.25)]
    b.append(line(150, 70, 520, 70, SEA, 12))
    for x in (60, 110, 160):
        b.append(f'<polyline points="{x + 34},34 {x},70 {x + 34},106" fill="none" stroke="{SEA}" '
                 f'stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(circ(520, 70, 16, SEA_L, None))
    return w, h, "".join(b)


def part_bead(base, shade, hl):
    w = h = 96
    return w, h, bevel_circ(48, 48, 34, base, shade, 8, 8) + circ(38, 36, 9, hl, None)


def part_btn_big(pressed):
    w = h = 280
    b = [circ(140, 140, 116, AMB_D, OUT, SW)]
    if pressed:
        b.append(bevel_circ(140, 150, 92, "#E9963D", AMB_D, 10))
    else:
        b.append(bevel_circ(140, 132, 98, AMB, AMB_D, 22) + rr(92, 70, 56, 20, 10, AMB_L, None))
    return w, h, "".join(b)


def part_lamp(r, size, base, shade, lit, glow_col=None, core=None):
    w = h = size
    c = size / 2
    b = []
    if lit:
        b.append(glow(c, c, size / 2, glow_col, 0.6))
    b.append(bevel_circ(c, c, r, base, shade, r * 0.18, max(6, r * 0.12)))
    if core:
        b.append(circ(c, c - r * 0.12, r * 0.5, core, None))
    b.append(circ(c - r * 0.35, c - r * 0.4, r * 0.18, "#FFFFFF", None,
                  extra=f' opacity="{0.75 if lit else 0.25}"'))
    return w, h, "".join(b)


def part_btn_square(base, shade, pressed=False, glow_col=None):
    w = h = 220
    b = []
    if glow_col:
        b.append(glow(110, 110, 110, glow_col, 0.5))
    if pressed:
        b.append(bevel_rr(28, 34, 164, 158, 28, shade, shade, 0))
        b.append(bevel_rr(28, 40, 164, 152, 28, base, shade, 10))
    else:
        b.append(bevel_rr(28, 28, 164, 164, 28, base, shade, 30))
        b.append(rr(48, 46, 50, 14, 7, "#FFFFFF", None, extra=' opacity="0.45"'))
    return w, h, "".join(b)


def all_parts():
    return {
        "slider_knob": part_slider_knob(),
        "thrust_marker": part_thrust_marker(),
        "gyro_bead": part_bead(AMB, AMB_D, AMB_L),
        "gyro_bead_locked": part_bead(SEA, SEA_D, SEA_L),
        "btn_big_round_idle": part_btn_big(False),
        "btn_big_round_pressed": part_btn_big(True),
        "lamp_small_unlit": part_lamp(24, 100, GLASS, GLASS_D, False),
        "lamp_small_lit_amber": part_lamp(24, 100, AMB, AMB_D, True, AMB, AMB_L),
        "lamp_small_lit_seafoam": part_lamp(24, 100, SEA, SEA_D, True, SEA, SEA_L),
        "lamp_round_unlit": part_lamp(76, 240, GLASS, GLASS_D, False),
        "lamp_round_lit": part_lamp(76, 240, AMB, AMB_D, True, AMB, AMB_L),
        "btn_square_idle": part_btn_square(CREAM, CREAM_D),
        "btn_square_pressed": part_btn_square(CREAM_D, "#C9B086", True),
        "btn_square_correct": part_btn_square(SEA, SEA_D, False, SEA),
        "btn_square_wrong": part_btn_square(CORAL, CORAL_D, False, CORAL),
    }


# ---------- minimap ----------
MW, MH = 1600, 900
ROOMS = {  # x, y, w, h (bridge gets a rounded nose on its right side)
    "hydroponics": (330, 128, 220, 160),
    "galley": (630, 92, 420, 260),
    "bridge": (1130, 112, 330, 226),
    "reactor": (110, 356, 190, 268),
    "sick_bay": (340, 392, 210, 176),
    "radio_room": (680, 420, 300, 180),
    "cargo_hold": (1080, 408, 390, 330),
    "switchboard": (110, 694, 236, 136),
    "locker_room": (720, 694, 230, 136),
}
CORRIDORS = {
    "hydroponics-galley": [(550, 208), (630, 208)],
    "galley-bridge": [(1050, 225), (1130, 225)],
    "hydroponics-sick_bay": [(440, 288), (440, 392)],
    "sick_bay-reactor": [(300, 480), (340, 480)],
    "galley-radio_room": [(830, 352), (830, 420)],
    "radio_room-cargo_hold": [(980, 510), (1080, 510)],
    "bridge-cargo_hold": [(1275, 338), (1275, 408)],
    "reactor-switchboard": [(205, 624), (205, 694)],
    "switchboard-radio_room": [(346, 762), (610, 762), (610, 540), (680, 540)],
}
ROOM_FILL = "#262B4A"


def mm_icon(name, cx, cy, s=40):
    A = AMB
    st = f'fill="none" stroke="{A}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"'
    if name == "galley":  # big round button
        return (f'<rect x="{cx - s}" y="{cy + s * 0.3}" width="{2 * s}" height="{s * 0.5}" rx="8" fill="{A}"/>'
                f'<path d="M{cx - s * 0.68},{cy + s * 0.3} A{s * 0.68},{s * 0.68} 0 0 1 {cx + s * 0.68},{cy + s * 0.3} Z" fill="{A}"/>'
                + line(cx - s * 0.68, cy + s * 0.3, cx + s * 0.68, cy + s * 0.3, IND, 6)
                + f'<rect x="{cx - s * 0.35}" y="{cy - s * 0.25}" width="{s * 0.2}" height="{s * 0.25}" rx="4" fill="{IND}" opacity="0.4"/>')
    if name == "bridge":  # steering wheel
        g = [f'<circle cx="{cx}" cy="{cy}" r="{s * 0.66}" {st}/>', f'<circle cx="{cx}" cy="{cy}" r="9" fill="{A}"/>']
        for k in range(8):
            a = math.radians(k * 45 + 22.5)
            g.append(line(cx + 10 * math.cos(a), cy + 10 * math.sin(a), cx + s * math.cos(a), cy + s * math.sin(a), A, 7))
        return "".join(g)
    if name == "reactor":  # atom
        g = [f'<ellipse cx="{cx}" cy="{cy}" rx="{s}" ry="{s * 0.36}" transform="rotate({r} {cx} {cy})" {st.replace('stroke-width="8"', 'stroke-width="6"')}/>'
             for r in (0, 60, 120)]
        return "".join(g) + f'<circle cx="{cx}" cy="{cy}" r="9" fill="{A}"/>'
    if name == "switchboard":  # lightning bolt
        p = [(0.2, -1), (-0.6, 0.15), (-0.05, 0.15), (-0.25, 1), (0.6, -0.2), (0.05, -0.2)]
        return (f'<polygon points="{" ".join(f"{f(cx + x * s)},{f(cy + y * s)}" for x, y in p)}" fill="{A}" '
                f'stroke="{A}" stroke-width="4" stroke-linejoin="round"/>')
    if name == "radio_room":  # satellite dish
        k = s * 1.1
        d = (f'<g transform="rotate(-35 {cx} {cy})"><path d="M{cx - k},{cy - 6} Q{cx},{cy + k * 1.15} {cx + k},{cy - 6} Z" fill="{A}"/>'
             + line(cx, cy + k * 0.4, cx, cy - k * 0.55, A, 7) + f'<circle cx="{cx}" cy="{cy - k * 0.6}" r="9" fill="{A}"/></g>')
        return (d + line(cx + 10, cy + 20, cx + 10, cy + k * 0.85, A, 9)
                + line(cx - k * 0.45, cy + k * 0.88, cx + k * 0.65, cy + k * 0.88, A, 9))
    if name == "cargo_hold":  # crate
        k = s * 0.8
        return (f'<rect x="{cx - k}" y="{cy - k}" width="{2 * k}" height="{2 * k}" rx="6" {st}/>'
                + line(cx - k, cy - k, cx + k, cy + k, A, 7) + line(cx + k, cy - k, cx - k, cy + k, A, 7)
                + f'<rect x="{cx - k + 12}" y="{cy - k + 12}" width="{2 * k - 24}" height="{2 * k - 24}" fill="none" stroke="{A}" stroke-width="4"/>')
    if name == "sick_bay":  # heart
        return (f'<path d="M{cx},{cy + s * 0.85} C{cx - s * 1.25},{cy} {cx - s * 0.75},{cy - s * 1.0} {cx},{cy - s * 0.38} '
                f'C{cx + s * 0.75},{cy - s * 1.0} {cx + s * 1.25},{cy} {cx},{cy + s * 0.85} Z" fill="{A}"/>')
    if name == "hydroponics":  # leaf
        return (f'<path d="M{cx - s * 0.75},{cy + s * 0.75} C{cx - s * 0.85},{cy - s * 0.4} {cx + s * 0.1},{cy - s * 0.95} '
                f'{cx + s * 0.85},{cy - s * 0.85} C{cx + s * 0.85},{cy + s * 0.05} {cx + s * 0.15},{cy + s * 0.85} '
                f'{cx - s * 0.75},{cy + s * 0.75} Z" fill="{A}"/>' + line(cx - s * 0.75, cy + s * 0.75, cx + s * 0.35, cy - s * 0.35, IND, 6))
    if name == "locker_room":  # clock
        return (f'<circle cx="{cx}" cy="{cy}" r="{s * 0.85}" {st}/>' + line(cx, cy, cx, cy - s * 0.5, A, 7)
                + line(cx, cy, cx + s * 0.4, cy + 4, A, 7) + f'<circle cx="{cx}" cy="{cy}" r="6" fill="{A}"/>')
    return ""


def room_shape(name, x, y, w, h):
    st = f'fill="{ROOM_FILL}" stroke="{SEA}" stroke-width="8" stroke-linejoin="round"'
    if name == "bridge":
        n = 90  # rounded nose
        d = (f"M{x + 26},{y} H{x + w - n - 20} C{x + w + 10},{y} {x + w + 10},{y + h} {x + w - n - 20},{y + h} "
             f"H{x + 26} Q{x},{y + h} {x},{y + h - 26} V{y + 26} Q{x},{y} {x + 26},{y} Z")
        return f'<path d="{d}" {st}/>'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" {st}/>'


def minimap():
    s = [f'<rect width="{MW}" height="{MH}" fill="{IND}"/>']
    grid = "".join(line(x, 0, x, MH, "#24203F", 2, "butt") for x in range(50, MW, 50))
    grid += "".join(line(0, y, MW, y, "#24203F", 2, "butt") for y in range(50, MH, 50))
    s.append(f'<g id="grid">{grid}</g>')
    hull = ("M150,52 H1250 C1470,52 1560,250 1560,450 C1560,650 1470,866 1250,866 H150 "
            "Q70,866 70,786 V132 Q70,52 150,52 Z")
    s.append(f'<g id="hull"><path d="{hull}" fill="#1F1C38" stroke="{CREAM}" stroke-width="7"/>'
             + "".join(rr(40, y, 32, 70, 10, IND, CREAM, 6) for y in (190, 415, 640))
             + "".join(circ(1500 - i * 0, 450, 0, AMB, None) for i in range(0)) + "</g>")
    cor = []
    for k, pts in CORRIDORS.items():
        p = " ".join(f"{a},{b}" for a, b in pts)
        cor.append(f'<g id="corr_{k.replace("-", "__")}"><polyline points="{p}" fill="none" stroke="{SEA}" '
                   f'stroke-width="30" stroke-linejoin="round"/><polyline points="{p}" fill="none" stroke="{IND}" '
                   f'stroke-width="14" stroke-linejoin="round"/></g>')
    s.append('<g id="corridors">' + "".join(cor) + "</g>")
    rooms_json = {}
    rg = []
    for name, (x, y, w, h) in ROOMS.items():
        cx, cy = x + w / 2, y + h / 2
        if name == "bridge":
            cx = x + (w - 30) / 2
        rg.append(f'<g id="room_{name}">{room_shape(name, x, y, w, h)}{mm_icon(name, cx, cy, 50 if name == "galley" else 40)}</g>')
        rooms_json[name] = {"group_id": f"room_{name}", "cx": cx, "cy": cy, "x": x, "y": y, "w": w, "h": h,
                            "connected": name != "locker_room"}
    s.append('<g id="rooms">' + "".join(rg) + "</g>")
    # amber accents: bridge nose lights
    s.append('<g id="accents">' + "".join(circ(1540, 450 + d, 7, AMB, None) for d in (-40, 0, 40)) + "</g>")
    return "".join(s), rooms_json


# ---------- export + verification ----------
def render(svg_path, png_path, width=None):
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=width)


def draw_sockets(img, sockets, scale=1.0):
    d = ImageDraw.Draw(img)
    M = (255, 0, 255, 255)
    for so in sockets:
        k = so["shape"]
        if k == "rect":
            d.rectangle([so["x"] * scale, so["y"] * scale, (so["x"] + so["w"]) * scale, (so["y"] + so["h"]) * scale], outline=M, width=4)
        elif k in ("circle",):
            r = so["r"]
            d.ellipse([(so["cx"] - r) * scale, (so["cy"] - r) * scale, (so["cx"] + r) * scale, (so["cy"] + r) * scale], outline=M, width=4)
        elif k == "ring":
            for rr_ in (so["r"] - so["width"] / 2, so["r"] + so["width"] / 2):
                d.ellipse([(so["cx"] - rr_) * scale, (so["cy"] - rr_) * scale, (so["cx"] + rr_) * scale, (so["cy"] + rr_) * scale], outline=M, width=3)
            d.ellipse([(so["notch_x"] - 10) * scale, (so["notch_y"] - 10) * scale, (so["notch_x"] + 10) * scale, (so["notch_y"] + 10) * scale], fill=M)
        elif k == "hline":
            d.line([so["x1"] * scale, so["y"] * scale, so["x2"] * scale, so["y"] * scale], fill=(0, 255, 255, 255), width=3)
        elif k == "vline":
            d.line([so["x"] * scale, so["y1"] * scale, so["x"] * scale, so["y2"] * scale], fill=(0, 255, 255, 255), width=3)
        cx, cy = so.get("cx", so.get("x")), so.get("cy", so.get("y", so.get("y1")))
        if k in ("rect", "circle"):
            d.line([cx * scale - 12, cy * scale, cx * scale + 12, cy * scale], fill=M, width=3)
            d.line([cx * scale, cy * scale - 12, cx * scale, cy * scale + 12], fill=M, width=3)


def paste_center(img, part_png, cx, cy):
    p = Image.open(part_png).convert("RGBA")
    img.alpha_composite(p, (int(round(cx - p.width / 2)), int(round(cy - p.height / 2))))


def main():
    for d in (OUTDIR, PARTS, DEBUG):
        d.mkdir(parents=True, exist_ok=True)
    parts = all_parts()
    parts_json = {}
    for name, (w, h, body) in parts.items():
        p = PARTS / f"{name}.svg"
        extra = ' data-pivot="48,48"' if name.startswith("gyro_bead") else ""
        p.write_text(svg_doc(w, h, body, name).replace(f'<g id="{name}">', f'<g id="{name}"{extra}>'))
        render(p, PARTS / f"{name}.png")
        parts_json[name] = {"w": w, "h": h, "anchor": "center", "file": f"parts/{name}.svg"}

    panels = {}
    for name, fn in (("panel_thrusters", panel_thrusters), ("panel_gyro", panel_gyro), ("panel_memory", panel_memory)):
        body, sockets = fn()
        p = OUTDIR / f"{name}.svg"
        p.write_text(svg_doc(W, H, body, name))
        render(p, OUTDIR / f"{name}.png")
        panels[name] = {"file": f"{name}.svg", "size": [W, H], "sockets": sockets}
    meta = {
        "space": "pixels in the 2048x1536 panel image; parts are drawn at the same scale and anchored at their center",
        "angles": "degrees clockwise from straight up",
        "panels": panels, "parts": parts_json,
    }
    (OUTDIR / "panels2.json").write_text(json.dumps(meta, indent=2))

    # debug overlay straight from the JSON (not from the drawing code)
    meta = json.loads((OUTDIR / "panels2.json").read_text())
    for name, pj in meta["panels"].items():
        img = Image.open(OUTDIR / f"{name}.png").convert("RGBA")
        draw_sockets(img, pj["sockets"])
        img.save(DEBUG / f"{name}_sockets.png")
        # assembled: parts placed by JSON
        img = Image.open(OUTDIR / f"{name}.png").convert("RGBA")
        for so in pj["sockets"]:
            part = None
            if so["id"] == "power_lamp":
                part, x, y = "lamp_small_lit_amber", so["cx"], so["cy"]
            elif so["id"] == "slider_knob_path":
                part, x, y = "slider_knob", so["x"], so["y1"] + (so["y2"] - so["y1"]) * 0.3
            elif so["id"] == "thrust_marker_path":
                part, x, y = "thrust_marker", so["x"], so["y1"] + (so["y2"] - so["y1"]) * 0.3
            elif so["shape"] == "ring":
                a = math.radians(so["notch_angle_deg"] + (0 if so["id"] == "groove_0" else 70))
                part = "gyro_bead_locked" if so["id"] == "groove_0" else "gyro_bead"
                x, y = so["cx"] + so["r"] * math.sin(a), so["cy"] - so["r"] * math.cos(a)
            elif so["id"] == "button_big":
                part, x, y = "btn_big_round_idle", so["cx"], so["cy"]
            elif so["id"] in ("lamp_left", "lamp_right"):
                part, x, y = ("lamp_small_lit_amber" if so["id"] == "lamp_left" else "lamp_small_unlit"), so["cx"], so["cy"]
            elif so["id"].startswith("lamp_"):
                part, x, y = ("lamp_round_lit" if so["id"] in ("lamp_00", "lamp_12") else "lamp_round_unlit"), so["cx"], so["cy"]
            elif so["id"].startswith("button_"):
                v = {"button_00": "btn_square_pressed", "button_11": "btn_square_correct", "button_22": "btn_square_wrong"}
                part, x, y = v.get(so["id"], "btn_square_idle"), so["cx"], so["cy"]
            elif so["id"].startswith("progress_"):
                part = "lamp_small_lit_seafoam" if so["id"] in ("progress_0", "progress_1") else "lamp_small_unlit"
                x, y = so["cx"], so["cy"]
            if part:
                paste_center(img, PARTS / f"{part}.png", x, y)
        img.save(DEBUG / f"{name}_assembled.png")

    # minimap
    body, rooms = minimap()
    mp = OUTDIR / "minimap.svg"
    mp.write_text(svg_doc(MW, MH, body, "minimap"))
    render(mp, OUTDIR / "minimap.png")
    render(mp, OUTDIR / "minimap_320.png", 320)
    (OUTDIR / "minimap_rooms.json").write_text(json.dumps({
        "size": [MW, MH], "small_size": [320, 180], "small_scale": 0.2,
        "rooms": rooms,
        "corridors": {k: v for k, v in CORRIDORS.items()},
    }, indent=2))
    img = Image.open(OUTDIR / "minimap.png").convert("RGBA")
    d = ImageDraw.Draw(img)
    for r in rooms.values():
        d.rectangle([r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]], outline=(255, 0, 255, 255), width=3)
        d.ellipse([r["cx"] - 6, r["cy"] - 6, r["cx"] + 6, r["cy"] + 6], fill=(255, 0, 255, 255))
    img.save(DEBUG / "minimap_rooms_overlay.png")
    preview(parts)


def preview(parts):
    """PREVIEW.png: every piece labeled on cream (labels are for the sheet only, not in the art)."""
    from PIL import ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    sheet = Image.new("RGBA", (2020, 1860), CREAM)
    d = ImageDraw.Draw(sheet)
    tiles = [("panel_thrusters", OUTDIR / "panel_thrusters.png"), ("panel_gyro", OUTDIR / "panel_gyro.png"),
             ("panel_memory", OUTDIR / "panel_memory.png"), ("minimap (1600x900)", OUTDIR / "minimap.png")]
    for i, (lab, fp) in enumerate(tiles):
        im = Image.open(fp).convert("RGBA")
        im = im.resize((640, int(im.height * 640 / im.width)), Image.LANCZOS)
        x, y = 20 + i * 670 if i < 3 else 20, 50 if i < 3 else 600
        sheet.alpha_composite(im, (x, y))
        d.text((x, y - 32), lab, fill=OUT, font=font)
    mini = Image.open(OUTDIR / "minimap_320.png").convert("RGBA")
    sheet.alpha_composite(mini, (690, 600))
    d.text((690, 568), "minimap_320 (1:1)", fill=OUT, font=font)
    d.text((1030, 568), "moving parts (shown at 0.5x of panel scale)", fill=OUT, font=font)
    x, y, rowh = 1030, 610, 0
    for name in parts:
        im = Image.open(PARTS / f"{name}.png").convert("RGBA")
        im = im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS)
        if x + max(im.width, 150) > 2000:
            x, y, rowh = 1030, y + rowh + 40, 0
        sheet.alpha_composite(im, (x, y))
        d.text((x, y + im.height + 4), name, fill=OUT, font=sm)
        x += max(im.width, len(name) * 10) + 24
        rowh = max(rowh, im.height + 10)
    d.text((20, 1270), "socket check: magenta = panels2.json sockets drawn on top of the art", fill=OUT, font=font)
    for i, n in enumerate(("panel_thrusters", "panel_gyro", "panel_memory")):
        im = Image.open(DEBUG / f"{n}_assembled.png").convert("RGBA").resize((480, 360), Image.LANCZOS)
        sheet.alpha_composite(im, (20 + i * 500, 1310))
        im = Image.open(DEBUG / f"{n}_sockets.png").convert("RGBA").resize((240, 180), Image.LANCZOS)
        sheet.alpha_composite(im, (20 + i * 500 + 240, 1675))
        d.text((20 + i * 500, 1680), "assembled from JSON", fill=OUT, font=sm)
    sheet.save(OUTDIR / "PREVIEW.png")


if __name__ == "__main__":
    main()
