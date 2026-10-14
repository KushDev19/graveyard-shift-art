"""Job A generator: HUD action buttons, badges and meeting extras for GRAVEYARD SHIFT.
Usage: python art-jobs/out/A_icons/build.py
Writes svg/*.svg, png/*.png and PREVIEW.png next to this file. Needs cairosvg + Pillow."""
import colorsys
import math
import pathlib
import re

import cairosvg
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
SVG_DIR, PNG_DIR = HERE / "svg", HERE / "png"

# palette
O = "#2A1E35"        # outline plum
INDIGO = "#1B1830"
INDIGO_D = "#13102A"
PLUM = "#3D2A4F"
PLUM_L = "#5A4470"
TEAL = "#2F6F73"
TEAL_D = "#245457"
TEAL_L = "#4E9497"
SEA = "#7FC8B8"
SEA_D = "#5BA696"
SEA_L = "#B4E3D8"
AMBER = "#F5A54A"
AMBER_D = "#D9822E"
AMBER_L = "#FFD08A"
CREAM = "#F4E6C8"
CREAM_D = "#D9C29B"
CREAM_L = "#FFF8EA"
CORAL = "#E8574A"
CORAL_D = "#B9392F"
CORAL_L = "#F48C7F"
PINK = "#D9738C"
PINK_D = "#B4566F"
GREY = "#CDCCD4"
GREY_D = "#A3A1AE"
GREY_L = "#ECEBF1"
RIM = "#C9D3E0"
GLASS = "#221D3A"


# ---------- helpers ----------
def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc(cx, cy, r, a0, a1):
    """Clockwise arc (screen coords, 0 deg = right, 90 = down)."""
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}"


def line(color, d, w, ow, cap="round"):
    """A stroked line with a plum outline around it."""
    return (f'<path d="{d}" fill="none" stroke="{O}" stroke-width="{w + 2 * ow}" stroke-linecap="{cap}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"/>')


def shp(d, fill, ow, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{O}" stroke-width="{ow}" stroke-linejoin="round" {extra}/>'


def circ(cx, cy, r, fill, ow=0, extra=""):
    s = f' stroke="{O}" stroke-width="{ow}"' if ow else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s} {extra}/>'


def ell(cx, cy, rx, ry, fill, ow=0, extra=""):
    s = f' stroke="{O}" stroke-width="{ow}"' if ow else ""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"{s} {extra}/>'


def star4(cx, cy, r, fill, ow):
    k = r * 0.22
    d = (f"M{cx} {cy - r} Q{cx + k} {cy - k} {cx + r} {cy} Q{cx + k} {cy + k} {cx} {cy + r} "
         f"Q{cx - k} {cy + k} {cx - r} {cy} Q{cx - k} {cy - k} {cx} {cy - r} Z")
    return shp(d, fill, ow)


def svg_doc(name, size, body, defs=""):
    d = f"<defs>{defs}</defs>" if defs else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
            f'<g id="{name}">{d}{body}</g></svg>')


# ---------- big button base (viewBox 256) ----------
def button_base(danger, uid):
    ring, sh, hi = (CORAL, CORAL_D, CORAL_L) if danger else (CREAM, CREAM_D, CREAM_L)
    screws = "".join(circ(*[round(v, 1) for v in pt(128, 126, 103, a)], 5.5, sh, 3) for a in (45, 135, 225, 315))
    defs = f'<clipPath id="disc_{uid}"><circle cx="128" cy="128" r="80"/></clipPath>'
    body = (
        '<g id="base">'
        f'{circ(128, 135, 120, O)}'                                   # bottom thickness
        f'{circ(128, 128, 116, sh, 8)}'                                # ring shadow + outline
        f'{circ(128, 123, 104, ring)}'                                 # ring face (bevel)
        f'<path d="{arc(128, 123, 96, 200, 255)}" fill="none" stroke="{hi}" stroke-width="8" stroke-linecap="round"/>'
        f'{screws}'
        f'{circ(128, 128, 84, INDIGO_D, 8)}'                           # disc + outline
        f'<g clip-path="url(#disc_{uid})">{circ(128, 140, 82, INDIGO)}'
        f'<path d="{arc(128, 128, 76, 30, 150)}" fill="none" stroke="#2A2548" stroke-width="7" stroke-linecap="round"/></g>'
        '</g>')
    return defs, body


OW = 6  # icon outline in big buttons


