#!/usr/bin/env python3
"""Job P round 5 (geometry): flat layout guides for the ship map repaint.

Copy of make_guides_v4.py with the floor rebuilt from the real wall contours:
  floor = room polygon - wall masses (full precision, no simplifying or snapping)
  furniture = cyan holes in the floor; neighbour floors = other polygons - wall masses
  doorways = contact lines between two floors with no wall mass between (one rotated rectangle each)
  band = the v4 mitred band method run on the new floor edges (12 px smoothing for the band only)
Needs shapely (pip install shapely). Input: art-jobs/data/ship_geometry.json only.
Output: art-jobs/out/P_ship_guides_v5/
Usage : python art-jobs/tools/ship/make_guides_v5.py [--ids A,B | --ids none] [--preview] [--compare] [--report]
"""
import json, os, math, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, MultiLineString, box, GeometryCollection
from shapely.ops import unary_union, nearest_points
from shapely import make_valid, set_precision

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
GEO = os.path.join(ROOT, 'art-jobs', 'data', 'ship_geometry.json')
OUT = os.path.join(ROOT, 'art-jobs', 'out', 'P_ship_guides_v5')
V1 = os.path.join(ROOT, 'art-jobs', 'out', 'P_ship_guides')
V4 = os.path.join(ROOT, 'art-jobs', 'out', 'P_ship_guides_v4')
NOTES = os.path.join(HERE, 'report_notes_v5.md')

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
COMPARE_IDS = ['HYDRO', 'LOWER', 'TURRET', 'UPPER', 'DEFLECTOR', 'REACTOR', 'CARGO', 'BRIDGE']
WALL_NAMES = {'ShipRight', 'ShipLeft', 'InteriorLeft', 'UpperSecurityWall', 'MedBayWall', 'ReactorUpperWall'}

STRIP = 60.0; STATION_R = 28.0; SNAP_DEG = 3.0
CONTACT_R = 16.0       # two floors count as touching when closer than 2 x this (map px); the room polygons are up to 13 px apart
WALL_R = 6.0           # a floor edge this close to a wall mass is solid, not a doorway
MERGE_GAP = 120.0      # merge contact fragments of one neighbour closer than this
MIN_DOOR = 40.0        # shortest doorway
MIN_SPECK_AREA = 300.0; MIN_SPECK_THICK = 6.0   # stray floor slivers (area, 2A/perimeter) are dropped
BAND_SMOOTH = 12.0     # band-only edge smoothing tolerance
MIN_PIECE = 180.0; TOUCH_DOOR = 20.0; DOOR_PIECE = 300.0
CLOSE_MAP_PX = 12.0
BAND_H_FRAC = 0.22; BAND_H_MAX = 260.0
STATION_MAX_MOVE = 60.0

# ----------------------------------------------------------------- geometry helpers (from v4)
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


def _box(a, k, pad):
    r = k // 2; p = np.pad(a.astype(np.int32), r, constant_values=int(pad))
    c = np.pad(p.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]

def close_mask(a, k):
    return _box(_box(a, k, 0) > 0, k, 1) == k * k


def polys_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    if g.geom_type in ('MultiPolygon', 'GeometryCollection'): return [p for x in g.geoms for p in polys_of(x)]
    return []

def lines_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == 'LineString': return [g]
    if g.geom_type in ('MultiLineString', 'GeometryCollection'): return [l for x in g.geoms for l in lines_of(x)]
    return []

def clean_poly(pts): return make_valid(Polygon(np.round(np.asarray(pts, float), 1)))

def bbox(poly):
    p = np.asarray(poly, float); return p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()

