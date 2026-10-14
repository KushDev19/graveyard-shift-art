"""Job I: Radio Room + Bridge -> layered SVG (trace, verify, export).
Usage: python build_i.py radio|bridge [masks]
  masks : only compute masks and write check/<room>_masks.png (fast segmentation check)
Pipeline per layer: hand shape -> outline-snapped mask (flood from outside through
non-outline pixels) -> children removed + repainted (inpaint) -> edge-preserving
flatten (mean shift) -> vtracer stacked colour trace -> SVG -> render -> MAE check."""
import io, json, math, pathlib, re, sys
import numpy as np, cv2, vtracer, cairosvg
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent
REPO = OUT.parents[2]
CHECK = OUT / 'check'
CREAM = (244, 230, 200)


def lum(a):
    a = a.astype(np.float32)
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114


def kern(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def dil(m, r):
    return cv2.dilate(m.astype(np.uint8), kern(r)).astype(bool) if r > 0 else m


def ero(m, r):
    return cv2.erode(m.astype(np.uint8), kern(r)).astype(bool) if r > 0 else m


def fill_holes(m):
    m8 = np.pad(m.astype(np.uint8), 1)
    ff = m8.copy()
    h, w = ff.shape
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    return (m8.astype(bool) | (ff == 0))[1:-1, 1:-1]


def shape_mask(H, W, spec):
    m = np.zeros((H, W), np.uint8)
    for t, v in spec:
        if t == 'poly':
            cv2.fillPoly(m, [np.int32(v)], 1)
        elif t == 'rect':
            x0, y0, x1, y1 = v
            m[y0:y1, x0:x1] = 1
        elif t == 'ellipse':
            cx, cy, rx, ry = v[:4]
            cv2.ellipse(m, (cx, cy), (rx, ry), v[4] if len(v) > 4 else 0, 0, 360, 1, -1)
        elif t == 'circle':
            cv2.circle(m, (v[0], v[1]), v[2], 1, -1)
        elif t == 'line':  # thick line (x0,y0,x1,y1,width)
            cv2.line(m, (v[0], v[1]), (v[2], v[3]), 1, v[4])
    return m.astype(bool)


def bbox(m, pad=0, H=None, W=None):
    ys, xs = np.where(m)
    H = H or m.shape[0]
    W = W or m.shape[1]
    return max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + 1 + pad, W), min(ys.max() + 1 + pad, H)


def refine(img, P, T=58, pad=10, open_r=6, minfrac=0.35):
    """Snap a generous hand shape to the painted outlines."""
    x0, y0, x1, y1 = bbox(P, pad + 4)
    crop = img[y0:y1, x0:x1]
    reg = dil(P[y0:y1, x0:x1], pad)
    free = (lum(crop) >= T) | ~reg
    _, lab = cv2.connectedComponents(free.astype(np.uint8), connectivity=4)
    outl = np.unique(lab[~reg])
    bg = np.isin(lab, outl) & free
    obj = fill_holes(reg & ~bg)
    if open_r:
        core = cv2.morphologyEx(obj.astype(np.uint8), cv2.MORPH_OPEN, kern(open_r)).astype(bool)
        obj = core | (obj & dil(core, open_r))
    obj = fill_holes(dil(obj, 4) & reg)
    if obj.sum() < minfrac * P[y0:y1, x0:x1].sum():
        print('  refine fallback (leak)', int(obj.sum()), int(P[y0:y1, x0:x1].sum()))
        obj = P[y0:y1, x0:x1]
    out = np.zeros_like(P)
    out[y0:y1, x0:x1] = obj
    return out


