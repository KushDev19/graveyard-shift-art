"""Job C generator: task panels + moving parts + panels.json.
Socket coordinates are defined once here and written both into the SVG art and panels.json.
Usage: python art-jobs/out/C_task_panels/src/build.py   (then src/verify.py)"""
import json
import math
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent
W, H = 2048, 1536

# palette
OL = "#2A1E35"; IND = "#1B1830"; PLUM = "#3D2A4F"; PLUM_D = "#2F2140"; PLUM_L = "#56406C"
TEAL = "#2F6F73"; TEAL_D = "#245A5E"; TEAL_DD = "#1C4649"; TEAL_L = "#3F8489"
SEA = "#7FC8B8"; AMB = "#F5A54A"; AMB_D = "#D9862E"; CREAM = "#F4E6C8"; CREAM_D = "#DCC7A0"
CREAM_L = "#FFF6E2"; CORAL = "#E8574A"; CORAL_D = "#C2443A"; PINK = "#D9738C"
WOOD = "#B8743F"; WOOD_D = "#95582F"; GRAIN = "#7C4728"
BRASS = "#E2AE4E"; BRASS_D = "#B5822F"; BRASS_L = "#F7D78E"
STEEL = "#C9C6CF"; STEEL_D = "#9E99A8"; STEEL_L = "#E6E4EA"
SW = 12   # main outline
SD = 8    # detail outline

CABLE = {  # name: (base, shadow, unlit lamp)
    "red": ("#E4483C", "#B8352C", "#7A3A38"),
    "yellow": ("#E9C046", "#C19A2C", "#7D6A3A"),
    "blue": ("#3F5FD9", "#2F47A8", "#3A4170"),
    "green": ("#6FD6B0", "#4FAE8C", "#3D6A5E"),
}
AMBER_UNLIT = "#8A6232"