# ----------------------------------------------------------------- data model
class Ship:
    def __init__(self):
        g = json.load(open(GEO)); self.g = g
        self.W, self.H = g['mapWidthPx'], g['mapHeightPx']
        self.orig = {r['name']: np.round(np.array(r['points'], float), 1) for r in g['rooms']}   # room polygons (JSON roomPolygon + crops)
        wall_parts, self.props = [], []
        for i, c in enumerate(g['collision']):
            pts = c['points']; nm = c['name']
            if nm in WALL_NAMES or (nm == '' and len(pts) == 56): wall_parts.append(clean_poly(pts))
            else: self.props.append((nm or 'prop%d' % i, clean_poly(pts)))
        self.walls = unary_union(wall_parts)
        self.poly = {n: clean_poly(p) for n, p in self.orig.items()}
        self.floor, self.stats = {}, {}
        for n, p in self.poly.items():
            f = p.difference(self.walls); keep = []; dropped = 0
            for c in polys_of(f):
                if c.area < MIN_SPECK_AREA or 2 * c.area / max(c.length, 1) < MIN_SPECK_THICK: dropped += 1; continue
                keep.append(c)
            fl = set_precision(unary_union(keep), 0.1) if keep else Polygon()
            self.floor[n] = fl
            self.stats[n] = {'poly_area': p.area, 'walled_pct': 100 * p.intersection(self.walls).area / p.area,
                             'floor_area': fl.area, 'specks_dropped': dropped, 'components': len(polys_of(fl))}
        self.room_props = {}
        for n, p in self.poly.items():
            self.room_props[n] = [(pn, pg) for pn, pg in self.props if p.contains(pg.centroid)]
            fur = unary_union([pg for _, pg in self.room_props[n]]) if self.room_props[n] else Polygon()
            self.stats[n]['walkable_area'] = self.floor[n].difference(fur).area
        self.find_doorways(); self.place_stations()

    # ---- doorways: contact lines between two floors with no wall mass between them
    def find_doorways(self):
        WB = self.walls.buffer(WALL_R); names = list(self.floor); buf = {n: self.floor[n].buffer(CONTACT_R) for n in names}
        self.doorways = []
        for i, A in enumerate(names):
            for B in names[i + 1:]:
                if self.floor[A].is_empty or self.floor[B].is_empty or not buf[A].intersects(buf[B]): continue
                lines = []
                for X, Y in ((A, B), (B, A)):
                    lines += lines_of(self.floor[X].boundary.difference(WB).intersection(buf[Y]))
                lines = [l for l in lines if l.length > 3]
                if not lines: continue
                par = list(range(len(lines)))
                def find(k):
                    while par[k] != k: par[k] = par[par[k]]; k = par[k]
                    return k
                for p in range(len(lines)):
                    for q in range(p + 1, len(lines)):
                        if lines[p].distance(lines[q]) <= MERGE_GAP: par[find(p)] = find(q)
                groups = {}
                for k in range(len(lines)): groups.setdefault(find(k), []).append(lines[k])
                for gl in groups.values():
                    pts = np.vstack([np.array([l.interpolate(t).coords[0] for t in np.arange(0, l.length, 4.0).tolist() + [l.length]]) for l in gl])
                    c = pts.mean(0); d = np.linalg.svd(pts - c)[2][0]
                    if abs(d[1]) <= math.sin(math.radians(SNAP_DEG)): d = np.array([1.0, 0.0])
                    elif abs(d[0]) <= math.sin(math.radians(SNAP_DEG)): d = np.array([0.0, 1.0])
                    pr = (pts - c) @ d; t0, t1 = float(pr.min()), float(pr.max())
                    if t1 - t0 < MIN_DOOR: continue
                    mid = c + d * (t0 + t1) / 2
                    self.doorways.append({'rooms': (A, B), 'c': mid, 'd': d, 'len': t1 - t0})

    def rects_of(self, name): return [r for r in self.doorways if name in r['rooms']]

    def door_rect(self):
        pts = np.array(self.g['door']['points'], float); x0, y0, x1, y1 = bbox(pts); ly = self.orig['Lobby'][:, 1].max()
        return np.array([[x0, ly - 4], [x1, ly - 4], [x1, y1], [x0, y1]])

    # ---- stations: dot at the centroid; moved to the nearest floor point within 60 px when it falls in solid
    def place_stations(self):
        self.stations = []
        for s in self.g['stations']:
            sp = Polygon(s['points']); c = sp.centroid if sp.is_valid and sp.area > 0 else Point(np.mean(s['points'], 0)); pt = Point(c.x, c.y)
            rooms = [n for n, f in self.floor.items() if f.covers(pt)]; moved = 0.0; p = np.array([c.x, c.y])
            if not rooms:
                dd = sorted((f.distance(pt), n) for n, f in self.floor.items() if not f.is_empty)
                if dd and dd[0][0] <= STATION_MAX_MOVE:
                    k = dd[0][1]; q = nearest_points(self.floor[k], pt)[0]; e = self.floor[k].buffer(-STATION_R)
                    if not e.is_empty and e.distance(q) <= STATION_R + 1: q = nearest_points(e, q)[0]   # nudge inside so the whole dot is on floor
                    p = np.array([q.x, q.y]); moved = float(np.hypot(*(p - [c.x, c.y])))
                    rooms = [n for n, f in self.floor.items() if f.covers(Point(*p))] or [k]
                else: moved = -1.0     # no floor within 60 px: left out of every guide
            self.stations.append({'name': s['name'], 'c': [c.x, c.y], 'p': p, 'moved': moved, 'rooms': rooms})