def icon_use():
    plate = (shp("M72 172 V180 A56 15 0 0 0 184 180 V172 Z", TEAL_D, OW) +
             ell(128, 172, 56, 15, TEAL, OW) + ell(128, 172, 40, 9, TEAL_D))
    btn = (shp("M96 148 V166 A32 9 0 0 0 160 166 V148 Z", AMBER_D, OW) +
           ell(128, 148, 32, 9, AMBER, OW) +
           f'<path d="M106 146 Q116 141 128 141" fill="none" stroke="{AMBER_L}" stroke-width="5" stroke-linecap="round"/>')
    ticks = (line(AMBER, "M84 140 L72 132", 7, 4) + line(AMBER, "M88 124 L78 112", 7, 4) +
             line(AMBER, "M172 140 L184 132", 7, 4))
    # mitten in local coords: fingers point toward -x, sleeve toward +x
    mit = "M-40 -6 Q-44 -26 -22 -28 H10 Q22 -28 22 -14 V18 Q22 30 8 30 H-24 Q-42 30 -40 10 Z"
    mitten = (
        f'<rect x="18" y="-24" width="70" height="48" rx="8" fill="{GREY}" stroke="{O}" stroke-width="{OW}"/>'
        f'<rect x="18" y="6" width="70" height="18" fill="{GREY_D}"/>'
        f'<rect x="18" y="-24" width="70" height="48" rx="8" fill="none" stroke="{O}" stroke-width="{OW}"/>'
        f'<rect x="14" y="-30" width="18" height="60" rx="7" fill="{GREY_D}" stroke="{O}" stroke-width="{OW}"/>'
        f'<path d="{mit}" fill="{GREY}"/>'
        f'<path d="M-40 8 Q-38 30 -24 30 H8 Q22 30 22 18 V10 Z" fill="{GREY_D}"/>'
        f'<path d="{mit}" fill="none" stroke="{O}" stroke-width="{OW}" stroke-linejoin="round"/>'
        f'<ellipse cx="-6" cy="-30" rx="17" ry="10" transform="rotate(-18 -6 -30)" fill="{GREY}" stroke="{O}" stroke-width="{OW}"/>'
        f'<path d="M-30 -18 Q-26 -22 -18 -22" fill="none" stroke="{GREY_L}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M-24 4 Q-10 8 2 4" fill="none" stroke="{O}" stroke-width="4" stroke-linecap="round"/>'
    )
    return (plate + btn + ticks +
            f'<g clip-path="url(#disc_use)"><g transform="translate(154 100) rotate(-38) scale(1.05)">{mitten}</g></g>')


def megaphone(ow, light=CREAM, shade=CREAM_D):
    """Megaphone pointing right, local coords centered near the horn middle."""
    horn = "M-46 -12 L12 -32 L12 32 L-46 12 Z"
    return (
        f'<rect x="-22" y="6" width="15" height="34" rx="6" transform="rotate(-8 -14 6)" fill="{shade}" stroke="{O}" stroke-width="{ow}"/>'
        f'<rect x="-62" y="-11" width="20" height="22" rx="6" fill="{TEAL}" stroke="{O}" stroke-width="{ow}"/>'
        f'<path d="{horn}" fill="{light}"/>'
        f'<path d="M-46 3 L12 14 L12 32 L-46 12 Z" fill="{shade}"/>'
        f'<path d="M-30 -17 L-20 -21 L-20 21 L-30 17 Z" fill="{AMBER}"/>'
        f'<path d="M-20 -21 L-13 -24 L-13 24 L-20 21 Z" fill="{CORAL}"/>'
        f'<path d="{horn}" fill="none" stroke="{O}" stroke-width="{ow}" stroke-linejoin="round"/>'
        f'<ellipse cx="13" cy="0" rx="11" ry="34" fill="{light}" stroke="{O}" stroke-width="{ow}"/>'
        f'<ellipse cx="15" cy="0" rx="6" ry="26" fill="{PLUM}"/>'
    )


def icon_report():
    waves = "".join(line(AMBER, arc(0, 0, r, -38, 38), 9, 5) for r in (38, 58))
    return f'<g transform="translate(116 132) rotate(-14) scale(1.15)">{megaphone(OW)}<g transform="translate(14 0)">{waves}</g></g>'


