"""Stage 2: trace objects + shell from the original, verify, export.
usage: python build.py <room> [objects|shell|all]"""
import sys, json, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
from jlib import *
from rooms import ROOMS

def save_png(a, p, half=True):
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if half:
        im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    im.save(p, optimize=True)

def split_masks(o, img, m):
    """Children cut out of an object (e.g. the monitor's heartbeat line)."""
    out = {}
    for cid, kind in o.get('split', []):
        if kind == 'green_glow':
            a = img.astype(int)
            c = (a[..., 1] > 150) & (a[..., 1] - a[..., 0] > 60)
            out[cid] = (ndi.binary_dilation(c & m, iterations=6) & m, 'overlay')
        else:
            out[cid] = (poly_mask(m.shape, sc(kind[1])) & m, 'cut')
    return out

def trace_obj(img, m, path, gid, extra='', scale=1):
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([img[y0:y1, x0:x1], np.where(m[y0:y1, x0:x1], 255, 0)]).astype(np.uint8)
    body = trace(rgba, scale=scale, color_precision=7, layer_difference=12)
    path.write_text(svg_doc(x1 - x0, y1 - y0, body, gid, extra))
    return int(x0), int(y0), int(x1 - x0), int(y1 - y0)

def objects(room):
    spec = ROOMS[room]; img = load(spec['src'])
    M = dict(np.load(OUT / 'work' / f'{room}_masks.npz'))
    od = OUT / room / 'objects'; od.mkdir(parents=True, exist_ok=True)
    meta = {}
    for o in spec['objects']:
        m = M[o['id']]; src = img
        kids = split_masks(o, img, m)
        cuts = {k: v[0] for k, v in kids.items() if v[1] == 'cut'}
        kids = {k: v[0] for k, v in kids.items() if v[1] == 'overlay'}
        for k, c in cuts.items():
            m = m & ~c
        M[o['id']] = m
        if kids:
            hole = np.zeros_like(m)
            for k in kids.values(): hole |= k
            src = img.copy()
            sub = cv2.inpaint(np.ascontiguousarray(img), hole.astype(np.uint8), 9, cv2.INPAINT_TELEA)
            src[hole] = sub[hole]
        extra = ''
        meta[o['id']] = dict(zip('xywh', trace_obj(src, m, od / f"{room}_{o['id']}.svg", o['id'], extra)))
        for cid, cm in kids.items():
            cm2 = cm & (np.abs(img.astype(int) - src.astype(int)).sum(2) > 30)
            cm2 = ndi.binary_dilation(cm2, iterations=2) & cm
            meta[cid] = dict(zip('xywh', trace_obj(img, cm2, od / f"{room}_{cid}.svg", cid)), parent=o['id'])
            M[cid] = cm2
        for cid, cm in cuts.items():
            meta[cid] = dict(zip('xywh', trace_obj(img, cm, od / f"{room}_{cid}.svg", cid)), parent=o['id'])
            M[cid] = cm
        print(o['id'], meta[o['id']], (od / f"{room}_{o['id']}.svg").stat().st_size // 1024, 'KB', flush=True)
    json.dump(meta, open(OUT / 'work' / f'{room}_objmeta.json', 'w'), indent=1)
    np.savez_compressed(OUT / 'work' / f'{room}_masks_final.npz', **M)

if __name__ == '__main__':
    room, stage = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'all')
    if stage in ('objects', 'all'): objects(room)

