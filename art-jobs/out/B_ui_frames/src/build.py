"""Job B generator: UI frames, Meeting Tablet kit, PREVIEW and meeting mock.
Usage: python build.py   (needs cairosvg, fonttools, Pillow; fonts in $GS_FONTS, see REPORT.md)
All lettering in delivered SVGs is converted to paths; no var(), no gradients, no rasters."""
import json
import math
import os
import pathlib

import cairosvg
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent
FONTS = pathlib.Path(os.environ.get("GS_FONTS", "/tmp/claude-0/fonts"))
REPO = OUT.parents[2]

OL = "#2A1E35"
INDIGO = "#1B1830"
PLUM = "#3D2A4F"
TEAL = "#2F6F73"
SEAFOAM = "#7FC8B8"
AMBER = "#F5A54A"
CREAM = "#F4E6C8"
CREAM_SH = "#DCC8A2"
CREAM_LIP = "#CDB78F"
CORAL = "#E8574A"
PINK = "#D9738C"
CREW = {"tomato": "#E4483C", "tangerine": "#F28A2E", "mustard": "#E9C046", "lime": "#A6D64A",
        "mint": "#6FD6B0", "sky": "#6EC3F0", "cobalt": "#3F5FD9", "grape": "#8E5AC8",
        "bubblegum": "#F07BB5", "cream": "#F4E6C8"}


# ---------- text to paths ----------
class Font:
    def __init__(self, name):
        self.f = TTFont(str(FONTS / name))
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def width(self, s, size, ls=0):
        sc = size / self.upm
        return sum(self.hmtx[self.cmap[ord(c)]][0] * sc + ls for c in s) - ls

    def path(self, s, x, y, size, fill, anchor="start", ls=0, extra=""):
        sc = size / self.upm
        w = self.width(s, size, ls)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        pen = SVGPathPen(self.gs)
        cur = 0.0
        for c in s:
            g = self.cmap[ord(c)]
            self.gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x0 + cur, y)))
            cur += self.hmtx[g][0] * sc + ls
        return f'<path d="{pen.getCommands()}" fill="{fill}" {extra}/>'


BUNGEE = Font("Bungee-Regular.ttf")
VT = Font("VT323-Regular.ttf")
SG5 = Font("SpaceGrotesk-500.ttf")
SG7 = Font("SpaceGrotesk-700.ttf")


# ---------- primitives ----------
def rr(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (f"M{x + r},{y} H{x + w - r} A{r},{r} 0 0 1 {x + w},{y + r} V{y + h - r} "
            f"A{r},{r} 0 0 1 {x + w - r},{y + h} H{x + r} A{r},{r} 0 0 1 {x},{y + h - r} "
            f"V{y + r} A{r},{r} 0 0 1 {x + r},{y} Z")


def circ(cx, cy, r):
    return f"M{cx - r},{cy} A{r},{r} 0 1 0 {cx + r},{cy} A{r},{r} 0 1 0 {cx - r},{cy} Z"


def bevel(pid, d, base, shade, dy, sw=4, stroke=OL):
    """Two-tone cel shape: shade color shows as a band along the bottom edge."""
    return (f'<clipPath id="{pid}"><path d="{d}"/></clipPath>'
            f'<path d="{d}" fill="{shade}"/>'
            f'<g clip-path="url(#{pid})"><path d="{d}" fill="{base}" transform="translate(0,{-dy})"/></g>'
            f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')


def screw(cx, cy, r=6):
    a = r * 0.55
    return (f'<g class="screw"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#E7D7B4" stroke="{OL}" stroke-width="{max(2, r / 3):.1f}"/>'
            f'<path d="M{cx - a},{cy + a} L{cx + a},{cy - a}" stroke="{OL}" stroke-width="{max(1.6, r / 3.5):.1f}" stroke-linecap="round"/></g>')


def lamp(cx, cy, r, color, glow=True):
    g = ""
    if glow:
        g = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r + k}" fill="{color}" opacity="{o}"/>'
                    for k, o in ((r * 1.4, 0.12), (r * 0.8, 0.2), (r * 0.35, 0.3)))
    return (g + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" stroke="{OL}" stroke-width="2.5"/>'
            f'<circle cx="{cx - r * 0.35}" cy="{cy - r * 0.35}" r="{r * 0.3}" fill="#FFF8E8" opacity="0.85"/>')


