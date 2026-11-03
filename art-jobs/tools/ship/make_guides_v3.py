#!/usr/bin/env python3
"""Job P round 3 (bands only): copy of make_guides_v2.py with a new back-wall band (mitred strips, stub trimming).

Below: the v2 description.

Same input, IDs, sizes, crops, colors and JSON fields as make_guides.py (v1), plus:
  1. doorways are ONE clean rotated rectangle per opening (fragments merged, clipped to the wall gap),
  2. the back-wall band is edge based (follows slanted upper walls),
  3. room polygons are simplified (25 px) and near-H/V edges snapped before drawing.
Doorway detection is cached (art-jobs/out/P_ship_guides_v2/check/doorway_cache.json).

Input : art-jobs/data/ship_geometry.json only.   Output: art-jobs/out/P_ship_guides_v2/
Usage : python art-jobs/tools/ship/make_guides_v2.py [--ids A,B | --ids none] [--preview] [--compare] [--report]
"""
import json, os, math, argparse, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
GEO = os.path.join(ROOT, 'art-jobs', 'data', 'ship_geometry.json')
OUT = os.path.join(ROOT, 'art-jobs', 'out', 'P_ship_guides_v3')
V2 = os.path.join(ROOT, 'art-jobs', 'out', 'P_ship_guides_v2')
V1 = os.path.join(ROOT, 'art-jobs', 'out', 'P_ship_guides')
NOTES = os.path.join(HERE, 'report_notes_v3.md')
CACHE = os.path.join(OUT, 'check', 'doorway_cache.json')
CACHE_V2 = os.path.join(V2, 'check', 'doorway_cache.json')

BLACK = (0, 0, 0); LIGHT = (200, 200, 200); MID = (140, 140, 140); DARK = (80, 80, 80)
AMBER = (245, 165, 74); CYAN = (0, 255, 255); SEAFOAM = (127, 200, 184)
PALETTE = {BLACK, LIGHT, MID, DARK, AMBER, CYAN, SEAFOAM}

GUIDES = [
    ('LOCKER', 'Lobby', (4096, 4096)), ('GALLEY', 'Cafeteria', (4096, 4096)),
    ('TURRET', 'Weapons', (4096, 4096)), ('HYDRO', 'O2', (4096, 4096)),
    ('BRIDGE', 'Navigation', (3277, 4096)), ('DEFLECTOR', 'Shields', (4096, 4096)),
    ('RADIO', 'Communications', (4096, 3277)), ('CARGO', 'Storage', (2731, 4096)),
    ('DISPATCH', 'Admin', (4096, 3277)), ('SWITCH', 'Electrical', (3072, 4096)),
    ('LOWER', 'LowerEngine', (4096, 4096)), ('UPPER', 'UpperEngine', (4096, 4096)),
    ('REACTOR', 'Reactor', (3072, 4096)), ('WATCH', 'Security', (3277, 4096)),
    ('SICKBAY', 'MedBay', (4096, 4096)), ('SHIP', 'whole map', (4096, 2731)),
]
COMPARE_IDS = ['DEFLECTOR', 'SICKBAY', 'WATCH', 'REACTOR', 'RADIO', 'HYDRO', 'LOCKER', 'GALLEY']

STEP = 4.0; WALL_NEAR = 40.0; TOUCH = 30.0; MIN_RUN = 40.0
STRIP = 60.0; STATION_R = 28.0
MERGE_GAP = 120.0      # merge doorway fragments of one neighbour closer than this
EXTEND_MAX = 50.0      # clip-to-gap search distance past the open stretch
WALL_HIT = 3.0         # "reached the wall" distance
SIMPLIFY_TOL = 25.0; SNAP_DEG = 3.0; AREA_LIMIT = 0.02
DEDUPE_DIST = 70.0

# ----------------------------------------------------------------- geometry
def pip(P, poly):
    x, y = P[:, 0], P[:, 1]; inside = np.zeros(len(P), bool); n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        cond = (y1 > y) != (y2 > y)
        with np.errstate(divide='ignore', invalid='ignore'):
            xi = (x2 - x1) * (y - y1) / (y2 - y1) + x1
        inside ^= cond & (x < xi)
    return inside

