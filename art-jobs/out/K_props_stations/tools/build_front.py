"""Job K: *_front versions. Each *_orig SVG is re-projected with a piecewise-affine mesh: the corners of every
face of the iso drawing (front, top, side, read off the source sheet) are moved to a front-facing 3/4 layout
like the room furniture (front face flat, top seen as a band, the side as a narrow strip). All layers and
state groups keep their ids; only coordinates change. Points outside the mesh follow the nearest face by
translation, so beacons and outline thickness keep their shape.
Run from this folder: python build_front.py [name ...]"""
import re, sys, json
import numpy as np
from PIL import Image
from svgcheck import render_rgba

OUT = __file__.rsplit('/tools/', 1)[0]


def T(origin, s, xoff=0):
    """tile (grid screenshot) coords -> source coords"""
    ox, oy = origin
    return lambda p: (ox + (p[0] - xoff) / s, oy + p[1] / s)


# Each mesh: (src_pts, dst_pts, triangles). Points in grid-tile units, converted with the same T for src and dst.
MESHES = {
    'station_keypad': dict(t=T((236, 11), 0.6), pts={
        'BLb': ((28, 495), (28, 600)), 'Nb': ((343, 600), (360, 600)), 'Rb': ((556, 495), (400, 565)),
        'BLt': ((28, 335), (28, 440)), 'Nt': ((343, 440), (360, 440)),
        'KL': ((130, 205), (28, 320)), 'KR': ((440, 300), (360, 320)),
        'SL': ((160, 58), (28, 170)), 'SR': ((470, 150), (360, 170)),
        'TL': ((250, 25), (50, 118)), 'TR': ((556, 125), (400, 118))},
        tris=['BLb Nb Nt', 'BLb Nt BLt', 'BLt Nt KR', 'BLt KR KL', 'KL KR SR', 'KL SR SL', 'SL SR TR', 'SL TR TL',
              'Nb Rb Nt', 'Nt Rb KR', 'KR Rb TR', 'KR TR SR']),
    'station_switchboard': dict(t=T((178, 1037), 0.7), pts={
        'BLb': ((45, 540), (45, 690)), 'Nb': ((470, 690), (496, 690)), 'Rb': ((700, 558), (536, 571)),
        'BLt': ((45, 395), (45, 548)), 'Nt': ((470, 548), (496, 548)),
        'DL': ((150, 300), (66, 485)), 'DR': ((585, 440), (517, 485)),
        'PL': ((150, 48), (66, 233)), 'PR': ((595, 185), (517, 233)),
        'TB': ((255, 33), (85, 177)), 'TR': ((700, 170), (536, 177))},
        tris=['BLb Nb Nt', 'BLb Nt BLt', 'BLt Nt DR', 'BLt DR DL', 'DL DR PR', 'DL PR PL', 'PL PR TR', 'PL TR TB',
              'Nb Rb Nt', 'Nt Rb DR', 'DR Rb TR', 'DR TR PR']),
    'station_tape': dict(t=T((170, 2048), 0.6), pts={
        'A': ((25, 322), (25, 440)), 'B': ((410, 440), (429, 440)), 'C': ((25, 258), (25, 382)),
        'D': ((410, 382), (429, 382)), 'E': ((232, 22), (63, 240)), 'F': ((617, 145), (467, 240)),
        'G': ((617, 292), (467, 298)), 'H': ((75, 492), (60, 595)), 'I': ((412, 597), (429, 595)),
        'J': ((580, 482), (467, 453))},
        tris=['C D F', 'C F E', 'A B D', 'A D C', 'D F G', 'D G B', 'A B I', 'A I H', 'B G J', 'B J I']),
    'station_scope': dict(t=T((175, 3096), 0.6), pts={
        'P1': ((24, 490), (24, 575)), 'P2': ((316, 575), (328, 575)), 'P3': ((578, 415), (365, 437)),
        'P4': ((28, 388), (24, 478)), 'P5': ((314, 478), (328, 478)), 'P6': ((91, 300), (37, 430)),
        'P7': ((404, 395), (341, 430)), 'P8': ((146, 30), (37, 155)), 'P9': ((446, 135), (341, 155)),
        'P10': ((578, 140), (365, 70))},
        tris=['P1 P2 P5', 'P1 P5 P4', 'P4 P5 P7', 'P4 P7 P6', 'P6 P7 P9', 'P6 P9 P8', 'P8 P9 P10',
              'P2 P3 P5', 'P5 P3 P7', 'P7 P3 P10', 'P7 P10 P9']),
    'timeclock': dict(t=T((3081, 1033), 0.6), pts={
        'Nb': ((125, 560), (125, 560)), 'Rb': ((522, 440), (540, 560)), 'Nt': ((125, 160), (125, 160)),
        'Rt': ((470, 85), (540, 160)), 'Lb': ((22, 505), (95, 510)), 'Lt': ((30, 135), (95, 110)),
        'Bk': ((330, 20), (510, 110))},
        tris=['Nb Rb Rt', 'Nb Rt Nt', 'Lb Nb Nt', 'Lb Nt Lt', 'Lt Nt Rt', 'Lt Rt Bk']),
    # single shear of the whole set (box front face flat, depth recedes up-right; mugs stay upright)
    'table_clutter': dict(t=T((4008, 90), 0.6), ring=False, pts={
        'B1': ((304, 282), (304, 282)), 'B2': ((306, 335), (306, 335)), 'B3': ((519, 428), (519, 335))}, groups=['donut_box'],
        tris=['B2 B3 B1']),
}
# vent, in source coords: frame quad (open drawing) -> floor rectangle seen from the front; open lid stands up
_ident = lambda p: p
_L, _T, _R, _B = (1659, 1628), (2154, 1398), (2721, 1728), (2226, 1958)
_Lp, _Bp, _Tp, _Rp = (1640, 1900), (2296, 1900), (1640, 1654), (2296, 1654)
def _ring(pts, k=1.15):
    """outer ring (k x around the centroid) so rounded rims and outline thickness stay inside the mesh"""
    cs = np.mean([p[0] for p in pts.values()], 0); cd = np.mean([p[1] for p in pts.values()], 0)
    return {n + '2': (tuple(cs + k * (np.array(s) - cs)), tuple(cd + k * (np.array(d) - cd))) for n, (s, d) in pts.items()}