def refine_gc(img, P, pad=30, iters=6):
    """GrabCut snap for objects on dark floors where outlines are washed out by glow."""
    x0, y0, x1, y1 = bbox(P, pad + 4)
    crop = np.ascontiguousarray(img[y0:y1, x0:x1])
    h, w = crop.shape[:2]
    sm = cv2.resize(crop, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    Pc = cv2.resize(P[y0:y1, x0:x1].astype(np.uint8), (w // 2, h // 2), interpolation=cv2.INTER_NEAREST).astype(bool)
    gm = np.full(Pc.shape, cv2.GC_BGD, np.uint8)
    gm[dil(Pc, pad // 2)] = cv2.GC_PR_BGD
    gm[Pc] = cv2.GC_PR_FGD
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(sm, gm, None, bg, fg, iters, cv2.GC_INIT_WITH_MASK)
    m = np.isin(gm, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR).astype(bool)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    if n > 1:
        big = st[1:, 4].max()
        m = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 0.05 * big])
    m = fill_holes(dil(m, 2))
    out = np.zeros_like(P)
    out[y0:y1, x0:x1] = m
    return out


def inpaint(img, mask, grow=4, r=6):
    m = dil(mask, grow)
    if not m.any():
        return img.copy()
    x0, y0, x1, y1 = bbox(m, 40)
    out = img.copy()
    out[y0:y1, x0:x1] = cv2.inpaint(img[y0:y1, x0:x1], m[y0:y1, x0:x1].astype(np.uint8), r, cv2.INPAINT_TELEA)
    return out


def inpaint_big(img, mask, grow=4, skip=3, take=6, side='both'):
    """Large holes (shell behind furniture): fill each masked row run with a straight blend
    between the clean colours just left and right of it. Keeps the flat wall/floor colour
    fields and horizontal seams; then smooth row-to-row jitter vertically."""
    m = dil(mask, grow)
    out = img.astype(np.float32).copy()
    H, W = m.shape
    for y in np.where(m.any(1))[0]:
        r = np.concatenate([[0], m[y].astype(np.int8), [0]])
        d = np.diff(r)
        for a, b in zip(np.where(d == 1)[0], np.where(d == -1)[0]):
            L = img[y, max(a - skip - take, 0):max(a - skip, 0)]
            R = img[y, min(b + skip, W):min(b + skip + take, W)]
            cl = np.median(L, 0) if len(L) and side != 'right' else None
            cr = np.median(R, 0) if len(R) and side != 'left' else None
            if cl is None and cr is None:
                continue
            cl = cr if cl is None else cl
            cr = cl if cr is None else cr
            t = np.linspace(0, 1, b - a)[:, None]
            out[y, a:b] = cl * (1 - t) + cr * t
    sm = cv2.blur(out, (1, 9))
    out[m] = sm[m]
    return np.clip(out, 0, 255).astype(np.uint8)


TRACE = dict(colormode='color', hierarchical='stacked', mode='spline', filter_speckle=6,
             color_precision=6, layer_difference=16, corner_threshold=60, length_threshold=4.0,
             splice_threshold=45, path_precision=1)
PATH_RE = re.compile(r'<path d="([^"]+)" fill="(#[0-9A-Fa-f]{6})" transform="translate\((-?[\d.]+),(-?[\d.]+)\)"\s*/>')


def trace(rgb, alpha, scale=1, ms=(6, 14), repair=True, repair_T=14, repair_k=12, **kw):
    if scale > 1:
        h, w = alpha.shape
        rgb = cv2.resize(rgb, (w // scale, h // scale), interpolation=cv2.INTER_AREA)
        alpha = cv2.resize(alpha.astype(np.uint8) * 255, (w // scale, h // scale), interpolation=cv2.INTER_AREA) > 127
    if ms:
        rgb = cv2.pyrMeanShiftFiltering(np.ascontiguousarray(rgb), ms[0], ms[1])
    rgba = np.dstack([rgb, alpha.astype(np.uint8) * 255])
    b = io.BytesIO()
    Image.fromarray(rgba).save(b, 'PNG')
    s = vtracer.convert_raw_image_to_svg(b.getvalue(), img_format='png', **{**TRACE, **kw})
    paths = []
    raw = re.findall(r'<path\b[^>]*/>', s)
    for el in raw:
        md = re.search(r'\bd="([^"]*)"', el)
        if not md or not md.group(1).strip():
            continue
        d = md.group(1).strip()
        f = re.search(r'fill="(#[0-9A-Fa-f]{6})"', el).group(1).upper()
        m = re.search(r'translate\((-?[\d.]+),\s*(-?[\d.]+)\)', el)
        tx, ty = (round(float(m.group(1)), 1), round(float(m.group(2)), 1)) if m else (0, 0)
        t = '' if (tx, ty) == (0, 0) else f' transform="translate({tx:g},{ty:g})"'
        paths.append(f'<path d="{d}" fill="{f}"{t}/>')
    body = '\n'.join(paths)
    if repair:  # vtracer sometimes drops a whole colour cluster: find and re-fill such areas
        hs, ws = alpha.shape
        r = render(svg_doc(ws, hs, body))
        if r.shape[:2] == alpha.shape:
            comp = over(np.zeros_like(rgb, np.float32), r, 0, 0)
            err = cv2.blur(np.abs(comp - rgb.astype(np.float32)).mean(-1) * alpha, (7, 7))
            bad = cv2.morphologyEx(((err > repair_T) & alpha).astype(np.uint8), cv2.MORPH_OPEN, kern(3))
            n, lb, st, _ = cv2.connectedComponentsWithStats(bad)
            bad = np.isin(lb, [i for i in range(1, n) if st[i, 4] > 150])
            if bad.any():
                body += '\n' + qtrace(rgb, dil(bad, 1) & alpha, 1, k=repair_k, stars=False)
    if scale > 1:
        body = f'<g transform="scale({scale})">\n{body}\n</g>'
    return body


def qtrace(rgb, alpha, scale=1, k=40, eps=0.9, stars=True):
    """Fallback tracer for soft painted gradients (nebulae): k-means posterise, then one
    even-odd polygon path per colour band, largest first, each grown 1 px to hide seams."""
    dots = []
    if stars:  # small bright specks become exact circles (k-means + median would erase them)
        sp = (lum(rgb) > 205) & alpha
        n, lb, st, cen = cv2.connectedComponentsWithStats(sp.astype(np.uint8))
        for i in range(1, n):
            if 3 <= st[i, 4] <= 900 and max(st[i, 2], st[i, 3]) < 40:
                c = rgb[lb == i].mean(0).astype(int)
                rr = math.sqrt(st[i, 4] / math.pi) + 0.6
                dots.append(f'<circle cx="{cen[i][0] + .5:.1f}" cy="{cen[i][1] + .5:.1f}" r="{rr:.1f}" fill="#{c[0]:02X}{c[1]:02X}{c[2]:02X}"/>')
    if scale > 1:
        h, w = alpha.shape
        rgb = cv2.resize(rgb, (w // scale, h // scale), interpolation=cv2.INTER_AREA)
        alpha = cv2.resize(alpha.astype(np.uint8) * 255, (w // scale, h // scale), interpolation=cv2.INTER_AREA) > 127
    lab = cv2.cvtColor(cv2.GaussianBlur(rgb, (0, 0), 1.0), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    rng = np.random.default_rng(1)
    idx = rng.choice(len(lab), min(60000, len(lab)), replace=False)
    _, _, cen = cv2.kmeans(lab[idx], k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 3, cv2.KMEANS_PP_CENTERS)
    d2 = ((lab[:, None, :] - cen[None]) ** 2).sum(-1)
    labels = d2.argmin(1).astype(np.uint8).reshape(alpha.shape)
    labels = cv2.medianBlur(labels, 5)
    flat = rgb.reshape(-1, 3)
    out = []
    order = np.argsort([-(labels == i).sum() for i in range(k)])
    for n, i in enumerate(order):
        m = (labels == i) & alpha
        if m.sum() < 6:
            continue
        col = np.median(flat[(labels == i).ravel()], 0).astype(int)
        if n:
            m = dil(m, 1) & alpha
        else:
            m = alpha.copy()
        cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        d = ''.join('M' + ' '.join(f'{p[0][0]} {p[0][1]}' for p in cv2.approxPolyDP(c, eps, True)) + 'Z' for c in cs if len(c) > 2)
        if d:
            out.append(f'<path fill-rule="evenodd" d="{d}" fill="#{col[0]:02X}{col[1]:02X}{col[2]:02X}"/>')
    body = '\n'.join(out)
    if scale > 1:
        body = f'<g transform="scale({scale})">\n{body}\n</g>'
    return body + ('\n' + '\n'.join(dots) if dots else '')


def trace_best(rgb, alpha, scale=1, ms=(6, 14), cands=None, cap_kb=1400, base=None):
    """vtracer's colour clustering is input-sensitive (it can drop a big cluster), so trace
    with a few settings, render each and keep the most faithful one under the size cap."""
    cands = cands or [{}, dict(color_precision=8, layer_difference=8)]
    h, w = alpha.shape
    best = None
    for c in cands:
        if 'qtrace' in c:
            body = qtrace(rgb, alpha, scale, k=c['qtrace'])
        else:
            body = trace(rgb, alpha, scale, ms=ms, **{**(base or {}), **c})
        r = render(svg_doc(w, h, body))
        if r.shape[:2] != alpha.shape:
            r = cv2.resize(r, (w, h))
        e = mae(over(np.zeros_like(rgb, np.float32), r, 0, 0), rgb, alpha)
        kb = len(body) / 1024
        ok = kb < cap_kb
        sc = e + kb / 400  # ~1 MB of SVG is worth ~2.5 MAE
        if best is None or (ok and (not best[2] or sc < best[5])):
            best = (e, kb, ok, body, c, sc)
    print(f'    best {best[4]} mae {best[0]:.2f} {best[1]:.0f}KB')
    return best[3]


def svg_doc(w, h, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'{inner}\n</svg>\n')


def render(svg_text, w=None):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=w)
    return np.array(Image.open(io.BytesIO(png)).convert('RGBA'))


def over(base, rgba, x, y):
    out = base.astype(np.float32).copy()
    if x < 0 or y < 0 or y + rgba.shape[0] > out.shape[0] or x + rgba.shape[1] > out.shape[1]:
        X0, Y0 = max(x, 0), max(y, 0)
        X1, Y1 = min(x + rgba.shape[1], out.shape[1]), min(y + rgba.shape[0], out.shape[0])
        rgba = rgba[Y0 - y:Y1 - y, X0 - x:X1 - x]
        x, y = X0, Y0
    h, w = rgba.shape[:2]
    a = rgba[..., 3:4].astype(np.float32) / 255
    out[y:y + h, x:x + w] = out[y:y + h, x:x + w] * (1 - a) + rgba[..., :3] * a
    return out


def mae(a, b, m):
    H, W = m.shape
    ds = lambda x: cv2.resize(x.astype(np.float32), (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    mm = ds(m.astype(np.float32)) > 0.5
    if not mm.any():
        return float('nan')
    return float(np.abs(ds(a) - ds(b))[mm].mean())


def shrink(im, maxw=1400):
    im = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)) if isinstance(im, np.ndarray) else im
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    return im


FONT = None


def save_check(im, path):
    """Check images are for eyes only: 256-colour PNG keeps the repo light."""
    im.convert('RGB').quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)


def font(sz):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def glow_svg(W, H, lights, gid):
    defs, circ = [], []
    for i, L in enumerate(lights):
        gidn = f'{gid}_g{i}'
        stops = L.get('stops', [(0, L.get('a', .55)), (1, 0)])
        st = ''.join(f'<stop offset="{o}" stop-color="{L["color"]}" stop-opacity="{a}"/>' for o, a in stops)
        if L.get('poly'):  # straight light spill (e.g. through a door): linear fade over a floor polygon
            gx0, gx1 = L['grad']
            defs.append(f'<linearGradient id="{gidn}" gradientUnits="userSpaceOnUse" x1="{gx0}" y1="0" x2="{gx1}" y2="0">{st}</linearGradient>')
            circ.append(f'<path d="M' + 'L'.join(f'{x} {y}' for x, y in L['poly']) + f'Z" fill="url(#{gidn})"/>')
            continue
        defs.append(f'<radialGradient id="{gidn}">{st}</radialGradient>')
        if L.get('ry'):
            circ.append(f'<ellipse cx="{L["x"]}" cy="{L["y"]}" rx="{L["radius"]}" ry="{L["ry"]}" fill="url(#{gidn})"/>')
        else:
            circ.append(f'<circle cx="{L["x"]}" cy="{L["y"]}" r="{L["radius"]}" fill="url(#{gidn})"/>')
    return svg_doc(W, H, f'<defs>{"".join(defs)}</defs>\n<g id="{gid}" style="mix-blend-mode:screen">\n' + '\n'.join(circ) + '\n</g>')


# ---------------------------------------------------------------- build
def build(cfg, masks_only=False):
    room = cfg['room']
    src = REPO / 'raw_originals' / cfg['src']
    img = np.array(Image.open(src).convert('RGB'))
    H, W = img.shape[:2]
    rdir = OUT / room
    (rdir / 'objects').mkdir(parents=True, exist_ok=True)
    CHECK.mkdir(exist_ok=True)
    layers = cfg['layers']
    by = {L['id']: L for L in layers}
    # 1. masks
    for L in layers:
        print(' mask', L['id'])
        if 'maskfn' in L:
            m = L['maskfn'](img, H, W)
        else:
            P = shape_mask(H, W, L['shape'])
            mode = L.get('refine', True)
            if mode == 'gc':
                m = refine_gc(img, P)
            elif mode:
                m = refine(img, P, T=L.get('T', 58), pad=L.get('pad', 10), open_r=L.get('open', 6))
            else:
                m = P
        L['mask'] = m
    for L in layers:
        for e in L.get('exclude', []):
            L['mask'] = L['mask'] & ~dil(by[e]['mask'], 1)
        if L.get('clipshape'):
            L['mask'] &= shape_mask(H, W, L['clipshape'])
    space = by.get('space')
    # overlay for segmentation check
    ov = img.astype(np.float32) * 0.45
    rng = np.random.default_rng(3)
    for L in layers:
        c = rng.integers(60, 255, 3)
        ov[L['mask']] = ov[L['mask']] * 0.3 + c * 0.7 + 0
    ovi = shrink(ov, 2000)
    d = ImageDraw.Draw(ovi)
    s = ovi.width / W
    for L in layers:
        x0, y0, x1, y1 = bbox(L['mask'])
        d.text((x0 * s + 2, y0 * s + 2), L['id'], fill=(255, 255, 255), font=font(14))
    save_check(ovi, CHECK / f'{room}_masks.png')
    print('masks done')
    if masks_only:
        return
    # 2. per-layer source pixels (children removed + repainted)
    top = [L for L in layers if not L.get('parent') and L['kind'] == 'object']
    results = []
    for L in layers:
        if L['kind'] == 'shell':
            continue
        kids = [k for k in layers if k.get('parent') == L['id']]
        m = L['mask']
        x0, y0, x1, y1 = bbox(m)
        if L['kind'] == 'space':  # padded so the layer can drift behind the frame
            pad = L.get('padout', 60)
            x0, y0, x1, y1 = bbox(m, pad)
            region = np.zeros_like(m)
            region[y0:y1, x0:x1] = True
            km = np.zeros_like(m)
            for k in kids:
                km |= k['mask']
            srcimg = inpaint(img, km, grow=5) if km.any() else img
            outside = region & ~ero(m, 4)
            sub = srcimg[y0:y1, x0:x1].copy()
            sub = cv2.inpaint(sub, outside[y0:y1, x0:x1].astype(np.uint8), 12, cv2.INPAINT_TELEA)
            alpha = region[y0:y1, x0:x1]
            L['xy'] = (x0, y0)
        else:
            srcimg = img
            for k in kids:
                srcimg = inpaint(srcimg, k['mask'] & m, grow=L.get('kidgrow', 3))
            if L.get('srcfn'):
                srcimg = L['srcfn'](srcimg, L, by)
            if L.get('fillexcl'):  # repaint where an excluded neighbour (chair, lamp) covered this object
                ex = np.zeros_like(m)
                for e in L.get('exclude', []):
                    ex |= by[e]['mask']
                closed = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, kern(L['fillexcl'])).astype(bool)
                fill = closed & ~m & ex
                srcimg = inpaint(srcimg, fill, grow=2)
                L['alpha'] = m | fill
            am = L.get('alpha', m)
            x0, y0, x1, y1 = bbox(am, 10 if L.get('vector') else 0)
            sub = srcimg[y0:y1, x0:x1]
            alpha = am[y0:y1, x0:x1]
            L['xy'] = (x0, y0)
        h, w = alpha.shape
        print('trace', L['id'], w, h)
        if L.get('vector'):  # clean geometry instead of a trace (e.g. meter needles)
            inner = L['vector'](L, x0, y0)
        elif L.get('unproject'):  # ellipse disc traced as a circle, squashed back (rotatable)
            cx, cy, k = L['unproject']
            hh = int(round(h / k))
            sub2 = cv2.resize(sub, (w, hh), interpolation=cv2.INTER_CUBIC)
            al2 = cv2.resize(alpha.astype(np.uint8), (w, hh), interpolation=cv2.INTER_NEAREST).astype(bool)
            body = trace_best(sub2, al2, 1, base=L.get('tr'))
            lcx, lcy = cx - x0, (cy - y0) / k
            inner = (f'<g transform="translate({lcx},{cy - y0}) scale(1,{k})">\n'
                     f'<g id="{L["id"]}_spin" data-pivot="0,0">\n<g transform="translate({-lcx},{-lcy:.1f})">\n{body}\n</g>\n</g>\n</g>')
        else:
            inner = trace_best(sub, alpha, L.get('scale', 1), ms=L.get('ms', (6, 14)), cands=L.get('cands'), base=L.get('tr'))
        piv = ''
        if L.get('pivot'):
            px, py = L['pivot']
            piv = f' data-pivot="{px - x0},{py - y0}"'
        txt = svg_doc(w, h, f'<g id="{room}_{L["id"]}"{piv}>\n{inner}\n</g>')
        fn = (rdir / 'objects' if L['kind'] == 'object' else rdir) / f'{room}_{L["id"]}.svg'
        fn.write_text(txt)
        L['file'] = fn
        L['svg'] = txt
        L['wh'] = (w, h)
    # 3. shell
    allobj = np.zeros((H, W), bool)
    for L in top:
        allobj |= L['mask']
    for L in layers:
        if L['kind'] == 'lights':
            allobj |= L['mask']
    hole = ero(space['mask'], 3) if space else np.zeros((H, W), bool)
    print('shell inpaint')
    lights = cfg['lights_fn'](layers, by) if 'lights_fn' in cfg else cfg.get('lights', [])
    pools = [L for L in lights if L.get('baked') is False]  # painted light pools taken out of the shell
    lights = [L for L in lights if L.get('baked') is not False]
    (rdir / f'{room}_lights_glow.svg').write_text(glow_svg(W, H, lights, f'{room}_lights_glow'))
    pools_r = None
    if pools:
        ptxt = glow_svg(W, H, pools, f'{room}_light_pools')
        (rdir / f'{room}_light_pools.svg').write_text(ptxt)
        pools_r = render(ptxt)
        Image.fromarray(pools_r).resize((W // 2, H // 2), Image.LANCZOS).save(rdir / f'{room}_light_pools.png')
    shimg = inpaint_big(img, allobj & ~hole)
    if pools_r is not None:  # un-screen the painted light pools; they come back as SVG gradients
        ga = pools_r[..., :3].astype(np.float32) / 255 * (pools_r[..., 3:4].astype(np.float32) / 255)
        ga[allobj] = 0  # only where the floor is actually seen
        base = (shimg.astype(np.float32) / 255 - ga) / np.maximum(1 - ga, 1e-3)
        shimg = np.clip(base * 255, 0, 255).astype(np.uint8)
    sh = (W // 2) * 2, (H // 2) * 2
    body = trace_best(shimg[:sh[1], :sh[0]], np.ones((sh[1], sh[0]), bool), 2, ms=cfg.get('shell_ms', (3, 8)),
                      cands=cfg.get('shell_cands', [dict(color_precision=8, layer_difference=6, repair_T=10, repair_k=24),
                                                    dict(color_precision=8, layer_difference=9, repair_T=10, repair_k=24)]))
    clip, cattr = '', ''
    if hole.any():  # window opening: the space layer shows through this cut-out
        cs, _ = cv2.findContours(hole.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        d = ''.join('M' + ' '.join(f'{p[0][0]} {p[0][1]}' for p in cv2.approxPolyDP(c, 1.2, True)) + 'Z' for c in cs)
        clip = f'<defs><clipPath id="{room}_window_cut"><path clip-rule="evenodd" d="M0 0H{W}V{H}H0Z{d}"/></clipPath></defs>\n'
        cattr = f' clip-path="url(#{room}_window_cut)"'
    shell_txt = svg_doc(W, H, f'{clip}<g id="{room}_shell"{cattr}>\n{body}\n</g>')
    shell_fn = rdir / f'{room}_shell.svg'
    shell_fn.write_text(shell_txt)
    Image.fromarray(shimg).resize((W // 4, H // 4)).save(CHECK / f'{room}_shell_repaint.jpg', quality=85)
    # 4. glow layer
    # 5. render, composite, verify
    print('verify')
    comp = np.zeros((H, W, 3), np.float32)
    order = [L for L in layers if L['kind'] == 'space'] + [L for L in layers if L.get('parent') == 'space']
    rest = [L for L in layers if L not in order and L['kind'] != 'shell']
    rest.sort(key=lambda L: (L.get('sortY', 0) if not L.get('parent') else by[L['parent']].get('sortY', 0) + .5))
    renders = {}
    for L in layers:
        if 'svg' in L:
            renders[L['id']] = render(L['svg'])
    for L in order:
        comp = over(comp, renders[L['id']], *L['xy'])
    shell_r = render(shell_txt)
    comp = over(comp, shell_r, 0, 0)
    if pools_r is not None:  # screen blend, as the painting's soft light pool
        g = pools_r[..., :3].astype(np.float32) * (pools_r[..., 3:4].astype(np.float32) / 255)
        comp = comp + g * (1 - comp / 255)
    for L in rest:
        comp = over(comp, renders[L['id']], *L['xy'])
    ref = img.astype(np.float32)
    rep = []
    for L in layers:
        if 'svg' not in L:
            continue
        r = renders[L['id']]
        x0, y0 = L['xy']
        w, h = L['wh']
        o = over(ref[y0:y0 + h, x0:x0 + w], r, 0, 0)
        for k in layers:  # assembled: children drawn on top of their parent
            if k.get('parent') == L['id'] and 'svg' in k:
                o = over(o, renders[k['id']], k['xy'][0] - x0, k['xy'][1] - y0)
        mk = L['mask'][y0:y0 + h, x0:x0 + w] if L['kind'] != 'space' else (L['mask'] & ~dil(allobj, 0))[y0:y0 + h, x0:x0 + w]
        e = mae(o, ref[y0:y0 + h, x0:x0 + w], mk)
        # outline alignment: edge maps (Canny) distance at full res
        ea = cv2.Canny(cv2.cvtColor(np.clip(o, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY), 60, 150) > 0
        eb = cv2.Canny(cv2.cvtColor(img[y0:y0 + h, x0:x0 + w], cv2.COLOR_RGB2GRAY), 60, 150) > 0
        dt = cv2.distanceTransform((~eb).astype(np.uint8), cv2.DIST_L2, 3)
        sel = ea & dil(mk, 2)
        med = float(np.median(dt[sel])) if sel.any() else 0
        p90 = float(np.percentile(dt[sel], 90)) if sel.any() else 0
        kb = len(L['svg']) / 1024
        rep.append(dict(id=L['id'], kind=L['kind'], file=str(L['file'].relative_to(OUT)), x=x0, y=y0, w=w, h=h,
                        mae=round(e, 2), edge_med=round(med, 1), edge_p90=round(p90, 1), kb=round(kb)))
        print(f"  {L['id']:18s} MAE {e:5.2f}  edge med {med:.1f} p90 {p90:.1f}px  {kb:6.0f} KB")
        # check images
        pad = 30
        X0, Y0 = max(x0 - pad, 0), max(y0 - pad, 0)
        X1, Y1 = min(x0 + w + pad, W), min(y0 + h + pad, H)
        a_ = ref[Y0:Y1, X0:X1]
        b_ = over(a_, r, x0 - X0, y0 - Y0)
        cre = np.full_like(a_, 0) + np.array(CREAM, np.float32)
        c_ = over(cre, r, x0 - X0, y0 - Y0)
        save_check(shrink(np.hstack([a_, b_, c_]), 1800), CHECK / f'{room}_{L["id"]}_side_by_side.png')
        save_check(shrink(a_ * .5 + b_ * .5, 1000), CHECK / f'{room}_{L["id"]}_onion.png')
        # exports: half-scale RGBA png
        Image.fromarray(r).resize((max(w // 2, 1), max(h // 2, 1)), Image.LANCZOS).save(L['file'].with_suffix('.png'))
    full = mae(comp, ref, np.ones((H, W), bool))
    shell_vis = ~allobj & ~(space['mask'] if space else False)
    e_sh = mae(over(np.zeros_like(ref), shell_r, 0, 0), ref, shell_vis & ~hole)
    rep.insert(0, dict(id='shell', kind='shell', file=str(shell_fn.relative_to(OUT)), x=0, y=0, w=W, h=H,
                       mae=round(e_sh, 2), kb=round(len(shell_txt) / 1024)))
    rep.insert(0, dict(id='FULL_COMPOSITE', mae=round(full, 2)))
    print(f'  shell MAE {e_sh:.2f} {len(shell_txt) / 1024:.0f} KB   full composite MAE {full:.2f}')
    Image.fromarray(shell_r).resize((W // 2, H // 2), Image.LANCZOS).save(shell_fn.with_suffix('.png'))
    Image.fromarray(render(glow_svg(W, H, lights, 'g'))).resize((W // 2, H // 2), Image.LANCZOS).save(rdir / f'{room}_lights_glow.png')
    compu = np.clip(comp, 0, 255).astype(np.uint8)
    save_check(shrink(np.vstack([img, compu]), 1400), CHECK / f'{room}_full_side_by_side.png')
    save_check(shrink(img * .5 + comp * .5, 1600), CHECK / f'{room}_full_onion.png')
    Image.fromarray(compu).resize((W // 2, H // 2), Image.LANCZOS).save(rdir / f'{room}_composite.png')
    # 6. manifest + debug overlay
    man = cfg['manifest']
    man.update(room=room, source=f'raw_originals/{cfg["src"]}', size=[W, H], shell=f'{room}_shell.svg',
               glow=f'{room}_lights_glow.svg', lights=lights)
    if pools:
        man['light_pools'] = dict(file=f'{room}_light_pools.svg', blend='screen', layer='above_shell_below_objects',
                                  note='part of the faithful look (removed from the shell); keep on, may pulse', pools=pools)
    objs, kids = [], []
    for L in layers:
        if 'svg' not in L:
            continue
        x0, y0 = L['xy']
        w, h = L['wh']
        e = dict(id=L['id'], file=str(L['file'].relative_to(rdir)), x=int(x0), y=int(y0), w=int(w), h=int(h))
        if L.get('pivot'):
            e['pivot'] = [int(L['pivot'][0]), int(L['pivot'][1])]
        if L.get('note'):
            e['note'] = L['note']
        if L['kind'] == 'space':
            e['layer'] = 'behind_shell'
            man['background'] = e
            continue
        if L.get('parent') == 'space':
            e['layer'] = 'behind_shell'
            e['parent'] = 'space'
            man.setdefault('background_children', []).append(e)
            continue
        if L.get('parent'):
            e['parent'] = L['parent']
            kids.append(e)
            continue
        e['sortY'] = int(L.get('sortY', y0 + h))
        if L.get('collision'):
            e['collision'] = L['collision']
        if L.get('floor'):
            e['layer'] = 'floor'
        objs.append(e)
    man['objects'] = objs
    man['children'] = kids
    (rdir / f'{room}.json').write_text(json.dumps(man, indent=1))
    dbg = Image.fromarray(compu).convert('RGBA')
    ov = Image.new('RGBA', dbg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for poly in man['walkable']:
        d.polygon([tuple(p) for p in poly], fill=(0, 255, 0, 70), outline=(0, 200, 0, 255))
    for o in objs:
        if o['sortY'] == 0:
            continue
        if o.get('collision'):
            d.polygon([tuple(p) for p in o['collision']], fill=(255, 0, 0, 90), outline=(255, 0, 0, 255))
        d.line([(o['x'], o['sortY']), (o['x'] + o['w'], o['sortY'])], fill=(40, 90, 255, 255), width=8)
    for dr in man['doors']:
        d.rectangle([dr['x'], dr['y'], dr['x'] + dr['w'], dr['y'] + dr['h']], outline=(0, 255, 255, 255), width=10)
    pts = []
    for k, v in man['anchors'].items():
        for p in (v if isinstance(v[0], list) else [v]):
            pts.append((k, p))
    for k, p in pts:
        d.ellipse([p[0] - 30, p[1] - 30, p[0] + 30, p[1] + 30], fill=(255, 230, 0, 255), outline=(0, 0, 0, 255), width=4)
        d.text((p[0] + 36, p[1] - 30), k, fill=(255, 230, 0, 255), font=font(56))
    for L in lights:
        d.ellipse([L['x'] - 12, L['y'] - 12, L['x'] + 12, L['y'] + 12], outline=(255, 140, 0, 255), width=4)
    save_check(Image.alpha_composite(dbg, ov).convert('RGB').resize((W // 3, H // 3), Image.LANCZOS), CHECK / f'{room}_manifest_debug.png')
    (CHECK / f"{room}_scores.json").write_text(json.dumps(rep, indent=1, default=int))
    return rep


if __name__ == '__main__':
    import rooms_i
    cfg = getattr(rooms_i, sys.argv[1].upper())
    build(cfg, masks_only=len(sys.argv) > 2 and sys.argv[2] == 'masks')
