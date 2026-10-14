"""Door SVG builder (front bulkhead door + side-wall slab). Units = pixels of the 5504 px room paintings."""
OL = '#2A1E35'
FW, FH = 860, 900                      # front canvas
OX0, OX1, OY0, OY1, ORAD = 140, 720, 200, 860, 100   # doorway opening
SEAM, SLIDE = 430, 330
SKEW = (0.24, -0.5)                    # side wall: x = 0.24u, y = v - 0.5u (left wall, receding to the right)
DEPTH = 36                             # side slab thickness (screen px)
SW, SH = 260, 1340                     # side canvas
STX, STY = 8, 0.5 * FW + 20


def rt(x0, y0, x1, y1, r):
    return f'M{x0},{y1}V{y0 + r}A{r},{r} 0 0,1 {x0 + r},{y0}H{x1 - r}A{r},{r} 0 0,1 {x1},{y0 + r}V{y1}Z'


OPEN_D = rt(OX0, OY0, OX1, OY1, ORAD)
LEFT_D = (f'M60,150H{SEAM}V470H{SEAM + 30}Q{SEAM + 40},470 {SEAM + 40},478V582Q{SEAM + 40},590 {SEAM + 30},590'
          f'H{SEAM}V900H60Z')
RIGHT_D = (f'M{SEAM},150H800V900H{SEAM}V590H{SEAM + 30}Q{SEAM + 40},590 {SEAM + 40},582V478'
           f'Q{SEAM + 40},470 {SEAM + 30},470H{SEAM}Z')


def defs(P):
    return f'''<defs>
<clipPath id="{P}open"><path d="{OPEN_D}"/></clipPath>
<clipPath id="{P}hzL"><rect x="140" y="752" width="290" height="62"/></clipPath>
<clipPath id="{P}hzR"><rect x="430" y="752" width="290" height="62"/></clipPath>
<radialGradient id="{P}lamp"><stop offset="0" stop-color="#FFC870" stop-opacity=".75"/><stop offset="1" stop-color="#F5A54A" stop-opacity="0"/></radialGradient>
</defs>'''


def hazard(P, side, x0):
    stripes = ''.join(f'<path d="M{x},814L{x + 28},814L{x + 90},752L{x + 62},752Z" fill="#3D2A4F"/>'
                      for x in range(x0 - 80, x0 + 320, 56))
    return (f'<g clip-path="url(#{P}hz{side})"><rect x="{x0}" y="752" width="290" height="62" fill="#F2B33D"/>{stripes}</g>'
            f'<rect x="{x0}" y="752" width="290" height="62" fill="none" stroke="{OL}" stroke-width="5"/>')


def half(P, side):
    left = side == 'L'
    d = LEFT_D if left else RIGHT_D
    x0 = 140 if left else 430
    ins = (175, 395) if left else (465, 685)
    rivx = (160, 410) if left else (450, 700)
    groove = 398 if left else 488
    riv = ''.join(f'<circle cx="{x}" cy="{y}" r="6" fill="#B9CFCE" stroke="{OL}" stroke-width="3"/>'
                  for x in rivx for y in (232, 720))
    gid = 'door_left' if left else 'door_right'
    return f'''<g id="{gid}" data-slide="{-SLIDE if left else SLIDE},0">
<path d="{d}" fill="#93B2B2"/>
<rect x="{x0}" y="640" width="290" height="100" fill="#7C9D9E"/>
<rect x="{ins[0]}" y="262" width="{ins[1] - ins[0]}" height="330" rx="22" fill="#86A6A7" stroke="#5E8285" stroke-width="5"/>
<rect x="{ins[0] + 12}" y="274" width="{ins[1] - ins[0] - 24}" height="20" rx="10" fill="#B4CDCC"/>
<rect x="{groove - 7}" y="330" width="14" height="190" rx="7" fill="#5E8285" stroke="{OL}" stroke-width="3"/>
<rect x="{x0}" y="628" width="290" height="14" fill="#B4CDCC"/>
{hazard(P, side, x0)}
{riv}
<path d="{d}" fill="none" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>
</g>'''


def doorway():
    return f'''<g id="doorway">
<path d="{OPEN_D}" fill="#1B1830"/>
<path d="M{OX0},{OY1}L230,700H630L{OX1},{OY1}Z" fill="#2E2645"/>
<path d="M230,700V300Q230,280 250,280H610Q630,280 630,300V700" fill="#241E3A"/>
<path d="M250,700H610" stroke="#7FC8B8" stroke-width="4" opacity=".35"/>
<path d="M{OX0},{OY1}L230,700M{OX1},{OY1}L630,700" stroke="#3D2A4F" stroke-width="4"/>
</g>'''