def rect_poly(r):
    c, d = np.asarray(r['c']), np.asarray(r['d']); n = np.array([-d[1], d[0]]); h = r['len'] / 2; t = STRIP / 2
    return np.array([c - d * h - n * t, c + d * h - n * t, c + d * h + n * t, c - d * h + n * t])

# ----------------------------------------------------------------- crop box (from the room polygon: identical to v1 to v4)
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

def draw_geom(cv, g, m):
    d = ImageDraw.Draw(m)
    for p in polys_of(g):
        d.polygon(cv.px(np.array(p.exterior.coords)), fill=255)
        for r in p.interiors: d.polygon(cv.px(np.array(r.coords)), fill=0)
    return m

def geom_mask(cv, g): return draw_geom(cv, g, cv.mask())

def line_hit(q, t, qb, tb):
    """intersection of line q + s*t with line qb + u*tb; returns point or None."""
    M = np.array([[t[0], -tb[0]], [t[1], -tb[1]]])
    if abs(np.linalg.det(M)) < 1e-6: return None
    s, u = np.linalg.solve(M, qb - q); return q + s * t

def inside_shape(P, shape):
    return pip(P, shape)

def band_mask(cv, ring, comp, h, shapes, m, info):
    """v3 band: pieces are chains of consecutive up-facing edges (outward normal y < -0.3) cut at doorways.
    A chain is a strip between the wall and its inward offset by h; joints are mitred (shared offset corner),
    a chain end at a non-banded wall is clipped along that wall's line, a chain end at a doorway is square.
    Short pieces (< 180 px) are dropped."""
    poly = ring; n = len(poly)
    E = []
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]; e = b - a; L = math.hypot(*e)
        if L < 1: E.append(None); continue
        t = e / L; nrm = np.array([t[1], -t[0]])
        inward = nrm if comp.covers(Point((a + b) / 2 + nrm * 3)) else -nrm
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
    dr = ImageDraw.Draw(m)
    for ch in chains:
        segs = []
        for (i, r) in ch:
            t0, t1, s0, s1 = runs[i][r]; e = E[i]
            segs.append({'i': i, 'p0': e['a'] + e['t'] * t0, 'p1': e['a'] + e['t'] * t1, 't': e['t'], 'n': e['n'], 'len': t1 - t0})
        total = sum(s['len'] for s in segs)
        if total < MIN_PIECE: info['dropped_short'] += 1; continue
        # doorway proximity: pieces beside a doorway are kept only when >= MIN_PIECE (checked above); pieces on a hall
        # neck wall sit on a different polygon edge than the doorway, so no extra distance rule is applied (see REPORT_v3).
        dpts = np.vstack([np.linspace(q['p0'], q['p1'], max(2, int(q['len'] / 10) + 2)) for q in segs])
        if total < DOOR_PIECE and any(poly_dist(dpts, sh).min() <= TOUCH_DOOR for sh in shapes): info['dropped_near_door'] += 1; continue
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