def seg_dist(P, A, B):
    out = np.full(len(P), np.inf)
    if len(A) == 0: return out
    for s in range(0, len(P), 1500):
        p = P[s:s + 1500][:, None, :]
        ab = (B - A)[None]; ap = p - A[None]
        L2 = (ab ** 2).sum(-1); L2 = np.where(L2 == 0, 1e-9, L2)
        t = np.clip((ap * ab).sum(-1) / L2, 0, 1)
        c = A[None] + t[..., None] * ab
        out[s:s + 1500] = np.sqrt(((p - c) ** 2).sum(-1)).min(1)
    return out

def edges(poly, closed=True):
    poly = np.asarray(poly, float)
    A = poly[:-1] if not closed else poly
    B = poly[1:] if not closed else np.roll(poly, -1, 0)
    return A, B

def poly_dist(P, poly):
    poly = np.asarray(poly, float); A, B = edges(poly)
    d = seg_dist(P, A, B); d[pip(P, poly)] = 0.0
    return d

def boundary_samples(poly, step=STEP):
    poly = np.asarray(poly, float); pts = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        n = max(1, int(math.hypot(*(b - a)) / step)); t = np.arange(n) / n
        pts.append(a[None] + t[:, None] * (b - a)[None])
    return np.vstack(pts)

def centroid(poly):
    p = np.asarray(poly, float)
    if len(p) < 3: return p.mean(0)
    x, y = p[:, 0], p[:, 1]; x2, y2 = np.roll(x, -1), np.roll(y, -1)
    cr = x * y2 - x2 * y; a = cr.sum() / 2
    if abs(a) < 1e-6: return p.mean(0)
    return np.array([((x + x2) * cr).sum() / (6 * a), ((y + y2) * cr).sum() / (6 * a)])

def bbox(poly):
    p = np.asarray(poly, float); return p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()

def area(poly):
    p = np.asarray(poly, float); x, y = p[:, 0], p[:, 1]
    return abs((x * np.roll(y, -1) - np.roll(x, -1) * y).sum()) / 2

# ----------------------------------------------------------------- polygon cleaning (change 3)
def dp(pts, tol):
    n = len(pts); keep = np.zeros(n, bool); keep[0] = keep[-1] = True; stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1: continue
        d = seg_dist(pts[i + 1:j], pts[i][None], pts[j][None]); k = int(d.argmax())
        if d[k] > tol:
            keep[i + 1 + k] = True; stack += [(i, i + 1 + k), (i + 1 + k, j)]
    return np.where(keep)[0]

def simplify_closed(poly, tol):
    n = len(poly); k = int(np.argmax(np.hypot(*(poly - poly[0]).T)))
    ch1 = poly[:k + 1]; ch2 = np.vstack([poly[k:], poly[:1]])
    i1 = dp(ch1, tol); i2 = dp(ch2, tol)
    return [int(i) for i in i1] + [k + int(i) for i in i2[1:-1]]

def snap_hv(poly, deg=SNAP_DEG):
    n = len(poly); P = poly.copy(); par = {'x': list(range(n)), 'y': list(range(n))}
    def find(a, i):
        while par[a][i] != i: par[a][i] = par[a][par[a][i]]; i = par[a][i]
        return i
    for i in range(n):
        j = (i + 1) % n; d = P[j] - P[i]
        ang = math.degrees(math.atan2(abs(d[1]), abs(d[0])))
        if ang <= deg: par['y'][find('y', i)] = find('y', j)
        elif ang >= 90 - deg: par['x'][find('x', i)] = find('x', j)
    out = P.copy()
    for a, c in (('x', 0), ('y', 1)):
        g = {}
        for i in range(n): g.setdefault(find(a, i), []).append(i)
        for m in g.values(): out[m, c] = P[m, c].mean()
    return out

def clean_polygon(poly):
    poly = np.asarray(poly, float); a0 = area(poly)
    for tol in (SIMPLIFY_TOL, 20, 15, 10, 6, 3, 1, 0.1):
        idx = simplify_closed(poly, tol)
        if len(idx) < 3: continue
        s = snap_hv(poly[idx])
        ch = abs(area(s) - a0) / a0
        if ch < AREA_LIMIT: break
    A, B = edges(s)
    return s, {'tol': tol, 'verts_before': len(poly), 'verts_after': len(s), 'area_change_pct': round(ch * 100, 3),
               'max_vertex_shift': round(float(np.hypot(*(s - poly[idx]).T).max()), 2),
               'max_boundary_dev': round(float(seg_dist(poly, A, B).max()), 2)}