_vp = {'L': (_L, _Lp), 'B': (_B, _Bp), 'R': (_R, _Rp), 'T': (_T, _Tp)}
_vp.update(_ring(_vp))
MESHES['vent_frame'] = dict(t=_ident, pts=_vp, tris=['L B R', 'L R T', 'L L2 B2', 'L B2 B', 'B B2 R2', 'B R2 R',
                                                    'R R2 T2', 'R T2 T', 'T T2 L2', 'T L2 L'])


class Homog:
    """Projective map from a source quad to a target quad (flat floor objects: no kink along a diagonal)."""
    def __init__(self, src, dst):
        import cv2
        self.H = cv2.getPerspectiveTransform(np.float32(src), np.float32(dst))

    def __call__(self, P):
        P = np.asarray(P, float)
        Q = np.c_[P, np.ones(len(P))] @ self.H.T
        self.last_dist = np.zeros(len(P))
        return Q[:, :2] / Q[:, 2:3]


class Mesh:
    def __init__(self, m):
        t = m['t']
        self.names = list(m['pts'])
        self.src = np.array([t(m['pts'][n][0]) for n in self.names], float)
        self.dst = np.array([t(m['pts'][n][1]) for n in self.names], float)
        self.tris = [[self.names.index(n) for n in tr.split()] for tr in m['tris']]
        self.ncore = len(self.tris)
        if m.get('ring', True):
            # smooth outer ring (1.3x around the centroid) so outline thickness and rounded corners map continuously
            import cv2
            hull = cv2.convexHull(self.src.astype(np.float32), returnPoints=False)[:, 0]
            cs, cd = self.src.mean(0), self.dst.mean(0)
            n0 = len(self.src)
            self.src = np.vstack([self.src, cs + 1.3 * (self.src[hull] - cs)])
            self.dst = np.vstack([self.dst, cd + 1.3 * (self.dst[hull] - cd)])
            for k in range(len(hull)):
                i, j = hull[k], hull[(k + 1) % len(hull)]
                i2, j2 = n0 + k, n0 + (k + 1) % len(hull)
                self.tris += [[i, j, j2], [i, j2, i2]]
        self.aff = []
        for tr in self.tris:
            S = np.c_[self.src[tr], np.ones(3)]
            self.aff.append(np.linalg.solve(S, self.dst[tr]))  # 3x2: [x y 1] @ A

    def __call__(self, P):
        P = np.asarray(P, float)
        if len(self.tris) == 1:  # a single triangle is a global affine map
            self.last_dist = np.zeros(len(P))
            return np.c_[P, np.ones(len(P))] @ self.aff[0]
        out = np.full_like(P, np.nan)
        best = np.full(len(P), np.inf)
        for k, tr in enumerate(self.tris):
            a, b, c = self.src[tr]
            v0, v1, v2 = c - a, b - a, P - a
            den = v0[0] * v1[1] - v1[0] * v0[1]
            u = (v2[:, 0] * v1[1] - v1[0] * v2[:, 1]) / den
            v = (v0[0] * v2[:, 1] - v2[:, 0] * v0[1]) / den
            inside = (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9)
            # distance to triangle (0 inside): approximate by clamping barycentrics
            uc = np.clip(u, 0, 1); vc = np.clip(v, 0, 1); s = uc + vc
            s = np.maximum(s, 1e-9)
            uc = np.where(s > 1, uc / s, uc); vc = np.where(s > 1, vc / s, vc)
            Q = a + uc[:, None] * v0 + vc[:, None] * v1
            d = np.where(inside, 0, np.hypot(*(P - Q).T))
            upd = d < best
            mapped = np.c_[Q, np.ones(len(P))] @ self.aff[k] + (P - Q)
            out[upd] = mapped[upd]; best[upd] = d[upd]
            if k == self.ncore - 1:
                core = best.copy()
        self.last_dist = core  # distance to the object's own faces (ring excluded): drives the rigid rule
        return out