def icon_eliminate():
    # deflating balloon (right) with a pop burst where the pin tip touches it
    burst_pts = []
    for i in range(16):
        r = 30 if i % 2 == 0 else 15
        burst_pts.append(pt(140, 112, r, i * 22.5 - 10))
    burst = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in burst_pts) + " Z"
    burst2 = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in
                             [pt(140, 112, (16 if i % 2 == 0 else 8), i * 22.5 - 10) for i in range(16)]) + " Z"
    balloon = ("M168 70 C188 66 200 82 196 100 C194 110 198 116 190 124 C182 132 176 128 168 132 "
               "C158 134 150 124 152 112 C150 100 156 96 154 88 C154 78 160 72 168 70 Z")
    bal = (
        line(CREAM_D, "M174 140 C168 150 180 156 174 166 C170 174 176 178 172 184", 4, 3) +
        shp("M168 130 L178 130 L174 142 Z", PINK_D, 5) +
        shp(balloon, PINK, OW) +
        f'<path d="M188 92 C192 104 186 116 176 124" fill="none" stroke="{PINK_D}" stroke-width="9" stroke-linecap="round"/>'
        f'<path d="{balloon}" fill="none" stroke="{O}" stroke-width="{OW}" stroke-linejoin="round"/>'
        f'<path d="M166 84 Q172 80 178 82" fill="none" stroke="#F3B3C2" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M172 100 Q178 104 176 110 M164 112 Q168 116 166 120" fill="none" stroke="{O}" stroke-width="3.5" stroke-linecap="round"/>'
    )
    puffs = line(CREAM, "M188 70 L194 62", 5, 3) + line(CREAM, "M200 84 L208 81", 5, 3)
    pin = (
        line(GREY, "M84 176 L104 90", 11, 5) +                  # back wire to clasp
        line(GREY, "M84 176 L142 116", 11, 5) +                 # point leg
        f'<path d="M84 176 L104 90" fill="none" stroke="{GREY_L}" stroke-width="3" stroke-linecap="round" transform="translate(-2 0)"/>'
        f'<path d="M140 118 L146 112" fill="none" stroke="{GREY_D}" stroke-width="5" stroke-linecap="round"/>'
        f'{circ(84, 178, 15, GREY, OW)}{circ(84, 178, 6, GREY_D, 4)}'
        f'<rect x="-14" y="-18" width="28" height="36" rx="9" transform="translate(106 84) rotate(13)" fill="{AMBER}" stroke="{O}" stroke-width="{OW}"/>'
        f'<rect x="-6" y="-12" width="12" height="20" rx="4" transform="translate(106 84) rotate(13)" fill="{AMBER_D}"/>'
    )
    return (f'<g transform="translate(128 130) scale(1.08) translate(-138 -126)">'
            + shp(burst, CREAM, OW) + f'<path d="{burst2}" fill="{AMBER}"/>' + bal + puffs + pin + '</g>')


def icon_vent():
    grate = (
        shp("M66 150 L190 150 L202 192 L54 192 Z", TEAL, OW) +
        shp("M78 158 L178 158 L186 184 L70 184 Z", INDIGO, 4) +
        "".join(line(TEAL_L, f"M{76 + i * 1.5:.0f} {163 + i * 6} L{180 - i * 1.5 + i * 3:.0f} {163 + i * 6}", 4, 0) for i in range(4))
    )
    arrow = ("M112 152 V108 H92 L128 62 L164 108 H144 V152 Z")
    arr = (f'<path d="{arrow}" fill="{AMBER}"/>'
           f'<path d="M128 62 L164 108 H144 V152 H128 Z" fill="{AMBER_D}"/>'
           f'<path d="{arrow}" fill="none" stroke="{O}" stroke-width="{OW}" stroke-linejoin="round"/>'
           f'<path d="M118 100 V138" stroke="{AMBER_L}" stroke-width="5" stroke-linecap="round"/>')

    def puff(cx, cy, s):
        parts = [(0, 0, 13), (14, -6, 11), (-13, -3, 10), (4, -14, 9)]
        out = "".join(circ(cx + dx * s, cy + dy * s, r * s, O) for dx, dy, r in [(a, b, c + 3.5) for a, b, c in parts])
        out += "".join(circ(cx + dx * s, cy + dy * s, r * s, CREAM) for dx, dy, r in parts)
        out += circ(cx + 4 * s, cy + 2 * s, 8 * s, CREAM_D)
        return out
    return grate + arr + puff(88, 150, 1.0) + puff(170, 148, 1.05)


def icon_sabotage():
    handle = "M-58 -11 H34 V11 H-58 Z"
    head = "M82 -10 L56 -10 L56 10 L82 10 A27 27 0 1 1 82 -10 Z"
    w = (
        f'<g fill="none" stroke="{O}" stroke-width="{2 * OW}" stroke-linejoin="round">'
        f'<path d="{handle}"/><path d="{head}"/><circle cx="-58" cy="0" r="21"/></g>'
        f'<path d="{handle}" fill="{GREY}"/><path d="{head}" fill="{GREY}"/>{circ(-58, 0, 21, GREY)}'
        f'<path d="M-58 2 H34 V11 H-58 Z" fill="{GREY_D}"/>'
        f'<path d="M-40 -4 H24" stroke="{GREY_L}" stroke-width="4" stroke-linecap="round"/>'
        f'{circ(-58, 0, 9, INDIGO, OW)}'
    )
    sparks = (star4(176, 70, 17, AMBER, 4) + star4(194, 112, 11, CREAM, 4) + star4(150, 56, 9, AMBER_L, 3.5) +
              circ(186, 88, 4.5, AMBER, 3) + circ(160, 76, 3.5, CREAM, 2.5))
    return f'<g transform="translate(118 140) rotate(-42) scale(1.12)">{w}</g>' + sparks