# ----------------------------------------------------------------- data model
def runs_of(m, S):
    if not m.any(): return []
    if m.all(): return [S]
    start = int(np.where(~m)[0][0]); o = np.roll(m, -start); Sr = np.roll(S, -start, 0); runs = []; i = 0
    while i < len(o):
        if o[i]:
            j = i
            while j < len(o) and o[j]: j += 1
            runs.append(Sr[i:j]); i = j
        else: i += 1
    return runs

class Ship:
    def __init__(self):
        g = json.load(open(GEO)); self.g = g
        self.W, self.H = g['mapWidthPx'], g['mapHeightPx']
        self.orig = {r['name']: np.array(r['points'], float) for r in g['rooms']}   # used for crops, membership, doorway search
        self.rooms, self.cleaninfo = {}, {}
        for n, p in self.orig.items(): self.rooms[n], self.cleaninfo[n] = clean_polygon(p)   # drawn polygons
        self.stations = [(s['name'], centroid(s['points'])) for s in g['stations']]
        self.door = np.array(g['door']['points'], float)
        self.classify_collision(); self.find_doorways()

    def classify_collision(self):
        self.props, self.walls = [], []
        for i, c in enumerate(self.g['collision']):
            pts = np.array(c['points'], float); nm = c['name']
            isprop = nm.startswith('Table') or nm in ('AdminTable', 'Chair')
            if not nm:
                x0, y0, x1, y1 = bbox(pts)
                for rp in self.orig.values():
                    if pip(boundary_samples(pts, 20), rp).mean() > 0.8 and max(x1 - x0, y1 - y0) < 800: isprop = True
            if isprop: self.props.append((nm or 'prop%d' % i, pts))
            else:
                closed = np.hypot(*(pts[0] - pts[-1])) <= 120
                A, B = edges(pts, closed=closed); self.walls.append((nm or 'wall%d' % i, A, B))
        self.wallA = np.vstack([w[1] for w in self.walls]); self.wallB = np.vstack([w[2] for w in self.walls])

    # -------- change 1: doorway rectangles (cached)
    def find_doorways(self):
        key = hashlib.sha1((open(GEO, 'rb').read().hex() + 'v2-%s-%s-%s-%s-%s' % (STEP, WALL_NEAR, TOUCH, MERGE_GAP, EXTEND_MAX)).encode()).hexdigest()
        for cp in (CACHE, CACHE_V2):
            if os.path.exists(cp):
                c = json.load(open(cp))
                if c.get('key') == key: self.doorways = c['rooms']; return
        self.doorways = {n: self.rects_for(n, p) for n, p in self.orig.items()}
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump({'key': key, 'rooms': self.doorways}, open(CACHE, 'w'))

    def rects_for(self, name, poly):
        S = boundary_samples(poly); dwall = seg_dist(S, self.wallA, self.wallB)
        frags = []   # (neighbour, samples)
        for other, op in self.orig.items():
            if other == name: continue
            m = (dwall >= WALL_NEAR) & (poly_dist(S, op) <= TOUCH)
            for r in runs_of(m, S):
                if len(r) >= 3: frags.append((other, r))
        par = list(range(len(frags)))
        def find(i):
            while par[i] != i: par[i] = par[par[i]]; i = par[i]
            return i
        for i in range(len(frags)):
            for j in range(i + 1, len(frags)):
                dm = np.sqrt(((frags[i][1][:, None] - frags[j][1][None]) ** 2).sum(-1)).min()
                if (frags[i][0] == frags[j][0] and dm <= MERGE_GAP) or dm <= TOUCH: par[find(i)] = find(j)
        groups = {}
        for i in range(len(frags)): groups.setdefault(find(i), []).append(i)
        out = []
        for gi in groups.values():
            pts = np.vstack([frags[i][1] for i in gi]); c = pts.mean(0)
            d = np.linalg.svd(pts - c)[2][0]
            if abs(d[1]) <= math.sin(math.radians(SNAP_DEG)): d = np.array([1.0, 0.0])
            elif abs(d[0]) <= math.sin(math.radians(SNAP_DEG)): d = np.array([0.0, 1.0])
            proj = (pts - c) @ d; t0, t1 = float(proj.min()), float(proj.max())
            if t1 - t0 < MIN_RUN: continue
            ends = []
            for t, sg in ((t0, -1), (t1, 1)):
                e = c + d * t; ex = np.arange(0, EXTEND_MAX + 1, 2.0)
                dd = seg_dist(e[None] + sg * d[None] * ex[:, None], self.wallA, self.wallB)
                hit = np.where(dd <= WALL_HIT)[0]
                ends.append(t + sg * (ex[hit[0]] if len(hit) else 0.0))
            mid = c + d * (ends[0] + ends[1]) / 2
            out.append({'room': name, 'c': [float(mid[0]), float(mid[1])], 'd': [float(d[0]), float(d[1])],
                        'len': float(ends[1] - ends[0]), 'nbr': sorted({frags[i][0] for i in gi})})
        return out

    def aligned_rects(self, name):
        """doorway rectangles of one room, centre line moved onto the cleaned boundary edge that carries them."""
        A, B = edges(self.rooms[name]); res = []
        for r in self.doorways[name]:
            c = np.array(r['c']); d = np.array(r['d']); best = None
            for a, b in zip(A, B):
                e = b - a; L = math.hypot(*e)
                if L < 1: continue
                ed = e / L; nrm = np.array([-ed[1], ed[0]]); off = float((c - a) @ nrm); t = float((c - a) @ ed)
                if abs(ed[0] * d[1] - ed[1] * d[0]) > 0.17 or not (-60 <= t <= L + 60) or abs(off) > 45: continue
                if best is None or abs(off) < abs(best[0]): best = (off, nrm, ed)
            if best: c = c - best[1] * best[0]; d = best[2]
            res.append({'room': name, 'c': c, 'd': d, 'len': r['len']})
        return res

    def all_rects(self):
        keep = []
        for n in self.rooms:
            for r in self.aligned_rects(n):
                if any(np.hypot(*(r['c'] - k['c'])) < DEDUPE_DIST and abs(r['d'][0] * k['d'][1] - r['d'][1] * k['d'][0]) < 0.4 for k in keep): continue
                keep.append(r)
        return keep

    def door_rect(self):
        x0, y0, x1, y1 = bbox(self.door); ly = self.rooms['Lobby'][:, 1].max()
        return np.array([[x0, ly - 4], [x1, ly - 4], [x1, y1], [x0, y1]])

