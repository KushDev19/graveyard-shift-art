"""Job K: *_orig ship props from sheet 15: time clock (states), table clutter, vent frame + hinged lid.
Run from this folder: python build_ship.py [timeclock] [clutter] [vent]"""
import sys, json
from kcommon import *
from trace import trace_layers, contour_path, hexc
from svgcheck import check, render_rgba
import build_orig as B

OUT = B.OUT
SRC15 = '15_PROPS_SHIP.png'


def clock_split(img, reg, ox, oy, s):
    """Screen (top-most zone) and card-slot zone get their own named groups."""
    n, cc, st, cen = cv2.connectedComponentsWithStats(reg.astype(np.uint8))
    comps = sorted(range(1, n), key=lambda j: cen[j][1])
    out = ''
    for r, j in enumerate(comps):
        if st[j, 4] < 300:
            continue
        gid = f'screen_{s}' if r == 0 else (f'card_slot_glow' if s == 'ready' else f'card_slot_{s}') + (f'_{r}' if r > 1 else '')
        lay, _, _ = trace_layers(img, cc == j, k=14, ox=ox, oy=oy, min_island=150)
        out += f'    <g id="{gid}">\n' + B.paths(lay, '      ') + '    </g>\n'
    return out


def timeclock(im, log):
    B.build('timeclock', [SHIP['timeclock_idle'], SHIP['timeclock_ready']], im, log,
            names=('idle', 'ready'), src=SRC15, split=clock_split)