# ---------- primitives ----------
def rr(x, y, w, h, r, fill="none", stroke=OL, sw=SW, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{s} {extra}/>'


def circ(cx, cy, r, fill="none", stroke=OL, sw=SW, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s} {extra}/>'


def line(x1, y1, x2, y2, stroke=OL, sw=SD):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round"/>')


def path(d, fill="none", stroke=OL, sw=SW, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{s} {extra}/>'


def bevel(x, y, w, h, r, base, shadow, depth, sw=SW, light=None):
    """Raised block: shadow band along the bottom, optional highlight line on top."""
    o = [rr(x, y, w, h, r, shadow, None), rr(x, y, w, h - depth, r, base, None)]
    if light:
        o.append(line(x + r, y + sw * 1.6, x + w - r, y + sw * 1.6, light, sw * 0.8))
    o.append(rr(x, y, w, h, r, "none", OL, sw))
    return "".join(o)


def recess(x, y, w, h, r, base, shadow, depth, sw=SW, lip=None):
    """Sunken well: shadow lip along the top (light from above), optional light lip at bottom."""
    o = [rr(x, y, w, h, r, shadow, None), rr(x, y + depth, w, h - depth, r, base, None)]
    if lip:
        o.append(f'<path d="M{x + r} {y + h - sw * 1.2} H{x + w - r}" stroke="{lip}" '
                 f'stroke-width="{sw * 0.7}" stroke-linecap="round"/>')
    o.append(rr(x, y, w, h, r, "none", OL, sw))
    return "".join(o)


def screw(cx, cy, r=30, base=STEEL, shadow=STEEL_D, ang=25):
    a = math.radians(ang)
    dx, dy = math.cos(a) * r * 0.6, math.sin(a) * r * 0.6
    clip = f"sc{cx}_{cy}"
    return (f'<clipPath id="{clip}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            + circ(cx, cy, r, base, None)
            + f'<rect x="{cx - r}" y="{cy + r * 0.25}" width="{2 * r}" height="{r}" fill="{shadow}" clip-path="url(#{clip})"/>'
            + circ(cx, cy, r, "none", OL, SD)
            + line(cx - dx, cy - dy, cx + dx, cy + dy, OL, 7)
            + line(cx + dy, cy - dx, cx - dy, cy + dx, OL, 7))


def stripe(x, y, w, band=28, gap=0):
    """cream-amber-coral triple racing stripe, horizontal."""
    o = []
    for i, c in enumerate((CREAM_L, AMB, CORAL)):
        o.append(rr(x, y + i * (band + gap), w, band, band / 2, c, OL, SD))
    return "".join(o)


def lamp_socket(cx, cy, r, unlit, bezel=STEEL, bezel_d=STEEL_D):
    """Bezel ring with an unlit dome; lamp_lit part covers the dome (diameter 2r)."""
    return (circ(cx, cy, r + 16, bezel_d, OL, SD) + circ(cx, cy - 4, r + 10, bezel, None)
            + circ(cx, cy, r, unlit, OL, SD)
            + f'<ellipse cx="{cx - r * 0.3}" cy="{cy - r * 0.35}" rx="{r * 0.3}" ry="{r * 0.2}" fill="#FFFFFF" opacity="0.25"/>')


def svg(w, h, body, comment):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'<!-- {comment} -->\n{body}\n</svg>\n')


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def arc_band(cx, cy, r0, r1, a0, a1):
    """Annular sector between radii r0<r1 from angle a0 to a1 (degrees, ccw from +x, y up)."""
    x0, y0 = pol(cx, cy, r1, a0); x1, y1 = pol(cx, cy, r1, a1)
    x2, y2 = pol(cx, cy, r0, a1); x3, y3 = pol(cx, cy, r0, a0)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 0 if a1 > a0 else 1
    return (f"M{x0:.1f} {y0:.1f} A{r1} {r1} 0 {large} {sweep} {x1:.1f} {y1:.1f} "
            f"L{x2:.1f} {y2:.1f} A{r0} {r0} 0 {large} {1 - sweep} {x3:.1f} {y3:.1f} Z")


def face(fill, shadow):
    """Panel slab filling the whole image."""
    return bevel(8, 8, W - 16, H - 16, 80, fill, shadow, 26)


# ---------- panel 1: keypad ----------
def panel_keypad():
    S = {}
    b = [face(CREAM, CREAM_D)]
    for x, y in ((84, 84), (W - 84, 84), (84, H - 110), (W - 84, H - 110)):
        b.append(screw(x, y, 34))
    b.append(stripe(160, 48, W - 320, 28))
    # gauge housing + dial (horizontal semicircle, flat side down)
    gx, gy, R = 520, 500, 250
    b.append(bevel(220, 196, 600, 344, 40, CREAM_L, CREAM_D, 18))
    b.append(recess(244, 216, 552, 300, 30, PLUM, PLUM_D, 14))
    b.append(path(f"M{gx - R} {gy} A{R} {R} 0 0 1 {gx + R} {gy} Z", CREAM_L, OL, SD))
    b.append(path(arc_band(gx, gy, R - 70, R - 14, 32, 2), CORAL, OL, 6))
    b.append(path(arc_band(gx, gy, R - 70, R - 14, 60, 32), AMB, OL, 6))
    for i in range(13):
        a = 178 - i * 176 / 12
        major = i % 3 == 0
        x0, y0 = pol(gx, gy, R - (88 if major else 80), a); x1, y1 = pol(gx, gy, R - (118 if major else 100), a)
        b.append(line(x0, y0, x1, y1, OL, 9 if major else 6))
    # speaker grille between gauge and display
    b.append(bevel(872, 220, 236, 300, 34, CREAM_L, CREAM_D, 16))
    for i in range(6):
        b.append(recess(912, 252 + i * 40, 156, 22, 11, PLUM, PLUM_D, 6, sw=6))
    piv = (gx, gy - 28)
    S["gauge_needle"] = dict(kind="needle", x=piv[0], y=piv[1], w=56, h=190, pivot=list(piv),
                             part="vu_needle", scale=round(190 / 266, 3),
                             note="rotate around pivot; -88 deg (left) .. +88 deg (right), coral zone = +58..+88")
    # LED display window, empty and unlit
    dx, dy, dw, dh = 1150, 216, 700, 300
    b.append(bevel(dx - 30, dy - 20, dw + 60, dh + 50, 40, CREAM_L, CREAM_D, 18))
    b.append(recess(dx, dy, dw, dh, 26, "#4A3424", "#33241A", 22))
    b.append(f'<path d="M{dx + 60} {dy + dh - 30} L{dx + 200} {dy + 40} H{dx + 260} L{dx + 120} {dy + dh - 30} Z" fill="#FFFFFF" opacity="0.07"/>')
    S["display"] = dict(kind="text", x=dx + dw / 2, y=dy + dh / 2 + 11, w=dw - 40, h=dh - 62,
                        note="live VT323 amber text (#F5A54A), glow optional")
    # key well, lower 65 %
    wx, wy, ww, wh = 140, 566, W - 280, 780
    b.append(recess(wx, wy, ww, wh, 50, PLUM, PLUM_D, 28, lip=PLUM_L))
    ks, gapx, gapy = 260, 70, 90
    x0 = wx + (ww - (5 * ks + 4 * gapx)) / 2 + ks / 2
    y0 = wy + 14 + (wh - (2 * ks + gapy)) / 2 + ks / 2
    n = 0
    for r in range(2):
        for c in range(5):
            cx, cy = x0 + c * (ks + gapx), y0 + r * (ks + gapy)
            b.append(recess(cx - ks / 2, cy - ks / 2, ks, ks, 44, "#33243F", "#251A2F", 22, sw=SD, lip=PLUM_L))
            S[f"key_{n}"] = dict(kind="key", x=cx, y=cy, w=ks, h=ks, part="key_idle", scale=1.0,
                                 note=f"row {r} col {c}; states key_idle/pressed/correct/wrong")
            n += 1
    # coral warning stripes along the bottom + amber lamp
    hx, hy, hw, hh = 160, 1376, 1600, 92
    b.append(f'<clipPath id="haz"><rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="24"/></clipPath>')
    hz = [f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" fill="{CREAM_L}"/>']
    for i in range(-2, 32):
        sx = hx + i * 60
        hz.append(f'<path d="M{sx} {hy + hh} L{sx + 30} {hy + hh} L{sx + 30 + hh} {hy} L{sx + hh} {hy} Z" fill="{CORAL}"/>')
    b.append(f'<g clip-path="url(#haz)">{"".join(hz)}</g>')
    b.append(rr(hx, hy, hw, hh, 24, "none", OL, SD))
    lx, ly = 1850, 1422
    b.append(lamp_socket(lx, ly, 28, AMBER_UNLIT))
    S["lamp"] = dict(kind="lamp", x=lx, y=ly, w=56, h=56, part="lamp_lit_amber", scale=round(56 / 68, 3))
    return svg(W, H, "".join(b), "GRAVEYARD SHIFT task panel: Reactor Override keypad. Empty sockets; see panels.json"), S


# ---------- panel 2: switchboard ----------
def panel_switchboard():
    S = {}
    b = [face(WOOD, WOOD_D)]
    # wood grain on the frame
    for y, amp in ((40, 10), (124, 14), (1440, 12), (1480, 8)):
        b.append(path(f"M120 {y} C 500 {y - amp}, 800 {y + amp}, 1100 {y} S 1700 {y - amp}, 1930 {y}", "none", GRAIN, 6))
    for x in (46, 118, W - 46, W - 118):
        b.append(path(f"M{x} 220 C {x + 8} 600, {x - 10} 900, {x} 1320", "none", GRAIN, 6))
    b.append(path("M300 1460 q 40 -22 80 0 q -40 22 -80 0 Z", "none", GRAIN, 5))
    b.append(path("M1620 34 q 50 -18 100 0 q -50 18 -100 0 Z", "none", GRAIN, 5))
    # brass corner caps
    for (x, y, rot) in ((8, 8, 0), (W - 8, 8, 90), (W - 8, H - 8, 180), (8, H - 8, 270)):
        cap = (f'<g transform="translate({x} {y}) rotate({rot})">'
               + path("M0 80 A80 80 0 0 1 80 0 H210 V100 H100 V210 H0 Z", BRASS_D, None)
               + path("M0 80 A80 80 0 0 1 80 0 H210 V84 H84 V210 H0 Z", BRASS, None)
               + path("M0 80 A80 80 0 0 1 80 0 H210 V100 H100 V210 H0 Z", "none", OL, SW)
               + '</g>')
        b.append(cap)
    for x, y in ((54, 50), (W - 54, 50), (W - 54, H - 54), (54, H - 54)):
        b.append(screw(x, y, 22, BRASS_L, BRASS_D))
    b.append(stripe(230, 40, W - 460, 28))
    # inner teal-steel face
    ix, iy, iw, ih = 150, 160, W - 300, 1230
    b.append(recess(ix, iy, iw, ih, 36, "#4E7F84", "#3B676C", 22))
    # felt cable area
    fx, fy, fw, fh = 584, 210, 916, 1130
    b.append(recess(fx, fy, fw, fh, 40, PLUM, PLUM_D, 30, lip=PLUM_L))
    b.append(rr(fx + 26, fy + 46, fw - 52, fh - 72, 24, "none", PLUM_L, 6, 'stroke-dasharray="22 16"'))
    S["felt"] = dict(kind="area", x=fx + fw / 2, y=fy + 15 + fh / 2, w=fw - 24, h=fh - 50,
                     note="cables are drawn here by code")
    left = ["red", "yellow", "blue", "green"]
    right = ["green", "red", "blue", "yellow"]
    ys = [350, 630, 910, 1190]
    for side, (jx, lx, p0, p1, order) in (("out", (330, 470, 214, 548, left)), ("in", (1640, 1790, 1536, 1862, right))):
        # jack strip plate
        b.append(bevel(p0, 196, p1 - p0, 1158, 30, "#5E9196", "#4A7A7F", 14))
        for i, (y, col) in enumerate(zip(ys, order)):
            b.append(circ(jx, y + 6, 80, BRASS_D, OL, SW))
            b.append(circ(jx, y, 72, BRASS, None))
            b.append(circ(jx, y, 50, BRASS_D, OL, SD))
            b.append(circ(jx, y, 32, IND, OL, SD))
            b.append(f'<ellipse cx="{jx - 34}" cy="{y - 42}" rx="18" ry="9" fill="{BRASS_L}" transform="rotate(-35 {jx - 34} {y - 42})"/>')
            S[f"jack_{side}_{i}"] = dict(kind="jack", x=jx, y=y, w=64, h=64, color=col, ring_r=80,
                                         part=("plug_" + col) if side == "out" else "jack_ring",
                                         note=("plug start; put plug anchor here" if side == "out" else "target jack"))
            b.append(lamp_socket(lx, y, 30, CABLE[col][2]))
            S[f"lamp_{side}_{i}"] = dict(kind="lamp", x=lx, y=y, w=60, h=60, color=col,
                                         part=f"lamp_lit_{col}", scale=round(60 / 68, 3))
        for sy in (226, 1324):
            b.append(screw((p0 + p1) / 2, sy, 16, BRASS_L, BRASS_D))
    # amber power lamp on the bottom rail
    b.append(lamp_socket(W / 2, 1460, 24, AMBER_UNLIT, BRASS, BRASS_D))
    S["lamp_power"] = dict(kind="lamp", x=W / 2, y=1460, w=48, h=48, part="lamp_lit_amber", scale=round(48 / 68, 3))
    return svg(W, H, "".join(b), "GRAVEYARD SHIFT task panel: Patch the Switchboard. Empty jacks; see panels.json"), S


# ---------- panel 3: tape deck ----------
def panel_tape():
    S = {}
    b = [face(CREAM, CREAM_D)]
    for x, y in ((80, 80), (W - 80, 80), (80, H - 104), (W - 80, H - 104)):
        b.append(screw(x, y, 32))
    b.append(stripe(160, 34, W - 320, 28))
    # brushed teal faceplate
    px, py, pw, ph = 140, 150, W - 280, 1220
    b.append(recess(px, py, pw, ph, 44, TEAL, TEAL_D, 22))
    b.append(f'<clipPath id="plate"><rect x="{px + 8}" y="{py + 30}" width="{pw - 16}" height="{ph - 40}" rx="40"/></clipPath>')
    br = []
    for i, y in enumerate(range(py + 60, py + ph - 20, 46)):
        off = (i * 397) % 900
        br.append(line(px + 60 + off * 0.3, y, px + 60 + off * 0.3 + 380 + (i * 131) % 300, y, TEAL_L, 4))
        br.append(line(px + 900 + off * 0.5, y + 18, px + 900 + off * 0.5 + 260 + (i * 71) % 200, y + 18, TEAL_L, 4))
    b.append(f'<g clip-path="url(#plate)" opacity="0.55">{"".join(br)}</g>')
    # reel recesses + spindles
    for name, cx in (("reel_left", 560), ("reel_right", W - 560)):
        cy = 520
        b.append(circ(cx, cy, 316, CREAM_D, OL, SW))
        b.append(circ(cx, cy - 6, 304, CREAM, None))
        b.append(circ(cx, cy, 290, TEAL_DD, OL, SD))
        b.append(path(arc_band(cx, cy, 262, 290, 20, 160), "#163A3C", None))
        b.append(circ(cx, cy, 290, "none", OL, SD))
        b.append(circ(cx, cy, 56, STEEL_D, OL, SD))
        b.append(circ(cx, cy - 4, 46, STEEL, None))
        b.append(circ(cx, cy, 22, IND, OL, 6))
        for a in (90, 210, 330):
            x0, y0 = pol(cx, cy, 20, a); x1, y1 = pol(cx, cy, 44, a)
            b.append(line(x0, y0, x1, y1, OL, 10))
        S[name] = dict(kind="reel", x=cx, y=cy, w=560, h=560, part="reel_full" if name == "reel_left" else "reel_empty",
                       scale=1.0, note="rotate around center; swap reel_full/reel_empty as tape transfers")
    # tape-head assembly + guide rollers
    b.append(bevel(904, 560, 240, 190, 30, PLUM, PLUM_D, 16))
    b.append(bevel(964, 600, 120, 70, 22, STEEL, STEEL_D, 14, sw=SD))
    b.append(rr(1004, 612, 40, 30, 8, IND, OL, 6))
    for rx in (944, 1104):
        b.append(circ(rx, 712, 22, STEEL_D, OL, SD))
        b.append(circ(rx, 708, 14, STEEL, None))
    for rx in (850, W - 850):
        b.append(circ(rx, 640, 34, STEEL_D, OL, SD))
        b.append(circ(rx, 634, 24, STEEL, None))
        b.append(circ(rx, 640, 10, OL, None))
    # power lamp between reels
    b.append(lamp_socket(W / 2, 320, 26, AMBER_UNLIT))
    S["lamp_power"] = dict(kind="lamp", x=W / 2, y=320, w=52, h=52, part="lamp_lit_amber", scale=round(52 / 68, 3))
    # VU meter
    vx, vy, vw, vh = 200, 890, 560, 410
    b.append(bevel(vx - 26, vy - 26, vw + 52, vh + 60, 60, CREAM_L, CREAM_D, 20))
    b.append(recess(vx, vy, vw, vh, 48, CREAM_L, CREAM_D, 18))
    cx, cy, R = vx + vw / 2, vy + vh - 50, 300
    b.append(path(arc_band(cx, cy, R - 34, R - 14, 140, 74), AMB, OL, 5))
    b.append(path(arc_band(cx, cy, R - 34, R - 14, 74, 40), CORAL, OL, 5))
    for i in range(11):
        a = 140 - i * 10
        major = i % 2 == 0
        x0, y0 = pol(cx, cy, R - 44, a); x1, y1 = pol(cx, cy, R - (90 if major else 70), a)
        b.append(line(x0, y0, x1, y1, CORAL_D if a < 74 else OL, 8 if major else 5))
    b.append(path(f"M{vx + 8} {vy + vh - 70} H{vx + vw - 8} V{vy + vh - 40} Q{vx + vw - 8} {vy + vh} {vx + vw - 48} {vy + vh} H{vx + 48} Q{vx + 8} {vy + vh} {vx + 8} {vy + vh - 40} Z", PLUM, OL, SD))
    S["vu_needle"] = dict(kind="needle", x=cx, y=cy, w=56, h=250, pivot=[cx, cy], part="vu_needle",
                          scale=round(250 / 266, 3), note="rotate -50 deg (left) .. +50 deg (right); coral = +16..+50")
    # progress window
    qx, qy, qw, qh = 830, 990, 600, 130
    b.append(bevel(qx - 22, qy - 22, qw + 44, qh + 54, 36, CREAM_L, CREAM_D, 16))
    b.append(recess(qx, qy, qw, qh, 24, PLUM_D, IND, 18))
    S["progress"] = dict(kind="bar", x=qx + qw / 2, y=qy + 9 + qh / 2, w=qw - 44, h=qh - 58,
                         note="fill left to right with amber rect (rx 14); slider_knob may ride on it")
    # toggles
    for tx in (900, 1130, 1360):
        b.append(bevel(tx - 48, 1210, 96, 120, 22, CREAM_L, CREAM_D, 12, sw=SD))
        b.append(circ(tx, 1272, 22, STEEL_D, OL, SD))
        b.append(path(f"M{tx - 14} 1272 L{tx - 20} 1196 Q{tx} 1180 {tx + 20} 1196 L{tx + 14} 1272 Z", STEEL, OL, SD))
        b.append(path(f"M{tx + 2} 1270 L{tx + 6} 1200", "none", STEEL_L, 6))
    # big button socket
    bx, by = W - 400, 1080
    b.append(circ(bx, by, 196, CREAM_D, OL, SW))
    b.append(circ(bx, by - 8, 182, CREAM_L, None))
    b.append(circ(bx, by, 168, PLUM_D, OL, SD))
    b.append(circ(bx, by + 14, 154, PLUM, None))
    b.append(circ(bx, by, 168, "none", OL, SD))
    S["big_button"] = dict(kind="button", x=bx, y=by, w=320, h=320, part="btn_big_amber", scale=1.0,
                           note="pressed state: btn_big_amber_pressed at the same spot")
    return svg(W, H, "".join(b), "GRAVEYARD SHIFT task panel: Tape Transfer reel deck. Empty sockets; see panels.json"), S


# ---------- parts ----------
def key(state):
    base, shade, glow = {"idle": (CREAM, CREAM_D, None), "pressed": (CREAM_D, "#C4AE86", None),
                         "correct": (SEA, "#5FA898", "#D8FFF3"), "wrong": (CORAL, CORAL_D, "#FFD0C8")}[state]
    s, top = 240, (16 if state == "pressed" else 0)
    depth = 12 if state == "pressed" else 30
    o = []
    if glow:
        o.append(f'<defs><radialGradient id="g"><stop offset="0" stop-color="{glow}" stop-opacity="0.9"/>'
                 f'<stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>'
                 f'<clipPath id="k"><rect x="10" y="10" width="{s - 20}" height="{s - 20 - depth}" rx="40"/></clipPath></defs>')
    o.append(f'<g transform="translate(0 {top})">')
    o.append(rr(6, 6, s - 12, s - 12 - top, 44, shade, None))
    o.append(rr(6, 6, s - 12, s - 12 - top - depth, 44, base, None))
    if glow:
        o.append(f'<g clip-path="url(#k)"><ellipse cx="{s / 2}" cy="{(s - depth) / 2}" rx="{s * 0.48}" ry="{s * 0.42}" fill="url(#g)"/></g>')
    if state != "pressed":
        o.append(path(f"M50 34 H{s - 70}", "none", "#FFFFFF", 10, 'opacity="0.55"'))
    o.append(rr(6, 6, s - 12, s - 12 - top, 44, "none", OL, SW))
    o.append("</g>")
    return svg(s, s, "".join(o), f"key_{state}: fits a 260 px key socket, centered")


def plug(col):
    base, sh, _ = CABLE[col]
    o = []
    # coiled cable stub (left), loops back to front
    for i in range(6):
        x = 10 + i * 24
        o.append(f'<ellipse cx="{x + 20}" cy="64" rx="22" ry="36" fill="{sh}" stroke="{OL}" stroke-width="{SD}"/>')
        o.append(f'<ellipse cx="{x + 16}" cy="58" rx="12" ry="26" fill="{base}"/>')
    # grip body
    o.append(bevel(150, 16, 130, 96, 30, base, sh, 22))
    for gx in (186, 214, 242):
        o.append(line(gx, 32, gx, 80, sh, 8))
    # brass collar + tip
    o.append(bevel(274, 26, 34, 76, 10, BRASS, BRASS_D, 14, sw=SD))
    o.append(path("M306 46 H350 Q366 46 366 62 Q366 78 350 78 H306 Z", BRASS, OL, SD))
    o.append(line(332, 48, 332, 76, BRASS_D, 6))
    o.append(path("M312 54 H346", "none", BRASS_L, 6))
    body = f'<g data-anchor-tip="340,62" data-anchor-cable="10,64">{"".join(o)}</g>'
    return svg(380, 124, body, f"plug_{col}: points right. Anchor tip 340,62 goes on a jack center; cable attaches at 10,64")


def cable_seg(col):
    base, sh, _ = CABLE[col]
    o = [f'<rect x="0" y="4" width="64" height="40" fill="{base}"/>',
         f'<rect x="0" y="30" width="64" height="14" fill="{sh}"/>',
         line(0, 4, 64, 4, OL, SD), line(0, 44, 64, 44, OL, SD)]
    return svg(64, 48, "".join(o), f"cable_seg_{col}: tile horizontally, stretch along the plug to jack vector")


def reel(full):
    c = 280
    o = []
    if full:
        o.append(circ(c, c, 236, "#3A2C33", OL, SD))
        for r in (200, 160, 120):
            o.append(circ(c, c, r, "none", "#4A3A42", 4))
    else:
        o.append(circ(c, c, 104, "#3A2C33", OL, SD))
    # cream flange with three cut-out windows (evenodd), rotation-invariant shading ring
    holes = []
    for a in (90, 210, 330):
        x0, y0 = pol(c, c, 96, a - 28); x1, y1 = pol(c, c, 96, a + 28)
        x2, y2 = pol(c, c, 220, a + 22); x3, y3 = pol(c, c, 220, a - 22)
        holes.append(f"M{x0:.1f} {y0:.1f} A96 96 0 0 0 {x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} A220 220 0 0 1 {x3:.1f} {y3:.1f} Z")
    disc = f"M{c - 270} {c} A270 270 0 1 0 {c + 270} {c} A270 270 0 1 0 {c - 270} {c} Z"
    o.append(path(disc + " " + " ".join(holes), CREAM, OL, SW, 'fill-rule="evenodd"'))
    o.append(circ(c, c, 252, "none", CREAM_D, 16))
    o.append(circ(c, c, 270, "none", OL, SW))
    o.append(circ(c, c, 72, CREAM_L, OL, SD))
    o.append(circ(c, c, 34, IND, OL, 6))
    for a in (90, 210, 330):
        x, y = pol(c, c, 34, a)
        o.append(circ(x, y, 9, CREAM_L, None))
    return svg(560, 560, "".join(o), ("reel_full" if full else "reel_empty") + ": rotate around 280,280")


def needle():
    o = [path("M30 14 L37 270 L23 270 Z", PLUM, OL, 6),
         circ(30, 280, 26, PLUM_D, OL, SD), circ(30, 276, 16, PLUM_L, None), circ(30, 280, 7, OL, None)]
    return svg(60, 320, f'<g id="needle" data-pivot="30,280">{"".join(o)}</g>',
               "vu_needle: points straight up, pivot 30,280 (length 266 from pivot to tip)")


def big_button(pressed):
    c, o = 160, []
    o.append(circ(c, c + 4, 150, "#B86F2A", OL, SW))
    off = 16 if pressed else 0
    o.append(circ(c, c - 4 + off, 132, AMB_D, None))
    o.append(circ(c, c - 16 + off, 118, AMB, None))
    o.append(circ(c, c - 16 + off, 118, "none", OL, SD))
    if not pressed:
        o.append(f'<ellipse cx="{c - 44}" cy="{c - 70}" rx="38" ry="20" fill="#FFE2B0" transform="rotate(-30 {c - 44} {c - 70})"/>')
    else:
        o.append(f'<ellipse cx="{c - 40}" cy="{c - 52}" rx="30" ry="15" fill="#FFE2B0" opacity="0.7" transform="rotate(-30 {c - 40} {c - 52})"/>')
    o.append(circ(c, c + 4, 150, "none", OL, SW))
    return svg(320, 320, "".join(o), "btn_big_amber" + ("_pressed" if pressed else "") + ": centered in the 320 px socket")


def slider_knob():
    o = [bevel(10, 8, 64, 116, 22, CREAM, CREAM_D, 22),
         line(30, 40, 54, 40, CREAM_D, 8), line(30, 60, 54, 60, CREAM_D, 8), line(30, 80, 54, 80, CREAM_D, 8)]
    return svg(84, 132, "".join(o), "slider_knob: center 42,66; rides on the progress bar")


def lamp(col, lit):
    if col == "amber":
        base, sh, unl = AMB, AMB_D, AMBER_UNLIT
    else:
        base, sh, unl = CABLE[col]
    c, r, o = 60, 34, []
    if lit:
        o.append(f'<defs><radialGradient id="h"><stop offset="0.35" stop-color="{base}" stop-opacity="0.75"/>'
                 f'<stop offset="1" stop-color="{base}" stop-opacity="0"/></radialGradient></defs>')
        o.append(circ(c, c, 60, "url(#h)", None))
        o.append(circ(c, c, r, base, OL, SD))
        o.append(circ(c, c - 6, r - 12, "#FFFFFF", None, extra='opacity="0.45"'))
        o.append(f'<ellipse cx="{c - 11}" cy="{c - 13}" rx="10" ry="6" fill="#FFFFFF"/>')
    else:
        o.append(circ(c, c, r, unl, OL, SD))
        o.append(f'<ellipse cx="{c - 10}" cy="{c - 12}" rx="10" ry="6" fill="#FFFFFF" opacity="0.25"/>')
    return svg(120, 120, "".join(o), f"lamp: dome diameter 68 centered at 60,60 (glow reaches the edges)")


def jack_ring():
    c, o = 90, []
    d = f"M{c - 80} {c} A80 80 0 1 0 {c + 80} {c} A80 80 0 1 0 {c - 80} {c} Z M{c - 40} {c} A40 40 0 1 1 {c + 40} {c} A40 40 0 1 1 {c - 40} {c} Z"
    o.append(path(d, BRASS_D, None, 0, 'fill-rule="evenodd" transform="translate(0 6)"'))
    o.append(path(d, BRASS, OL, SW, 'fill-rule="evenodd"'))
    o.append(f'<ellipse cx="{c - 36}" cy="{c - 46}" rx="18" ry="9" fill="{BRASS_L}" transform="rotate(-35 {c - 36} {c - 46})"/>')
    return svg(180, 180, "".join(o), "jack_ring: front collar, center 90,90; draw over a plug tip to fake insertion")


def main():
    panels = {}
    for name, fn, title in (("panel_keypad", panel_keypad, "Reactor Override"),
                            ("panel_switchboard", panel_switchboard, "Patch the Switchboard"),
                            ("panel_tape", panel_tape, "Tape Transfer")):
        s, sockets = fn()
        (OUT / f"{name}.svg").write_text(s, encoding="utf-8")
        for v in sockets.values():
            for k in ("x", "y", "w", "h"):
                v[k] = round(v[k], 1)
        panels[name] = dict(title=title, svg=f"{name}.svg", png=f"{name}.png", size=[W, H], sockets=sockets)
    parts_dir = OUT / "task_parts"; parts_dir.mkdir(exist_ok=True)
    parts = {}
    def put(n, s, info):
        (parts_dir / f"{n}.svg").write_text(s, encoding="utf-8"); parts[n] = info
    for st in ("idle", "pressed", "correct", "wrong"):
        put(f"key_{st}", key(st), dict(size=[240, 240], anchor=[120, 120]))
    for col in CABLE:
        put(f"plug_{col}", plug(col), dict(size=[380, 124], anchor=[340, 62], cable_attach=[10, 64]))
        put(f"cable_seg_{col}", cable_seg(col), dict(size=[64, 48], anchor=[0, 24], tile="x"))
    for col in list(CABLE) + ["amber"]:
        put(f"lamp_lit_{col}", lamp(col, True), dict(size=[120, 120], anchor=[60, 60], dome=68))
    put("lamp_unlit", lamp("amber", False), dict(size=[120, 120], anchor=[60, 60], dome=68))
    put("reel_full", reel(True), dict(size=[560, 560], anchor=[280, 280], pivot=[280, 280]))
    put("reel_empty", reel(False), dict(size=[560, 560], anchor=[280, 280], pivot=[280, 280]))
    put("vu_needle", needle(), dict(size=[60, 320], anchor=[30, 280], pivot=[30, 280], length=266))
    put("btn_big_amber", big_button(False), dict(size=[320, 320], anchor=[160, 160]))
    put("btn_big_amber_pressed", big_button(True), dict(size=[320, 320], anchor=[160, 160]))
    put("slider_knob", slider_knob(), dict(size=[84, 132], anchor=[42, 66]))
    put("jack_ring", jack_ring(), dict(size=[180, 180], anchor=[90, 90]))
    doc = dict(
        about="GRAVEYARD SHIFT Job C task panels. All coordinates are pixels in the 2048x1536 panel space. "
              "Socket x,y = CENTER of the socket; w,h = its size. Place a part by putting its anchor on the socket "
              "center and scaling by socket.scale (parts are drawn at panel scale, so scale is 1.0 unless given). "
              "If the panel is displayed at another size, multiply everything by displayWidth/2048.",
        panels=panels, parts=parts)
    (OUT / "panels.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print("ok", {k: len(v["sockets"]) for k, v in panels.items()}, len(parts), "parts")


if __name__ == "__main__":
    main()