def rect_poly(r):
    c, d = np.asarray(r['c']), np.asarray(r['d']); n = np.array([-d[1], d[0]]); h = r['len'] / 2; t = STRIP / 2
    return np.array([c - d * h - n * t, c + d * h - n * t, c + d * h + n * t, c - d * h + n * t])

def in_rect(P, r):
    c, d = np.asarray(r['c']), np.asarray(r['d']); n = np.array([-d[1], d[0]]); q = P - c
    return (np.abs(q @ d) <= r['len'] / 2) & (np.abs(q @ n) <= STRIP / 2)

# ----------------------------------------------------------------- crop box (from the ORIGINAL polygon: identical to v1)
def crop_box(ship, area_name, out_size):
    if area_name == 'whole map': x0, y0, x1, y1 = 0, 0, ship.W, ship.H
    else:
        x0, y0, x1, y1 = bbox(ship.orig[area_name]); w, h = x1 - x0, y1 - y0
        x0 -= .12 * w; x1 += .12 * w; y0 -= .12 * h; y1 += .12 * h
    w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; asp = out_size[0] / out_size[1]
    if w / h < asp: w = h * asp
    else: h = w / asp
    return [cx - w / 2, cy - h / 2, w, h]

# ----------------------------------------------------------------- drawing
class Canvas:
    def __init__(self, rect, size): self.rect, self.size = rect, size; self.s = size[0] / rect[2]
    def px(self, pts):
        p = np.asarray(pts, float); return [(float((x - self.rect[0]) * self.s), float((y - self.rect[1]) * self.s)) for x, y in p]
    def mask(self): return Image.new('L', self.size, 0)
    def poly_mask(self, pts, m=None):
        m = m or self.mask(); ImageDraw.Draw(m).polygon(self.px(pts), fill=255); return m

def paint(img, mask, color):
    a = np.array(img); a[np.array(mask) > 0] = color; return Image.fromarray(a)

MIN_PIECE = 180.0      # band pieces shorter than this (map px) are dropped
NEAR_DOOR = 120.0      # (unused: see report; pieces beside a doorway must be >= MIN_PIECE)
BAND_H_FRAC = 0.22; BAND_H_MAX = 260.0

