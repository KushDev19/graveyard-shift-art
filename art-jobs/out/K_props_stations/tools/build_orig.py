"""Job K: build the *_orig station SVGs (shared body + state layers) from sheet 14, verify, export.
Run from this folder: python build_orig.py [station_name ...]"""
import sys, json
from kcommon import *
from trace import trace_layers, contour_path, hexc, outline_mask
from svgcheck import check, render_rgba

OUT = ROOT + '/art-jobs/out/K_props_stations'
PAD = 70


def box_rect(shape, box, ox, oy, m=6):
    """Mask of the object's own box (+ margin): drops fragments of neighbouring sprites."""
    r = np.zeros(shape[:2], bool)
    x, y, w, h = box
    r[max(0, y - oy - m):y - oy + h + m, max(0, x - ox - m):x - ox + w + m] = True
    return r


def clean_region(diff, mask, open_r=5, close_r=21, grow=7, min_area=400):
    r = (diff & mask).astype(np.uint8)
    r = cv2.morphologyEx(r, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_r, open_r)))
    r = cv2.morphologyEx(r, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_r, close_r)))
    n, cc, st, _ = cv2.connectedComponentsWithStats(r)
    keep = np.zeros_like(r)
    for j in range(1, n):
        if st[j, 4] >= min_area:
            keep[cc == j] = 1
    # fill holes
    cs, _ = cv2.findContours(keep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    keep = cv2.drawContours(np.zeros_like(keep), cs, -1, 1, -1)
    keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    return keep.astype(bool) & mask


def cell_region(c0, m0, ms, dres, cell_thr=20, px_thr=42):
    """Changed region = outline-bounded cells of the idle drawing whose mean residual is high,
    plus strongly changed pixels and any new silhouette (beacon); grown to cover their outline."""
    out = outline_mask(c0, m0)
    cells = (m0 & ~out).astype(np.uint8)
    n, cc = cv2.connectedComponents(cells, connectivity=4)
    sums = np.bincount(cc.ravel(), weights=dres.ravel(), minlength=n)
    cnts = np.bincount(cc.ravel(), minlength=n)
    mean = sums / np.maximum(cnts, 1)
    big = cnts > 0.03 * m0.sum()
    med = np.zeros(n)
    for j in np.flatnonzero(big & (mean > cell_thr)):
        med[j] = np.median(dres[cc == j])
    # big cells: only a uniform recolor counts (a painted glow covering part of a panel does not)
    sel = (mean > cell_thr) & (~big | (med > 18)) & (cnts > 30) & (cnts < 0.25 * m0.sum())
    sel[0] = False
    reg = sel[cc]
    strong = clean_region((dres > px_thr) & m0 & ms, ms, grow=2)
    newsil = clean_region(ms & ~m0, ms, grow=2)
    cells = reg | newsil
    core = cv2.dilate(cells.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))).astype(bool) & (ms | m0)
    core_unused = cv2.dilate(core.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))).astype(bool) & (ms | m0)
    # strong change outside any changed cell = soft painted glow (haze): returned separately, drawn as gradients
    haze = clean_region(strong & ~core, ms, grow=0, min_area=1500)
    # small solid changes that are not haze (thin parts) stay in the traced region
    return core, haze, cells


def haze_glows(c0, img, haze, ox, oy, gid, glow_rgb=(255, 190, 90), cells=None):
    """One soft ring glow per lit part that has painted haze around it."""
    out = ''
    if cells is None or not haze.any():
        return out
    n, cc, st, _ = cv2.connectedComponentsWithStats(cells.astype(np.uint8))
    for j in range(1, n):
        if st[j, 4] < 800:
            continue
        comp = cc == j
        if st[j, 4] < 0.45 * st[j, 2] * st[j, 3] or st[j, 4] > 0.08 * cells.size:
            continue  # only compact lit parts (screens, slots, lamps) glow
        near = haze & cv2.dilate(comp.astype(np.uint8), np.ones((61, 61), np.uint8)).astype(bool)
        if near.sum() < 400:
            continue
        a, _ = fit_tint(c0, img, near)
        if a < 0.05:
            continue
        x, y, w, h = st[j, :4]
        op = min(0.6, a * 1.6)
        g = f'{gid}_glow{j}'
        c = hexc(glow_rgb)
        out += (f'    <radialGradient id="{g}" gradientUnits="objectBoundingBox"><stop offset="0.45" stop-color="{c}" stop-opacity="0"/>'
                f'<stop offset="0.6" stop-color="{c}" stop-opacity="{op:.2f}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>\n'
                f'    <ellipse cx="{ox + x + w / 2:.0f}" cy="{oy + y + h / 2:.0f}" rx="{w / 2 / 0.55:.0f}" ry="{h / 2 / 0.55:.0f}" fill="url(#{g})"/>\n')
    return out


