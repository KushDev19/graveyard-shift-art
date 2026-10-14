"""Generate the tileable corridor art (hall_h, hall_v, hall_corner_ru, hall_corner_rd) as SVG,
render PNGs at half scale and build a seam/style preview.

All coordinates are in Galley-native pixels (the Galley room art is 5504x3072).
Layout reference: approved corridor concept (images/20.jpg) re-measured at Galley scale.

hall_h   2000 x 2664, tiles left/right, period 2000 (lamp at x=0, porthole at x=1000).
hall_v   2364 x 1000, tiles up/down, period 1000 (lamps on both wall tops at y=500).
corners  3132 x 3664. Both junction edges are mirror symmetric, so the left-hand corners
         can be made by flipping these horizontally.
"""
import math
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import svgtools  # noqa: E402

ROOT = svgtools.ROOT
OUT = ROOT / "frontend/public/assets/ship/hall"
WORK = ROOT / "art/work"

C = dict(
    out="#1B1830", ol="#421840", plum="#613E5E",
    wall="#5F838C", shade="#4B6079", seamD="#445A6C", seamL="#6E9FA4", rivet="#4C6079",
    pipeT="#5C6D85", pipeB="#778E97",
    cream="#EBD1AF", amber="#E89954", coral="#E36E61",
    bbHL="#8A9AA1", bb="#767F90",
    floor="#425468", fseamD="#3C4C5F", fseamL="#465A6C", dash="#EECCA8",
    topHL="#8BA1AA", top="#5D808B", topD="#525C70",
    rim="#AE998F", rimD="#8A7A80", glass="#FDBF6A", glassHot="#FFF0A0", cage="#C8645A",
    ring="#8F999F", ringD="#6F7884", ringL="#AEB6BA",
)
OLW = 14

# ---------------------------------------------------------------- hall_h rows
HP = 2000            # horizontal period
HH = 2664            # strip height
FT = 98              # face top (below frame)
FACE_BOT = 1458      # baseboard top
FLOOR_T, FLOOR_B = 1564, 2464
CL_Y = (FLOOR_T + FLOOR_B) // 2   # 2014
LAMP_Y, PORT_Y = 688, 784
BASE_BANDS = [(84, 98, "ol"), (98, FACE_BOT, "wall"), (98, 184, "shade"), (274, 306, "shade"),
              (404, 436, "shade")]
OVER_BANDS = [(184, 198, "ol"), (198, 229, "pipeT"), (229, 260, "pipeB"), (260, 274, "ol"),
              (334, 348, "ol"), (348, 369, "pipeT"), (369, 390, "pipeB"), (390, 404, "ol"),
              (1126, 1136, "seamD"), (1136, 1142, "seamL"),
              (673, 747, "cream"), (747, 821, "amber"), (821, 895, "coral"),
              (FACE_BOT, 1472, "ol"), (1472, 1490, "bbHL"), (1490, 1550, "bb"), (1550, FLOOR_T, "ol")]
LEDGE_BANDS = [(FLOOR_B, 2478, "ol"), (2478, 2496, "topHL"), (2496, 2556, "top"), (2556, 2566, "topD"),
               (2566, HH, "ol"), (2580, 2650, "plum")]

# ---------------------------------------------------------------- hall_v columns (left band)
VP = 1000
WV = 2364
S = 732              # floor left edge
X0 = S + 900         # floor right edge (1632)
CL_X = (S + X0) // 2  # 1182
V_STRIPE = [(150, 224, "cream"), (224, 298, "amber"), (298, 372, "coral")]
V_LAMP_X = 540
V_LAMP_Y = 500


def mx(x):
    return WV - x


# ---------------------------------------------------------------- primitives
def rect(x0, y0, x1, y1, col, extra=""):
    if x1 <= x0 or y1 <= y0:
        return ""
    return f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" fill="{C.get(col, col)}"{extra}/>'


def circ(cx, cy, r, col, extra=""):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{C.get(col, col)}"{extra}/>'


def defs():
    return f"""<defs>
<radialGradient id="gHalo"><stop offset="0" stop-color="#FFC070" stop-opacity="0.62"/>
<stop offset="0.45" stop-color="#FFB45E" stop-opacity="0.26"/><stop offset="1" stop-color="#FFB45E" stop-opacity="0"/></radialGradient>
<radialGradient id="gPool"><stop offset="0" stop-color="#F4A45E" stop-opacity="0.42"/>
<stop offset="0.55" stop-color="#F4A45E" stop-opacity="0.22"/><stop offset="1" stop-color="#F4A45E" stop-opacity="0"/></radialGradient>
<radialGradient id="gDot"><stop offset="0" stop-color="#FFC768" stop-opacity="0.75"/>
<stop offset="1" stop-color="#FFB45E" stop-opacity="0"/></radialGradient>
<linearGradient id="gCone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFC77E" stop-opacity="0.62"/>
<stop offset="0.6" stop-color="#FFBE74" stop-opacity="0.30"/><stop offset="1" stop-color="#FFB468" stop-opacity="0.10"/></linearGradient>
<filter id="soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="26"/></filter>
<filter id="softS" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="16"/></filter>
</defs>"""