def line_hit(q, t, qb, tb):
    """intersection of line q + s*t with line qb + u*tb; returns point or None."""
    M = np.array([[t[0], -tb[0]], [t[1], -tb[1]]])
    if abs(np.linalg.det(M)) < 1e-6: return None
    s, u = np.linalg.solve(M, qb - q); return q + s * t

def inside_shape(P, shape):
    return pip(P, shape)

def band_mask(cv, poly, shapes):
    """v3 band: pieces are chains of consecutive up-facing edges (outward normal y < -0.3) cut at doorways.
    A chain is a strip between the wall and its inward offset by h; joints are mitred (shared offset corner),
    a chain end at a non-banded wall is clipped along that wall's line, a chain end at a doorway is square.
    Short pieces (< 180 px) are dropped."""
    x0, y0, x1, y1 = bbox(poly); h = min(BAND_H_FRAC * (y1 - y0), BAND_H_MAX); n = len(poly)
    E = []
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]; e = b - a; L = math.hypot(*e)
        if L < 1: E.append(None); continue
        t = e / L; nrm = np.array([t[1], -t[0]])
        inward = nrm if pip(((a + b) / 2 + nrm * 3)[None], poly)[0] else -nrm
        E.append({'a': a, 'b': b, 't': t, 'L': L, 'n': inward, 'q': inward[1] > 0.3})
    # free runs per qualifying edge
    runs = {}     # edge -> list of (t0, t1, startsAtVertex, endsAtVertex)
    for i, e in enumerate(E):
        if e is None or not e['q']: continue
        ts = np.unique(np.append(np.arange(0, e['L'], 2.0), e['L'])); pts = e['a'] + ts[:, None] * e['t']
        free = np.ones(len(pts), bool)
        for s in shapes: free &= ~inside_shape(pts, s)
        lst = []; k = 0
        while k < len(free):
            if free[k]:
                j = k
                while j < len(free) and free[j]: j += 1
                lst.append((ts[k], ts[j - 1], k == 0, j == len(free))); k = j
            else: k += 1
        runs[i] = lst
    # chains: link end-of-run to start-of-run on next edge
    nodes = [(i, r) for i, lst in runs.items() for r in range(len(lst))]
    nxt = {}; prv = {}
    for (i, r) in nodes:
        if runs[i][r][3]:
            j = (i + 1) % n
            if j in runs and runs[j] and runs[j][0][2]: nxt[(i, r)] = (j, 0); prv[(j, 0)] = (i, r)
    chains = []; seen = set()
    for nd in nodes:
        if nd in prv or nd in seen: continue
        ch = [nd]; seen.add(nd)
        while ch[-1] in nxt and nxt[ch[-1]] not in seen: ch.append(nxt[ch[-1]]); seen.add(ch[-1])
        chains.append(ch)
    m = cv.mask(); dr = ImageDraw.Draw(m); info = {'pieces': 0, 'dropped_short': 0, 'dropped_near_door': 0}
    for ch in chains:
        segs = []
        for (i, r) in ch:
            t0, t1, s0, s1 = runs[i][r]; e = E[i]
            segs.append({'i': i, 'p0': e['a'] + e['t'] * t0, 'p1': e['a'] + e['t'] * t1, 't': e['t'], 'n': e['n'], 'len': t1 - t0})
        total = sum(s['len'] for s in segs)
        if total < MIN_PIECE: info['dropped_short'] += 1; continue
        # doorway proximity: pieces beside a doorway are kept only when >= MIN_PIECE (checked above); pieces on a hall
        # neck wall sit on a different polygon edge than the doorway, so no extra distance rule is applied (see REPORT_v3).
        info['pieces'] += 1
        # offset corners
        k = len(segs); S = [None] * k; T = [None] * k
        for j, s in enumerate(segs):
            S[j] = s['p0'] + s['n'] * h; T[j] = s['p1'] + s['n'] * h
        for j in range(k - 1):
            na, nb = segs[j]['n'], segs[j + 1]['n']; den = 1 + float(na @ nb)
            mv = (na + nb) / max(den, 0.25); mv = mv if np.hypot(*mv) <= 4 else mv / np.hypot(*mv) * 4
            S[j + 1] = T[j] = segs[j]['p1'] + mv * h
        for end in (0, 1):                      # chain ends: clip along the neighbouring wall unless it is a doorway cut
            j = 0 if end == 0 else k - 1; s = segs[j]; i = s['i']; r = [rr for (ii, rr) in ch if ii == i][0]
            at_vertex = runs[i][r][2] if end == 0 else runs[i][r][3]
            if not at_vertex: continue
            nb = E[(i - 1) % n] if end == 0 else E[(i + 1) % n]
            if nb is None or nb['q']: continue
            q0 = s['p0'] if end == 0 else s['p1']
            hit = line_hit(q0 + s['n'] * h, s['t'], q0, nb['t'])
            if hit is not None and np.hypot(*(hit - q0)) <= 4 * h:
                if end == 0: S[j] = hit
                else: T[j] = hit
        for j, s in enumerate(segs):
            if s['len'] < 1: continue
            dr.polygon(cv.px([s['p0'], s['p1'], T[j], S[j]]), fill=255)
    return m, info