NUM = re.compile(r'-?\d+(?:\.\d+)?')


def map_d(d, f, pre=None):
    """Map every subpath; a subpath lying mostly outside the mesh (beacon, glow, stray outline) moves rigidly."""
    fmt = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')
    res = []
    for sub in re.findall(r'M[^M]*', d):
        P = np.array([float(v) for v in NUM.findall(sub)]).reshape(-1, 2)
        if pre is not None:
            P = P @ pre[:, :2].T + pre[:, 2]
        Q = f(P)
        far = (f.last_dist > 30).mean() > 0.6
        if far and len(P) > 2:
            # only compact parts (beacon, lamp glow) move rigidly; thin slivers along an outline follow the mesh
            x, y = P[:, 0], P[:, 1]
            area = abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) / 2
            per = np.hypot(*np.diff(np.vstack([P, P[:1]]), axis=0).T).sum()
            far = 4 * np.pi * area / max(per * per, 1e-9) > 0.2
        if far:
            c = P.mean(0, keepdims=True)
            Q = P + (f(c) - c)
        it = iter(Q.ravel())
        res.append(NUM.sub(lambda m: fmt(next(it)), sub))
    return ''.join(res)


def parse_matrix(s):
    a, b, c, d, e, f_ = map(float, re.search(r'matrix\(([^)]*)\)', s).group(1).split())
    return np.array([[a, c, e], [b, d, f_]])