def stripe_base(cx, top, rx, ry, h, ow, uid):
    side = f"M{cx - rx} {top} V{top + h} A{rx} {ry} 0 0 0 {cx + rx} {top + h} V{top} Z"
    bands = "".join(
        f'<path d="M{cx - rx} {top + off} A{rx} {ry} 0 0 0 {cx + rx} {top + off} V{top + h + ry + 4} H{cx - rx} Z" fill="{c}"/>'
        for off, c in ((h * 0.38, AMBER), (h * 0.7, CORAL)))
    return (f'<clipPath id="side_{uid}"><path d="{side}"/></clipPath>'
            f'<path d="{side}" fill="{CREAM}"/><g clip-path="url(#side_{uid})">{bands}</g>'
            f'<path d="{side}" fill="none" stroke="{O}" stroke-width="{ow}" stroke-linejoin="round"/>')


def icon_emergency():
    base = stripe_base(128, 160, 60, 16, 22, OW, "emg") + ell(128, 160, 60, 16, GREY, OW) + ell(128, 160, 50, 11, GREY_D)
    btn = (shp("M90 140 V154 A38 11 0 0 0 166 154 V140 Z", CORAL_D, OW) + ell(128, 140, 38, 12, CORAL, OW) +
           f'<path d="M102 136 Q114 131 128 131" fill="none" stroke="{CORAL_L}" stroke-width="5" stroke-linecap="round"/>')
    dome_d = "M74 158 V116 A54 56 0 0 1 182 116 V158 A54 14 0 0 1 74 158 Z"
    dome = (f'<path d="{dome_d}" fill="#BFE6DC" fill-opacity="0.42"/>'
            f'<path d="{dome_d}" fill="none" stroke="{O}" stroke-width="{OW}" stroke-linejoin="round"/>'
            f'<path d="{arc(128, 116, 42, 200, 250)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M90 120 V138" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="7" stroke-linecap="round"/>'
            f'{circ(156, 84, 5, "#FFFFFF", 0, "fill-opacity=\"0.85\"")}')
    return base + btn + dome


def icon_map():
    xs, ytop, h = (62, 106, 150, 194), (80, 94), 92
    panels, cols = [], (SEA, SEA_D, SEA)
    out = ""
    for i in range(3):
        x0, x1 = xs[i], xs[i + 1]
        y0, y1 = (ytop[0], ytop[1]) if i % 2 == 0 else (ytop[1], ytop[0])
        d = f"M{x0} {y0} L{x1} {y1} L{x1} {y1 + h} L{x0} {y0 + h} Z"
        panels.append(d)
        out += f'<path d="{d}" fill="{cols[i]}"/>'
        # blueprint grid
        for k in (1, 2):
            t = k / 3
            out += f'<path d="M{x0} {y0 + h * t:.1f} L{x1} {y1 + h * t:.1f}" stroke="{SEA_L if i != 1 else SEA}" stroke-width="3"/>'
        out += f'<path d="M{(x0 + x1) / 2} {(y0 + y1) / 2 + 2} V{(y0 + y1) / 2 + h - 2}" stroke="{SEA_L if i != 1 else SEA}" stroke-width="3"/>'
    out += "".join(f'<path d="{d}" fill="none" stroke="{O}" stroke-width="{OW}" stroke-linejoin="round"/>' for d in panels)
    route = "M74 158 Q90 140 100 150 Q112 160 124 138 Q134 120 152 128 Q164 134 170 116"
    out += f'<path d="{route}" fill="none" stroke="{AMBER}" stroke-width="6" stroke-linecap="round" stroke-dasharray="2 11"/>'
    # pin marker
    out += shp("M172 116 C160 102 160 86 172 84 C184 86 184 102 172 116 Z", CORAL, 5) + circ(172, 96, 5, CREAM, 3)
    out += circ(74, 158, 6, AMBER, 4)
    return out


def icon_chat():
    bub = "M64 70 H192 Q206 70 206 84 V144 Q206 158 192 158 H112 L80 188 L88 158 H64 Q50 158 50 144 V84 Q50 70 64 70 Z"
    return (f'<path d="{bub}" fill="{CREAM}"/>'
            f'<path d="M50 136 V144 Q50 158 64 158 H88 L84 174 L112 158 H192 Q206 158 206 144 V136 Z" fill="{CREAM_D}"/>'
            f'<path d="{bub}" fill="none" stroke="{O}" stroke-width="{OW}" stroke-linejoin="round"/>'
            f'<path d="M66 84 H120" stroke="{CREAM_L}" stroke-width="6" stroke-linecap="round"/>'
            + "".join(circ(x, 114, 13, AMBER, 5) + f'<path d="{arc(x, 114, 7, 200, 260)}" fill="none" stroke="{AMBER_L}" stroke-width="4" stroke-linecap="round"/>'
                      for x in (92, 128, 164)))


BUTTONS = [
    ("btn_use", False, icon_use),
    ("btn_report", False, icon_report),
    ("btn_eliminate", True, icon_eliminate),
    ("btn_vent", True, icon_vent),
    ("btn_sabotage", True, icon_sabotage),
    ("btn_emergency", False, icon_emergency),
    ("btn_map", False, icon_map),
    ("btn_chat", False, icon_chat),
]


