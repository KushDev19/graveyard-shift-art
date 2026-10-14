"""Job H build: python build.py REACTOR|SWITCH  (run from this folder)."""
import sys, json, pathlib, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import seg, rooms, inpaint, svgtools as sv, masks as mk

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[2]
S = 2  # work scale


def bbox(m, pad=3):
    ys, xs = np.nonzero(m)
    x0, y0 = max(xs.min() - pad, 0) // 2 * 2, max(ys.min() - pad, 0) // 2 * 2
    x1, y1 = (xs.max() + pad + 2) // 2 * 2, (ys.max() + pad + 2) // 2 * 2
    return x0, y0, min(x1, m.shape[1] // 2 * 2), min(y1, m.shape[0] // 2 * 2)


def piece_svg(img, layers, box, title, extra_attr=None):
    """layers: list of (gid, mask). box in work px. Returns svg text in source px units."""
    x0, y0, x1, y1 = box
    groups = []
    for gid, m in layers:
        paths = sv.trace(img[y0:y1, x0:x1], m[y0:y1, x0:x1])
        ex = (extra_attr or {}).get(gid, '')
        groups.append(sv.group(gid, paths, 'scale(2)', ex))
    return sv.doc((x1 - x0) * S, (y1 - y0) * S, ''.join(groups), title)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def export_png(svg_text, w_src, path):
    a = sv.render(svg_text, w_src // 2)
    Image.fromarray(a).save(path, optimize=True)
    return a


def k(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def dil(m, r):
    return cv2.dilate(m.astype(np.uint8), k(r)) > 0


def paste(canvas, rgba, x, y):
    h, w = rgba.shape[:2]
    h = min(h, canvas.shape[0] - y); w = min(w, canvas.shape[1] - x)
    a = rgba[:h, :w, 3:4] / 255.0
    canvas[y:y + h, x:x + w, :3] = canvas[y:y + h, x:x + w, :3] * (1 - a) + rgba[:h, :w, :3] * a


def build_room(R, special):
    name = R['room']
    full = Image.open(ROOT / R['source']).convert('RGB')
    W, H = full.size
    W2, H2 = W // 2 * 2, H // 2 * 2
    scratch = HERE / '_cache'
    scratch.mkdir(exist_ok=True)
    img, masks = mk.build(R, scratch / f'{name}_masks.npz')
    h, w = img.shape[:2]
    objs, hole = [], np.zeros((h, w), bool)
    for p in R['pieces']:
        m = masks[p['id']]
        hole |= m
        if p.get('kind') == 'steam' or not m.any():
            continue
        md = dil(m, 1)
        if p.get('fill_under'):
            # repaint the desk top under the props that sit on it, so the desk works on its own
            hull = np.zeros((h, w), np.uint8)
            pts = np.column_stack(np.nonzero(m)[::-1]).astype(np.int32)
            cv2.fillPoly(hull, [cv2.convexHull(pts)], 1)
            under = np.zeros((h, w), bool)
            for q in p['fill_under']:
                under |= masks[q]
            under = dil(under, 2) & (hull > 0) & ~m
            md = dil(m | under, 1)
            dimg = inpaint.telea(img, under, md)
            box = bbox(md)
            o = dict(svg=piece_svg(dimg, [(p['id'], md)], box, f'{name} {p["id"]}'), box=box)
        elif p['id'] in special:
            o = special[p['id']](img, md, p, R)
        else:
            box = bbox(md)
            x0, y0, x1, y1 = box
            if (x1 - x0) * (y1 - y0) < 90000 or p.get('fullres'):
                fimg = np.asarray(full)
                fm = cv2.resize(md[y0:y1, x0:x1].astype(np.float32), ((x1 - x0) * 2, (y1 - y0) * 2), interpolation=cv2.INTER_LINEAR) > 0.5
                paths = sv.trace(fimg[y0 * 2:y1 * 2, x0 * 2:x1 * 2], fm, speckle=6)
                svg = sv.doc((x1 - x0) * 2, (y1 - y0) * 2, sv.group(p['id'], paths), f'{name} {p["id"]}')
            else:
                svg = piece_svg(img, [(p['id'], md)], box, f'{name} {p["id"]}')
            o = dict(svg=svg, box=box)
        if 'glow' in p:
            gx, gy, gr, gc = p['glow']
            o.setdefault('extra_files', {})[f'{name}_{p["id"]}_glow.svg'] = glow_svg(gr * 2, gr * 2, gc, f'{p["id"]} glow (additive)')
            o['glow_w'] = gr * 2
            o['glow_box'] = [gx - gr, gy - gr, gr * 2, gr * 2]
            o.setdefault('layers', {})['glow'] = f'objects/{name}_{p["id"]}_glow.svg'
        o.update(id=p['id'], p=p, mask=m)
        objs.append(o)
        print('traced', p['id'], len(o['svg']) // 1024, 'KB')
    vv = seg.hsv(img)[2]
    hole_d = dil(hole, 3)
    shell_img = inpaint.repaint(img, hole_d, R['zones'], h, w)
    shell_img = R.get('shell_fix', lambda a, im: a)(shell_img, img)
    Image.fromarray(shell_img).save(scratch / f'{name}_shell_raster.png')
    shell_paths = sv.trace_quant(shell_img, np.ones((h, w), bool))
    shell_svg = sv.doc(W2, H2, sv.group(f'{name}_shell', shell_paths, 'scale(2)'), f'{name} shell')
    print('shell', len(shell_svg) // 1024, 'KB')
    return dict(R=R, name=name, W=W2, H=H2, img=img, masks=masks, objs=objs, shell_svg=shell_svg, full=full)


def order(objs):
    rank = {'wall': 0, 'floor': 1, 'sorted': 2}
    return sorted(objs, key=lambda o: (rank[o['p'].get('layer', 'sorted')], o['p'].get('sortY', 0)))


def verify_and_export(B):
    name, img, W, H = B['name'], B['img'], B['W'], B['H']
    h, w = img.shape[:2]
    chk = OUT / 'check'; chk.mkdir(exist_ok=True)
    objdir = OUT / 'objects'; objdir.mkdir(exist_ok=True)
    pngdir = OUT / 'png'; pngdir.mkdir(exist_ok=True)
    write(OUT / f'{name}_shell.svg', B['shell_svg'])
    comp = export_png(B['shell_svg'], W, pngdir / f'{name}_shell.png')[..., :3].astype(float).copy()
    comp = comp[:h, :w]
    renders = {}
    for o in order(B['objs']):
        x0, y0, x1, y1 = o['box']
        f = objdir / f'{name}_{o["id"]}.svg'
        write(f, o['svg'])
        o['file'] = f'objects/{f.name}'
        a = export_png(o['svg'], (x1 - x0) * 2, pngdir / f'{name}_{o["id"]}.png')
        for lname, ltxt in o.get('extra_files', {}).items():
            write(objdir / lname, ltxt)
            export_png(ltxt, (x1 - x0) * 2 if 'glow' not in lname else o.get('glow_w', (x1 - x0) * 2), pngdir / lname.replace('.svg', '.png'))
        renders[o['id']] = a
        paste(comp, a, x0, y0)
    Image.fromarray(comp.astype(np.uint8)).save(chk / f'{name}_composite.png')
    # metrics on 4x downscale (quarter source)
    q = lambda a: cv2.resize(a.astype(np.float32), (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    o4 = np.asarray(B['full'].resize((W // 4, H // 4), Image.BOX), np.float32)
    c4 = q(comp)
    err = np.abs(o4 - c4).mean(2)
    metrics = {}
    anyobj = np.zeros((h, w), bool)
    for o in B['objs']:
        m4 = cv2.resize(o['mask'].astype(np.float32), (W // 4, H // 4), interpolation=cv2.INTER_AREA) > 0.25
        metrics[o['id']] = round(float(err[m4].mean()), 2)
        anyobj |= o['mask']
        # check images
        x0, y0, x1, y1 = o['box']
        mx = 20
        cx0, cy0, cx1, cy1 = max(x0 - mx, 0), max(y0 - mx, 0), min(x1 + mx, w), min(y1 + mx, h)
        orig = img[cy0:cy1, cx0:cx1]
        cc = comp[cy0:cy1, cx0:cx1].astype(np.uint8)
        sbs = np.concatenate([orig, np.full((orig.shape[0], 8, 3), 255, np.uint8), cc], 1)
        sc = min(1.0, 1400 / sbs.shape[1])
        Image.fromarray(sbs).resize((int(sbs.shape[1] * sc), int(sbs.shape[0] * sc))).save(chk / f'{name}_{o["id"]}_side_by_side.png')
        on = orig.astype(float).copy()
        lay = np.zeros((cy1 - cy0, cx1 - cx0, 4))
        a = renders[o['id']]
        lay[y0 - cy0:y0 - cy0 + a.shape[0], x0 - cx0:x0 - cx0 + a.shape[1]] = a[:cy1 - y0, :cx1 - x0]
        al = lay[..., 3:4] / 255 * 0.5
        on = on * (1 - al) + lay[..., :3] * al
        sc = min(1.0, 900 / on.shape[1])
        Image.fromarray(on.astype(np.uint8)).resize((int(on.shape[1] * sc), int(on.shape[0] * sc))).save(chk / f'{name}_{o["id"]}_onion.png')
    s4 = cv2.resize((~anyobj).astype(np.float32), (W // 4, H // 4), interpolation=cv2.INTER_AREA) > 0.99
    metrics['_shell_visible'] = round(float(err[s4].mean()), 2)
    metrics['_room_total'] = round(float(err.mean()), 2)
    sbs = np.concatenate([np.asarray(B['full'].resize((W // 4, H // 4), Image.BOX)), np.full((H // 4, 8, 3), 255, np.uint8), c4.astype(np.uint8)], 1)
    Image.fromarray(sbs).save(chk / f'{name}_room_side_by_side.png')
    return metrics, comp


def glow_svg(w, h, color, title, rx=None, ry=None, stops=((0, 0.85), (0.45, 0.35), (1, 0))):
    rx, ry = rx or w / 2, ry or h / 2
    st = ''.join(f'<stop offset="{o}" stop-color="{color}" stop-opacity="{a}"/>' for o, a in stops)
    defs = f'<radialGradient id="g">{st}</radialGradient>'
    return sv.doc(w, h, f'<g id="glow"><ellipse cx="{w / 2}" cy="{h / 2}" rx="{rx}" ry="{ry}" fill="url(#g)"/></g>', title, defs)


def core_handler(img, m, p, R):
    import coresplit
    housing, disc, cage, sphere = coresplit.split(img, m)
    sph_img = inpaint.telea(img, cage & disc, disc)
    box = bbox(m)
    x0, y0, x1, y1 = box
    parts = {}
    for gid, src, mm in [('core_housing', img, housing), ('core_sphere', sph_img, disc), ('core_cage', img, cage)]:
        if gid == 'core_sphere':
            parts[gid] = sv.trace_quant(src[y0:y1, x0:x1], dil(mm, 1)[y0:y1, x0:x1], n=28, speckle=4, median=3)
        else:
            parts[gid] = sv.trace(src[y0:y1, x0:x1], dil(mm, 1)[y0:y1, x0:x1])
    W, H = (x1 - x0) * 2, (y1 - y0) * 2
    ys, xs = np.nonzero(disc)
    cx, cy = (xs.min() + xs.max()) / 2 * 2 - x0 * 2, (ys.min() + ys.max()) / 2 * 2 - y0 * 2
    rx, ry = (xs.max() - xs.min()) * 1.0 + 0, (ys.max() - ys.min()) * 1.0
    gw, gh = int(rx * 2.2) // 2 * 2, int(ry * 2.2) // 2 * 2
    glow = glow_svg(gw, gh, '#FF8A5C', 'reactor core glow (additive, pulse opacity 0..0.6)')
    combined = sv.doc(W, H, ''.join(sv.group(g, parts[g], 'scale(2)') for g in parts), 'reactor core (housing, sphere, cage)')
    files = {f'reactor_{g}.svg': sv.doc(W, H, sv.group(g, parts[g], 'scale(2)'), f'reactor {g}') for g in parts}
    files['reactor_core_glow.svg'] = glow
    return dict(svg=combined, box=box, extra_files=files, glow_w=gw,
                layers={g: f'objects/reactor_{g}.svg' for g in parts} | {'core_glow': 'objects/reactor_core_glow.svg'},
                glow_box=[int(x0 * 2 + cx - gw / 2), int(y0 * 2 + cy - gh / 2), gw, gh], pulse_center=[int(x0 * 2 + cx), int(y0 * 2 + cy)])


def steam_sprite(full, rect, out_name):
    x0, y0, x1, y1 = rect
    crop = np.asarray(full.crop(rect))
    hh, ss, vv = seg.hsv(crop)
    light = (vv > 0.55) & (ss < 0.3)
    light = cv2.morphologyEx(light.astype(np.uint8), cv2.MORPH_OPEN, k(14)) > 0   # drop the thin jet streak
    n, lab, st, _ = cv2.connectedComponentsWithStats(light.astype(np.uint8), 8)
    light = lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    light = seg.clean(light, 3, 50)
    ring = dil(light, 22) & ~light & (vv < 0.32)
    oc = '#%02X%02X%02X' % tuple(np.median(crop[ring], 0).astype(int))
    light = cv2.morphologyEx(light.astype(np.uint8), cv2.MORPH_OPEN, k(6)) > 0
    sil = seg.clean(dil(light, 15), 3, 50)
    bx = bbox(sil, 4)
    sx0, sy0, sx1, sy1 = bx
    cnts, _ = cv2.findContours(sil[sy0:sy1, sx0:sx1].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    d = ''.join('M' + ' '.join(f'{p[0][0]},{p[0][1]}' for p in cv2.approxPolyDP(c, 1.2, True)) + 'Z' for c in cnts)
    inner = sv.trace(crop[sy0:sy1, sx0:sx1], dil(light, 1)[sy0:sy1, sx0:sx1], speckle=6)
    w, h = sx1 - sx0, sy1 - sy0
    body = f'<g id="steam_puff" data-pivot="{w // 2},{h // 2}"><path id="outline" d="{d}" fill="{oc}" stroke="{oc}" stroke-width="3" stroke-linejoin="round"/>' + sv.group('fill', inner)[0:] + '</g>'
    txt = sv.doc(w, h, body, 'steam puff particle sprite')
    return txt, (x0 + sx0, y0 + sy0, w, h)


def manifest(B, metrics):
    R = B['R']
    objs = []
    for o in order(B['objs']):
        p = o['p']
        x0, y0, x1, y1 = o['box']
        e = dict(id=p['id'], file=o['file'], x=int(x0 * 2), y=int(y0 * 2), w=int((x1 - x0) * 2), h=int((y1 - y0) * 2),
                 layer=p.get('layer', 'sorted'), sortY=p.get('sortY', int(y1 * 2)), collision=[list(c) for c in p.get('collision', [])])
        if 'pivot' in p:
            e['pivot'] = p['pivot']
        for key in ('layers', 'glow_box', 'pulse_center', 'note', 'lamps'):
            if key in o:
                e[key] = o[key]
        for key in ('note', 'attach'):
            if key in p:
                e[key] = p[key]
        e['mae'] = metrics.get(p['id'])
        objs.append(e)
    return dict(room=B['name'], source=R['source'], size=[B['W'], B['H']], shell=f'{B["name"]}_shell.svg',
                lights_file=f'{B["name"]}_lights.svg', layer_order='shell, wall, floor, sorted (by sortY, with players), lights',
                objects=objs, walkable=[list(p) for p in R['walkable']], doors=R['doors'], anchors=R['anchors'],
                lights=R['lights'], sprites=B.get('sprites', {}), mae=metrics)


def lights_svg(B):
    defs, body = '', ''
    for L in B['R']['lights']:
        defs += (f'<radialGradient id="l_{L["id"]}"><stop offset="0" stop-color="{L["color"]}" stop-opacity="0.55"/>'
                 f'<stop offset="0.5" stop-color="{L["color"]}" stop-opacity="0.2"/><stop offset="1" stop-color="{L["color"]}" stop-opacity="0"/></radialGradient>')
        body += f'<circle id="light_{L["id"]}" cx="{L["x"]}" cy="{L["y"]}" r="{L["radius"]}" fill="url(#l_{L["id"]})"/>'
    return sv.doc(B['W'], B['H'], f'<g id="{B["name"]}_lights">{body}</g>', f'{B["name"]} light pools (additive overlay)', defs)


def debug(B, man, comp):
    sc = 0.25
    im = Image.fromarray(comp.astype(np.uint8)).resize((B['W'] // 4, B['H'] // 4)).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    P = lambda pts: [(x * sc, y * sc) for x, y in pts]
    d.polygon(P(man['walkable']), fill=(0, 255, 0, 50), outline=(0, 255, 0, 255))
    for o in man['objects']:
        if o['collision']:
            d.polygon(P(o['collision']), fill=(255, 0, 0, 70), outline=(255, 0, 0, 255))
        if o['layer'] == 'sorted':
            d.line([(o['x'] * sc, o['sortY'] * sc), ((o['x'] + o['w']) * sc, o['sortY'] * sc)], fill=(40, 120, 255, 255), width=2)
        d.rectangle([o['x'] * sc, o['y'] * sc, (o['x'] + o['w']) * sc, (o['y'] + o['h']) * sc], outline=(255, 255, 255, 90))
        d.text((o['x'] * sc + 3, o['y'] * sc + 2), o['id'], fill=(255, 255, 255, 255))
    for dr in man['doors']:
        d.rectangle([dr['x'] * sc, dr['y'] * sc, (dr['x'] + dr['w']) * sc, (dr['y'] + dr['h']) * sc], outline=(255, 0, 255, 255), width=2)
    def pts(v):
        return [v] if isinstance(v[0], (int, float)) else v
    for name, v in man['anchors'].items():
        for x, y in pts(v):
            d.ellipse([x * sc - 6, y * sc - 6, x * sc + 6, y * sc + 6], fill=(255, 230, 0, 255), outline=(0, 0, 0, 255))
            d.text((x * sc + 8, y * sc - 6), name, fill=(255, 230, 0, 255))
    for L in man['lights']:
        r = L['radius'] * sc
        d.ellipse([L['x'] * sc - r, L['y'] * sc - r, L['x'] * sc + r, L['y'] * sc + r], outline=(255, 200, 80, 160))
    Image.alpha_composite(im, ov).convert('RGB').save(OUT / 'check' / f'{B["name"]}_manifest_debug.png')


def run(key):
    R = getattr(rooms, key)
    special = {'core': core_handler}
    special.update(EXTRA_SPECIAL.get(key, {}))
    B = build_room(R, special)
    for d in ('png', 'objects', 'check'):
        (OUT / d).mkdir(exist_ok=True)
    sprites = {}
    for sp in R.get('steam_sprite', []):
        txt, b = steam_sprite(B['full'], sp['rect'], sp['file'])
        write(OUT / 'objects' / sp['file'], txt)
        export_png(txt, b[2], OUT / 'png' / sp['file'].replace('.svg', '.png'))
        sprites['steam_puff'] = dict(file='objects/' + sp['file'], w=b[2], h=b[3], source_xy=[int(b[0]), int(b[1])], pivot=[b[2] // 2, b[3] // 2])
    B['sprites'] = sprites
    metrics, comp = verify_and_export(B)
    write(OUT / f'{B["name"]}_lights.svg', lights_svg(B))
    export_png(lights_svg(B), B['W'], OUT / 'png' / f'{B["name"]}_lights.png')
    man = manifest(B, metrics)
    write(OUT / f'{B["name"]}.json', json.dumps(man, indent=1, default=int))
    debug(B, man, comp)
    print(json.dumps(metrics, indent=0))


def switch_handler(img, m, p, R):
    hh, ss, vv = seg.hsv(img)
    bulb = m & (hh >= 165) & (hh <= 215) & (ss > 0.3) & (vv > 0.75)
    bulb = seg.clean(cv2.morphologyEx(bulb.astype(np.uint8), cv2.MORPH_OPEN, k(1)) > 0, 1, 25)
    zone = dil(bulb, 12) & m
    # one group per bulb: every lamp pixel goes to its nearest measured bulb position (Voronoi)
    seeds = np.array(p['lamp_seeds'], float) / 2
    yy, xx = np.nonzero(zone)
    d = (xx[:, None] - seeds[None, :, 0]) ** 2 + (yy[:, None] - seeds[None, :, 1]) ** 2
    lab = np.zeros(zone.shape, np.int32)
    lab[yy, xx] = d.argmin(1) + 1
    n = len(seeds) + 1
    st = np.zeros((n, 5), int)
    for i in range(1, n):
        y_, x_ = np.nonzero(lab == i)
        if len(x_):
            st[i] = [x_.min(), y_.min(), x_.max() - x_.min() + 1, y_.max() - y_.min() + 1, len(x_)]
    # unlit version: glass dimmed, cyan halo pulled back to the panel colour
    hsvi = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    panel = m & ~dil(bulb, 30) & (vv > 0.45) & (vv < 0.9) & (hh >= 150) & (hh <= 220) & (ss > 0.1)
    ph, ps = np.median(hsvi[..., 0][panel]), np.median(hsvi[..., 1][panel])
    off = hsvi.copy()
    b = bulb
    off[..., 1][b] *= 0.7
    off[..., 2][b] *= 0.45
    halo = zone & ~bulb & (vv > 0.3)
    off[..., 0][halo] = ph
    off[..., 1][halo] = np.minimum(off[..., 1][halo], ps)
    off[..., 2][halo] *= 0.93
    off = cv2.cvtColor(off.astype(np.uint8), cv2.COLOR_HSV2RGB)
    box = bbox(m)
    x0, y0, x1, y1 = box
    body = sv.trace(off[y0:y1, x0:x1], m[y0:y1, x0:x1])
    lamp_groups, lamps = [], []
    order_ = [i for i in range(1, n) if st[i, 4] > 0]
    for j, i in enumerate(order_):
        lm = lab == i
        paths = sv.trace(img[y0:y1, x0:x1], lm[y0:y1, x0:x1], speckle=2)
        gid = f'lamp_{j + 1:02d}'
        lamp_groups.append(sv.group(gid, paths, 'scale(2)'))
        lx, ly, lw, lh = st[i, :4]
        lamps.append(dict(id=gid, x=int(lx * 2), y=int(ly * 2), w=int(lw * 2), h=int(lh * 2), cx=int((lx + lw / 2) * 2), cy=int((ly + lh / 2) * 2)))
    W, H = (x1 - x0) * 2, (y1 - y0) * 2
    bodyg = sv.group('switchboard_body', body, 'scale(2)')
    lampg = '<g id="switchboard_lamps">' + ''.join(lamp_groups) + '</g>'
    files = {'switchboard_switchboard_body.svg': sv.doc(W, H, bodyg, 'switchboard body, lamps unlit'),
             'switchboard_switchboard_lamps.svg': sv.doc(W, H, lampg, 'switchboard lamps, lit (blink per lamp_NN group)')}
    return dict(svg=sv.doc(W, H, bodyg + lampg, 'switchboard (body + lit lamps)'), box=box, extra_files=files,
                layers={'body': 'objects/switchboard_switchboard_body.svg', 'lamps': 'objects/switchboard_switchboard_lamps.svg'}, lamps=lamps)


EXTRA_SPECIAL = {'SWITCH': {'switchboard': switch_handler}}

if __name__ == '__main__':
    run(sys.argv[1])