def _box(a, k, pad):
    r = k // 2; p = np.pad(a.astype(np.int32), r, constant_values=int(pad))
    c = np.pad(p.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]

def close_mask(a, k):
    return _box(_box(a, k, 0) > 0, k, 1) == k * k


def build_band(cv, floor, shapes):
    """v4 band on the new floor: smoothed (12 px, band only) floor edges that face up the screen."""
    x0, y0, x1, y1 = floor.bounds; h = min(BAND_H_FRAC * (y1 - y0), BAND_H_MAX)
    m = cv.mask(); info = {'pieces': 0, 'dropped_short': 0, 'dropped_near_door': 0}
    for comp in polys_of(floor.simplify(BAND_SMOOTH, preserve_topology=True)):
        for ring in [comp.exterior] + list(comp.interiors):
            pts = np.array(ring.coords)[:-1]
            if len(pts) >= 3: band_mask(cv, pts, comp, h, shapes, m, info)
    return m, info

def build(ship, gid, area_name, out_size):
    rect = crop_box(ship, area_name, out_size); cv = Canvas(rect, out_size); img = Image.new('RGB', out_size, BLACK)
    whole = area_name == 'whole map'; door = ship.door_rect(); binfo = None
    win = box(rect[0] - 50, rect[1] - 50, rect[0] + rect[2] + 50, rect[1] + rect[3] + 50)
    if whole:
        img = paint(img, geom_mask(cv, unary_union(list(ship.floor.values()))), LIGHT)
        rect_list = ship.doorways; amber = cv.mask()
        for r in rect_list: cv.poly_mask(rect_poly(r), amber)
        cv.poly_mask(door, amber); img = paint(img, amber, AMBER)
        nd = len(rect_list) + 1; cyan_geom = unary_union([pg for _, pg in ship.props]); sts = [s for s in ship.stations if s['moved'] >= 0]
    else:
        fl = ship.floor[area_name]
        others = unary_union([f for n, f in ship.floor.items() if n != area_name]).intersection(win)
        img = paint(img, geom_mask(cv, others), DARK)
        own = geom_mask(cv, fl); img = paint(img, own, LIGHT)
        rect_list = ship.rects_of(area_name); amber = cv.mask(); shapes = [rect_poly(r) for r in rect_list]; nd = len(rect_list)
        if area_name in ('Lobby', 'Cafeteria'): shapes.append(door); nd += 1
        for sh in shapes: cv.poly_mask(sh, amber)
        cyan_geom = unary_union([pg for _, pg in ship.room_props[area_name]]).intersection(fl)
        sts = [s for s in ship.stations if area_name in s['rooms'] and s['moved'] >= 0]
        pm = geom_mask(cv, cyan_geom); sm = cv.mask(); d = ImageDraw.Draw(sm); r_ = STATION_R * cv.s
        for s in sts:
            (cx, cy), = cv.px([s['p']]); d.ellipse([cx - r_, cy - r_, cx + r_, cy + r_], fill=255)
        bm, binfo = build_band(cv, fl, shapes)
        own_a = np.array(own) > 0; k = 2 * max(1, round(CLOSE_MAP_PX * cv.s)) + 1
        closed = close_mask((np.array(bm) > 0) | ~own_a, k)
        band = closed & own_a & ~(np.array(amber) > 0) & ~(np.array(pm) > 0) & ~(np.array(sm) > 0)
        a = np.array(img); a[band] = MID; img = Image.fromarray(a)
        img = paint(img, amber, AMBER)
    img = paint(img, geom_mask(cv, cyan_geom), CYAN)
    sm = cv.mask(); d = ImageDraw.Draw(sm); r_ = STATION_R * cv.s
    for s in sts:
        (cx, cy), = cv.px([s['p']]); d.ellipse([cx - r_, cy - r_, cx + r_, cy + r_], fill=255)
    img = paint(img, sm, SEAFOAM)
    nprops = len(ship.props) if whole else len(ship.room_props[area_name])
    info = {'id': gid, 'area': area_name, 'mapRect': [round(v, 2) for v in rect], 'outSize': list(out_size),
            'scale': round(cv.s, 6), 'roomPolygon': ([] if whole else ship.orig[area_name].tolist()),
            'crewHeightPct': round(130 / rect[3] * 100, 3), 'polished': 5}
    counts = {'doorways': nd, 'props': nprops, 'stations': len(sts)}
    if binfo: counts.update(binfo)
    ov = list(rect_list) + ([{'poly': door}] if (whole or area_name in ('Lobby', 'Cafeteria')) else [])
    return img, info, counts, cv, ov, [{'p': s['p']} for s in sts]