def build_button(name, danger, fn):
    uid = name.split("_", 1)[1]
    defs, base = button_base(danger, uid)
    icon = fn()
    return svg_doc(name, 256, base + f'<g id="icon">{icon}</g>', defs)


# ---------- badges (viewBox 128, outline 5) ----------
BW = 5


def helmet(cx, cy, r, visor=AMBER, visor_d=AMBER_D, antenna=GREY, glass=GLASS):
    vw, vh = r * 1.22, r * 0.82
    return (
        line(GREY_D, f"M{cx} {cy - r + 2} Q{cx} {cy - r - 10} {cx + 4} {cy - r - 16}", 3.5, 3) +
        circ(cx + 4, cy - r - 17, 5.5, antenna, 3.5) +
        ell(cx, cy - r + 1, 8, 5, antenna, 3.5) +
        circ(cx, cy, r, RIM, BW) + circ(cx, cy, r - 5, glass) +
        f'<rect x="{cx - vw / 2:.1f}" y="{cy - vh / 2 - 1:.1f}" width="{vw:.1f}" height="{vh:.1f}" rx="{r * 0.34:.1f}" fill="{visor}" stroke="{visor_d}" stroke-width="3.5"/>'
        f'<path d="M{cx - vw / 2 + 6:.1f} {cy - vh / 2 + 6:.1f} H{cx - 2:.1f}" stroke="{AMBER_L if visor == AMBER else GREY_L}" stroke-width="3.5" stroke-linecap="round"/>'
        f'<path d="{arc(cx, cy, r - 10, 200, 245)}" fill="none" stroke="#E7E4F6" stroke-width="5" stroke-linecap="round"/>'
        + circ(round(cx - r * 0.42, 1), round(cy - r * 0.15, 1), 2.6, "#E7E4F6")
    )


def b_crown():
    body = "M22 92 L16 42 L42 62 L64 30 L86 62 L112 42 L106 92 Z"
    return (f'<path d="{body}" fill="{AMBER}"/><path d="M64 30 L86 62 L112 42 L106 92 H64 Z" fill="{AMBER_D}"/>'
            f'<path d="{body}" fill="none" stroke="{O}" stroke-width="{BW}" stroke-linejoin="round"/>'
            f'<rect x="18" y="84" width="92" height="22" rx="7" fill="{AMBER_D}" stroke="{O}" stroke-width="{BW}"/>'
            f'<path d="M26 90 H70" stroke="{AMBER}" stroke-width="4" stroke-linecap="round"/>'
            + circ(16, 42, 7, AMBER_L, 4) + circ(64, 28, 8, AMBER_L, 4) + circ(112, 42, 7, AMBER_L, 4)
            + "".join(shp(f"M{x} 86 L{x + 9} 95 L{x} 104 L{x - 9} 95 Z", CREAM, 3.5) for x in (38, 64, 90))
            + "".join(f'<path d="M{x - 3} 93 L{x} 90" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>' for x in (38, 64, 90)))


def b_voted():
    check = "M38 66 L56 84 L92 46"
    return (f'<g transform="rotate(-12 64 64)">'
            + circ(64, 66, 52, CORAL_D, BW) + circ(64, 62, 48, CORAL)
            + f'<circle cx="64" cy="62" r="38" fill="none" stroke="{CREAM}" stroke-width="4" stroke-dasharray="10 6"/>'
            + line(CREAM, check, 13, 5) + '</g>')


def b_skip():
    a = "M26 88 Q36 34 64 34 Q90 34 98 72"
    return (circ(64, 66, 54, CREAM_D, BW) + circ(64, 62, 50, CREAM)
            + line(PLUM, "M64 66 V98", 9, 4) + line(PLUM, "M40 100 H88", 7, 4)
            + line(AMBER, a, 11, 5)
            + shp("M86 70 L108 66 L102 88 Z", AMBER, 4.5))


def b_ghost():
    tail = ("M24 58 C22 86 32 100 46 108 C58 114 72 112 84 118 C94 123 104 121 112 112 "
            "C102 114 96 108 98 98 C100 90 104 84 104 72 L104 58 Z")
    return (f'<path d="{tail}" fill="{SEA}" stroke="{O}" stroke-width="{BW}" stroke-linejoin="round"/>'
            f'<path d="M84 64 C90 86 82 100 70 106" fill="none" stroke="{SEA_D}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M48 98 Q56 104 66 104" fill="none" stroke="{SEA_L}" stroke-width="4" stroke-linecap="round"/>'
            + helmet(64, 58, 36, visor=SEA_L, visor_d=SEA_D, antenna=SEA, glass="#3B7570"))


def b_caller():
    return (circ(64, 66, 54, AMBER_D, BW) + circ(64, 62, 50, AMBER) + circ(64, 64, 38, INDIGO, BW)
            + f'<g transform="translate(60 66) rotate(-14) scale(0.62)">{megaphone(7)}</g>')