def feature_masks(cv, props, stations):
    pm = cv.mask()
    for nme, p in props: cv.poly_mask(p, pm)
    sm = cv.mask(); d = ImageDraw.Draw(sm); r = STATION_R * cv.s
    for nme, c in stations:
        (cx, cy), = cv.px([c]); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return pm, sm

def build(ship, gid, area_name, out_size):
    rect = crop_box(ship, area_name, out_size); cv = Canvas(rect, out_size); img = Image.new('RGB', out_size, BLACK)
    whole = area_name == 'whole map'; door = ship.door_rect(); binfo = None
    if whole:
        for p in ship.rooms.values(): img = paint(img, cv.poly_mask(p), LIGHT)
        rect_list = ship.all_rects(); amber = cv.mask()
        for r in rect_list: cv.poly_mask(rect_poly(r), amber)
        cv.poly_mask(door, amber); img = paint(img, amber, AMBER)
        nd = len(rect_list) + 1; props = ship.props; stations = ship.stations
    else:
        room = ship.rooms[area_name]
        for nm, p in ship.rooms.items():
            if nm != area_name: img = paint(img, cv.poly_mask(p), DARK)
        own = cv.poly_mask(room); img = paint(img, own, LIGHT)
        rect_list = ship.aligned_rects(area_name); amber = cv.mask(); shapes = [rect_poly(r) for r in rect_list]
        nd = len(rect_list)
        if area_name in ('Lobby', 'Cafeteria'): shapes.append(door); nd += 1
        for sh in shapes: cv.poly_mask(sh, amber)
        orig = ship.orig[area_name]
        props = [(n, p) for n, p in ship.props if pip(centroid(p)[None], orig)[0]]
        stations = [(n, c) for n, c in ship.stations if pip(c[None], orig)[0]]
        pm, sm = feature_masks(cv, props, stations)
        bm, binfo = band_mask(cv, room, shapes)
        band = (np.array(bm) > 0) & (np.array(own) > 0) & ~(np.array(amber) > 0) & ~(np.array(pm) > 0) & ~(np.array(sm) > 0)
        a = np.array(img); a[band] = MID; img = Image.fromarray(a)
        img = paint(img, amber, AMBER)
    pm, sm = feature_masks(cv, props, stations)
    img = paint(img, pm, CYAN); img = paint(img, sm, SEAFOAM)
    info = {'id': gid, 'area': area_name, 'mapRect': [round(v, 2) for v in rect], 'outSize': list(out_size),
            'scale': round(cv.s, 6), 'roomPolygon': ([] if whole else ship.rooms[area_name].round(1).tolist()),
            'crewHeightPct': round(130 / rect[3] * 100, 3), 'polished': 3}
    counts = {'doorways': nd, 'props': len(props), 'stations': len(stations)}
    if binfo: counts.update(binfo)
    ov = rect_list + [{'poly': door}] if (whole or area_name in ('Lobby', 'Cafeteria')) else rect_list
    return img, info, counts, cv, ov, stations


def overlay(img, cv, area_name, ship, rects, stations):
    half = img.resize((img.width // 2, img.height // 2), Image.NEAREST); d = ImageDraw.Draw(half)
    P = lambda pts: [(x * .5, y * .5) for x, y in cv.px(pts)]
    for p in (ship.rooms.values() if area_name == 'whole map' else [ship.rooms[area_name]]):
        pts = P(p); d.line(pts + [pts[0]], fill=(255, 0, 255), width=3)
    for r in rects:
        pts = P(r['poly'] if 'poly' in r else rect_poly(r)); d.line(pts + [pts[0]], fill=(255, 255, 0), width=3)
    for n, c in stations:
        (x, y), = P([c]); rr = STATION_R * cv.s * .5 + 3; d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 0, 255), width=3)
    return half