def overlay(img, cv, area_name, ship, rects, stations):
    half = img.resize((img.width // 2, img.height // 2), Image.NEAREST); d = ImageDraw.Draw(half)
    P = lambda pts: [(x * .5, y * .5) for x, y in cv.px(pts)]
    for n in (ship.floor if area_name == 'whole map' else [area_name]):
        for p in polys_of(ship.floor[n]): pts = P(np.array(p.exterior.coords)); d.line(pts, fill=(255, 0, 255), width=3)
    for r in rects:
        pts = P(r['poly'] if 'poly' in r else rect_poly(r)); d.line(pts + [pts[0]], fill=(255, 255, 0), width=3)
    for s in stations:
        (x, y), = P([s['p']]); rr = STATION_R * cv.s * .5 + 3; d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 0, 255), width=3)
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
    if area_name == 'whole map': res.update(bbox_ok=True, bbox_dx=None, band_outside_px=None); return res
    rx, ry, _, _ = info['mapRect']; s = info['scale']; tf = lambda pts: [(float((x - rx) * s), float((y - ry) * s)) for x, y in pts]
    M = Image.new('L', (w, h), 0); dd = ImageDraw.Draw(M); dd.polygon(tf(info['roomPolygon']), fill=255)
    for c in json.load(open(GEO))['collision']:         # expected floor: room polygon minus the wall masses (raster, independent of shapely)
        if c['name'] in WALL_NAMES or (c['name'] == '' and len(c['points']) == 56): dd.polygon(tf(c['points']), fill=0)
    M = np.array(M) > 0
    F = is_(LIGHT) | is_(MID) | is_(CYAN) | is_(SEAFOAM) | (is_(AMBER) & M)
    res['band_outside_px'] = int((is_(MID) & ~(_box(M, 5, 0) > 0)).sum())   # 2 px tolerance for edge rasterisation
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
    sheet.save(os.path.join(OUT, 'PREVIEW_v5.png'))