def tape(angle):
    d = "M-40 -8 L40 -8 L36 -4 L40 0 L36 4 L40 8 L-40 8 L-36 4 L-40 0 L-36 -4 Z"
    return (f'<g transform="translate(64 68) rotate({angle})">{shp(d, "#7A6296", 4)}'
            f'<path d="M-34 -2.5 H34" stroke="#A48CBE" stroke-width="3" stroke-linecap="round"/></g>')


def b_eliminated():
    return helmet(64, 70, 42, visor=AMBER_D, visor_d="#B66A22") + tape(32) + tape(-32)


def b_settings():
    pts = []
    n = 8
    for i in range(n):
        base = i * 360 / n
        for off, r in ((-15, 40), (-9, 52), (9, 52), (15, 40)):
            pts.append(pt(64, 64, r, base + off))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    return (f'<clipPath id="gearclip"><path d="{d}"/></clipPath>'
            f'<path d="{d}" fill="{CREAM}"/><g clip-path="url(#gearclip)">{circ(78, 80, 52, CREAM_D)}</g>'
            f'<path d="{d}" fill="none" stroke="{O}" stroke-width="{BW}" stroke-linejoin="round"/>'
            + circ(64, 64, 28, CREAM, BW) + circ(64, 64, 13, PLUM, BW)
            + f'<path d="{arc(64, 64, 21, 200, 250)}" fill="none" stroke="{CREAM_L}" stroke-width="4" stroke-linecap="round"/>')


def b_leave():
    door = "M25 25 L54 33 L54 100 L25 107 Z"
    return (f'<rect x="14" y="14" width="70" height="104" rx="10" fill="{CREAM}" stroke="{O}" stroke-width="{BW}"/>'
            f'<rect x="14" y="100" width="70" height="18" rx="8" fill="{CREAM_D}"/>'
            f'<rect x="14" y="14" width="70" height="104" rx="10" fill="none" stroke="{O}" stroke-width="{BW}"/>'
            f'<rect x="25" y="25" width="48" height="82" rx="5" fill="{INDIGO}" stroke="{O}" stroke-width="3"/>'
            f'<path d="{door}" fill="{TEAL}"/><path d="M42 30 L54 33 L54 100 L42 103 Z" fill="{TEAL_D}"/>'
            f'<path d="{door}" fill="none" stroke="{O}" stroke-width="{BW}" stroke-linejoin="round"/>'
            f'<path d="M31 37 L46 41 V53 L31 51 Z" fill="{SEA}" stroke="{O}" stroke-width="3" stroke-linejoin="round"/>'
            + circ(46, 70, 4, AMBER, 3)
            + shp("M50 56 H82 V40 L114 66 L82 92 V76 H50 Z", AMBER, BW)
            + f'<path d="M82 76 H50 V68 H104 L82 86 Z" fill="{AMBER_D}"/>'
            + f'<path d="M50 56 H82 V40 L114 66 L82 92 V76 H50 Z" fill="none" stroke="{O}" stroke-width="{BW}" stroke-linejoin="round"/>')


def b_mic(muted):
    capsule = '<rect x="44" y="12" width="40" height="66" rx="20"'
    out = (line(GREY, "M30 54 Q30 92 64 92 Q98 92 98 54", 7, 4.5)
           + line(GREY, "M64 92 V108", 7, 4.5)
           + f'<rect x="40" y="104" width="48" height="12" rx="6" fill="{GREY_D}" stroke="{O}" stroke-width="{BW}"/>'
           + f'{capsule} fill="{CREAM}" stroke="{O}" stroke-width="{BW}"/>'
           + f'<path d="M74 22 Q80 30 80 44 V58 Q80 72 66 74" fill="none" stroke="{CREAM_D}" stroke-width="7" stroke-linecap="round"/>'
           + f'{capsule} fill="none" stroke="{O}" stroke-width="{BW}"/>'
           + "".join(f'<path d="M54 {y} H74" stroke="{PLUM}" stroke-width="4" stroke-linecap="round"/>' for y in (28, 38, 48))
           + f'<rect x="44" y="58" width="40" height="8" fill="{AMBER}" stroke="{O}" stroke-width="3.5"/>')
    if muted:
        out += line(CORAL, "M20 20 L108 108", 11, 5)
    else:
        out += (line(SEA, arc(64, 44, 50, -30, 20), 5, 3.5) + line(SEA, arc(64, 44, 50, 160, 210), 5, 3.5))
    return out


def b_task_done():
    return (circ(64, 66, 54, SEA_D, BW) + circ(64, 62, 50, SEA)
            + f'<path d="{arc(64, 62, 42, 200, 250)}" fill="none" stroke="{SEA_L}" stroke-width="6" stroke-linecap="round"/>'
            + line(CREAM, "M36 64 L56 84 L94 44", 15, 5))