def fit_tint(base, tgt, sel):
    """tgt ~ base + a*(T - base). Returns a, T (rgb)."""
    x = base[sel].astype(np.float64); y = tgt[sel].astype(np.float64)
    A = np.zeros((len(x) * 3, 4)); b = np.zeros(len(x) * 3)
    for c in range(3):
        A[c::3, c] = 1; A[c::3, 3] = -x[:, c]; b[c::3] = y[:, c] - x[:, c]
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    a = float(np.clip(sol[3], 0, 0.9))
    T = np.clip(sol[:3] / a, 0, 255) if a > 0.02 else np.zeros(3)
    return a, T


def paths(layers, ind='    '):
    return ''.join(f'{ind}<path fill="{f}" d="{d}"/>\n' for f, d in layers)


def glow_svg(gid, cx, cy, r, color, op):
    return (f'    <radialGradient id="{gid}" cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="{op:.2f}"/><stop offset="0.45" stop-color="{color}" stop-opacity="{op * 0.75:.2f}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>\n'
            f'    <circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="url(#{gid})"/>\n')


def state_view(svg, state, names=('idle', 'highlight', 'done')):
    """Return SVG text with only `state` visible."""
    for s in names:
        vis = 'inline' if s == state else 'none'
        svg = svg.replace(f'<g id="state_{s}" display="inline"', f'<g id="state_{s}" display="{vis}"')
        svg = svg.replace(f'<g id="state_{s}" display="none"', f'<g id="state_{s}" display="{vis}"')
    return svg