def warp_svg(text, mesh, group_meshes=None):
    """Map all coordinates; group_meshes: {group_id: Mesh} overrides inside that <g id>."""
    out, stack, pad = [], [], []
    allpts = []
    for line in text.split('\n'):
        m = re.match(r'\s*<g id="([^"]+)"', line)
        if m:
            stack.append(m.group(1))
        cur = mesh
        for gid in stack:
            if group_meshes and gid in group_meshes:
                cur = group_meshes[gid]
        pre = None
        if 'transform="matrix(' in line and m:
            pre = parse_matrix(line); stack[-1] = stack[-1]
            line = re.sub(r' transform="matrix\([^)]*\)"', '', line)
            pad.append(pre)
        elif m:
            pad.append(None)
        cur_pre = next((p for p in reversed(pad) if p is not None), None) if pad else None
        if ' d="' in line:
            line = re.sub(r' d="([^"]*)"', lambda mm: ' d="' + map_d(mm.group(1), cur, cur_pre) + '"', line)
            allpts.append(np.array([float(v) for v in NUM.findall(re.search(r' d="([^"]*)"', line).group(1))]).reshape(-1, 2))
        for attr in ('cx', 'cy'):
            pass
        if '<circle' in line or '<ellipse' in line or '<radialGradient' in line and 'userSpaceOnUse' in line:
            cx, cy = float(re.search(r' cx="([-\d.]+)"', line).group(1)), float(re.search(r' cy="([-\d.]+)"', line).group(1))
            P = np.array([[cx, cy]])
            if cur_pre is not None:
                P = P @ cur_pre[:, :2].T + cur_pre[:, 2]
            nx, ny = cur(P)[0]
            line = re.sub(r' cx="[-\d.]+"', f' cx="{nx:.0f}"', line, count=1)
            line = re.sub(r' cy="[-\d.]+"', f' cy="{ny:.0f}"', line, count=1)
            line = re.sub(r'rotate\(([-\d.]+) [-\d.]+ [-\d.]+\)', lambda mm: f'rotate({mm.group(1)} {nx:.0f} {ny:.0f})', line)
        if 'data-pivot="' in line:
            px, py = map(float, re.search(r'data-pivot="([-\d.]+),([-\d.]+)"', line).groups())
            nx, ny = cur(np.array([[px, py]]))[0]
            line = re.sub(r'data-pivot="[^"]*"', f'data-pivot="{nx:.0f},{ny:.0f}"', line)
        if re.match(r'\s*</g>', line) and stack:
            stack.pop(); pad.pop()
        out.append(line)
    text = '\n'.join(out)
    P = np.vstack(allpts)
    x0, y0 = np.floor(P.min(0) - 40); x1, y1 = np.ceil(P.max(0) + 40)
    return text, (int(x0), int(y0), int(x1 - x0), int(y1 - y0))


def set_viewbox(text, vb):
    x, y, w, h = vb
    text = re.sub(r'viewBox="[^"]*"', f'viewBox="{x} {y} {w} {h}"', text, count=1)
    text = re.sub(r' width="\d+" height="\d+"', f' width="{w}" height="{h}"', text, count=1)
    return text.replace('traced from raw_originals', 'front-facing re-projection (tools/build_front.py) of the trace of raw_originals')


def show(text, state, names):
    for s in names:
        text = re.sub(f'<g id="state_{s}" display="[a-z]+"', f'<g id="state_{s}" display="{"inline" if s == state else "none"}"', text)
    return text