def check_objects(room, ids=None):
    spec = ROOMS[room]; img = load(spec['src'])
    M = dict(np.load(OUT / 'work' / f'{room}_masks_final.npz'))
    meta = json.load(open(OUT / 'work' / f'{room}_objmeta.json'))
    cd = OUT / room / 'check'; cd.mkdir(parents=True, exist_ok=True)
    res = {}
    for oid, b in meta.items():
        if ids and oid not in ids: continue
        x, y, w, h = b['x'], b['y'], b['w'], b['h']
        r = render(OUT / room / 'objects' / f'{room}_{oid}.svg', w, h)
        for kid, kb in meta.items():
            if kb.get('parent') == oid:
                kr = render(OUT / room / 'objects' / f'{room}_{kid}.svg', kb['w'], kb['h'])
                big = np.zeros((h, w, 4)); dx, dy = kb['x'] - x, kb['y'] - y
                big[dy:dy + kb['h'], dx:dx + kb['w']] = kr
                a = big[..., 3:4] / 255; r = r.astype(float); r[..., :3] = big[..., :3] * a + r[..., :3] * (1 - a)
                r[..., 3:4] = np.maximum(r[..., 3:4], big[..., 3:4])
        orig = img[y:y + h, x:x + w].astype(float)
        comp = over(img, r, x, y)[y:y + h, x:x + w]
        m = ndi.binary_dilation(M[oid][y:y + h, x:x + w], iterations=6)
        res[oid] = round(mae4(comp, orig, m), 2)
        sep = np.full((h, 12, 3), 244.0); sep[..., 1] = 230; sep[..., 2] = 200
        save_png(np.hstack([orig, sep, comp]), cd / f'{oid}_side_by_side.png', half=False)
        a = r[..., 3:4] / 255.0 * 0.5
        save_png(r[..., :3] * a + orig * (1 - a), cd / f'{oid}_onion.png', half=False)
    print(res)
    json.dump(res, open(OUT / 'work' / f'{room}_mae.json', 'w'), indent=1)
    return res

if __name__ == '__main__' and stage in ('check', 'all'):
    check_objects(room)

def row_interp(a, m):
    """Fill masked runs in each row by linear interpolation between the run's neighbours."""
    a = a.astype(float).copy()
    H, W = m.shape
    for y in range(H):
        row = m[y]
        if not row.any(): continue
        d = np.diff(np.r_[0, row.astype(int), 0])
        for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            l = a[y, max(0, s - 4):s].mean(0) if s > 0 else None
            r = a[y, e:min(W, e + 4)].mean(0) if e < W else None
            l = r if l is None else l; r = l if r is None else r
            t = np.linspace(0, 1, e - s)[:, None]
            a[y, s:e] = l * (1 - t) + r * t
    return a