def screen(pid, x, y, w, h, r, sw=4, glow=TEAL):
    """Dark CRT glass with a faint glow band hugging the inside edge (uniform along edges)."""
    d = rr(x, y, w, h, r)
    rings = "".join(
        f'<path d="{rr(x + k, y + k, w - 2 * k, h - 2 * k, max(2, r - k))}" fill="none" stroke="{glow}" '
        f'stroke-width="{s}" opacity="{o}"/>' for k, s, o in ((3, 6, 0.45), (7, 6, 0.22), (12, 7, 0.1)))
    glint = (f'<path d="M{x + r * 0.55},{y + r + 10} A{r * 0.6},{r * 0.6} 0 0 1 {x + r + 10},{y + r * 0.55}" '
             f'fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.28"/>')
    return (f'<clipPath id="{pid}"><path d="{d}"/></clipPath>'
            f'<path d="{d}" fill="{INDIGO}"/><g clip-path="url(#{pid})">{rings}</g>{glint}'
            f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{sw}"/>')


def stripe(x0, x1, y, h_amber, h_coral, gap=3):
    """Cream-amber-coral racing stripe (cream is the bezel itself)."""
    ra, rc = h_amber / 2, h_coral / 2
    return (f'<g id="racing_stripe"><path d="M{x0 + ra},{y + ra} H{x1 - ra}" stroke="{AMBER}" stroke-width="{h_amber}" stroke-linecap="round"/>'
            f'<path d="M{x0 + rc},{y + h_amber + gap + rc} H{x1 - rc}" stroke="{CORAL}" stroke-width="{h_coral}" stroke-linecap="round"/></g>')


def svg(w, h, body, title=""):
    t = f"<title>{title}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f"{t}{body}</svg>")


# ---------- B1 frames and controls ----------
def crt_panel(p, w, h, bez, bot, r_out, r_scr, screw_r, stripe_h):
    s = bez // 2 + 1
    out = rr(2, 2, w - 4, h - 4, r_out)
    sx, sy, sw_, sh = bez, bez, w - 2 * bez, h - bez - bot
    lip = f'<path d="{rr(sx - 5, sy - 5, sw_ + 10, sh + 10, r_scr + 5)}" fill="{CREAM_LIP}"/>'
    ys = h - bot + (bot - stripe_h[0] - stripe_h[1] - 3) / 2 + 1
    so = bez + r_scr * 0.2
    body = (f'<g id="bezel">{bevel(p + "b", out, CREAM, CREAM_SH, max(5, bez // 3))}{lip}</g>'
            f'<g id="screen">{screen(p + "s", sx, sy, sw_, sh, r_scr)}</g>'
            f'<g id="stripe">{stripe(so + screw_r * 2 + 4, w - so - screw_r * 2 - 4, ys, *stripe_h)}</g>'
            f'<g id="screws">{screw(s + 1, s + 1, screw_r)}{screw(w - s - 1, s + 1, screw_r)}'
            f'{screw(s + 1, h - bot / 2, screw_r)}{screw(w - s - 1, h - bot / 2, screw_r)}</g>')
    ins = {"left": bez + r_scr, "right": bez + r_scr, "top": bez + r_scr, "bottom": bot + r_scr}
    return svg(w, h, body), ins


def toast(w=360, h=64):
    d = rr(2, 2, w - 4, h - 4, (h - 4) / 2)
    body = (f'<g id="pill">{bevel("tb", d, CREAM, CREAM_SH, 6)}</g>'
            f'<g id="lamp">{lamp(34, h / 2 - 2, 10, AMBER)}</g>'
            f'<g id="stripe">{stripe(60, w - 30, h - 15, 3, 3, 2)}</g>')
    return svg(w, h, body), {"left": 60, "right": 34, "top": 0, "bottom": 0}


def bubble(w=280, h=150):
    bh, r = 112, 26
    d = (f"M{2 + r},2 H{w - 2 - r} A{r},{r} 0 0 1 {w - 2},{2 + r} V{bh - r} A{r},{r} 0 0 1 {w - 2 - r},{bh} "
         f"H74 L24,{h - 3} L40,{bh} H{2 + r} A{r},{r} 0 0 1 2,{bh - r} V{2 + r} A{r},{r} 0 0 1 {2 + r},2 Z")
    hi = f'<path d="M20,34 A20,20 0 0 1 40,14" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.6"/>'
    return svg(w, h, f'<g id="bubble">{bevel("bb", d, CREAM, CREAM_SH, 6)}{hi}</g>'), \
        {"left": 80, "right": 30, "top": 30, "bottom": h - bh + 26}


BTN = {"idle": (AMBER, "#C9782C", "#2A1E35"), "pressed": ("#E8923A", "#B86A24", "#2A1E35"),
       "disabled": ("#9C90A8", "#74687F", "#5A4E66"), "danger": (CORAL, "#A93A33", "#FFF4E0")}


def button(state, w=200, h=64):
    face, shade, _ = BTN[state]
    top = 5 if state == "pressed" else 2
    bev = 4 if state == "pressed" else 9
    d = rr(2, top, w - 4, h - 2 - top, (h - 2 - top) / 2)
    hi = ("" if state in ("pressed", "disabled") else
          f'<path d="M22,{top + 15} A14,14 0 0 1 34,{top + 9}" fill="none" stroke="#FFF8E8" stroke-width="4" stroke-linecap="round" opacity="0.7"/>')
    return svg(w, h, f'<g id="btn_{state}">{bevel("pb" + state, d, face, shade, bev)}{hi}</g>'), \
        {"left": 32, "right": 32, "top": 0, "bottom": 0}


def progress_trough(w=400, h=40):
    out = rr(2, 2, w - 4, h - 4, (h - 4) / 2)
    ch = rr(8, 8, w - 16, h - 16, (h - 16) / 2)
    body = (f'<g id="bezel">{bevel("pt", out, CREAM, CREAM_SH, 4)}</g>'
            f'<g id="channel"><path d="{ch}" fill="{INDIGO}" stroke="{OL}" stroke-width="3"/>'
            f'<path d="M{8 + 12},{11.5} H{w - 20}" stroke="{TEAL}" stroke-width="2" opacity="0.6" stroke-linecap="round"/></g>')
    return svg(w, h, body), {"left": 20, "right": 20, "top": 0, "bottom": 0}


def candy(w, h, period=24, sw=11):
    polys = "".join(f'<path d="M{x},{h} L{x + sw},{h} L{x + sw + h},0 L{x + h},0 Z" fill="{AMBER}"/>'
                    for x in range(-2 * period - h, w + period, period))
    return f'<rect width="{w}" height="{h}" fill="{SEAFOAM}"/>{polys}'


def progress_fill(w=380, h=20):
    d = rr(1.5, 1.5, w - 3, h - 3, (h - 3) / 2)
    body = (f'<clipPath id="pf"><path d="{d}"/></clipPath><g clip-path="url(#pf)">{candy(w, h)}'
            f'<rect x="0" y="{h - 5}" width="{w}" height="5" fill="{OL}" opacity="0.18"/>'
            f'<path d="M10,5 H{w - 10}" stroke="#FFFFFF" stroke-width="2.5" opacity="0.45" stroke-linecap="round"/></g>'
            f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="2.5"/>')
    return svg(w, h, f'<g id="fill">{body}</g>')


def progress_tile(w=24, h=20):
    return svg(w, h, f'<g id="fill_tile">{candy(w, h)}</g>')


DIAL = 112


def dial_ring():
    c = DIAL / 2
    ticks = "".join(
        f'<path d="M{c + 47 * math.sin(a)},{c - 47 * math.cos(a)} L{c + 51 * math.sin(a)},{c - 51 * math.cos(a)}" '
        f'stroke="{OL}" stroke-width="{3 if i % 3 == 0 else 2}" stroke-linecap="round"/>'
        for i, a in enumerate(math.radians(k * 30) for k in range(12)))
    body = (f'<g id="ring">{bevel("dr", circ(c, c, 53), CREAM, CREAM_SH, 5)}{ticks}'
            f'<circle cx="{c}" cy="{c}" r="43" fill="{PLUM}" stroke="{OL}" stroke-width="3"/>'
            f'<circle cx="{c}" cy="{c}" r="37" fill="none" stroke="{OL}" stroke-width="8" opacity="0.5"/></g>')
    return svg(DIAL, DIAL, body)


def dial_arc(frac=1.0, color=AMBER):
    c, r = DIAL / 2, 37
    if frac >= 0.999:
        a = f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="8"/>'
    else:
        e = math.radians(360 * frac)
        a = (f'<path d="M{c},{c - r} A{r},{r} 0 {1 if frac > 0.5 else 0} 1 {c + r * math.sin(e):.2f},{c - r * math.cos(e):.2f}" '
             f'fill="none" stroke="{color}" stroke-width="8" stroke-linecap="round"/>')
    return svg(DIAL, DIAL, f'<g id="arc" data-pivot="{c},{c}">{a}</g>')


def dial_center():
    c = DIAL / 2
    body = (f'<g id="center"><circle cx="{c}" cy="{c}" r="31" fill="{INDIGO}" stroke="{OL}" stroke-width="3"/>'
            f'<circle cx="{c}" cy="{c}" r="27" fill="none" stroke="{TEAL}" stroke-width="5" opacity="0.4"/>'
            f'<path d="M{c - 19},{c - 8} A21,21 0 0 1 {c - 8},{c - 19}" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.3"/></g>')
    return svg(DIAL, DIAL, body)


def chat_button(s=64):
    d = rr(2, 2, s - 4, s - 4, 18)
    b = rr(15, 15, 34, 24, 9)
    icon = (f'<path d="{b} M22,38 L19,48 L31,38 Z" fill="{INDIGO}"/>'
            f'<path d="{b}" fill="{INDIGO}" stroke="{OL}" stroke-width="2"/><path d="M22,37 L19,48 L31,37" fill="{INDIGO}" stroke="{OL}" stroke-width="2" stroke-linejoin="round"/>'
            + "".join(f'<circle cx="{x}" cy="27" r="3" fill="{AMBER}"/>' for x in (24, 32, 40)))
    return svg(s, s, f'<g id="chat_button">{bevel("cb", d, CREAM, CREAM_SH, 6)}{icon}</g>')


def unread_dot(s=24):
    c = s / 2
    return svg(s, s, f'<g id="unread_dot"><circle cx="{c}" cy="{c}" r="{c - 2}" fill="{PINK}" stroke="{OL}" stroke-width="3"/>'
                     f'<circle cx="{c - 3.5}" cy="{c - 3.5}" r="2.6" fill="#FFF4F0" opacity="0.9"/></g>')


def chat_drawer(w=360, h=540):
    out = rr(2, 2, w - 4, h - 4, 28)
    bez, top, bot = 16, 52, 78
    sx, sy, sw_, sh = bez, top, w - 2 * bez, h - top - bot
    lip = f'<path d="{rr(sx - 5, sy - 5, sw_ + 10, sh + 10, 17)}" fill="{CREAM_LIP}"/>'
    well = rr(bez, h - bot + 14, w - 2 * bez, 44, 14)
    body = (f'<g id="bezel">{bevel("db", out, CREAM, CREAM_SH, 6)}{lip}</g>'
            f'<g id="titlebar">{lamp(30, 27, 7, AMBER)}{stripe(46, 92, 21, 4, 4, 2)}'
            f'{screw(w - 22, 26, 6)}</g>'
            f'<g id="screen">{screen("ds", sx, sy, sw_, sh, 12)}</g>'
            f'<g id="input_well"><path d="{well}" fill="{INDIGO}" stroke="{OL}" stroke-width="3"/>'
            f'<path d="{rr(bez + 4, h - bot + 18, w - 2 * bez - 8, 36, 11)}" fill="none" stroke="{TEAL}" stroke-width="3" opacity="0.35"/></g>'
            f'<g id="screws">{screw(22, h - 12, 5)}{screw(w - 22, h - 12, 5)}</g>')
    return svg(w, h, body), {"left": 104, "right": 40, "top": top + 12, "bottom": bot + 12}


# ---------- B2 Meeting Tablet ----------
TW, TH = 1280, 720
TB = (40, 14, 1200, 698)            # tablet body
SCR = (72, 46, 1136, 610)           # screen (inside bezel)
PLATE_W, PLATE_H, PM = 536, 78, 8   # plate body size and glow margin
GRID_X = (96, 648)
GRID_Y0, GRID_DY = 148, 85


def tablet_frame():
    x, y, w, h = TB
    out = rr(x, y, w, h, 44)
    sx, sy, sw_, sh = SCR
    grips = "".join(f'<path d="{rr(gx, 250, 26, 220, 11)}" fill="{TEAL}" stroke="{OL}" stroke-width="4"/>'
                    f'<path d="M{gx + 9},266 V454" stroke="{SEAFOAM}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>'
                    for gx in (22, TW - 48))
    slots = "".join(f'<path d="M{600},{y0} H{680}" stroke="{CREAM_LIP}" stroke-width="5" stroke-linecap="round"/>'
                    f'<path d="M{600},{y0 - 1} H{680}" stroke="{OL}" stroke-width="2" stroke-linecap="round" opacity="0.55"/>'
                    for y0 in (26, 35))
    plaque = (f'<path d="{rr(560, 670, 160, 30, 10)}" fill="{PLUM}" stroke="{OL}" stroke-width="3"/>'
              + BUNGEE.path("NIGHTJAR", 640, 692, 17, CREAM, "middle", 1.5))
    body = (f'<g id="grips">{grips}</g>'
            f'<g id="bezel">{bevel("tf", out, CREAM, CREAM_SH, 9)}'
            f'<path d="{rr(sx - 7, sy - 7, sw_ + 14, sh + 14, 27)}" fill="{CREAM_LIP}"/></g>'
            f'<g id="speaker">{slots}</g>'
            f'<g id="lamps">{lamp(110, 30, 6, AMBER)}{lamp(1170, 30, 6, SEAFOAM)}</g>'
            f'<g id="screen">{screen("ts", sx, sy, sw_, sh, 22, 4)}</g>'
            f'<g id="stripe">{stripe(96, 540, 677, 6, 8)}{stripe(740, 1184, 677, 6, 8)}</g>'
            f'<g id="plaque">{plaque}</g>'
            f'<g id="screws">{screw(62, 36, 7)}{screw(1218, 36, 7)}{screw(62, 688, 7)}{screw(1218, 688, 7)}</g>')
    return svg(TW, TH, body, "Meeting Tablet frame")


def tablet_title():
    w, h = 640, 56
    t = "WHO'S THE IMPOSTOR?"
    body = (BUNGEE.path(t, w / 2 + 3, 46, 42, OL, "middle")
            + BUNGEE.path(t, w / 2, 43, 42, AMBER, "middle"))
    return svg(w, h, f'<g id="title">{body}</g>')


PLATE_STYLE = {
    "alive": dict(face=PLUM, shade="#30213F", ring=TEAL, slot="#241A33", well=INDIGO),
    "you": dict(face=PLUM, shade="#30213F", ring=TEAL, slot="#241A33", well=INDIGO),
    "selected": dict(face="#4C3663", shade="#3A2850", ring=AMBER, slot="#2A1F3B", well=INDIGO),
    "voted": dict(face=PLUM, shade="#30213F", ring=TEAL, slot="#241A33", well=INDIGO),
    "caller": dict(face=PLUM, shade="#30213F", ring=TEAL, slot="#241A33", well=INDIGO),
    "eliminated": dict(face="#2A2136", shade="#221B2C", ring="#3B3349", slot="#1E1828", well="#17142A"),
    "disconnected": dict(face="#4A4754", shade="#3D3A46", ring="#6A6673", slot="#3A3743", well="#2E2C37"),
}
SLOT = (366, 12, 156, 54)   # status area, plate-local (body coords)
WELL = (42, 39, 29)          # portrait well cx, cy, r


def plate_body(state, pid):
    s = PLATE_STYLE[state]
    m = PM
    d = rr(m + 2, m + 2, PLATE_W - 4, PLATE_H - 4, 16)
    glow = ""
    if state == "selected":
        glow = "".join(f'<path d="{d}" fill="none" stroke="{AMBER}" stroke-width="{k}" opacity="{o}"/>'
                       for k, o in ((16, 0.12), (11, 0.2), (7, 0.35)))
    cx, cy, r = WELL[0] + m, WELL[1] + m, WELL[2]
    sx, sy, sw_, sh = SLOT
    parts = [glow, bevel(pid, d, s["face"], s["shade"], 5)]
    if state not in ("eliminated", "disconnected"):
        parts.append(f'<path d="M{m + 20},{m + 7} H{m + PLATE_W - 20}" stroke="#FFFFFF" stroke-width="2" opacity="0.12" stroke-linecap="round"/>')
    parts.append(f'<g id="portrait_well" data-center="{cx},{cy}" data-r="{r - 3}">'
                 f'<circle cx="{cx}" cy="{cy}" r="{r + 2}" fill="{s["ring"]}" stroke="{OL}" stroke-width="3"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="{r - 3}" fill="{s["well"]}" stroke="{OL}" stroke-width="2.5"/></g>')
    parts.append(f'<g id="status_area"><path d="{rr(m + sx, m + sy, sw_, sh, 12)}" fill="{s["slot"]}" stroke="{OL}" stroke-width="2.5"/></g>')
    if state == "you":
        parts.append(f'<path d="{rr(m + 6, m + 6, PLATE_W - 12, PLATE_H - 12, 12)}" fill="none" stroke="{AMBER}" stroke-width="3.5"/>')
    if state == "selected":
        parts.append(f'<path d="{d}" fill="none" stroke="{AMBER}" stroke-width="4"/>')
    if state == "voted":
        parts.append(f'<g id="voted_lamp">{lamp(m + sx - 16, m + sy + sh / 2, 6, SEAFOAM)}</g>')
    if state == "caller":
        parts.append(f'<g id="badge_socket" data-center="{cx + 22},{cy + 22}">'
                     f'<circle cx="{cx + 22}" cy="{cy + 22}" r="13" fill="{INDIGO}" stroke="{AMBER}" stroke-width="3"/></g>')
    if state == "disconnected":
        px, py = m + sx + sw_ / 2, m + sy + sh / 2
        c = "#7E7A88"
        parts.append(f'<g id="unplugged" opacity="0.9">'
                     f'<path d="M{px - 34},{py} H{px - 12}" stroke="{c}" stroke-width="4" stroke-linecap="round"/>'
                     f'<path d="{rr(px - 14, py - 8, 12, 16, 3)}" fill="{c}"/>'
                     f'<path d="M{px - 2},{py - 4} H{px + 3} M{px - 2},{py + 4} H{px + 3}" stroke="{c}" stroke-width="3" stroke-linecap="round"/>'
                     f'<path d="{rr(px + 10, py - 8, 12, 16, 3)}" fill="{c}"/>'
                     f'<path d="M{px + 22},{py} H{px + 36}" stroke="{c}" stroke-width="4" stroke-linecap="round"/></g>')
    return "".join(parts)


def plate_svg(state):
    return svg(PLATE_W + 2 * PM, PLATE_H + 2 * PM, f'<g id="plate_{state}">{plate_body(state, "p" + state)}</g>')


def vote_btn(kind, s=40):
    d = rr(2, 2, s - 4, s - 4, (s - 4) / 2)
    if kind == "confirm":
        face, shade = SEAFOAM, "#5EA595"
        g = f'<path d="M12,20 L18,26 L29,13" fill="none" stroke="{OL}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>'
    else:
        face, shade = "#9C90A8", "#74687F"
        g = f'<path d="M13,12 L27,26 M27,12 L13,26" stroke="{OL}" stroke-width="4.5" stroke-linecap="round"/>'
    return svg(s, s, f'<g id="btn_vote_{kind}">{bevel("vb" + kind, d, face, shade, 5, 3)}{g}</g>')


# ---------- mock-only helpers ----------
def portrait(cx, cy, r, color, dead=False, grey=False):
    """Simple on-model helmet portrait (code draws the real puppet in game)."""
    suit = "#7A7486" if grey else color
    rim, glass, visor = "#C6D0DA", "#221C3A", AMBER
    if grey:
        rim, visor = "#8C8896", "#6E6A78"
    if dead:
        rim, visor = "#5E5870", "#3A3150"
    clip = f'<clipPath id="pc{cx}{cy}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
    g = (f'<g clip-path="url(#pc{cx}{cy})" opacity="{0.55 if dead else 1}">'
         f'<ellipse cx="{cx}" cy="{cy + r * 0.86}" rx="{r * 0.98}" ry="{r * 0.56}" fill="{suit}" stroke="{OL}" stroke-width="2.5"/>'
         f'<path d="M{cx - r * 0.12},{cy + r * 0.45} V{cy + r * 0.95} M{cx + r * 0.12},{cy + r * 0.45} V{cy + r * 0.95}" stroke="{OL}" stroke-width="1.6" opacity="0.5"/>'
         f'<path d="M{cx},{cy - r * 0.76} V{cy - r * 0.9}" stroke="{OL}" stroke-width="2.5"/>'
         f'<circle cx="{cx}" cy="{cy - r * 0.92}" r="{r * 0.13}" fill="{AMBER if not (dead or grey) else rim}" stroke="{OL}" stroke-width="2"/>'
         f'<circle cx="{cx}" cy="{cy - r * 0.1}" r="{r * 0.68}" fill="{rim}" stroke="{OL}" stroke-width="2.5"/>'
         f'<circle cx="{cx}" cy="{cy - r * 0.1}" r="{r * 0.5}" fill="{glass}" stroke="{OL}" stroke-width="1.5"/>'
         f'<path d="{rr(cx - r * 0.36, cy - r * 0.12, r * 0.72, r * 0.28, r * 0.14)}" fill="{visor}" stroke="{OL}" stroke-width="1.8"/>'
         f'<path d="M{cx - r * 0.38},{cy - r * 0.26} A{r * 0.4},{r * 0.4} 0 0 1 {cx - r * 0.12},{cy - r * 0.5}" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.75"/></g>')
    if dead:
        k = r * 0.32
        g += f'<path d="M{cx - k},{cy - k} L{cx + k},{cy + k} M{cx + k},{cy - k} L{cx - k},{cy + k}" stroke="{OL}" stroke-width="7" stroke-linecap="round"/>' \
             f'<path d="M{cx - k},{cy - k} L{cx + k},{cy + k} M{cx + k},{cy - k} L{cx - k},{cy + k}" stroke="#8D8499" stroke-width="3.5" stroke-linecap="round"/>'
    return clip + g


def megaphone_badge(cx, cy):
    return (f'<circle cx="{cx}" cy="{cy}" r="11" fill="{AMBER}" stroke="{OL}" stroke-width="2.5"/>'
            f'<path d="M{cx - 6},{cy - 2.5} L{cx + 4},{cy - 7} V{cy + 7} L{cx - 6},{cy + 2.5} Z" fill="{OL}"/>'
            f'<path d="M{cx - 7},{cy - 2.5} V{cy + 2.5}" stroke="{OL}" stroke-width="3"/>')


def voted_stamp(x, y):
    body = (f'<path d="{rr(-58, -17, 116, 34, 8)}" fill="none" stroke="{AMBER}" stroke-width="3.5"/>'
            + BUNGEE.path("VOTED", 0, 9, 22, AMBER, "middle", 1))
    return f'<g transform="translate({x},{y}) rotate(-7)" opacity="0.95">{body}</g>'


def mock_svg():
    parts = [tablet_frame()[tablet_frame().index(">") + 1:-6]]
    parts.append(f'<g transform="translate(320,58)">{tablet_title()[tablet_title().index(">") + 1:-6]}</g>')
    # caller line, names colored
    seg = [("Mint", CREW["mint"]), (" reported ", CREAM), ("Tomato", CREW["tomato"])]
    tw = sum(SG7.width(t, 21) for t, _ in seg)
    x = 640 - tw / 2
    for t, c in seg:
        parts.append(SG7.path(t, x, 130, 21, c))
        x += SG7.width(t, 21)
    parts.append(VT.path("NIGHTJAR COMMS // MTG 03", 98, 74, 22, SEAFOAM, extra='opacity="0.75"'))
    parts.append(VT.path("BODY IN GALLEY", 98, 96, 22, SEAFOAM, extra='opacity="0.55"'))
    # chat button + dot
    cb = chat_button()
    parts.append(f'<g transform="translate(1122,62)">{cb[cb.index(">") + 1:-6]}</g>')
    ud = unread_dot()
    parts.append(f'<g transform="translate(1170,56)">{ud[ud.index(">") + 1:-6]}</g>')
    parts.append(f'<path d="M96,141 H1184" stroke="{TEAL}" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round" opacity="0.8"/>')
    players = [("Mint", "caller", "REPORTER"), ("Cobalt", "you", "YOU"),
               ("Sky", "selected", "YOUR PICK?"), ("Grape", "voted", ""),
               ("Mustard", "alive", ""), ("Lime", "voted", ""),
               ("Tangerine", "voted", ""), ("Bubblegum", "disconnected", "DISCONNECTED"),
               ("Cream", "alive", ""), ("Tomato", "eliminated", "FOUND IN GALLEY")]
    for i, (name, st, sub) in enumerate(players):
        px, py = GRID_X[i % 2], GRID_Y0 + GRID_DY * (i // 2)
        g = [plate_body(st, f"m{i}")]
        cx, cy = WELL[0] + PM, WELL[1] + PM
        g.append(portrait(cx, cy, WELL[2] - 3, CREW[name.lower()], st == "eliminated", st == "disconnected"))
        ncol = {"eliminated": "#6E6380", "disconnected": "#9A96A3"}.get(st, AMBER if st == "you" else CREAM)
        ny = PM + (37 if sub else 48)
        g.append(SG7.path(name, PM + 90, ny, 25, ncol))
        if st == "eliminated":
            nw = SG7.width(name, 25)
            g.append(f'<path d="M{PM + 88},{ny - 8} H{PM + 92 + nw}" stroke="#6E6380" stroke-width="3" stroke-linecap="round"/>')
        if sub:
            scol = {"you": AMBER, "caller": AMBER, "selected": SEAFOAM, "eliminated": "#6E6380", "disconnected": "#7E7A88"}[st]
            g.append(VT.path(sub, PM + 90, PM + 62, 22, scol, ls=1))
        sx, sy, sw_, sh = SLOT
        if st == "caller":
            g.append(megaphone_badge(cx + 22, cy + 22))
        if st == "voted":
            g.append(voted_stamp(PM + sx + sw_ / 2, PM + sy + sh / 2))
        if st == "selected":
            for k, kind in enumerate(("cancel", "confirm")):
                vb = vote_btn(kind, 40)
                g.append(f'<g transform="translate({PM + sx + 22 + k * 64},{PM + sy + 7})">{vb[vb.index(">") + 1:-6]}</g>')
        parts.append(f'<g transform="translate({px - PM},{py - PM})">{"".join(g)}</g>')
    # bottom bar
    b = button("idle", 200, 64)[0]
    parts.append(f'<g transform="translate(96,582)">{b[b.index(">") + 1:-6]}</g>')
    parts.append(BUNGEE.path("SKIP VOTE", 196, 622, 22, OL, "middle", 1))
    parts.append(VT.path("PICK A PLATE TO VOTE, OR SKIP", 640, 622, 26, SEAFOAM, "middle", 1, 'opacity="0.85"'))
    for f in (dial_ring(), dial_arc(0.72), dial_center()):
        parts.append(f'<g transform="translate(1116,578) scale(0.6429)">{f[f.index(">") + 1:-6]}</g>')
    parts.append(VT.path("1:42", 1100, 632, 52, AMBER, "end", 1))
    parts.append(SG7.path("VOTING", 1100 - VT.width("1:42", 52, 1) - 12, 625, 19, CREAM, "end", 1))
    return svg(TW, TH, "".join(parts))


# ---------- export ----------
def write(name, content, w, h):
    (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
    cairosvg.svg2png(bytestring=content.encode(), write_to=str(OUT / "png" / f"{name}@1x.png"), output_width=w, output_height=h)
    cairosvg.svg2png(bytestring=content.encode(), write_to=str(OUT / "png" / f"{name}@2x.png"), output_width=2 * w, output_height=2 * h)


def nineslice(img, ins, size, scale=2):
    """Pillow nine-slice used to prove the frames stretch cleanly."""
    l, r, t, b = (int(ins[k] * scale) for k in ("left", "right", "top", "bottom"))
    W, H = img.size
    w, h = size
    out = Image.new("RGBA", size)
    xs, ys = [(0, l, 0, l), (l, W - r, l, w - r), (W - r, W, w - r, w)], [(0, t, 0, t), (t, H - b, t, h - b), (H - b, H, h - b, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if sx1 > sx0 and sy1 > sy0 and dx1 > dx0 and dy1 > dy0:
                out.paste(img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.NEAREST), (dx0, dy0))
    return out


def main():
    (OUT / "png").mkdir(exist_ok=True)
    meta = {"_note": "Insets in px at 1x; multiply by 2 for @2x textures. Phaser: this.add.nineslice(x, y, key, null, w, h, left, right, top, bottom). top/bottom 0 means 3-slice (height fixed)."}
    frames = {
        "panel_crt_lg": crt_panel("lg", 480, 320, 24, 40, 30, 16, 7, (5, 6)),
        "panel_crt_sm": crt_panel("sm", 240, 160, 18, 26, 18, 10, 4.5, (3, 4)),
        "toast_banner": toast(),
        "speech_bubble": bubble(),
        "progress_trough": progress_trough(),
        "chat_drawer": chat_drawer(),
    }
    for st in BTN:
        frames[f"btn_pill_{st}"] = button(st)
    sizes = {}
    for name, (s, ins) in frames.items():
        w, h = (int(v) for v in s.split('width="')[1].split('"')[0:3:2])
        sizes[name] = (w, h)
        write(name, s, w, h)
        meta[name] = {"file": f"{name}.svg", "size": [w, h], "insets": ins}
    meta["btn_pill_idle"]["label"] = {"font": "Bungee", "size": 22, "colors": {k: v[2] for k, v in BTN.items()},
                                      "pressed_offset_y": 3, "note": "label is live text, centered; nudge +3px when pressed"}
    meta["speech_bubble"]["tail_tip"] = [24, 147]
    meta["chat_drawer"]["zones"] = {"title": [16, 8, 328, 40], "messages": [16, 52, 328, 410], "input": [16, 476, 328, 44]}
    meta["panel_crt_lg"]["content"] = [24, 24, 432, 256]
    meta["panel_crt_sm"]["content"] = [18, 18, 204, 116]
    singles = {
        "progress_fill": (progress_fill(), 380, 20),
        "progress_fill_tile": (progress_tile(), 24, 20),
        "timer_dial_ring": (dial_ring(), DIAL, DIAL),
        "timer_dial_arc": (dial_arc(1.0), DIAL, DIAL),
        "timer_dial_center": (dial_center(), DIAL, DIAL),
        "chat_button": (chat_button(), 64, 64),
        "chat_unread_dot": (unread_dot(), 24, 24),
        "btn_vote_confirm": (vote_btn("confirm"), 40, 40),
        "btn_vote_cancel": (vote_btn("cancel"), 40, 40),
        "tablet_frame": (tablet_frame(), TW, TH),
        "tablet_title": (tablet_title(), 640, 56),
    }
    for st in PLATE_STYLE:
        singles[f"plate_{st}"] = (plate_svg(st), PLATE_W + 2 * PM, PLATE_H + 2 * PM)
    for name, (s, w, h) in singles.items():
        sizes[name] = (w, h)
        write(name, s, w, h)
    meta["progress"] = {"fill_offset_in_trough": [10, 10], "fill_max_size": [380, 20],
                        "note": "Crop progress_fill (setCrop) to the progress width, or use progress_fill_tile as a TileSprite with a rounded mask; do not scale the stripes."}
    meta["timer_dial"] = {"layers": ["timer_dial_ring", "timer_dial_arc", "timer_dial_center"], "size": [DIAL, DIAL],
                          "arc": {"cx": 56, "cy": 56, "r": 37, "width": 8, "start_deg": -90, "clockwise": True, "colors": {"discuss": SEAFOAM, "voting": AMBER, "last10s": CORAL}},
                          "note": "Draw the arc with Phaser Graphics (lineStyle 8, arc r 37) between ring and center, or mask timer_dial_arc."}
    meta["vote_plate"] = {"svg_size": [PLATE_W + 2 * PM, PLATE_H + 2 * PM], "body_offset": [PM, PM], "body_size": [PLATE_W, PLATE_H],
                          "portrait_well": {"cx": WELL[0] + PM, "cy": WELL[1] + PM, "r": WELL[2] - 3},
                          "name": {"x": PM + 90, "baseline": PM + 37, "font": "Space Grotesk 700", "size": 25, "sub_baseline": PM + 62, "sub_font": "VT323 22"},
                          "status_area": [SLOT[0] + PM, SLOT[1] + PM, SLOT[2], SLOT[3]],
                          "caller_badge_center": [WELL[0] + PM + 22, WELL[1] + PM + 22],
                          "selected_buttons": {"cancel": [SLOT[0] + PM + 22, SLOT[1] + PM + 7], "confirm": [SLOT[0] + PM + 86, SLOT[1] + PM + 7], "size": 40},
                          "states": list(PLATE_STYLE), "fixed_size": True}
    meta["meeting_tablet"] = {"canvas": [TW, TH], "body": list(TB), "screen": list(SCR),
                              "title": {"file": "tablet_title.svg", "pos": [320, 58]}, "caller_line": {"x": 640, "baseline": 130, "font": "Space Grotesk 700 21", "anchor": "middle"},
                              "chat_button": [1122, 62], "unread_dot": [1170, 56],
                              "plates": [[GRID_X[i % 2] - PM, GRID_Y0 + GRID_DY * (i // 2) - PM] for i in range(10)],
                              "skip_button": [96, 582, 200, 64], "timer_dial": [1116, 578, 72, 72], "timer_text_right": [1100, 632],
                              "slide_in": "place at (0,0); tween y from 720 to 0 (Back.easeOut, ~450 ms) over a 60% #101326 dim layer"}
    (OUT / "nineslice.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # mock
    m = mock_svg()
    (HERE / "meeting_mock.svg").write_text(m, encoding="utf-8")
    cairosvg.svg2png(bytestring=m.encode(), write_to=str(HERE / "_mock_fg.png"), output_width=TW, output_height=TH)
    bg = Image.open(REPO / "art-jobs/refs/01_galley.jpg").convert("RGBA")
    bg = bg.resize((TW, round(bg.height * TW / bg.width)))
    bg = bg.crop((0, 0, TW, TH)) if bg.height >= TH else bg.resize((TW, TH))
    bg = Image.alpha_composite(bg, Image.new("RGBA", (TW, TH), (16, 30, 46, 196)))
    mock = Image.alpha_composite(bg, Image.open(HERE / "_mock_fg.png"))
    mock.convert("RGB").save(OUT / "meeting_mock.png")
    (HERE / "_mock_fg.png").unlink()
    preview(sizes, meta)


def preview(sizes, meta):
    W, H = 1600, 2160
    im = Image.new("RGBA", (W, H), CREAM)
    dr = ImageDraw.Draw(im)
    lab = ImageFont.truetype(str(FONTS / "SpaceGrotesk-700.ttf"), 18)
    head = ImageFont.truetype(str(FONTS / "Bungee-Regular.ttf"), 34)
    btnf = ImageFont.truetype(str(FONTS / "Bungee-Regular.ttf"), 22)

    def put(name, x, y, label=None, scale=1):
        p = Image.open(OUT / "png" / f"{name}@{'2x' if scale == 2 else '1x'}.png").convert("RGBA")
        im.alpha_composite(p, (x, y))
        dr.text((x, y + p.height + 4), label or name, fill=OL, font=lab)
        return p

    dr.text((40, 24), "JOB B  UI FRAMES + MEETING TABLET KIT", fill=OL, font=head)
    put("panel_crt_lg", 40, 90)
    put("panel_crt_sm", 560, 90)
    put("chat_drawer", 1200, 90, "chat_drawer 360x540")
    put("toast_banner", 560, 300)
    put("speech_bubble", 840, 90)
    for i, st in enumerate(BTN):
        p = put(f"btn_pill_{st}", 40 + i * 230, 450, f"btn_pill_{st}")
        col = BTN[st][2]
        dy = 3 if st == "pressed" else 0
        dr.text((40 + i * 230 + 100, 450 + 30 + dy), "VOTE" if st != "danger" else "EJECT", fill=col, font=btnf, anchor="mm")
    put("progress_trough", 40, 560)
    trough = Image.open(OUT / "png" / "progress_trough@1x.png")
    fill = Image.open(OUT / "png" / "progress_fill@1x.png").crop((0, 0, 250, 20))
    t2 = trough.copy()
    t2.alpha_composite(fill, (10, 10))
    im.alpha_composite(t2, (480, 560))
    dr.text((480, 604), "trough + fill cropped to 65%", fill=OL, font=lab)
    put("progress_fill", 40, 640)
    put("progress_fill_tile", 460, 640, "fill_tile")
    x = 40
    for n in ("timer_dial_ring", "timer_dial_arc", "timer_dial_center"):
        put(n, x, 700, n.replace("timer_dial_", "dial "))
        x += 130
    dial = Image.new("RGBA", (DIAL, DIAL))
    for f in (dial_ring(), dial_arc(0.72), dial_center()):
        cairosvg.svg2png(bytestring=f.encode(), write_to=str(HERE / "_t.png"))
        dial.alpha_composite(Image.open(HERE / "_t.png"))
    (HERE / "_t.png").unlink()
    im.alpha_composite(dial, (430, 700))
    dr.text((430, 816), "dial composed", fill=OL, font=lab)
    put("chat_button", 700, 720)
    put("chat_unread_dot", 790, 720, "dot")
    put("btn_vote_confirm", 860, 720, "confirm")
    put("btn_vote_cancel", 950, 720, "cancel")
    # stretch test
    dr.text((40, 860), "NINE-SLICE STRETCH TEST (from nineslice.json insets, @2x textures scaled 0.5)", fill=OL, font=lab)
    x = 40
    for name, sz in (("panel_crt_lg", (1400, 360)), ("panel_crt_sm", (700, 480)), ("toast_banner", (1000, 128)),
                     ("btn_pill_idle", (560, 128)), ("speech_bubble", (900, 300)), ("chat_drawer", (720, 700))):
        src = Image.open(OUT / "png" / f"{name}@2x.png").convert("RGBA")
        st = nineslice(src, meta[name]["insets"], sz).resize((sz[0] // 2, sz[1] // 2), Image.LANCZOS)
        if x + st.width > W - 20:
            x = 40
        pos = {"panel_crt_lg": (40, 890), "panel_crt_sm": (760, 890), "toast_banner": (40, 1270),
               "btn_pill_idle": (580, 1270), "speech_bubble": (40, 1350), "chat_drawer": (1200, 890)}[name]
        im.alpha_composite(st, pos)
    dr.text((40, 1540), "VOTE PLATES (552x94 incl. glow margin)", fill=OL, font=lab)
    for i, st in enumerate(PLATE_STYLE):
        put(f"plate_{st}", 40 + (i % 2) * 580, 1570 + (i // 2) * 130, f"plate_{st}")
    m = Image.open(OUT / "meeting_mock.png").convert("RGBA").resize((400, 225), Image.LANCZOS)
    im.alpha_composite(m, (1180, 1570))
    dr.text((1180, 1800), "meeting_mock.png (1280x720)", fill=OL, font=lab)
    tf = Image.open(OUT / "png" / "tablet_frame@1x.png").convert("RGBA").resize((400, 225), Image.LANCZOS)
    im.alpha_composite(tf, (1180, 1830))
    dr.text((1180, 2058), "tablet_frame (1280x720 canvas)", fill=OL, font=lab)
    tt = Image.open(OUT / "png" / "tablet_title@1x.png").convert("RGBA")
    tt = tt.resize((400, round(tt.height * 400 / tt.width)), Image.LANCZOS)
    bgt = Image.new("RGBA", (tt.width + 16, tt.height + 12), INDIGO)
    bgt.alpha_composite(tt, (8, 6))
    im.alpha_composite(bgt, (600, 2020))
    dr.text((600, 2020 + bgt.height + 4), "tablet_title (on indigo)", fill=OL, font=lab)
    im.convert("RGB").save(OUT / "PREVIEW.png")


if __name__ == "__main__":
    main()
