#!/usr/bin/env python3
"""Job P: flat layout guides for the ship map repaint.

Input : art-jobs/data/ship_geometry.json (polygons/points in map px, map 8842 x 6174)
Output: art-jobs/out/P_ship_guides/{guides,check}/<ID>.png|json, PREVIEW.png, REPORT.md

Usage : python art-jobs/tools/ship/make_guides.py [--ids SHIP,GALLEY,LOCKER] [--preview] [--report]
Only Pillow + NumPy. No anti-aliasing: every guide uses exactly the palette below.
"""
import json, sys, os, math, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
GEO = os.path.join(ROOT, 'art-jobs', 'data', 'ship_geometry.json')
OUT = os.path.join(ROOT, 'art-jobs', 'out', 'P_ship_guides')
NOTES = os.path.join(HERE, 'report_notes.md')

BLACK = (0, 0, 0); LIGHT = (200, 200, 200); MID = (140, 140, 140); DARK = (80, 80, 80)
AMBER = (245, 165, 74); CYAN = (0, 255, 255); SEAFOAM = (127, 200, 184)
PALETTE = {BLACK, LIGHT, MID, DARK, AMBER, CYAN, SEAFOAM}

# ID, area name in json, output size
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

STEP = 4.0        # boundary sampling step, map px
WALL_NEAR = 40.0  # doorway: not within this of a wall
TOUCH = 30.0      # doorway: within this of a neighbour polygon
MIN_RUN = 40.0    # shortest doorway stretch kept
STRIP = 60.0      # doorway strip thickness
STATION_R = 28.0