def b_warning():
    tri = "M64 20 L112 104 L16 104 Z"
    return (f'<path d="{tri}" fill="{O}" stroke="{O}" stroke-width="{18 + 2 * BW}" stroke-linejoin="round"/>'
            f'<path d="{tri}" fill="{AMBER}" stroke="{AMBER}" stroke-width="18" stroke-linejoin="round"/>'
            f'<path d="M64 20 L112 104 L64 104 Z" fill="{AMBER_D}" stroke="{AMBER_D}" stroke-width="18" stroke-linejoin="round" clip-path="url(#warnclip)"/>'
            f'<clipPath id="warnclip"><path d="M64 0 H128 V128 H64 Z"/></clipPath>'
            f'<path d="M64 46 V78" stroke="{PLUM}" stroke-width="14" stroke-linecap="round"/>'
            + circ(64, 98, 8, PLUM))


def b_disconnected():
    plug = (f'<g transform="translate(44 82) rotate(-35)">'
            + line(GREY, "M-14 0 C-22 0 -24 8 -30 10", 8, 4.5)
            + line(GREY_D, "M14 -9 H30 M14 9 H30", 6, 3.5)
            + f'<rect x="-16" y="-17" width="32" height="34" rx="8" fill="{CREAM}" stroke="{O}" stroke-width="{BW}"/>'
            + f'<rect x="2" y="-13" width="10" height="26" rx="3" fill="{CREAM_D}"/></g>')
    sock = (f'<g transform="translate(88 44) rotate(-35) scale(0.75)">'
            f'<rect x="-14" y="-24" width="30" height="48" rx="9" fill="{TEAL}" stroke="{O}" stroke-width="{BW}"/>'
            + circ(-3, -9, 4, INDIGO) + circ(-3, 9, 4, INDIGO) + '</g>')
    zap = shp("M62 50 L74 60 L66 64 L78 78 L58 66 L67 62 Z", AMBER, 3.5)
    return (circ(64, 66, 54, PLUM, BW) + circ(64, 62, 50, PLUM_L)
            + '<clipPath id="dcclip"><circle cx="64" cy="62" r="48"/></clipPath>'
            + f'<g clip-path="url(#dcclip)">{plug}</g>' + sock + zap)


def s_confirm():
    return (circ(48, 51, 42, O) + circ(48, 48, 41, SEA_D, 5) + circ(48, 45, 36, SEA)
            + line(CREAM, "M30 48 L43 61 L67 36", 10, 4))


def s_cancel():
    return (circ(48, 51, 42, O) + circ(48, 48, 41, CORAL_D, 5) + circ(48, 45, 36, CORAL)
            + line(CREAM, "M34 31 L62 59 M62 31 L34 59", 10, 4))


def s_dot():
    return circ(16, 16, 11, CORAL, 3.5) + circ(12.5, 12.5, 3, CORAL_L)


def helmet_front():
    suit = "var(--suit, #CDCCD4)"
    shade = f'fill="{O}" fill-opacity="0.22"'
    body = "M22 122 C22 102 40 92 64 92 C88 92 106 102 106 122 Q106 126 102 126 H26 Q22 126 22 122 Z"
    return (
        f'<g id="body"><path d="{body}" fill="{suit}"/>'
        f'<path d="M84 96 C98 102 106 110 106 122 Q106 126 102 126 H80 Z" {shade}/>'
        f'<path d="{body}" fill="none" stroke="{O}" stroke-width="{BW}" stroke-linejoin="round"/>'
        f'<rect x="56" y="100" width="16" height="20" rx="3" fill="{CREAM}" stroke="{O}" stroke-width="3"/>'
        f'<rect x="61" y="101.5" width="5" height="17" fill="{AMBER}"/><rect x="66" y="101.5" width="4.5" height="17" fill="{CORAL}"/></g>'
        f'<g id="collar"><ellipse cx="64" cy="92" rx="38" ry="9" fill="{suit}" stroke="{O}" stroke-width="{BW}"/>'
        f'<ellipse cx="64" cy="95" rx="30" ry="4" {shade}/></g>'
        f'<g id="head">{helmet(64, 54, 37, antenna=suit)}</g>'
    )


BADGES = [
    ("badge_host_crown", b_crown), ("badge_voted_stamp", b_voted), ("badge_skip", b_skip),
    ("badge_ghost", b_ghost), ("badge_caller", b_caller), ("badge_eliminated", b_eliminated),
    ("badge_settings", b_settings), ("badge_leave", b_leave), ("badge_mic_on", lambda: b_mic(False)),
    ("badge_mic_muted", lambda: b_mic(True)), ("badge_task_done", b_task_done), ("badge_warning", b_warning),
    ("badge_disconnected", b_disconnected),
]


def cooldown_ring():
    c = 2 * math.pi * 100
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">'
        '<g id="cooldown_ring">'
        f'<g id="track"><circle cx="128" cy="128" r="100" fill="none" stroke="{O}" stroke-width="30" stroke-opacity="0.72"/></g>'
        f'<g id="arc"><circle id="arc_stroke" cx="128" cy="128" r="100" fill="none" stroke="{AMBER}" stroke-width="16" '
        f'stroke-linecap="round" stroke-dasharray="{c:.2f} {c:.2f}" stroke-dashoffset="{c * 0.35:.2f}" '
        'transform="rotate(-90 128 128)"/></g>'
        '</g></svg>')