def frame(P, lamp=True):
    outer = rt(60, 120, 800, 872, 170)
    bolts = ''.join(f'<circle cx="{x}" cy="{y}" r="8" fill="#B9CFCE" stroke="{OL}" stroke-width="3.5"/>'
                    for x, y in [(96, 330), (96, 560), (96, 790), (764, 330), (764, 790), (250, 150), (610, 150)])
    lp = ''
    if lamp:
        lp = f'''<g id="lamp" data-pivot="430,110">
<circle cx="430" cy="100" r="84" fill="url(#{P}lamp)"/>
<rect x="388" y="98" width="84" height="24" rx="8" fill="#5A7F82" stroke="{OL}" stroke-width="5"/>
<path d="M398,100A32,34 0 0,1 462,100Z" fill="#F5A54A" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>
<path d="M440,72A32,34 0 0,1 462,100H446Z" fill="#D9853A"/>
<path d="M410,92A22,24 0 0,1 424,74" fill="none" stroke="#FFE7B8" stroke-width="6" stroke-linecap="round"/>
</g>'''
    return f'''<g id="frame">
<path d="{outer} {OPEN_D}" fill="#7FA3A4" fill-rule="evenodd"/>
<path d="{rt(OX0 - 26, OY0 - 26, OX1 + 26, OY1, ORAD + 26)} {OPEN_D}" fill="#5A7F82" fill-rule="evenodd"/>
<path d="M60,872V290A170,170 0 0,1 230,120H430V146H232A146,146 0 0,0 86,292V872Z" fill="#9DBCBC"/>
<path d="M800,872V290A170,170 0 0,0 630,120H430V146H628A146,146 0 0,1 774,292V872Z" fill="#668C8E"/>
{bolts}
<rect x="742" y="470" width="44" height="78" rx="8" fill="#F4E6C8" stroke="{OL}" stroke-width="4"/>
<circle cx="764" cy="492" r="8" fill="#7FC8B8" stroke="{OL}" stroke-width="3"/>
<circle cx="764" cy="524" r="8" fill="#F5A54A" stroke="{OL}" stroke-width="3"/>
<path d="{outer} {OPEN_D}" fill="none" stroke="{OL}" stroke-width="8" stroke-linejoin="round"/>
<path d="{rt(OX0 - 26, OY0 - 26, OX1 + 26, OY1, ORAD + 26)}" fill="none" stroke="{OL}" stroke-width="4" opacity=".55"/>
<rect x="44" y="860" width="772" height="28" rx="6" fill="#4D6C70" stroke="{OL}" stroke-width="6"/>
{lp}
</g>'''


def front_body(P, opened, only=None):
    """Draw order: doorway, halves (clipped to opening), frame."""
    s = 1 if opened else 0
    parts = {
        'doorway': doorway(),
        'halves': (f'<g id="halves" clip-path="url(#{P}open)">'
                   f'<g transform="translate({-SLIDE * s},0)">{half(P, "L")}</g>'
                   f'<g transform="translate({SLIDE * s},0)">{half(P, "R")}</g></g>'),
        'door_left': half(P, 'L'), 'door_right': half(P, 'R'),
        'frame': frame(P),
    }
    keys = only or ['doorway', 'halves', 'frame']
    return '\n'.join(parts[k] for k in keys)


def svg_front(opened, only=None, P='df'):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {FW} {FH}" width="{FW}" height="{FH}" id="door_front">'
            f'{defs(P)}\n{front_body(P, opened, only)}\n</svg>')


def side_body(P, opened, only=None):
    a, b = SKEW
    m = f'matrix({a},{b},0,1,{STX},{STY})'
    outer = rt(60, 120, 800, 888, 170)
    ext = ''.join(f'<path d="{outer}" transform="translate({-DEPTH + i},0) {m}" fill="#466A6E"/>' for i in range(0, DEPTH, 3))
    ext += f'<path d="{outer}" transform="translate({-DEPTH},0) {m}" fill="none" stroke="{OL}" stroke-width="7"/>'
    keys = only or ['slab', 'doorway', 'halves', 'frame']
    body = {
        'slab': f'<g id="slab">{ext}</g>',
        'doorway': f'<g transform="{m}">{doorway()}</g>',
        'halves': (f'<g transform="{m}"><g id="halves" clip-path="url(#{P}open)">'
                   f'<g transform="translate({-SLIDE * opened},0)">{half(P, "L")}</g>'
                   f'<g transform="translate({SLIDE * opened},0)">{half(P, "R")}</g></g></g>'),
        'door_left': f'<g transform="{m}">{half(P, "L")}</g>',
        'door_right': f'<g transform="{m}">{half(P, "R")}</g>',
        'frame': f'<g transform="{m}">{frame(P, lamp=True)}</g>',
    }
    return '\n'.join(body[k] for k in keys)


def svg_side(opened, only=None, P='ds', mirror=False):
    inner = side_body(P, 1 if opened else 0, only)
    if mirror:
        inner = f'<g transform="translate({SW},0) scale(-1,1)">{inner}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SW} {SH}" width="{SW}" height="{SH}" id="door_side">'
            f'{defs(P)}\n{inner}\n</svg>')


def side_pt(u, v):
    a, b = SKEW
    return [round(a * u + STX, 1), round(b * u + v + STY, 1)]