# ----------------------------------------------------------------- checks
def check(gid, area_name):
    png = np.array(Image.open(os.path.join(OUT, 'guides', gid + '.png')).convert('RGB'))
    info = json.load(open(os.path.join(OUT, 'guides', gid + '.json'))); h, w = png.shape[:2]
    is_ = lambda c: (png == c).all(-1)
    known = np.zeros((h, w), bool)
    for c in PALETTE: known |= is_(c)
    res = {'size_ok': [w, h] == info['outSize'], 'off_palette_px': int((~known).sum())}
    v1 = os.path.join(V1, 'guides', gid + '.json')
    res['crop_same_as_v1'] = (json.load(open(v1))['mapRect'] == info['mapRect']) if os.path.exists(v1) else None
    if area_name == 'whole map': res.update(bbox_ok=True, bbox_dx=None); return res
    poly = np.array(info['roomPolygon']); rx, ry, _, _ = info['mapRect']; s = info['scale']
    M = Image.new('L', (w, h), 0); ImageDraw.Draw(M).polygon([(float((x - rx) * s), float((y - ry) * s)) for x, y in poly], fill=255)
    M = np.array(M) > 0
    res['band_outside_px'] = int((is_(MID) & ~M).sum())
    F = is_(LIGHT) | is_(MID) | is_(CYAN) | is_(SEAFOAM) | (is_(AMBER) & M)
    bb = lambda m: (lambda ys, xs: (xs.min(), ys.min(), xs.max(), ys.max()))(*np.where(m))
    d = [int(abs(i - j)) for i, j in zip(bb(F), bb(M))]
    res.update(bbox_ok=max(d) <= 2, bbox_dx=d); return res

# ----------------------------------------------------------------- sheets
def font(sz):
    try: return ImageFont.load_default(size=sz)
    except TypeError: return ImageFont.load_default()

def load(path, T):
    im = Image.open(path).convert('RGB'); sc = T / max(im.size)
    return im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.NEAREST)