def compare(ids=COMPARE_IDS, name='COMPARE.png'):
    ids = [g for g in ids if os.path.exists(os.path.join(OUT, 'guides', g + '.png'))]
    T, pad, lab = 440, 30, 56; per = 2; rows = math.ceil(len(ids) / per)
    sheet = Image.new('RGB', (per * (2 * T + pad) + pad * (per + 1), rows * (T + lab + pad) + pad), (244, 230, 200)); d = ImageDraw.Draw(sheet)
    for i, g in enumerate(ids):
        x = pad + (i % per) * (2 * T + 3 * pad); y = pad + (i // per) * (T + lab + pad)
        for k, (root, tag) in enumerate(((V4, 'v4'), (OUT, 'v5'))):
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
    json.dump({'rooms': ship.stats, 'stations': [{k: (v if not isinstance(v, np.ndarray) else v.round(1).tolist()) for k, v in s.items()} for s in ship.stations]},
              open(os.path.join(OUT, 'check', 'geometry.json'), 'w'), indent=1)
    if a.preview or a.report: preview()
    if a.compare or a.report: compare([i for i in a.cmp_ids.split(',') if i] or COMPARE_IDS, 'COMPARE5.png' if not a.cmp_ids else 'COMPARE5_partial.png')
    if a.report: write_report()

def write_report():
    stats = json.load(open(os.path.join(OUT, 'check', 'stats.json'))); geo = json.load(open(os.path.join(OUT, 'check', 'geometry.json')))
    v4p = os.path.join(V4, 'check', 'stats.json'); v4 = json.load(open(v4p)) if os.path.exists(v4p) else {}
    L = ['# Job P round 5 (geometry) report', '', 'Generated by `art-jobs/tools/ship/make_guides_v5.py` from `art-jobs/data/ship_geometry.json` only (shapely 2.x). v1 to v4 are untouched.', '',
         '## Per guide', '',
         '| ID | area | old polygon area px2 | old polygon inside walls | new floor area px2 | walkable (floor minus furniture) px2 | doorways (v4 -> v5) | props | stations | size | crop same as v1 | off-palette px | band px outside floor | bbox check (dx0,dy0,dx1,dy1 px) | band pieces kept | dropped short | dropped near doorway |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for gid, area_name, size in GUIDES:
        s = stats.get(gid)
        if not s: L.append('| %s | %s | not produced |' % (gid, area_name) + '|' * 14); continue
        g = geo['rooms'].get(area_name); bb = 'n/a' if s['bbox_dx'] is None else ('PASS ' if s['bbox_ok'] else 'FAIL ') + str(s['bbox_dx'])
        gs = ('%d | %.1f%% | %d | %d' % (g['poly_area'], g['walled_pct'], g['floor_area'], g['walkable_area'])) if g else 'n/a | n/a | n/a | n/a'
        L.append('| %s | %s | %s | %s -> %d | %d | %d | %s | %s | %d | %s | %s | %s | %s | %s |' % (gid, area_name, gs, v4.get(gid, {}).get('doorways', '?'), s['doorways'], s['props'], s['stations'],
                 'ok' if s['size_ok'] else 'WRONG', s['crop_same_as_v1'], s['off_palette_px'], s.get('band_outside_px', 'n/a'), bb,
                 s.get('pieces', 'n/a'), s.get('dropped_short', 'n/a'), s.get('dropped_near_door', 'n/a')))
    L += ['', '## Hallways (not a guide; same measurement)', '', '| polygon | old area px2 | inside walls | new floor area px2 | floor components | specks dropped |', '|---|---|---|---|---|---|']
    rooms_in_guides = {a for _, a, _ in GUIDES}
    for n, g in geo['rooms'].items():
        if n not in rooms_in_guides: L.append('| %s | %d | %.1f%% | %d | %d | %d |' % (n, g['poly_area'], g['walled_pct'], g['floor_area'], g['components'], g['specks_dropped']))
    L += ['', '## Stations', '', '| station | centroid | placed at | moved (map px) | rooms |', '|---|---|---|---|---|']
    for s in geo['stations']:
        mv = 'not moved' if s['moved'] == 0 else ('NO FLOOR WITHIN 60 PX, left out' if s['moved'] < 0 else '%.1f' % s['moved'])
        L.append('| %s | %s | %s | %s | %s |' % (s['name'], [round(v) for v in s['c']], [round(v) for v in s['p']], mv, ', '.join(s['rooms']) or '-'))
    L.append('')
    if os.path.exists(NOTES): L.append(open(NOTES).read())
    open(os.path.join(OUT, 'REPORT_v5.md'), 'w').write('\n'.join(L))

if __name__ == '__main__':
    main()