def export(text, vb, base, states=None, names=()):
    w, h = vb[2], vb[3]
    for s in (states or [None]):
        t = show(text, s, names) if s else text
        Image.fromarray(render_rgba(t, w // 2, h // 2).astype(np.uint8)).save(f'{OUT}/png/{base}' + (f'_{s}' if s else '') + '.png')


def run(name):
    log = {}
    if name.startswith('station_') or name == 'timeclock':
        names = ('idle', 'ready') if name == 'timeclock' else ('idle', 'highlight', 'done')
        text = open(f'{OUT}/{name}_orig.svg').read()
        w, vb = warp_svg(text, Mesh(MESHES[name]))
        w = set_viewbox(w, vb)
        open(f'{OUT}/{name}_front.svg', 'w').write(w)
        export(w, vb, f'{name}_front', names, names)
        log[name + '_front'] = {'viewBox': vb, 'kb': len(w) // 1024}
    elif name == 'table_clutter':
        text = open(f'{OUT}/table_clutter_orig.svg').read()
        # mugs are already front-facing cylinders: unchanged. The box is sheared (its corner hidden behind the red
        # mug was inpainted in the orig trace and stays covered by the mug)
        ident = Mesh(dict(t=_ident, ring=False, pts={'a': ((0, 0), (0, 0)), 'b': ((1e5, 0), (1e5, 0)), 'c': ((0, 1e5), (0, 1e5))}, tris=['a b c']))
        box = Mesh(MESHES['table_clutter'])
        # the red mug rides with the box where they overlap, so it keeps covering the box corner it hides
        dy = float(box(np.array([[4610.0, 700.0]]))[0, 1] - 700.0)
        shift = Mesh(dict(t=_ident, ring=False, pts={'a': ((0, 0), (0, dy)), 'b': ((1e5, 0), (1e5, dy)), 'c': ((0, 1e5), (0, 1e5 + dy))}, tris=['a b c']))
        w, vb = warp_svg(text, ident, {'donut_box': box, 'mug_red': shift})
        w = set_viewbox(w, vb)
        open(f'{OUT}/table_clutter_front.svg', 'w').write(w)
        export(w, vb, 'table_clutter_front')
        log['table_clutter_front'] = {'viewBox': vb, 'kb': len(w) // 1024}
    elif name == 'vent':
        fm = Homog([_L, _B, _R, _T], [_Lp, _Bp, _Rp, _Tp])
        # open lid: hinge stays on the mapped back edge, the lid stands up behind it
        HL, HR = (2040, 1600), (2622, 1792)
        hl, hr = fm(np.array([HL, HR]))
        lift = np.array([25, -430])
        lm = Homog([HL, HR, (2810, 1318), (2160, 1062)], [hl, hr, hr + lift, hl + lift])
        fr = open(f'{OUT}/vent_frame_orig.svg').read()
        li = open(f'{OUT}/vent_lid_orig.svg').read()
        wf, vbf = warp_svg(fr, fm)
        wl, vbl = warp_svg(li, fm, {'lid_open': lm})
        x0 = min(vbf[0], vbl[0]); y0 = min(vbf[1], vbl[1])
        x1 = max(vbf[0] + vbf[2], vbl[0] + vbl[2]); y1 = max(vbf[1] + vbf[3], vbl[1] + vbl[3])
        vb = (x0, y0, x1 - x0, y1 - y0)
        wf, wl = set_viewbox(wf, vb), set_viewbox(wl, vb)
        open(f'{OUT}/vent_frame_front.svg', 'w').write(wf)
        open(f'{OUT}/vent_lid_front.svg', 'w').write(wl)
        body = lambda t: t.split('\n', 2)[2].rsplit('</svg>', 1)[0]
        head = wf.split('\n', 1)[0] + '\n'
        for st in ('closed', 'open'):
            l2 = wl.replace('id="lid_closed" display="inline"', f'id="lid_closed" display="{"inline" if st == "closed" else "none"}"')
            l2 = l2.replace('id="lid_open" display="none"', f'id="lid_open" display="{"inline" if st == "open" else "none"}"')
            comp = head + body(wf) + body(l2) + '</svg>\n'
            Image.fromarray(render_rgba(comp, vb[2] // 2, vb[3] // 2).astype(np.uint8)).save(f'{OUT}/png/vent_front_{st}.png')
        Image.fromarray(render_rgba(wf, vb[2] // 2, vb[3] // 2).astype(np.uint8)).save(f'{OUT}/png/vent_frame_front.png')
        log['vent_front'] = {'viewBox': vb, 'kb': (len(wf) + len(wl)) // 1024}
    print(log)
    return log


if __name__ == '__main__':
    names = sys.argv[1:] or ['station_keypad', 'station_switchboard', 'station_tape', 'station_scope', 'timeclock', 'table_clutter', 'vent']
    logf = OUT + '/tools/log_front.json'
    try:
        L = json.load(open(logf))
    except Exception:
        L = {}
    for n in names:
        L.update(run(n))
    json.dump(L, open(logf, 'w'), indent=1)