def levels_svg(alpha, color, scale, gid, nlev=10, extra=''):
    """Alpha map (0..1) -> stacked flat-opacity contour paths of one color."""
    out = [f'<g id="{gid}"{extra} fill="{color}">']
    prev = 0.0
    amax = alpha.max()
    if amax < 0.01: return ''
    ts = np.linspace(amax / nlev, amax, nlev) - amax / nlev / 2
    for t in ts:
        mk = (alpha >= t).astype(np.uint8)
        cs, _ = cv2.findContours(mk, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        d = []
        for c in cs:
            if cv2.contourArea(c) < 4: continue
            c = cv2.approxPolyDP(c, 0.8, True)[:, 0] * scale
            d.append('M' + ' '.join(f'{x},{y}' for x, y in c) + 'Z')
        if not d: continue
        target = t + amax / nlev / 2
        op = 1 - (1 - target) / (1 - prev)  # stacked over previous coverage
        prev = target
        out.append(f'<path fill-opacity="{op:.3f}" fill-rule="evenodd" d="{" ".join(d)}"/>')
    out.append('</g>')
    return '\n'.join(out)

def cone_shapes(g, W, H):
    """Basis shapes for one lamp (SVG fragments in source px): wide cone, core cone, floor pool, bulb halo."""
    bx, by = [v * K for v in g['bulb']]
    yw = g.get('wall_y', 478) * K; yp = g.get('pool_y', 540) * K
    w1, w2 = g.get('w', 150) * K, g.get('core', 80) * K
    i = g['id']
    defs = (f'<linearGradient id="{i}_v" x1="0" y1="{by:.0f}" x2="0" y2="{yw:.0f}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{{c}}" stop-opacity="1"/><stop offset="1" stop-color="{{c}}" stop-opacity="0.15"/></linearGradient>'
            f'<radialGradient id="{i}_r"><stop offset="0" stop-color="{{c}}" stop-opacity="1"/><stop offset="1" stop-color="{{c}}" stop-opacity="0"/></radialGradient>')
    def trap(w0, w):
        return f'M{bx - w0:.0f},{by:.0f} L{bx + w0:.0f},{by:.0f} L{bx + w:.0f},{yw:.0f} L{bx - w:.0f},{yw:.0f}Z'
    t0 = g.get('top', 30) * K
    hx, hy = g.get('halo', (70, 70))
    shapes = [f'<path d="{trap(t0 * f0, w1 * f)}" fill="url(#{i}_v)" opacity="{{a}}"/>'
              for f0, f in [(1.4, 1.35), (1.15, 1.1), (1.0, 0.85), (0.8, 0.6), (0.6, w2 / w1)]]
    shapes += [f'<ellipse cx="{bx:.0f}" cy="{yp:.0f}" rx="{g.get("pool_rx", 210) * K * f:.0f}" ry="{g.get("pool_ry", 75) * K * f:.0f}" fill="url(#{i}_r)" opacity="{{a}}"/>'
               for f in (1.3, 0.8)]
    shapes += [f'<ellipse cx="{bx:.0f}" cy="{by + 8 * K:.0f}" rx="{hx * K * f:.0f}" ry="{hy * K * f:.0f}" fill="url(#{i}_r)" opacity="{{a}}"/>'
               for f in (1.0, 0.5)]
    return defs, shapes

def fit_lights(spec, D, valid, W, H, Wq, Hq):
    """NNLS-fit the opacity of every lamp's basis shapes jointly to the measured additive glow D (quarter res)."""
    from scipy.optimize import nnls
    glows = spec.get('glows', [])
    allB, owner, parts = [], [], []
    for gi, g in enumerate(glows):
        defs, shapes = cone_shapes(g, W, H); parts.append((defs, shapes))
        for sh in shapes:
            t = OUT / 'work' / '_b.svg'
            t.write_text(svg_doc(W, H, ['<defs>' + defs.replace('{c}', '#FFFFFF') + '</defs>', sh.replace('{a}', '1')]))
            allB.append(render(t, Wq, Hq)[..., 3] / 255.0); owner.append(gi)
    B = np.stack(allB, -1); owner = np.array(owner)
    reg = (B.sum(-1) > 0.02) & valid
    coef, _ = nnls(B[reg], D.mean(-1)[reg])
    body = []
    for gi, g in enumerate(glows):
        Bg = (B[..., owner == gi] * coef[owner == gi]).sum(-1)
        col = (D[reg] * Bg[reg][:, None]).sum(0)
        col = col / col.max() * 255 if col.max() > 0 else np.array([245, 165, 74.0])
        op = coef[owner == gi] / max(col.mean(), 1)
        c = '#%02X%02X%02X' % tuple(int(v) for v in col)
        g['color'] = c; g['opacity'] = [round(float(x), 3) for x in op]
        defs, shapes = parts[gi]
        frag = [f'<g id="{g["id"]}">', '<defs>' + defs.replace('{c}', c) + '</defs>']
        frag += [sh.replace('{a}', f'{min(a, 1):.3f}') for sh, a in zip(shapes, op) if a > 0.005]
        body.append('\n'.join(frag + ['</g>']))
    return body

def add_light(base, rgba):
    return np.clip(base + rgba[..., :3] * (rgba[..., 3:4] / 255.0), 0, 255)

def plane_interp(a, hole, plane, medmask=None):
    """Row interpolation of hole pixels using only same-plane, non-hole neighbours."""
    valid = ~ndi.binary_dilation(hole, iterations=6) & ndi.binary_erosion(plane, iterations=4)
    f = row_interp_valid(a, ~valid, valid, medmask=medmask)
    out = a.copy(); sel = hole & plane
    out[sel] = f[sel]
    return out

def row_interp_valid(a, todo, valid, short=50, fall=18.0, medmask=None):
    """Short gaps: interpolate neighbours. Long gaps: row median of the plane, eased into the neighbours."""
    a = a.astype(float).copy(); H, W = todo.shape
    for y in range(H):
        tx = np.nonzero(todo[y])[0]
        vx = np.nonzero(valid[y])[0]
        if len(tx) == 0 or len(vx) < 8: continue
        mx = vx if medmask is None else np.nonzero(medmask[y] & valid[y])[0]
        med = np.median(a[y, mx if len(mx) >= 6 else vx], 0)
        vals = np.stack([ndi.uniform_filter1d(a[y, vx, c], 5) for c in range(a.shape[2])], -1)
        idx = np.searchsorted(vx, tx)
        li = np.clip(idx - 1, 0, len(vx) - 1); ri = np.clip(idx, 0, len(vx) - 1)
        lx, rx = vx[li], vx[ri]
        dl = np.where(idx > 0, tx - lx, 10 ** 6); dr = np.where(idx < len(vx), rx - tx, 10 ** 6)
        gap = np.minimum(dl + dr, 10 ** 6)
        t = np.where((dl < 10 ** 6) & (dr < 10 ** 6), dl / np.maximum(gap, 1), np.where(dl < dr, 0.0, 1.0))[:, None]
        lin = vals[li] * (1 - t) + vals[ri] * t
        wl = np.exp(-dl / fall)[:, None]; wr = np.exp(-dr / fall)[:, None]
        ease = vals[li] * wl + vals[ri] * wr + med * np.clip(1 - wl - wr, 0, 1)
        ease = ease / np.maximum(wl + wr + np.clip(1 - wl - wr, 0, 1), 1e-6)
        a[y, tx] = np.where((gap < short)[:, None], lin, ease)
    return a

def repaint(spec, i2, hole):
    H2, W2 = hole.shape
    base = i2.astype(float)
    hole = hole.copy()
    for pf in spec.get('periodic', []):
        pm = cv2.resize(poly_mask((H2 * 2, W2 * 2), sc(pf['poly'])).astype(np.uint8), (W2, H2), interpolation=cv2.INTER_NEAREST).astype(bool)
        P = pf['period'] / 2
        ok = pm & ~ndi.binary_dilation(hole, iterations=4)
        todo = pm & hole
        for k in [1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 8, -8, 10, -10]:
            ys, xs = np.nonzero(todo)
            if len(ys) == 0: break
            sx = np.round(xs + k * P).astype(int)
            g = (sx >= 0) & (sx < W2)
            ys, xs, sx = ys[g], xs[g], sx[g]
            g = ok[ys, sx]
            base[ys[g], xs[g]] = base[ys[g], sx[g]]
            todo[ys[g], xs[g]] = False; hole[ys[g], xs[g]] = False
    left = hole.copy()
    for name, poly in spec['planes'].items():
        pm = cv2.resize(poly_mask((H2 * 2, W2 * 2), sc(poly)).astype(np.uint8), (W2, H2), interpolation=cv2.INTER_NEAREST).astype(bool)
        mm = None
        if name in spec.get('refx', {}):
            mm = np.zeros_like(pm)
            for xa, xb in spec['refx'][name]:
                mm[:, round(xa * K / 2):round(xb * K / 2)] = True
        base = plane_interp(base, hole, pm, mm)
        left &= ~pm
        if name == 'back':
            # continue vertical panel seams through repainted areas
            y0, y1 = [round(v * K / 2) for v in spec.get('seam_band', (55, 110))]
            band = base[y0:y1].mean(0).mean(-1)
            diff = band - ndi.median_filter(band, 31)
            prof = base[y0:y1].mean(0) - ndi.median_filter(base[y0:y1].mean(0), size=(31, 1))
            xs = [x for x in range(6, W2 - 6) if diff[x] < -10 and diff[x] == diff[x - 3:x + 4].min() and pm[(y0 + y1) // 2, x]
                  and prof[x, 0] - prof[x, 1] < 4]  # plum lines are lamp cords, not seams
            for x in xs:
                for dx in range(-5, 6):
                    col = (hole & pm)[:, x + dx]
                    base[col, x + dx] += prof[x + dx]
    if left.any():
        base = cv2.inpaint(np.clip(base, 0, 255).astype(np.uint8), left.astype(np.uint8), 7, cv2.INPAINT_TELEA).astype(float)
    return np.clip(base, 0, 255)

def shell(room):
    spec = ROOMS[room]; img = load(spec['src']); H, W = img.shape[:2]
    M = dict(np.load(OUT / 'work' / f'{room}_masks_final.npz'))
    hole = np.zeros((H, W), bool)
    for k, m in M.items(): hole |= m
    hole = ndi.binary_dilation(hole, iterations=3)
    h2 = cv2.resize(hole.astype(np.uint8), (W // 2, H // 2), interpolation=cv2.INTER_NEAREST)
    i2 = cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    for fill in spec.get('fills', []):  # hand patch copies for big repaints: (dst poly, dx, dy) in ref px
        pm = cv2.resize(poly_mask((H, W), sc(fill[0])).astype(np.uint8), (W // 2, H // 2), interpolation=cv2.INTER_NEAREST).astype(bool)
        dx, dy = round(fill[1] * K / 2), round(fill[2] * K / 2)
        ys, xs = np.nonzero(pm & h2.astype(bool))
        i2[ys, xs] = i2[ys + dy, xs + dx]; h2[ys, xs] = 0
    # --- lights: estimate additive glow inside the hand-drawn cones, quarter res
    lt_body, Hq, Wq = [], H // 4, W // 4
    q = cv2.resize(i2, (Wq, Hq), interpolation=cv2.INTER_AREA).astype(float)
    hq = cv2.resize(h2, (Wq, Hq), interpolation=cv2.INTER_NEAREST).astype(bool)
    hq = ndi.binary_dilation(hq, iterations=3)
    gm = np.zeros((Hq, Wq), int)
    for i, g in enumerate(spec.get('glows', [])):
        pm = cv2.resize(poly_mask((H, W), sc(g['poly'])).astype(np.uint8), (Wq, Hq), interpolation=cv2.INTER_NEAREST).astype(bool)
        gm[pm & (gm == 0)] = i + 1
    if gm.any():
        bad = (gm > 0) | hq
        U = row_interp_valid(q, bad, ~bad, short=10 ** 7)
        w = ((gm > 0) & ~hq).astype(float)
        D = np.clip(q - U, 0, None) * w[..., None]
        D = ndi.gaussian_filter(D, (8, 8, 0)) / np.maximum(ndi.gaussian_filter(w, 8), 0.05)[..., None]
        feather = ndi.gaussian_filter((gm > 0).astype(float), 6)
        D = D * feather[..., None]
        lt_body = fit_lights(spec, D, ~hq, W, H, Wq, Hq)
    lp = OUT / room / f'{room}_lights.svg'
    lp.write_text(svg_doc(W, H, lt_body))
    L = render(lp, W // 2, H // 2).astype(float)
    base2 = np.clip(i2.astype(float) - L[..., :3] * L[..., 3:4] / 255.0, 0, 255)
    if 'mist' in spec:
        mi = spec['mist']
        qd = cv2.resize(base2, (Wq, Hq), interpolation=cv2.INTER_AREA)
        rm = cv2.resize(poly_mask((H, W), sc(mi['region'])).astype(np.uint8), (Wq, Hq), interpolation=cv2.INTER_NEAREST).astype(bool)
        ok = rm & ~hq
        U = np.zeros_like(qd)
        rows = [y for y in range(Hq) if ok[y].sum() > 10]
        for y in rows:
            v = qd[y, ok[y]]; lum = v.mean(-1)
            U[y] = v[lum <= np.percentile(lum, 30)].mean(0)
        U = ndi.gaussian_filter1d(U, 6, axis=0)
        col = np.array([int(mi['color'][i:i + 2], 16) for i in (1, 3, 5)], float)
        Dm = np.clip(qd - U, 0, None) * ok[..., None]
        w = ok.astype(float)
        Dm = ndi.gaussian_filter(Dm, (5, 5, 0)) / np.maximum(ndi.gaussian_filter(w, 5), 0.05)[..., None] * rm[..., None]
        alpha = np.clip((Dm * col).sum(-1) / (col ** 2).sum(), 0, 0.9)
        alpha = np.clip(alpha - 0.05, 0, None)
        mp = OUT / room / f'{room}_mist.svg'
        mp.write_text(svg_doc(W, H, [levels_svg(alpha, mi['color'], 4, 'mist', nlev=16)]))
        Lm = render(mp, W // 2, H // 2).astype(float)
        base2 = np.clip(base2 - Lm[..., :3] * Lm[..., 3:4] / 255.0, 0, 255)
        print('mist KB', mp.stat().st_size // 1024)
    base2 = base2.astype(np.uint8)
    base2 = repaint(spec, base2, h2.astype(bool))
    rgba = np.dstack([base2, np.full(base2.shape[:2], 255)]).astype(np.uint8)
    Image.fromarray(rgba[..., :3]).save(OUT / 'work' / f'{room}_base.png')
    sp = OUT / room / f'{room}_shell.svg'
    sp.write_text(svg_doc(W, H, ['<g transform="scale(2)">'] + trace(rgba, 1, filter_speckle=10, layer_difference=16, color_precision=8) + ['</g>'], 'shell'))
    print('shell KB', sp.stat().st_size // 1024, 'lights KB', lp.stat().st_size // 1024)
    json.dump(spec.get('glows', []), open(OUT / 'work' / f'{room}_glows.json', 'w'))

if __name__ == '__main__' and stage in ('shell', 'all'):
    shell(room)

def compose(room, ids_hidden=()):
    spec = ROOMS[room]; img = load(spec['src']); H, W = img.shape[:2]
    meta = json.load(open(OUT / 'work' / f'{room}_objmeta.json'))
    out = render(OUT / room / f'{room}_shell.svg', W, H)[..., :3].astype(float)
    out = add_light(out, render(OUT / room / f'{room}_lights.svg', W, H).astype(float))
    if (OUT / room / f'{room}_mist.svg').exists():
        out = add_light(out, render(OUT / room / f'{room}_mist.svg', W, H).astype(float))
    shell_only = out.copy()
    order = [o['id'] for o in spec['objects']][::-1]
    for oid in order:
        for k in [oid] + [k for k, b in meta.items() if b.get('parent') == oid]:
            b = meta[k]
            r = render(OUT / room / 'objects' / f'{room}_{k}.svg', b['w'], b['h'])
            out = over(out, r, b['x'], b['y'])
    for e in spec.get('extra_layers', []):
        out = add_light(out, render(OUT / room / e, W, H).astype(float))
    cd = OUT / room / 'check'; cd.mkdir(exist_ok=True)
    M = dict(np.load(OUT / 'work' / f'{room}_masks_final.npz'))
    hole = np.zeros((H, W), bool)
    for m in M.values(): hole |= m
    rm = dict(room=round(mae4(out, img), 2), shell_region=round(mae4(out, img, ~ndi.binary_dilation(hole, iterations=6)), 2))
    print('room MAE', rm)
    json.dump(rm, open(OUT / 'work' / f'{room}_room_mae.json', 'w'))
    save_png(out, OUT / room / f'{room}_composite.png')
    save_png(shell_only, cd / f'{room}_shell_only.png')
    sep = np.zeros((H, 24, 3)) + (244, 230, 200)
    save_png(np.hstack([img, sep, out]), cd / f'{room}_side_by_side.png')
    save_png(img * 0.5 + out * 0.5, cd / f'{room}_onion.png')
    return out

if __name__ == '__main__' and stage in ('compose', 'all'):
    compose(room)