def clutter(im, log):
    c, (ox, oy) = crop(im, SHIP['table_clutter'], B.PAD)
    h, w = c.shape[:2]
    m = main_mask(c)
    # ownership: red mug = hull of its coral pixels (+ outline); box = box polygon minus red mug; the rest = mugs
    R = np.zeros_like(m); x0, y0, x1, y1 = np.array(RED_MUG_RECT) - [ox, oy, ox, oy]
    cr = c.astype(int)
    red = (cr[..., 0] > 170) & (cr[..., 1] < 140) & (cr[..., 2] < 130)
    R[y0:y1, x0:x1] = red[y0:y1, x0:x1]
    hull = cv2.convexHull(cv2.findNonZero(R.astype(np.uint8)))
    red_m = cv2.dilate(cv2.fillPoly(np.zeros(m.shape, np.uint8), [hull], 1), np.ones((17, 17), np.uint8)).astype(bool) & m
    cx0, cy0, cx1, cy1 = np.array(CREAM_MUG_RECT) - [ox, oy, ox, oy]
    lum = cr @ [0.3, 0.59, 0.11]
    C = np.zeros_like(m); C[cy0:cy1, cx0:cx1] = (lum > 185)[cy0:cy1, cx0:cx1] & m[cy0:cy1, cx0:cx1]
    n, cc, st, _ = cv2.connectedComponentsWithStats(C.astype(np.uint8))
    C = cc == 1 + int(np.argmax(st[1:, 4]))  # the mug body (largest light blob)
    hull = cv2.convexHull(cv2.findNonZero(C.astype(np.uint8)))
    cream_m = cv2.dilate(cv2.fillPoly(np.zeros(m.shape, np.uint8), [hull], 1), np.ones((17, 17), np.uint8)).astype(bool) & m & ~red_m
    tx0, ty0, tx1, ty1 = np.array(TEAL_MUG_RECT) - [ox, oy, ox, oy]
    teal_m = np.zeros_like(m); teal_m[ty0:ty1, tx0:tx1] = True
    teal_m &= m & ~red_m & ~cream_m
    poly = cv2.dilate(cv2.fillPoly(np.zeros(m.shape, np.uint8), [BOX_POLY - [ox, oy]], 1), np.ones((25, 25), np.uint8)).astype(bool)
    box_m = m & poly & ~red_m & ~cream_m & ~teal_m
    left = m & ~box_m & ~red_m & ~cream_m & ~teal_m  # handles, outlines, shadows outside the hulls
    for rect, which in ((CREAM_MUG_RECT, 'c'), (RED_MUG_RECT, 'r')):
        R2 = np.zeros_like(m); x0, y0, x1, y1 = np.array(rect) - [ox, oy, ox, oy]; R2[y0:y1, x0:x1] = True
        if which == 'c':
            cream_m |= left & R2
        else:
            red_m |= left & R2
        left &= ~R2
    teal_m |= left
    parts = [('mug_teal', teal_m), ('donut_box', box_m), ('mug_cream', cream_m), ('mug_red', red_m)]
    # the box corner hidden behind the red mug is inpainted (it shows only when the box is re-projected)
    bh = cv2.fillPoly(np.zeros(m.shape, np.uint8), [cv2.convexHull(cv2.findNonZero(box_m.astype(np.uint8)))], 1).astype(bool)
    hidden = bh & red_m
    box_img = cv2.inpaint(np.ascontiguousarray(c), hidden.astype(np.uint8), 15, cv2.INPAINT_TELEA)
    groups = []
    for gid, part in parts:
        img = box_img if gid == 'donut_box' else c
        part = part | hidden if gid == 'donut_box' else part
        lay, _, _ = trace_layers(img, part, k=18, ox=ox, oy=oy, min_island=120)
        groups.append(f'  <g id="{gid}">\n' + B.paths(lay) + '  </g>\n')
    text = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{ox} {oy} {w} {h}" width="{w}" height="{h}">\n'
            f'  <!-- table_clutter: traced from raw_originals/{SRC15}, source-pixel coordinates. -->\n'
            + ''.join(groups) + '</svg>\n')
    open(f'{OUT}/table_clutter_orig.svg', 'w').write(text)
    score = round(check(text, c, m, 'table_clutter_orig', OUT + '/check'), 2)
    Image.fromarray(render_rgba(text, w // 2, h // 2).astype(np.uint8)).save(f'{OUT}/png/table_clutter_orig.png')
    log['table_clutter_orig'] = {'mae': score, 'kb': len(text) // 1024, 'viewBox': [ox, oy, w, h]}
    print('clutter', score, len(text) // 1024, 'KB', [(g, int(p.sum())) for g, p in parts])


BOX_POLY = np.array([(4501, 560), (4761, 432), (4841, 110), (5255, 332), (5138, 590), (5138, 693), (4873, 820), (4505, 660)], np.int32)
RED_MUG_RECT = (4383, 590, 4700, 932)
CREAM_MUG_RECT = (4030, 420, 4360, 750)
TEAL_MUG_RECT = (4280, 280, 4600, 615)
LID_POLY = np.array([(2028, 1560), (2160, 1062), (2810, 1318), (2775, 1445), (2622, 1792), (2040, 1600)], np.int32)
HINGE = (2040, 1600, 2622, 1792)


def quad(mask):
    hull = cv2.convexHull(cv2.findNonZero(mask.astype(np.uint8)))
    peri = cv2.arcLength(hull, True)
    for e in np.linspace(0.01, 0.2, 60):
        q = cv2.approxPolyDP(hull, e * peri, True)
        if len(q) == 4:
            q = q[:, 0, :].astype(np.float32)
            # order: left, top, right, bottom
            return np.array([q[q[:, 0].argmin()], q[q[:, 1].argmin()], q[q[:, 0].argmax()], q[q[:, 1].argmax()]])
    raise RuntimeError('no quad')


def vent(im, log):
    co, (ox, oy) = crop(im, SHIP['vent_open'], B.PAD)
    cc_, (cx, cy) = crop(im, SHIP['vent_closed'], B.PAD)
    h, w = co.shape[:2]; hc, wc = cc_.shape[:2]
    mo = main_mask(co); mc = main_mask(cc_)
    P = np.zeros((h, w), np.uint8); cv2.fillPoly(P, [LID_POLY - [ox, oy]], 1); P = P.astype(bool)
    lid = mo & P
    frame_vis = mo & ~P
    # affine closed -> open frame from the 4 outer corners
    qo = quad(frame_vis | (P & cv2.dilate(frame_vis.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)))
    qo[1] = qo[0] + qo[2] - qo[3]  # back corner is hidden under the lid: complete the parallelogram
    qc = quad(mc)
    A = cv2.getAffineTransform(np.float32(qc[[0, 2, 3]] + [cx, cy]), np.float32(qo[[0, 2, 3]] + [ox, oy]))
    resid = np.abs(cv2.transform((qc + [cx, cy])[None], A)[0] - (qo + [ox, oy])).max()
    # frame: hidden back part (under the open lid) repainted from the warped closed drawing's rim + hole color
    Ain = A.copy(); Ain[:, 2] = A[:, 2] + A[:, :2] @ np.array([cx, cy]) - np.array([ox, oy])
    wc_img = cv2.warpAffine(cc_, Ain, (w, h), borderValue=(0, 255, 0))
    wc_m = cv2.warpAffine(mc.astype(np.uint8), Ain, (w, h), flags=cv2.INTER_NEAREST).astype(bool)
    dist = cv2.distanceTransform(wc_m.astype(np.uint8), cv2.DIST_L2, 5)
    hole = np.median(co[frame_vis & (co @ [0.3, 0.59, 0.11] < 90) & (cv2.distanceTransform(frame_vis.astype(np.uint8), cv2.DIST_L2, 5) > 40)], 0)
    fill = co.copy()
    under = P & wc_m
    fill[under] = np.where((dist[under] < 58)[:, None], wc_img[under], hole)
    fm = frame_vis | under
    frame_l, _, _ = trace_layers(fill, fm, k=16, ox=ox, oy=oy)
    lid_l, _, _ = trace_layers(co, lid, k=16, ox=ox, oy=oy)
    closed_l, _, _ = trace_layers(cc_, mc, k=16, ox=cx, oy=cy)
    mat = 'matrix(' + ' '.join(f'{v:.5f}' for v in (A[0, 0], A[1, 0], A[0, 1], A[1, 1], A[0, 2], A[1, 2])) + ')'
    piv = f'{(HINGE[0] + HINGE[2]) / 2:.0f},{(HINGE[1] + HINGE[3]) / 2:.0f}'
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{ox} {oy} {w} {h}" width="{w}" height="{h}">\n'
    note = f'  <!-- traced from raw_originals/{SRC15}; source-pixel coordinates of the open-vent drawing. -->\n'
    frame_svg = head + note + '  <g id="vent_frame">\n' + B.paths(frame_l) + '  </g>\n</svg>\n'
    lid_svg = (head + note + f'  <!-- Hinge line {HINGE}. lid_closed is the closed-vent drawing placed on the frame with an affine fit. -->\n'
               f'  <g id="lid_closed" display="inline" data-pivot="{piv}" transform="{mat}">\n' + B.paths(closed_l) + '  </g>\n'
               f'  <g id="lid_open" display="none" data-pivot="{piv}" data-hinge="{",".join(map(str, HINGE))}">\n' + B.paths(lid_l) + '  </g>\n</svg>\n')
    open(f'{OUT}/vent_frame_orig.svg', 'w').write(frame_svg)
    open(f'{OUT}/vent_lid_orig.svg', 'w').write(lid_svg)
    both = lambda st: head + '<g>' + frame_svg.split('\n', 2)[2].replace('</svg>\n', '') + B.state_view(lid_svg, st, ()).split('\n', 2)[2].replace(
        'id="lid_closed" display="inline"', f'id="lid_closed" display="{"inline" if st == "closed" else "none"}"').replace(
        'id="lid_open" display="none"', f'id="lid_open" display="{"inline" if st == "open" else "none"}"').replace('</svg>\n', '') + '</g></svg>\n'
    s_open = round(check(both('open'), co, mo, 'vent_orig_open', OUT + '/check'), 2)
    # closed: trace fidelity in the closed drawing's own frame + placement check against the warped original
    closed_native = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx} {cy} {wc} {hc}">' + B.paths(closed_l) + '</svg>'
    s_closed = round(check(closed_native, cc_, mc, 'vent_orig_closed', OUT + '/check'), 2)
    s_placed = round(check(both('closed'), np.where(wc_m[..., None], wc_img, co), wc_m | mo, 'vent_orig_closed_placed', OUT + '/check'), 2)
    for st in ('open', 'closed'):
        Image.fromarray(render_rgba(both(st), w // 2, h // 2).astype(np.uint8)).save(f'{OUT}/png/vent_orig_{st}.png')
    Image.fromarray(render_rgba(frame_svg, w // 2, h // 2).astype(np.uint8)).save(f'{OUT}/png/vent_frame_orig.png')
    log['vent_orig'] = {'mae': {'open': s_open, 'closed_trace': s_closed, 'closed_on_frame': s_placed},
                        'affine_corner_residual_px': round(float(resid), 1), 'kb': (len(frame_svg) + len(lid_svg)) // 1024,
                        'viewBox': [ox, oy, w, h], 'lid_closed_transform': mat, 'pivot': piv}
    print('vent', log['vent_orig'])


if __name__ == '__main__':
    im = load('15')
    logf = OUT + '/tools/log_orig.json'
    try:
        log = json.load(open(logf))
    except Exception:
        log = {}
    for job in (sys.argv[1:] or ['timeclock', 'clutter', 'vent']):
        globals()[job](im, log)
        json.dump(log, open(logf, 'w'), indent=1)