def build(name, boxes, im, log, names=('idle', 'highlight', 'done'), src='14_PROPS_STATIONS.png', split=None):
    c0, (ox, oy) = crop(im, boxes[0], PAD)
    h, w = c0.shape[:2]
    m0 = main_mask(c0) & box_rect(c0.shape, boxes[0], ox, oy)
    states = {'idle': (c0, m0)}
    for s, b in zip(names[1:], boxes[1:]):
        # same-size window, bottom-left anchored to this state's box, then refined by phase correlation
        sx = ox + (b[0] - boxes[0][0]); sy = oy + (b[1] + b[3]) - (boxes[0][1] + boxes[0][3])
        win = np.full((h, w, 3), (0, 255, 0), np.uint8)
        y0, x0 = max(0, sy), max(0, sx)
        src = im[y0:sy + h, x0:sx + w]
        win[y0 - sy:y0 - sy + src.shape[0], x0 - sx:x0 - sx + src.shape[1]] = src
        dx, dy = align(c0, win)
        win = cv2.warpAffine(win, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h), borderValue=(0, 255, 0))
        ms = main_mask(win) & box_rect(win.shape, (b[0] - sx + dx + ox, b[1] - sy + dy + oy, b[2], b[3]), ox, oy)
        states[s] = (win, ms)

    print(name, 'tracing body'); sys.stdout.flush()
    body, _, _ = trace_layers(c0, m0, k=22, ox=ox, oy=oy)

    parts = {}
    regions = {}
    for s in names[1:]:
        img, ms = states[s]
        both = m0 & ms
        d0 = np.abs(img.astype(int) - c0.astype(int)).max(2)
        a, T = fit_tint(c0, img, both & (d0 < 70))
        tinted = c0 + a * (T[None, None] - c0) if a > 0.04 else c0.astype(np.float64)
        dres = np.abs(img - tinted).max(2).astype(np.float32)
        reg, haze, cells = cell_region(c0, m0, ms, dres)
        raw = (img, cells)
        # the band around changed cells keeps the body look; glow there comes from the gradients
        img = np.where((reg & ~cv2.dilate(cells.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & m0)[..., None], c0, img)
        regions[s] = reg
        frac = float((d0 > 25)[m0 & ms & ~reg].mean())
        log[f'{name}.{s}.changed_frac'] = round(frac, 3)
        if frac < 0.35:
            a = 0.0  # local change only: no whole-body tint
        parts[s] = (a, T, img, ms, reg, haze, raw)
        log[f'{name}.{s}.tint'] = [round(a, 3), [int(v) for v in T]]
    ru = np.any([regions[s] for s in names[1:]], 0)
    idle_part = split(c0, ru & m0, ox, oy, 'idle') if split else paths(trace_layers(c0, ru & m0, k=14, ox=ox, oy=oy, min_island=150)[0])

    sil = contour_path(m0, 1.1, ox, oy, blur=3.2)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{ox} {oy} {w} {h}" width="{w}" height="{h}">\n',
           f'  <!-- {name}: traced from raw_originals/{src}, source-pixel coordinates. '
           f'Toggle exactly one of ' + ' / '.join('state_' + n for n in names) + '. -->\n',
           f'  <g id="body">\n{paths(body)}  </g>\n',
           f'  <g id="state_idle" display="inline">\n{idle_part}  </g>\n']
    for s in names[1:]:
        a, T, img, ms, reg, haze, raw = parts[s]
        g = f'  <g id="state_{s}" display="none">\n'
        if a > 0.04:
            g += f'    <path id="{s}_tint" fill="{hexc(T)}" fill-opacity="{a:.2f}" d="{sil}"/>\n'
        if a > 0.04:  # whole-object recolor: the state layer is a full trace of that drawing
            reg = ms
            g = g.replace(f'    <path id="{s}_tint"', f'    <path id="{s}_tint" display="none"')
            log[f'{name}.{s}.mode'] = 'full'
        if split:
            g += split(img, reg, ox, oy, s)
        else:
            lay, _, _ = trace_layers(img, reg, k=16 if reg is not ms else 22, ox=ox, oy=oy, min_island=150 if reg is not ms else 400)
            g += paths(lay)
        if reg is not ms and s != 'done':  # soft warm glow on top of the lit parts
            g += haze_glows(c0, raw[0], haze, ox, oy, f'{name}_{s}', cells=raw[1])
        # beacon / lamp glow: new silhouette above the body
        extra = ms & ~cv2.dilate(m0.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        n, cc, st, cen = cv2.connectedComponentsWithStats(extra.astype(np.uint8))
        if n > 1:
            j = 1 + int(np.argmax(st[1:, 4]))
            if st[j, 4] > 2000:
                bx, by, bw, bh = st[j, :4]
                col = np.median(img[cc == j], 0)
                g = g.replace(f'display="none">\n', f'display="none">\n' + glow_svg(f'{name}_{s}_glow', ox + bx + bw / 2, oy + by + bh * 0.45, bw * 1.05, '#8CF0C8', 0.55), 1)
                log[f'{name}.{s}.beacon_center'] = [int(ox + bx + bw / 2), int(oy + by + bh / 2)]
        g += '  </g>\n'
        svg.append(g)
    svg.append('</svg>\n')
    text = ''.join(svg)
    open(f'{OUT}/{name}_orig.svg', 'w').write(text)
    scores = {}
    for s in names:
        img, ms = states[s]
        scores[s] = round(check(state_view(text, s, names), img, ms, f'{name}_orig_{s}', OUT + '/check'), 2)
        rgba = render_rgba(state_view(text, s, names), w // 2, h // 2).astype(np.uint8)
        Image.fromarray(rgba).save(f'{OUT}/png/{name}_orig_{s}.png')
    log[f'{name}_orig'] = {'mae': scores, 'kb': len(text) // 1024, 'viewBox': [ox, oy, w, h]}
    print(name, scores, len(text) // 1024, 'KB')


if __name__ == '__main__':
    im = load('14')
    names = sys.argv[1:] or list(STATIONS)
    logf = OUT + '/tools/log_orig.json'
    try:
        log = json.load(open(logf))
    except Exception:
        log = {}
    for n in names:
        build(n, STATIONS[n], im, log)
        json.dump(log, open(logf, 'w'), indent=1)