# ----------------------------------------------------------------- geometry
def pip(P, poly):
    """point in polygon, vectorised ray cast. P (n,2), poly (m,2)."""
    x, y = P[:, 0], P[:, 1]
    inside = np.zeros(len(P), bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        cond = (y1 > y) != (y2 > y)
        with np.errstate(divide='ignore', invalid='ignore'):
            xi = (x2 - x1) * (y - y1) / (y2 - y1) + x1
        inside ^= cond & (x < xi)
    return inside

def seg_dist(P, A, B):
    """min distance from each point of P (n,2) to segments A->B (m,2)."""
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
    poly = np.asarray(poly, float)
    A, B = edges(poly)
    d = seg_dist(P, A, B)
    d[pip(P, poly)] = 0.0
    return d

def boundary_samples(poly, step=STEP):
    poly = np.asarray(poly, float); pts = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        n = max(1, int(math.hypot(*(b - a)) / step))
        t = np.arange(n) / n
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

# ----------------------------------------------------------------- data model
class Ship:
    def __init__(self):
        g = json.load(open(GEO))
        self.g = g
        self.W, self.H = g['mapWidthPx'], g['mapHeightPx']
        self.rooms = {r['name']: np.array(r['points'], float) for r in g['rooms']}
        self.stations = [(s['name'], centroid(s['points'])) for s in g['stations']]
        self.door = np.array(g['door']['points'], float)
        self.classify_collision()
        self.find_doorways()

    def classify_collision(self):
        """props = Table*, AdminTable, Chair, and unnamed shapes lying inside one room.
        Everything else is a wall chain (treated as polylines, not filled: the big
        hull shapes overlap rooms, so they are outlines of solid structure)."""
        self.props, self.walls = [], []   # props: (name, poly); walls: (A,B)
        for i, c in enumerate(self.g['collision']):
            pts = np.array(c['points'], float); nm = c['name']
            isprop = nm.startswith('Table') or nm in ('AdminTable', 'Chair')
            if not nm:
                m = pts.mean(0)
                for rp in self.rooms.values():
                    inside = pip(boundary_samples(pts, 20), rp).mean()
                    x0, y0, x1, y1 = bbox(pts)
                    if inside > 0.8 and max(x1 - x0, y1 - y0) < 800: isprop = True
            if isprop:
                self.props.append((nm or 'prop%d' % i, pts))
            else:
                closed = np.hypot(*(pts[0] - pts[-1])) <= 120
                A, B = edges(pts, closed=closed)
                self.walls.append((nm or 'wall%d' % i, A, B))
        self.wallA = np.vstack([w[1] for w in self.walls]); self.wallB = np.vstack([w[2] for w in self.walls])

    def find_doorways(self):
        """doorways[room] = list of runs, each run an (k,2) array of boundary samples."""
        self.doorways = {}
        for name, poly in self.rooms.items():
            S = boundary_samples(poly)
            dwall = seg_dist(S, self.wallA, self.wallB)
            touch = np.zeros(len(S), bool)
            for other, op in self.rooms.items():
                if other == name: continue
                touch |= poly_dist(S, op) <= TOUCH
            openm = (dwall >= WALL_NEAR) & touch
            runs = []
            if openm.all(): runs = [S]
            elif openm.any():
                start = int(np.where(~openm)[0][0])        # rotate so index 0 is closed
                o = np.roll(openm, -start); Sr = np.roll(S, -start, 0)
                i = 0
                while i < len(o):
                    if o[i]:
                        j = i
                        while j < len(o) and o[j]: j += 1
                        runs.append(Sr[i:j]); i = j
                    else: i += 1
            runs = [r for r in runs if len(r) * STEP >= MIN_RUN]
            self.doorways[name] = runs

# ----------------------------------------------------------------- crop box
def crop_box(ship, area, out_size):
    if area == 'whole map':
        x0, y0, x1, y1 = 0, 0, ship.W, ship.H
    else:
        x0, y0, x1, y1 = bbox(ship.rooms[area])
        w, h = x1 - x0, y1 - y0
        x0 -= .12 * w; x1 += .12 * w; y0 -= .12 * h; y1 += .12 * h
    w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    asp = out_size[0] / out_size[1]
    if w / h < asp: w = h * asp          # too narrow: grow width
    else: h = w / asp                    # too wide: grow height
    return [cx - w / 2, cy - h / 2, w, h]

# ----------------------------------------------------------------- drawing
class Canvas:
    def __init__(self, rect, size):
        self.rect, self.size = rect, size
        self.s = size[0] / rect[2]
    def px(self, pts):
        p = np.asarray(pts, float)
        return [(float((x - self.rect[0]) * self.s), float((y - self.rect[1]) * self.s)) for x, y in p]
    def mask(self):
        return Image.new('L', self.size, 0)
    def poly_mask(self, pts, m=None):
        m = m or self.mask(); ImageDraw.Draw(m).polygon(self.px(pts), fill=255); return m
    def strip_mask(self, run, m=None, thick=STRIP):
        m = m or self.mask(); d = ImageDraw.Draw(m); h = thick / 2
        for p, q in zip(run[:-1], run[1:]):
            t = q - p; L = math.hypot(*t)
            if L == 0: continue
            n = np.array([-t[1], t[0]]) / L * h
            d.polygon(self.px([p + n, q + n, q - n, p - n]), fill=255)
        return m

def paint(img, mask, color):
    a = np.array(img); a[np.array(mask) > 0] = color; return Image.fromarray(a)

def build(ship, gid, area, out_size):
    rect = crop_box(ship, area, out_size)
    cv = Canvas(rect, out_size)
    info = {'id': gid, 'area': area}
    img = Image.new('RGB', out_size, BLACK)
    whole = area == 'whole map'
    runs_used = []
    door_in = lambda: (gid in ('LOCKER', 'GALLEY', 'SHIP'))
    # door bridge: lobby bottom edge down to the door polygon
    lob = ship.rooms['Lobby']; dx0, dy0, dx1, dy1 = bbox(ship.door)
    bridge = np.array([[dx0, lob[:, 1].max() - 4], [dx1, lob[:, 1].max() - 4], [dx1, dy0 + 4], [dx0, dy0 + 4]])
    if whole:
        for p in ship.rooms.values(): img = paint(img, cv.poly_mask(p), LIGHT)
        amber = cv.mask()
        for nm, rs in ship.doorways.items():
            for r in rs: cv.strip_mask(r, amber); runs_used.append(r)
        cv.poly_mask(ship.door, amber); cv.poly_mask(bridge, amber)
        img = paint(img, amber, AMBER)
        nd = sum(len(r) for r in ship.doorways.values()) + 1
        props = ship.props
        stations = ship.stations
    else:
        room = ship.rooms[area]
        for nm, p in ship.rooms.items():
            if nm != area: img = paint(img, cv.poly_mask(p), DARK)
        own = cv.poly_mask(room); img = paint(img, own, LIGHT)
        own_a = np.array(own) > 0
        # doorways
        amber = cv.mask()
        for r in ship.doorways[area]: cv.strip_mask(r, amber); runs_used.append(r)
        nd = len(ship.doorways[area])
        if area in ('Lobby', 'Cafeteria'):
            cv.poly_mask(ship.door, amber); cv.poly_mask(bridge, amber); nd += 1
        am = np.array(amber) > 0
        # band (mid grey)
        x0, y0, x1, y1 = bbox(room)
        band_px = min(0.22 * (y1 - y0), 260.0) * cv.s
        a = np.array(img)
        top = own_a.argmax(0); has = own_a.any(0)
        rows = np.arange(own_a.shape[0])[:, None]
        for x in np.where(has)[0]:
            t = top[x]
            if am[t:t + 4, x].any(): continue          # top edge is a doorway here
            sel = (rows[:, 0] >= t) & (rows[:, 0] < t + band_px) & own_a[:, x]
            a[sel, x] = MID
        img = Image.fromarray(a)
        img = paint(img, amber, AMBER)
        props = [(n, p) for n, p in ship.props if pip(centroid(p)[None], room)[0]]
        stations = [(n, c) for n, c in ship.stations if pip(c[None], room)[0]]
    # props, stations
    pm = cv.mask()
    for n, p in props: cv.poly_mask(p, pm)
    img = paint(img, pm, CYAN)
    sm = cv.mask(); d = ImageDraw.Draw(sm); r = STATION_R * cv.s
    for n, c in stations:
        (cx, cy), = cv.px([c]); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img = paint(img, sm, SEAFOAM)
    info.update({'mapRect': [round(v, 2) for v in rect], 'outSize': list(out_size), 'scale': round(cv.s, 6),
                 'roomPolygon': ([] if whole else ship.rooms[area].round(1).tolist()),
                 'crewHeightPct': round(130 / rect[3] * 100, 3)})
    info['_counts'] = {'doorways': nd, 'props': len(props), 'stations': len(stations)}
    return img, info, cv, runs_used, stations

def overlay(img, cv, area, ship, runs, stations):
    half = img.resize((img.width // 2, img.height // 2), Image.NEAREST)
    d = ImageDraw.Draw(half); k = 0.5
    def P(pts): return [(x * k, y * k) for x, y in cv.px(pts)]
    polys = list(ship.rooms.values()) if area == 'whole map' else [ship.rooms[area]]
    for p in polys:
        pts = P(p); d.line(pts + [pts[0]], fill=(255, 0, 255), width=3)
    for r in runs:
        if len(r) > 1: d.line(P(r), fill=(255, 255, 0), width=5)
    for n, c in stations:
        (x, y), = P([c]); rr = STATION_R * cv.s * k + 3
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 0, 255), width=3)
    return half

# ----------------------------------------------------------------- checks
def check(gid, area, ship):
    png = np.array(Image.open(os.path.join(OUT, 'guides', gid + '.png')).convert('RGB'))
    info = json.load(open(os.path.join(OUT, 'guides', gid + '.json')))
    h, w = png.shape[:2]
    cols = {tuple(c) for c in np.unique(png.reshape(-1, 3), axis=0)}
    res = {'size_ok': [w, h] == info['outSize'], 'palette_ok': cols <= PALETTE, 'extra_colors': sorted(cols - PALETTE)}
    if area == 'whole map':
        res.update(bbox_ok=True, bbox_dx=None, note='n/a for SHIP'); return res
    poly = np.array(info['roomPolygon']); rx, ry, _, _ = info['mapRect']; s = info['scale']
    M = Image.new('L', (w, h), 0)
    ImageDraw.Draw(M).polygon([(float((x - rx) * s), float((y - ry) * s)) for x, y in poly], fill=255)
    M = np.array(M) > 0
    is_ = lambda c: (png == c).all(-1)
    F = is_(LIGHT) | is_(MID) | is_(CYAN) | is_(SEAFOAM) | (is_(AMBER) & M)
    def bb(m):
        ys, xs = np.where(m); return xs.min(), ys.min(), xs.max(), ys.max()
    a, b = bb(F), bb(M)
    d = [int(abs(i - j)) for i, j in zip(a, b)]
    lg = bb(is_(LIGHT))
    res.update(bbox_ok=max(d) <= 2, bbox_dx=d, light_only_bbox_inset=[int(i - j) for i, j in zip(lg, b)][:4])
    return res

# ----------------------------------------------------------------- preview / report
def font(sz):
    try: return ImageFont.load_default(size=sz)
    except TypeError: return ImageFont.load_default()

def preview():
    tiles = [(g, a, s) for g, a, s in GUIDES if os.path.exists(os.path.join(OUT, 'guides', g + '.png'))]
    cols = 4; T = 560; pad = 40; lab = 64
    rows = math.ceil(len(tiles) / cols)
    leg = [(LIGHT, 'floor of this room'), (MID, 'back-wall face'), (DARK, 'neighbour room / hall'), (BLACK, 'solid / outside'),
           (AMBER, 'doorway'), (CYAN, 'furniture'), (SEAFOAM, 'task station')]
    Wd = cols * (T + pad) + pad; Ht = rows * (T + lab + pad) + pad + 120
    sheet = Image.new('RGB', (Wd, Ht), (244, 230, 200)); d = ImageDraw.Draw(sheet); f = font(34)
    for i, (g, a, s) in enumerate(tiles):
        im = Image.open(os.path.join(OUT, 'guides', g + '.png')).convert('RGB')
        sc = T / max(im.size); im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.NEAREST)
        x = pad + (i % cols) * (T + pad); y = pad + (i // cols) * (T + lab + pad)
        sheet.paste(im, (x + (T - im.width) // 2, y + (T - im.height) // 2))
        d.rectangle([x - 1, y - 1, x + T, y + T], outline=(42, 30, 53), width=2)
        d.text((x + T // 2, y + T + 8), g, fill=(42, 30, 53), font=f, anchor='mt')
    y = Ht - 90; x = pad
    for c, t in leg:
        d.rectangle([x, y, x + 36, y + 36], fill=c, outline=(42, 30, 53), width=2)
        d.text((x + 46, y + 18), t, fill=(42, 30, 53), font=font(26), anchor='lm'); x += 46 + int(d.textlength(t, font=font(26))) + 40
    sheet.save(os.path.join(OUT, 'PREVIEW.png'))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default=''); ap.add_argument('--preview', action='store_true'); ap.add_argument('--report', action='store_true')
    a = ap.parse_args()
    ship = Ship()
    ids = [i for i in a.ids.split(',') if i]
    os.makedirs(os.path.join(OUT, 'guides'), exist_ok=True); os.makedirs(os.path.join(OUT, 'check'), exist_ok=True)
    stats = {}
    for gid, area, size in GUIDES:
        if ids and gid not in ids: continue
        img, info, cv, runs, st = build(ship, gid, area, size)
        counts = info.pop('_counts')
        img.save(os.path.join(OUT, 'guides', gid + '.png'))
        json.dump(info, open(os.path.join(OUT, 'guides', gid + '.json'), 'w'))
        overlay(img, cv, area, ship, runs, st).save(os.path.join(OUT, 'check', gid + '_overlay.png'))
        r = check(gid, area, ship); r.update(counts); r['mapRect'] = info['mapRect']; r['scale'] = info['scale']
        stats[gid] = r
        print(gid, counts, 'bbox', r.get('bbox_dx'), 'palette', r['palette_ok'], 'size', r['size_ok'])
    if stats:
        p = os.path.join(OUT, 'check', 'stats.json'); old = json.load(open(p)) if os.path.exists(p) else {}
        old.update(stats); json.dump(old, open(p, 'w'), indent=1)
    if a.preview or a.report: preview()
    if a.report: write_report()

def write_report():
    stats = json.load(open(os.path.join(OUT, 'check', 'stats.json')))
    L = ['# Job P report: layout guides for the ship map repaint', '',
         'Generated by `art-jobs/tools/ship/make_guides.py` from `art-jobs/data/ship_geometry.json` only.', '',
         '| ID | area | mapRect [x, y, w, h] | scale | doorways | props | stations | size | palette | bbox check (dx0,dy0,dx1,dy1 px) |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for gid, area, size in GUIDES:
        s = stats.get(gid)
        if not s: L.append('| %s | %s | not produced | | | | | | | |' % (gid, area)); continue
        bb = 'n/a' if s['bbox_dx'] is None else ('PASS ' if s['bbox_ok'] else 'FAIL ') + str(s['bbox_dx'])
        L.append('| %s | %s | %s | %s | %d | %d | %d | %s | %s | %s |' % (gid, area, s['mapRect'], s['scale'], s['doorways'], s['props'],
                 s['stations'], 'ok' if s['size_ok'] else 'WRONG', 'ok' if s['palette_ok'] else 'EXTRA %s' % s['extra_colors'], bb))
    L.append('')
    if os.path.exists(NOTES): L.append(open(NOTES).read())
    open(os.path.join(OUT, 'REPORT.md'), 'w').write('\n'.join(L))

if __name__ == '__main__':
    main()