# ---------- disabled variant ----------
def disable_color(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s *= 0.12
    l = 0.16 + l * 0.52
    r, g, b = colorsys.hls_to_rgb(0.72, l, s + 0.05)  # cool plum-grey tint keeps it in palette
    return "#{:02X}{:02X}{:02X}".format(*(round(v * 255) for v in (r, g, b)))


def make_disabled(svg):
    svg = re.sub(r"#[0-9A-Fa-f]{6}\b", lambda m: disable_color(m.group(0)), svg)
    return svg.replace('stroke-opacity="0.85"', 'stroke-opacity="0.35"').replace('fill-opacity="0.85"', 'fill-opacity="0.35"')


def no_vars(svg):
    return re.sub(r"var\(--[\w-]+,\s*(#[0-9A-Fa-f]{3,6})\)", r"\1", svg)


def write(name, svg, sizes):
    (SVG_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
    for s in sizes:
        suffix = f"@{s}" if len(sizes) > 1 else ""
        cairosvg.svg2png(bytestring=no_vars(svg).encode(), write_to=str(PNG_DIR / f"{name}{suffix}.png"),
                         output_width=s, output_height=s)


def main():
    SVG_DIR.mkdir(exist_ok=True)
    PNG_DIR.mkdir(exist_ok=True)
    for name, danger, fn in BUTTONS:
        svg = build_button(name, danger, fn)
        write(name, svg, (192, 256))
        write(f"{name}_disabled", make_disabled(svg), (192, 256))
    for name, fn in BADGES:
        write(name, svg_doc(name, 128, fn()), (128,))
    write("btn_confirm", svg_doc("btn_confirm", 96, s_confirm()), (96,))
    write("btn_cancel", svg_doc("btn_cancel", 96, s_cancel()), (96,))
    write("dot_unread", svg_doc("dot_unread", 32, s_dot()), (32,))
    write("icon_helmet_front", svg_doc("icon_helmet_front", 128, helmet_front()), (128, 64, 32))
    write("cooldown_ring", cooldown_ring(), (192, 256))
    preview()


def preview():
    items = ([(n, f"{n}@192.png") for n, _, _ in BUTTONS] +
             [(f"{n}_disabled", f"{n}_disabled@192.png") for n, _, _ in BUTTONS] +
             [(n, f"{n}.png") for n, _ in BADGES] +
             [("btn_confirm", "btn_confirm.png"), ("btn_cancel", "btn_cancel.png"), ("dot_unread", "dot_unread.png"),
              ("icon_helmet_front", "icon_helmet_front@128.png"), ("cooldown_ring (35%)", "cooldown_ring@192.png")])
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = big = ImageFont.load_default()
    cols, cw, ch = 8, 230, 250
    rows = math.ceil(len(items) / cols)
    W, H = cols * cw + 40, rows * ch + 330
    im = Image.new("RGBA", (W, H), CREAM)
    dr = ImageDraw.Draw(im)
    dr.text((20, 14), "GRAVEYARD SHIFT  Job A: HUD buttons + badges (2x exports)", fill=O, font=big)
    for i, (label, fn) in enumerate(items):
        x, y = 20 + (i % cols) * cw, 56 + (i // cols) * ch
        p = Image.open(PNG_DIR / fn).convert("RGBA")
        im.alpha_composite(p, (x + (cw - p.width) // 2, y + (200 - p.height) // 2))
        tw = dr.textlength(label, font=font)
        dr.text((x + (cw - tw) / 2, y + 208), label, fill=O, font=font)
    # display-size strip on a dark HUD background
    y0 = 56 + rows * ch + 10
    dr.rounded_rectangle((20, y0, W - 20, H - 20), 18, fill=INDIGO)
    dr.text((36, y0 + 10), "actual display size (96 / 64 / 48 / 32 px) on the dark HUD", fill=CREAM, font=font)
    x = 36
    strip = ([(f"{n}@192.png", 96) for n, _, _ in BUTTONS] + [(f"{n}.png", 64) for n, _ in BADGES] +
             [("btn_confirm.png", 48), ("btn_cancel.png", 48), ("icon_helmet_front@64.png", 32), ("dot_unread.png", 16)])
    yy = y0 + 40
    for fn, s in strip:
        p = Image.open(PNG_DIR / fn).convert("RGBA").resize((s, s), Image.LANCZOS)
        if x + s > W - 36:
            x, yy = 36, yy + 112
        im.alpha_composite(p, (x, yy + (96 - s) // 2))
        x += s + 14
    im.convert("RGB").save(HERE / "PREVIEW.png")


if __name__ == "__main__":
    main()