def preview():
    tiles = [g for g, a, s in GUIDES if os.path.exists(os.path.join(OUT, 'guides', g + '.png'))]
    cols, T, pad, lab = 4, 560, 40, 64; rows = math.ceil(len(tiles) / cols)
    leg = [(LIGHT, 'floor of this room'), (MID, 'back-wall face'), (DARK, 'neighbour room / hall'), (BLACK, 'solid / outside'),
           (AMBER, 'doorway'), (CYAN, 'furniture'), (SEAFOAM, 'task station')]
    sheet = Image.new('RGB', (cols * (T + pad) + pad, rows * (T + lab + pad) + pad + 120), (244, 230, 200)); d = ImageDraw.Draw(sheet)
    for i, g in enumerate(tiles):
        im = load(os.path.join(OUT, 'guides', g + '.png'), T)
        x = pad + (i % cols) * (T + pad); y = pad + (i // cols) * (T + lab + pad)
        sheet.paste(im, (x + (T - im.width) // 2, y + (T - im.height) // 2))
        d.rectangle([x - 1, y - 1, x + T, y + T], outline=(42, 30, 53), width=2)
        d.text((x + T // 2, y + T + 8), g, fill=(42, 30, 53), font=font(34), anchor='mt')
    y = sheet.height - 90; x = pad
    for c, t in leg:
        d.rectangle([x, y, x + 36, y + 36], fill=c, outline=(42, 30, 53), width=2)
        d.text((x + 46, y + 18), t, fill=(42, 30, 53), font=font(26), anchor='lm'); x += 46 + int(d.textlength(t, font=font(26))) + 40
    sheet.save(os.path.join(OUT, 'PREVIEW_v3.png'))

def compare(ids=COMPARE_IDS, name='COMPARE.png'):
    ids = [g for g in ids if os.path.exists(os.path.join(OUT, 'guides', g + '.png'))]
    T, pad, lab = 440, 30, 56; per = 2; rows = math.ceil(len(ids) / per)
    sheet = Image.new('RGB', (per * (2 * T + pad) + pad * (per + 1), rows * (T + lab + pad) + pad), (244, 230, 200)); d = ImageDraw.Draw(sheet)
    for i, g in enumerate(ids):
        x = pad + (i % per) * (2 * T + 3 * pad); y = pad + (i // per) * (T + lab + pad)
        for k, (root, tag) in enumerate(((V2, 'v2'), (OUT, 'v3'))):
            im = load(os.path.join(root, 'guides', g + '.png'), T); xx = x + k * (T + pad // 2)
            sheet.paste(im, (xx + (T - im.width) // 2, y + (T - im.height) // 2))
            d.rectangle([xx - 1, y - 1, xx + T, y + T], outline=(42, 30, 53), width=2)
            d.text((xx + T // 2, y + T + 8), '%s  %s' % (g, tag), fill=(42, 30, 53), font=font(30), anchor='mt')
    sheet.save(os.path.join(OUT, name))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default=''); ap.add_argument('--preview', action='store_true')
    ap.add_argument('--compare', action='store_true'); ap.add_argument('--report', action='store_true')
    ap.add_argument('--cmp-ids', default='')
    a = ap.parse_args(); ship = Ship()
    ids = [i for i in a.ids.split(',') if i]
    os.makedirs(os.path.join(OUT, 'guides'), exist_ok=True); os.makedirs(os.path.join(OUT, 'check'), exist_ok=True)
    stats = {}
    for gid, area_name, size in GUIDES:
        if ids and gid not in ids: continue
        if ids == ['none']: break
        img, info, counts, cv, rects, st = build(ship, gid, area_name, size)
        img.save(os.path.join(OUT, 'guides', gid + '.png')); json.dump(info, open(os.path.join(OUT, 'guides', gid + '.json'), 'w'))
        overlay(img, cv, area_name, ship, rects, st).save(os.path.join(OUT, 'check', gid + '_overlay.png'))
        r = check(gid, area_name); r.update(counts); r['mapRect'] = info['mapRect']; r['scale'] = info['scale']; stats[gid] = r
        print(gid, counts, 'bbox', r['bbox_dx'], 'offpal', r['off_palette_px'], 'band-outside', r.get('band_outside_px'), 'crop==v1', r['crop_same_as_v1'])
    p = os.path.join(OUT, 'check', 'stats.json'); old = json.load(open(p)) if os.path.exists(p) else {}
    old.update(stats); json.dump(old, open(p, 'w'), indent=1)
    if a.preview or a.report: preview()
    if a.compare or a.report: compare([i for i in a.cmp_ids.split(',') if i] or COMPARE_IDS, 'COMPARE3.png' if not a.cmp_ids else 'COMPARE3_partial.png')
    if a.report: write_report()

def write_report():
    stats = json.load(open(os.path.join(OUT, 'check', 'stats.json')))
    v2p = os.path.join(V2, 'check', 'stats.json'); v2 = json.load(open(v2p)) if os.path.exists(v2p) else {}
    L = ['# Job P round 3 (bands only) report', '', 'Generated by `art-jobs/tools/ship/make_guides_v3.py` from `art-jobs/data/ship_geometry.json` only. v1 and v2 are untouched.', '',
         '| ID | area | doorways (v2 -> v3) | props | stations | size | crop same as v1 | off-palette px | band px outside room polygon | bbox check (dx0,dy0,dx1,dy1 px) | band pieces kept | dropped short | dropped near doorway |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for gid, area_name, size in GUIDES:
        s = stats.get(gid)
        if not s: L.append('| %s | %s | not produced ||||||||||| ' % (gid, area_name)); continue
        bb = 'n/a' if s['bbox_dx'] is None else ('PASS ' if s['bbox_ok'] else 'FAIL ') + str(s['bbox_dx'])
        L.append('| %s | %s | %s -> %d | %d | %d | %s | %s | %d | %s | %s | %s | %s | %s |' % (gid, area_name, v2.get(gid, {}).get('doorways', '?'), s['doorways'], s['props'], s['stations'],
                 'ok' if s['size_ok'] else 'WRONG', s['crop_same_as_v1'], s['off_palette_px'], s.get('band_outside_px', 0) or 0, bb,
                 s.get('pieces', 'n/a'), s.get('dropped_short', 'n/a'), s.get('dropped_near_door', 'n/a')))
    L.append('')
    if os.path.exists(NOTES): L.append(open(NOTES).read())
    open(os.path.join(OUT, 'REPORT_v3.md'), 'w').write('\n'.join(L))

if __name__ == '__main__':
    main()