def svg_doc(w, h, body, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f"{defs()}{extra_defs}{body}</svg>")


# ---------------------------------------------------------------- decorations
def lamp(cx, cy, halo=True):
    s = []
    if halo:
        s.append(f'<circle cx="{cx}" cy="{cy}" r="290" fill="url(#gHalo)"/>')
    s.append(circ(cx, cy, 122, "ol"))
    s.append(circ(cx, cy, 108, "rim"))
    # darker lower rim (symmetric)
    s.append(f'<path d="M{cx - 108},{cy} A108 108 0 0 0 {cx + 108},{cy} A108 86 0 0 1 {cx - 108},{cy}Z" fill="{C["rimD"]}"/>')
    s.append(circ(cx, cy, 96, "ol"))
    s.append(circ(cx, cy, 86, "glass"))
    s.append(f'<ellipse cx="{cx}" cy="{cy + 34}" rx="58" ry="38" fill="{C["glassHot"]}"/>')
    cid = f"lg{int(cx)}_{int(cy)}"
    s.append(f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="86"/></clipPath>')
    s.append(f'<g clip-path="url(#{cid})" stroke="{C["cage"]}" stroke-width="9" fill="none">'
             f'<line x1="{cx}" y1="{cy - 90}" x2="{cx}" y2="{cy + 90}"/>'
             f'<ellipse cx="{cx}" cy="{cy}" rx="50" ry="88"/>'
             f'<line x1="{cx - 90}" y1="{cy + 46}" x2="{cx + 90}" y2="{cy + 46}"/>'
             f'<line x1="{cx - 90}" y1="{cy - 34}" x2="{cx + 90}" y2="{cy - 34}"/></g>')
    # small symmetric glints on the rim top
    s.append(f'<path d="M{cx - 52},{cy - 94} A100 100 0 0 1 {cx + 52},{cy - 94}" stroke="#D9C6B8" stroke-width="8" fill="none" stroke-linecap="round"/>')
    return "".join(s)


STARS = [(-90, -100, 6), (-30, -120, 4), (40, -95, 7), (100, -60, 4), (-120, -40, 4), (-60, -20, 5),
         (20, -45, 4), (80, 10, 6), (-100, 40, 4), (-20, 60, 6), (60, 70, 4), (110, 95, 4),
         (-70, 110, 5), (10, 125, 7), (-140, -70, 3), (130, -20, 3), (0, -10, 3)]


def porthole(cx, cy, uid):
    s = [f'<circle cx="{cx}" cy="{cy + 24}" r="252" fill="#3E5568" opacity="0.45"/>',
         circ(cx, cy, 250, "ol"), circ(cx, cy, 236, "ringD"), circ(cx, cy - 12, 226, "ring"),
         circ(cx, cy, 180, "ol")]
    cid = f"pg{uid}"
    s.append(f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="166"/></clipPath>')
    g = [rect(cx - 200, cy - 200, cx + 200, cy + 200, "#5A4785")]
    waves = [(-80, "#7A4E9C", 34), (-25, "#A458B4", -30), (25, "#D25FB0", 36), (78, "#EF7495", -28),
             (122, "#F99A85", 26)]
    for off, col, amp in waves:
        y = cy + off
        g.append(f'<path d="M{cx - 200},{y} C{cx - 110},{y - amp} {cx - 30},{y + amp} {cx + 40},{y} '
                 f'S{cx + 150},{y - amp} {cx + 200},{y + 6} L{cx + 200},{cy + 200} L{cx - 200},{cy + 200}Z" fill="{col}"/>')
    for dx, dy, r in STARS:
        g.append(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{r}" fill="#FFF4FA" opacity="0.92"/>')
    # inner lip, lower part of the glass
    g.append(f'<path d="M{cx - 160},{cy + 40} A164 164 0 0 0 {cx + 160},{cy + 40}" stroke="{C["ringL"]}" '
             f'stroke-width="18" fill="none"/>')
    s.append(f'<g clip-path="url(#{cid})">{"".join(g)}</g>')
    s.append(f'<path d="M{cx - 160},{cy + 40} A164 164 0 0 0 {cx + 160},{cy + 40}" stroke="{C["ol"]}" stroke-width="6" fill="none" transform="translate(0,-14)" opacity="0.0"/>')
    for i in range(8):
        a = math.pi / 2 + i * math.pi / 4
        rx, ry = cx + 208 * math.cos(a), cy + 208 * math.sin(a)
        s.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="14" fill="{C["ringL"]}" stroke="{C["ol"]}" stroke-width="7"/>')
    return "".join(s)


def rivet(x, y):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="none" stroke="{C["rivet"]}" stroke-width="8"/>'


def vseam(x, y0, y1):
    """Symmetric groove: dark centre with light lips on both sides (mirror safe)."""
    return rect(x - 11, y0, x - 5, y1, "seamL") + rect(x - 5, y0, x + 5, y1, "seamD") + rect(x + 5, y0, x + 11, y1, "seamL")


def hseam(y, x0, x1):
    return rect(x0, y - 11, x1, y - 5, "seamL") + rect(x0, y - 5, x1, y + 5, "seamD") + rect(x0, y + 5, x1, y + 11, "seamL")


def coupling(x, y0, y1):
    h = y1 - y0
    m = (y0 + y1) / 2
    return (f'<rect x="{x - 46}" y="{y0 - 26}" width="92" height="{h + 52}" rx="24" fill="{C["ol"]}"/>'
            f'<rect x="{x - 32}" y="{y0 - 12}" width="64" height="{h + 24}" rx="12" fill="{C["pipeB"]}"/>'
            f'<rect x="{x - 32}" y="{y0 - 12}" width="64" height="{(h + 24) / 2:.1f}" rx="10" fill="{C["pipeT"]}"/>'
            f'<path d="M{x - 8},{y0 - 10} Q{x - 30},{m} {x - 8},{y1 + 10}" stroke="{C["ol"]}" stroke-width="9" fill="none"/>'
            f'<path d="M{x - 20},{y0 - 4} Q{x - 34},{m} {x - 20},{y1 + 4}" stroke="#97AAB0" stroke-width="7" fill="none"/>')


def floor_light(x, y, vertical=False):
    w, h = (30, 62) if vertical else (62, 30)
    w2, h2 = (16, 46) if vertical else (46, 16)
    w3, h3 = (6, 26) if vertical else (26, 6)
    return (f'<circle cx="{x}" cy="{y}" r="70" fill="url(#gDot)"/>'
            f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="15" fill="{C["ol"]}"/>'
            f'<rect x="{x - w2 / 2}" y="{y - h2 / 2}" width="{w2}" height="{h2}" rx="8" fill="#FFBE62"/>'
            f'<rect x="{x - w3 / 2}" y="{y - h3 / 2}" width="{w3}" height="{h3}" rx="3" fill="#FFF3B8"/>')


# ---------------------------------------------------------------- hall_h pieces (one period, origin ox,oy)
def hh_face_seams(ox, oy):
    s = []
    for sx in (500, 1500):
        s.append(vseam(ox + sx, oy + FT, oy + FACE_BOT))
    return "".join(s)


def hh_cone(ox, oy, lx=0):
    x = ox + lx
    top, bot = oy + LAMP_Y + 60, oy + FLOOR_T
    return (f'<path d="M{x - 100},{top} L{x + 100},{top} L{x + 440},{bot} L{x - 440},{bot}Z" '
            f'fill="url(#gCone)" filter="url(#softS)"/>'
            f'<path d="M{x - 60},{top} L{x + 60},{top} L{x + 260},{bot} L{x - 260},{bot}Z" '
            f'fill="url(#gCone)" opacity="0.55" filter="url(#soft)"/>')


def hh_face_deco(ox, oy, lamps=(0, 2000), port=True, rivets=True, couplings=True, lift=None, uid=""):
    """Rivets, couplings, porthole, lamps. lift(x) gives an upward shift for the wrapped corner."""
    lf = lift or (lambda x: 0.0)
    s = []
    if rivets:
        for sx in (500, 1500):
            for dx in (-50, 50):
                x = ox + sx + dx
                for ry in (498, 1078):
                    s.append(("riv", x, oy + ry))
    out = []
    for kind, x, y in s:
        out.append(rivet(x, y - lf(x)))
    if couplings:
        for cx_, (a, b) in ((650, (184, 274)), (1350, (334, 404))):
            x = ox + cx_
            out.append(f'<g transform="translate(0,{-lf(x):.1f})">{coupling(x, oy + a + 14, oy + b - 14)}</g>')
    if port:
        out.append(porthole(ox + 1000, oy + PORT_Y, f"{uid}{ox}"))
    for lx in lamps:
        out.append(lamp(ox + lx, oy + LAMP_Y))
    return "".join(out)


def hh_floor_deco(ox, oy, pools=(0,), dashes=True, fseams=True):
    s = []
    for lx in pools:
        s.append(f'<ellipse cx="{ox + lx}" cy="{oy + FLOOR_T + 70}" rx="470" ry="200" fill="url(#gPool)"/>')
    if fseams:
        for sx in (500, 1500):
            x = ox + sx
            s.append(rect(x - 4, oy + FLOOR_T, x + 4, oy + FLOOR_B, "fseamD") + rect(x + 4, oy + FLOOR_T, x + 10, oy + FLOOR_B, "fseamL")
                     + rect(x - 10, oy + FLOOR_T, x - 4, oy + FLOOR_B, "fseamL"))
    if dashes:
        for k in range(4):
            x = ox + 60 + 500 * k
            s.append(rect(x, oy + CL_Y - 25, x + 380, oy + CL_Y + 25, "dash"))
    return "".join(s)


def hh_lights_x(ox):
    return [ox + 250 + 500 * k for k in range(4)]


def bands_rect(bands, x0, x1, oy):
    return "".join(rect(x0, oy + a, x1, oy + b, col) for a, b, col in bands)


# ---------------------------------------------------------------- hall_v pieces (one period, origin oy)
def hv_band_base(oy, x_off=0):
    """Stripe + seams + rivets for both bands over one period."""
    s = []
    for a, b, col in V_STRIPE:
        s.append(rect(a, oy, b, oy + VP, col))
        s.append(rect(mx(b), oy, mx(a), oy + VP, col))
    return "".join(s)


def hv_band_seams(oy, sides=("L", "R")):
    s = []
    for side in sides:
        x0, x1 = (108, 700) if side == "L" else (mx(700), mx(108))
        s.append(hseam(oy, x0, x1))
        for rx in (140, 668):
            x = rx if side == "L" else mx(rx)
            for dy in (-50, 50):
                s.append(rivet(x, oy + dy))
    return "".join(s)


def hv_floor_deco(oy, pools=True, dashes=True, fseam=True):
    s = []
    if pools:
        for x in (S + 90, X0 - 90):
            s.append(f'<ellipse cx="{x}" cy="{oy + V_LAMP_Y}" rx="250" ry="400" fill="url(#gPool)"/>')
    if fseam:
        s.append(rect(S, oy - 4, X0, oy + 4, "fseamD") + rect(S, oy + 4, X0, oy + 10, "fseamL") + rect(S, oy - 10, X0, oy - 4, "fseamL"))
    if dashes:
        for k in (-1, 0, 1):
            y = oy + 60 + 500 * k
            s.append(rect(CL_X - 25, y, CL_X + 25, y + 380, "dash"))
    return "".join(s)


# ================================================================= hall_h
def build_hall_h():
    b = []
    b.append(rect(0, 0, HP, FT, "ol") + rect(0, 14, HP, 84, "plum"))
    b.append(bands_rect(BASE_BANDS, 0, HP, 0))
    for ox in (-HP, 0, HP):
        b.append(hh_face_seams(ox, 0))
    b.append(bands_rect(OVER_BANDS, 0, HP, 0))
    b.append(rect(0, FLOOR_T, HP, FLOOR_B, "floor"))
    b.append('<g clip-path="url(#hhFloor)">' + "".join(hh_floor_deco(ox, 0) for ox in (-HP, 0, HP)) + "</g>")
    b.append(f'<g clip-path="url(#hhFace)">' + "".join(hh_cone(ox, 0) for ox in (-HP, 0, HP)) + "</g>")
    for ox in (-HP, 0, HP):
        b.append(hh_face_deco(ox, 0, lamps=(0,), uid="h"))
    b.append(bands_rect(LEDGE_BANDS, 0, HP, 0))
    for ox in (-HP, 0, HP):
        for x in hh_lights_x(ox):
            b.append(floor_light(x, 1520) + floor_light(x, FLOOR_B + 2))
    cp = (f'<clipPath id="hhFace"><rect x="-10" y="{FT}" width="{HP + 20}" height="{FLOOR_T - FT}"/></clipPath>'
          f'<clipPath id="hhFloor"><rect x="-10" y="{FLOOR_T}" width="{HP + 20}" height="{FLOOR_B - FLOOR_T}"/></clipPath>')
    return svg_doc(HP, HH, "".join(b), cp)


# ================================================================= hall_v
def build_hall_v():
    b = []
    b.append(rect(0, 0, WV, VP, "top"))
    for ox in (-VP, 0, VP):
        b.append(hv_band_base(ox))
    for oy in (0, VP):
        b.append(hv_band_seams(oy))
    # frames + bevel
    b.append(rect(98, 0, 108, VP, "topD") + rect(mx(108), 0, mx(98), VP, "topD"))
    b.append(rect(0, 0, 98, VP, "ol") + rect(14, 0, 84, VP, "plum"))
    b.append(rect(mx(98), 0, WV, VP, "ol") + rect(mx(84), 0, mx(14), VP, "plum"))
    # floor edges
    b.append(rect(700, 0, 718, VP, "topHL") + rect(718, 0, S, VP, "ol"))
    b.append(rect(X0 + 14, 0, X0 + 32, VP, "topHL") + rect(X0, 0, X0 + 14, VP, "ol"))
    b.append(rect(S, 0, X0, VP, "floor"))
    for oy in (-VP, 0, VP):
        b.append(hv_floor_deco(oy))
    for oy in (-VP, 0, VP):
        for y in (oy + 250, oy + 750):
            b.append(floor_light(S, y, True) + floor_light(X0, y, True))
    for oy in (-VP, 0, VP):
        b.append(lamp(V_LAMP_X, oy + V_LAMP_Y) + lamp(mx(V_LAMP_X), oy + V_LAMP_Y))
    return svg_doc(WV, VP, "".join(b))


# ================================================================= corners
CW, CH = 3132, 3664
RC = 160      # inner corner radius at the floor
RF = 120      # frame corner radius
RO = 120      # outer floor corner radius (ru only)


def dash_arc_pattern(length, start_on, end_on, dash=380, gap=120):
    """Dash array for an arc that starts inside a dash (start_on px left of it) and ends inside a dash
    (end_on px of it) or, when end_on is negative, inside a gap (-end_on px of gap)."""
    if end_on >= 0:
        mid = length - start_on - end_on
        best = None
        for n in range(0, 6):
            d = (mid - gap * (n + 1)) / n if n else None
            if n == 0:
                continue
            if d > 60:
                cand = (abs(d - dash), n, d)
                best = min(best, cand) if best else cand
        _, n, d = best
        arr = [start_on] + sum([[gap, d] for _ in range(n)], []) + [gap, end_on]
    else:
        g_end = -end_on
        mid = length - start_on - g_end
        best = None
        for n in range(1, 6):
            d = (mid - gap * n) / n
            if d > 60:
                cand = (abs(d - dash), n, d)
                best = min(best, cand) if best else cand
        _, n, d = best
        arr = [start_on] + sum([[gap, d] for _ in range(n)], []) + [g_end, 0.001]
    assert abs(sum(arr) - length) < 1, (sum(arr), length)
    return " ".join(f"{v:.2f}" for v in arr)


def frame_strokes(paths, clip_id):
    s = []
    for p in paths:
        s.append(f'<path d="{p}" fill="none" stroke="{C["topD"]}" stroke-width="118" clip-path="url(#{clip_id})"/>')
    for p in paths:
        s.append(f'<path d="{p}" fill="none" stroke="{C["ol"]}" stroke-width="98"/>')
    for p in paths:
        s.append(f'<path d="{p}" fill="none" stroke="{C["plum"]}" stroke-width="70"/>')
    return "".join(s)


def floor_with_edges(path):
    return (f'<path d="{path}" fill="none" stroke="{C["topHL"]}" stroke-width="64" stroke-linejoin="round"/>'
            f'<path d="{path}" fill="none" stroke="{C["ol"]}" stroke-width="28" stroke-linejoin="round"/>'
            f'<path d="{path}" fill="{C["floor"]}"/>')


def wrap_band(y1, y2, x_left, x_right, rc):
    """Horizontal band whose left end wraps around a rounded corner (lifted by the corner arc)."""
    return (f"M{x_right},{y1} L{x_left + rc},{y1} A{rc} {rc} 0 0 1 {x_left},{y1 - rc} "
            f"L{x_left},{y2 - rc} A{rc} {rc} 0 0 0 {x_left + rc},{y2} L{x_right},{y2}Z")


def build_corner_ru():
    Ya = 1000
    ox = CW - 2 * HP            # hall_h phase origin copies: ox, ox+HP, ox+2HP
    oxs = [ox, ox + HP, ox + 2 * HP]
    fy = Ya + 2615              # bottom frame centreline
    ty = Ya + 49                # top frame centreline
    inside = (f"M49,-60 L49,{fy - RF} A{RF} {RF} 0 0 0 {49 + RF},{fy} L{CW + 60},{fy} L{CW + 60},{ty} "
              f"L{2315 + RF},{ty} A{RF} {RF} 0 0 1 2315,{ty - RF} L2315,-60Z")
    frameA = f"M49,-60 L49,{fy - RF} A{RF} {RF} 0 0 0 {49 + RF},{fy} L{CW + 60},{fy}"
    frameB = f"M{CW + 60},{ty} L{2315 + RF},{ty} A{RF} {RF} 0 0 1 2315,{ty - RF} L2315,-60"
    ft, fb = Ya + FLOOR_T, Ya + FLOOR_B
    floor = (f"M{S},-60 L{S},{fb - RO} A{RO} {RO} 0 0 0 {S + RO},{fb} L{CW + 60},{fb} L{CW + 60},{ft} "
             f"L{X0 + RC},{ft} A{RC} {RC} 0 0 1 {X0},{ft - RC} L{X0},-60Z")
    face_clip = wrap_band(Ya + FT, Ya + FLOOR_T, X0, CW + 60, RC)

    def lift(x):
        d = X0 + RC - x
        if d <= 0:
            return 0.0
        d = min(d, RC)
        return RC - math.sqrt(RC * RC - d * d)

    cps = (f'<clipPath id="cIn"><path d="{inside}"/></clipPath>'
           f'<clipPath id="cFloor"><path d="{floor}"/></clipPath>'
           f'<clipPath id="cFace"><path d="{face_clip}"/></clipPath>'
           f'<clipPath id="cVF"><rect x="{S}" y="-60" width="900" height="{ft - RC + 60}"/></clipPath>'
           f'<clipPath id="cHF"><rect x="{X0 + RC}" y="{ft}" width="{CW}" height="900"/></clipPath>'
           f'<clipPath id="cBL"><rect x="108" y="-60" width="592" height="{fb + 60}"/></clipPath>'
           f'<clipPath id="cBR"><rect x="{mx(700)}" y="-60" width="592" height="{Ya + 200}"/></clipPath>')
    b = [rect(0, 0, CW, CH, "out"), f'<path d="{inside}" fill="{C["top"]}"/>']
    # wall-top bands of the vertical part
    stripeL = "".join(rect(a, -60, bb, fb, col) for a, bb, col in V_STRIPE)
    stripeR = "".join(rect(mx(bb), -60, mx(a), Ya + 200, col) for a, bb, col in V_STRIPE)
    b.append(stripeL + stripeR)
    segL = "".join(hv_band_seams(oy, ("L",)) for oy in (0, 1000, 2000, 3000))
    b.append(f'<g clip-path="url(#cBL)">{segL}{hseam(fb, 108, 700)}</g>')
    b.append(f'<g clip-path="url(#cBR)">{hv_band_seams(0, ("R",))}{hv_band_seams(1000, ("R",))}</g>')
    # floor
    b.append(floor_with_edges(floor))
    pools = "".join(f'<ellipse cx="{S + 90}" cy="{y}" rx="250" ry="400" fill="url(#gPool)"/>' for y in (500, 1500, 2500))
    pools += f'<ellipse cx="{X0 - 90}" cy="500" rx="250" ry="400" fill="url(#gPool)"/>'
    pools += "".join(f'<ellipse cx="{o}" cy="{Ya + FLOOR_T + 70}" rx="470" ry="200" fill="url(#gPool)"/>' for o in (CW,))
    b.append(f'<g clip-path="url(#cFloor)">{pools}</g>')
    vf = "".join(hv_floor_deco(oy, pools=False) for oy in (0, 1000, 2000, 3000))
    b.append(f'<g clip-path="url(#cVF)">{vf}</g>')
    hf = "".join(hh_floor_deco(o, Ya, pools=()) for o in oxs)
    b.append(f'<g clip-path="url(#cHF)">{hf}</g>')
    # centreline arc: vertical (x=CL_X) -> horizontal (y=Ya+CL_Y), centre (X0+RC, ft-RC), r=610
    r = X0 + RC - CL_X
    arc_len = math.pi / 2 * r
    y_start = ft - RC
    start_on = 440 - (y_start % 500) if 60 <= y_start % 500 < 440 else 0
    xh_end = (X0 + RC - CW) % 500
    end_on = xh_end - 60 if 60 <= xh_end < 440 else 0
    da = dash_arc_pattern(arc_len, start_on, end_on)
    b.append(f'<path d="M{CL_X},{y_start} A{r} {r} 0 0 0 {X0 + RC},{Ya + CL_Y}" fill="none" stroke="{C["dash"]}" '
             f'stroke-width="50" stroke-dasharray="{da}"/>')
    # frames
    b.append(frame_strokes([frameA, frameB], "cIn"))
    # back wall face, wrapped around the inner corner
    face = []
    for a, bb, col in BASE_BANDS:
        face.append(f'<path d="{wrap_band(Ya + a, Ya + bb, X0, CW + 60, RC)}" fill="{C[col]}"/>')
    face.append(f'<g clip-path="url(#cFace)">' + "".join(
        vseam(o + sx, Ya + FT, Ya + FACE_BOT) for o in oxs for sx in (500, 1500) if o + sx > X0 + RC) + "</g>")
    for a, bb, col in OVER_BANDS:
        face.append(f'<path d="{wrap_band(Ya + a, Ya + bb, X0, CW + 60, RC)}" fill="{C[col]}"/>')
    face.append(rect(X0, Ya + 84 - RC, X0 + OLW, Ya + FLOOR_T - RC, "ol"))
    for yb in (Ya + FT, Ya + FLOOR_T):     # radial outlines on the wrapped top edge and floor edge
        r_ = RC - OLW / 2
        cx_, cy_ = X0 + RC, yb - RC
        face.append(f'<path d="M{cx_ - r_},{cy_} A{r_} {r_} 0 0 0 {cx_},{cy_ + r_} L{cx_ + 4},{cy_ + r_}" '
                    f'fill="none" stroke="{C["ol"]}" stroke-width="{OLW}"/>')
    cones = "".join(hh_cone(o, Ya) for o in oxs if o >= X0 + RC + 300)
    face.append(f'<g clip-path="url(#cFace)">{cones}</g>')
    deco = []
    for o in oxs:
        lamps = tuple(lx for lx in (0,) if o + lx >= X0 + RC + 130)
        port = o + 1000 - 260 >= X0 + RC
        deco.append(hh_face_deco(o, Ya, lamps=lamps, port=port, lift=lift, uid="ru"))
    face.append(f'<g clip-path="url(#cFace)">{"".join(deco)}</g>')
    for o in oxs:
        for x in hh_lights_x(o):
            if x >= X0 + RC + 40:
                face.append(floor_light(x, Ya + 1520))
            if x >= S + RO + 40:
                face.append(floor_light(x, fb + 2))
    b.append("".join(face))
    # band floor lights + lamps
    for y in range(250, 4000, 500):
        if y <= fb - RO - 60:
            b.append(floor_light(S, y, True))
        if y <= Ya + 84 - RC - 60:
            b.append(floor_light(X0, y, True))
    for y in (500, 1500, 2500):
        b.append(lamp(V_LAMP_X, y))
    b.append(lamp(mx(V_LAMP_X), 500))
    return svg_doc(CW, CH, "".join(b), cps)


def build_corner_rd():
    oyv = -336                   # hall_v phase: y_v = y - oyv (mod 1000)
    ox = CW - 2 * HP
    oxs = [ox, ox + HP, ox + 2 * HP]
    ty, by = 49, 2615
    inside = (f"M49,{CH + 60} L49,{ty + RF} A{RF} {RF} 0 0 1 {49 + RF},{ty} L{CW + 60},{ty} L{CW + 60},{by} "
              f"L{2315 + RF},{by} A{RF} {RF} 0 0 0 2315,{by + RF} L2315,{CH + 60}Z")
    frameA = f"M49,{CH + 60} L49,{ty + RF} A{RF} {RF} 0 0 1 {49 + RF},{ty} L{CW + 60},{ty}"
    frameB = f"M{CW + 60},{by} L{2315 + RF},{by} A{RF} {RF} 0 0 0 2315,{by + RF} L2315,{CH + 60}"
    ft, fb = FLOOR_T, FLOOR_B
    floor = (f"M{S},{ft} L{CW + 60},{ft} L{CW + 60},{fb} L{X0 + RC},{fb} A{RC} {RC} 0 0 0 {X0},{fb + RC} "
             f"L{X0},{CH + 60} L{S},{CH + 60}Z")
    cps = (f'<clipPath id="cIn"><path d="{inside}"/></clipPath>'
           f'<clipPath id="cFloor"><path d="{floor}"/></clipPath>'
           f'<clipPath id="cFace"><rect x="{S}" y="{FT}" width="{CW}" height="{FLOOR_T - FT}"/></clipPath>'
           f'<clipPath id="cVF"><rect x="{S}" y="{fb + RC}" width="900" height="{CH}"/></clipPath>'
           f'<clipPath id="cHF"><rect x="{X0 + RC}" y="{ft}" width="{CW}" height="900"/></clipPath>'
           f'<clipPath id="cBL"><rect x="108" y="0" width="592" height="{CH + 60}"/></clipPath>'
           f'<clipPath id="cBR"><rect x="{mx(700)}" y="2664" width="592" height="{CH}"/></clipPath>')
    b = [rect(0, 0, CW, CH, "out"), f'<path d="{inside}" fill="{C["top"]}"/>']
    stripeL = "".join(rect(a, 0, bb, CH + 60, col) for a, bb, col in V_STRIPE)
    stripeR = "".join(rect(mx(bb), 2664, mx(a), CH + 60, col) for a, bb, col in V_STRIPE)
    b.append(stripeL + stripeR)
    oys = [oyv + 1000 * k for k in range(0, 5)]
    b.append(f'<g clip-path="url(#cBL)">{"".join(hv_band_seams(o, ("L",)) for o in oys)}</g>')
    b.append(f'<g clip-path="url(#cBR)">{"".join(hv_band_seams(o, ("R",)) for o in oys)}</g>')
    # left band floor-side edge along the face (above the floor)
    b.append(floor_with_edges(floor))
    b.append(rect(700, 98, 718, CH, "topHL") + rect(718, 98, S, CH, "ol"))
    lampsL = [o + V_LAMP_Y for o in oys if o + V_LAMP_Y - 122 >= 98 + 120]
    lampsR = [o + V_LAMP_Y for o in oys if o + V_LAMP_Y - 122 >= 2664 + 40]
    pools = "".join(f'<ellipse cx="{S + 90}" cy="{y}" rx="250" ry="400" fill="url(#gPool)"/>' for y in lampsL)
    pools += "".join(f'<ellipse cx="{X0 - 90}" cy="{y}" rx="250" ry="400" fill="url(#gPool)"/>' for y in lampsR)
    pools += "".join(f'<ellipse cx="{o}" cy="{FLOOR_T + 70}" rx="470" ry="200" fill="url(#gPool)"/>' for o in oxs if o >= S)
    b.append(f'<g clip-path="url(#cFloor)">{pools}</g>')
    vf = "".join(hv_floor_deco(o, pools=False) for o in oys)
    b.append(f'<g clip-path="url(#cVF)">{vf}</g>')
    hf = "".join(hh_floor_deco(o, 0, pools=()) for o in oxs)
    b.append(f'<g clip-path="url(#cHF)">{hf}</g>')
    # centreline arc: horizontal (y=CL_Y) from right -> vertical (x=CL_X) going down
    r = X0 + RC - CL_X
    arc_len = math.pi / 2 * r
    xh = (X0 + RC - CW) % 500           # phase at arc start, path runs leftwards
    start_on = xh - 60 if 60 <= xh < 440 else 0
    y_end = fb + RC
    yv = (y_end - oyv) % 500
    if 60 <= yv < 440:
        end = 440 - yv  # unused branch kept for clarity
        end_on = yv - 60
    else:
        end_on = -((60 - yv) % 500)       # remaining gap after the arc ends
        end_on = -(yv - 440) if yv >= 440 else end_on
    da = dash_arc_pattern(arc_len, start_on, end_on)
    b.append(f'<path d="M{X0 + RC},{CL_Y} A{r} {r} 0 0 0 {CL_X},{y_end}" fill="none" stroke="{C["dash"]}" '
             f'stroke-width="50" stroke-dasharray="{da}"/>')
    b.append(frame_strokes([frameA, frameB], "cIn"))
    face = [bands_rect(BASE_BANDS, S, CW, 0)]
    face.append(f'<g clip-path="url(#cFace)">' + "".join(hh_face_seams(o, 0) for o in oxs) + "</g>")
    face.append(bands_rect(OVER_BANDS, S, CW, 0))
    cones = "".join(hh_cone(o, 0) for o in oxs if o >= S)
    face.append(f'<g clip-path="url(#cFace)">{cones}</g>')
    deco = []
    for o in oxs:
        lamps = tuple(lx for lx in (0,) if o + lx >= S + 130)
        deco.append(hh_face_deco(o, 0, lamps=lamps, port=o + 1000 - 260 >= S, uid="rd"))
    face.append(f'<g clip-path="url(#cFace)">{"".join(deco)}</g>')
    for o in oxs:
        for x in hh_lights_x(o):
            if x >= S + 40:
                face.append(floor_light(x, 1520))
            if x >= X0 + RC + 40:
                face.append(floor_light(x, fb + 2))
    b.append("".join(face))
    for k in range(-1, 9):
        y = oyv + 250 + 500 * k
        if ft + 60 <= y <= CH + 40:
            b.append(floor_light(S, y, True))
        if fb + RC + 60 <= y <= CH + 40:
            b.append(floor_light(X0, y, True))
    for y in lampsL:
        b.append(lamp(V_LAMP_X, y))
    for y in lampsR:
        b.append(lamp(mx(V_LAMP_X), y))
    return svg_doc(CW, CH, "".join(b), cps)


# ================================================================= render
def render(svg_text, w, h, scale=0.5):
    cw, ch = int(round(w * scale)), int(round(h * scale))
    return svgtools.render_rgba([svg_text], 1, cw, ch)


def main(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    pieces = {
        "hall_h": (build_hall_h, HP, HH),
        "hall_v": (build_hall_v, WV, VP),
        "hall_corner_ru": (build_corner_ru, CW, CH),
        "hall_corner_rd": (build_corner_rd, CW, CH),
    }
    imgs = {}
    for name, (fn, w, h) in pieces.items():
        if only and name not in only:
            continue
        svg = fn()
        assert "--" not in svg.replace("-->", "")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        im = render(svg, w, h)
        im.save(OUT / f"{name}.png", optimize=True)
        imgs[name] = im
        print(name, im.size, (OUT / f"{name}.png").stat().st_size // 1024, "KB")
    return imgs


if __name__ == "__main__":
    main(sys.argv[1:] or None)
