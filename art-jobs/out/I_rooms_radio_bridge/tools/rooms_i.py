"""Room configs for Job I (source-pixel coordinates of the 5504x3072 originals)."""
import numpy as np, cv2
from build_i import shape_mask, refine, dil, ero, fill_holes, lum


def window_mask(seed, box, T=60):
    def fn(img, H, W):
        x0, y0, x1, y1 = box
        free = (lum(img[y0:y1, x0:x1]) >= T).astype(np.uint8)
        _, lab = cv2.connectedComponents(free, connectivity=4)
        m = lab == lab[seed[1] - y0, seed[0] - x0]
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))).astype(bool)
        m = fill_holes(m)
        out = np.zeros((H, W), bool)
        out[y0:y1, x0:x1] = m
        return out
    return fn


def needle(pivot, tip, width, start, arrow=True, stop=0, T=120):
    """Painted needle: geometry measured by hand from the original (pivot = dome centre,
    tip = arrow point). Mask = dark pixels in a thin band along it (stopping short of the
    scale arc so the arc stays intact) -> removed from the dial and redrawn as vector."""
    def fn(img, H, W):
        (px, py), (tx, ty) = pivot, tip
        L = float(np.hypot(tx - px, ty - py))
        vx, vy = (tx - px) / L, (ty - py) / L
        e = L - stop
        band = shape_mask(H, W, [('line', (int(px + vx * start), int(py + vy * start), int(px + vx * e), int(py + vy * e), int(width + 6)))])
        if arrow:
            nx, ny = -vy, vx
            hl, hw = width * 3.2, width * 1.7
            band |= shape_mask(H, W, [('poly', [(tx + vx * 3, ty + vy * 3), (tx - vx * hl + nx * hw, ty - vy * hl + ny * hw),
                                                (tx - vx * hl - nx * hw, ty - vy * hl - ny * hw)])])
        m = band & (lum(img) < T)
        dk = m & (lum(img) < 80)
        col = tuple(np.median(img[dk], 0).astype(int)) if dk.any() else (42, 30, 53)
        fn.geom = dict(pivot=(px, py), dir=(vx, vy), start=start, tip=L, width=width, color=col, arrow=arrow)
        return dil(m, 1) & dil(band, 1)
    return fn


def needle_svg(L, x0, y0):
    g = L['maskfn'].geom
    (px, py), (vx, vy) = g['pivot'], g['dir']
    nx, ny = -vy, vx
    s, t, w = g['start'], g['tip'], g['width']
    hl, hw = w * 2.9, w * 1.5  # arrow head proportions of the painted arrows
    P = lambda d, o=0: (px + vx * d + nx * o - x0, py + vy * d + ny * o - y0)
    c = '#%02X%02X%02X' % g['color']
    if not g['arrow']:
        a, b = P(s), P(t)
        return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{c}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
    a, b = P(s), P(t - hl * .8)
    tip, l, r = P(t), P(t - hl, hw), P(t - hl, -hw)
    return (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{c}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            f'<path d="M{tip[0]:.1f} {tip[1]:.1f}L{l[0]:.1f} {l[1]:.1f}L{r[0]:.1f} {r[1]:.1f}Z" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>')


def bulbs(boxes):
    def fn(img, H, W):
        band = shape_mask(H, W, boxes)
        a = img.astype(np.int16)
        br = band & (lum(img) > 200) & (a[..., 0] > 220)
        n, lab, st, _ = cv2.connectedComponentsWithStats(br.astype(np.uint8))
        keep = np.zeros((H, W), bool)
        for i in range(1, n):
            if st[i, 4] > 150:
                keep |= lab == i
        P = dil(keep, 26)
        P |= np.roll(P, -22, axis=0)
        return refine(img, P & dil(band, 20), T=58, pad=4, open_r=0, minfrac=0)
    return fn


def red_blobs(glass):
    def fn(img, H, W):
        G = shape_mask(H, W, [('poly', glass)])
        a = img.astype(np.int16)
        r = G & (a[..., 0] > 215) & (a[..., 1] < 128) & (a[..., 2] < 105)
        return fill_holes(dil(r, 3)) & ero(G, 2)
    return fn


def green_screens(img, H, W):
    a = img.astype(np.int16)
    box = shape_mask(H, W, [('rect', (1450, 850, 4080, 1500))])
    g = box & (a[..., 1] > 200) & (a[..., 1] - a[..., 0] > 45)
    n, lab, st, _ = cv2.connectedComponentsWithStats(dil(g, 3).astype(np.uint8))
    out = np.zeros((H, W), bool)
    for i in range(1, n):
        if st[i, 4] > 400:
            out |= fill_holes(lab == i)
    return out


def rug_mirror(srcimg, L, by):
    m = L['mask']
    ys, xs = np.where(m)
    top, bot = ys.min(), ys.max()
    cx = int(round((xs[ys < top + 6].mean() + xs[ys > bot - 6].mean() + xs.min() + xs.max()) / 4))
    H, W = m.shape
    mm = np.zeros_like(m)
    x0, x1 = max(2 * cx - W + 1, 0), min(2 * cx, W - 1)
    mm[:, x0:x1 + 1] = m[:, 2 * cx - np.arange(x0, x1 + 1)]
    hidden = mm & ~m
    out = srcimg.copy()
    yy, xx = np.where(hidden)
    out[yy, xx] = srcimg[yy, 2 * cx - xx]
    L['alpha'] = fill_holes(m | mm)
    L['note'] = f'parts hidden by armchair/records mirrored from the left half (axis x={cx})'
    return out


def radio_lights(layers, by):
    m = by['string_lights']['mask']
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    img_l = []
    for i in range(1, n):
        if st[i, 4] > 1500:
            img_l.append(dict(x=int(cen[i][0]), y=int(cen[i][1]) + 15, radius=95, color='#F5A54A', a=.5))
    img_l.sort(key=lambda d: (d['x'], d['y']))
    img_l.append(dict(x=3720, y=1580, radius=430, color='#F5A54A', a=.4, id='lava_lamp'))
    return img_l


RADIO = dict(room='radio', src='08_ROOM_RADIO.png', layers=[
    dict(id='space', kind='space', maskfn=window_mask((2750, 450), (1880, 170, 3660, 1190)), padout=60, scale=2, ms=None, cands=[dict(qtrace=48), dict(color_precision=8, layer_difference=5, filter_speckle=4), dict(color_precision=8, layer_difference=8, filter_speckle=4), dict(color_precision=8, layer_difference=6, filter_speckle=8)],
         note='nebula + stars seen through the porthole; drawn BEHIND the shell (shell has a hole there)'),
    dict(id='dish', kind='object', parent='space', shape=[('poly', [(2160, 640), (2260, 570), (2420, 610), (2580, 690), (2600, 640), (2650, 640),
                                                                    (2620, 760), (2580, 900), (2480, 1010), (2440, 1090), (2280, 1090), (2230, 1000), (2170, 880)])],
         note='radar dish outside the window, between nebula and frame'),
    dict(id='string_lights', kind='lights', maskfn=bulbs([('rect', (560, 120, 2250, 330)), ('rect', (3280, 120, 4960, 330)),
                                                          ('poly', [(4800, 120), (4990, 120), (5420, 1180), (5250, 1240)])]),
         sortY=0, note='bulbs + sockets; flicker with radio_lights_glow.svg'),
    dict(id='vu_meters', kind='object', ms=(2, 6), cands=[dict(filter_speckle=2), dict(color_precision=8, layer_difference=8, filter_speckle=2), dict(color_precision=8, layer_difference=12, filter_speckle=3)], refine=False, kidgrow=1, shape=[('poly', [(656, 395), (686, 340), (708, 330), (1252, 333), (1272, 355), (1272, 605), (1250, 634), (680, 634), (656, 610)])], sortY=0, note='wall unit'),
    dict(id='vu_needle_1', kind='object', vector=needle_svg, parent='vu_meters', maskfn=needle((805, 556), (757, 481), 8, 27), pivot=(805, 556)),
    dict(id='vu_needle_2', kind='object', vector=needle_svg, parent='vu_meters', maskfn=needle((1071, 556), (1031, 481), 8, 27), pivot=(1071, 556)),
    dict(id='tape_deck', kind='object', ms=(2, 6), cands=[dict(filter_speckle=2), dict(color_precision=8, layer_difference=8, filter_speckle=2), dict(color_precision=8, layer_difference=12, filter_speckle=3)], kidgrow=1, shape=[('rect', (585, 690, 1278, 1545))], sortY=1530,
         collision=[[600, 1420], [1270, 1420], [1270, 1535], [600, 1535]]),
    dict(id='reel_left', kind='object', parent='tape_deck', shape=[('circle', (752, 920, 172))], pivot=(748, 933), note='spin around pivot'),
    dict(id='reel_right', kind='object', parent='tape_deck', shape=[('circle', (1100, 920, 172))], pivot=(1098, 933), note='spin around pivot'),
    dict(id='vu_needle_3', kind='object', vector=needle_svg, parent='tape_deck', maskfn=needle((787, 1405), (755, 1350), 6.5, 17, arrow=False, stop=14), pivot=(787, 1405)),
    dict(id='vu_needle_4', kind='object', vector=needle_svg, parent='tape_deck', maskfn=needle((981, 1405), (950, 1350), 6.5, 17, arrow=False, stop=14), pivot=(981, 1405)),
    dict(id='cassette_shelf_upper', kind='object', shape=[('rect', (1262, 318, 1862, 600))], sortY=0, note='wall shelf'),
    dict(id='cassette_shelf_lower', kind='object', shape=[('rect', (1262, 600, 1862, 872))], sortY=0, note='wall shelf'),
    dict(id='cassette_crate', kind='object', shape=[('rect', (1262, 900, 1874, 1556))], sortY=1545,
         collision=[[1270, 1430], [1875, 1430], [1875, 1550], [1270, 1550]]),
    dict(id='armchair', kind='object', T=78, open=9, clipshape=[('poly', [(2700, 1000), (3615, 1000), (3615, 1805), (3445, 1805), (3445, 2200), (2700, 2200)])], shape=[('poly', [(2765, 1600), (2845, 1455), (3005, 1375), (3015, 1195), (3105, 1085), (3190, 1035), (3435, 1035), (3555, 1135),
                                                       (3630, 1295), (3630, 1765), (3485, 1845), (3480, 2010), (3425, 2135), (3235, 2125), (2945, 1965),
                                                       (2865, 1965), (2765, 1725)])], sortY=2085,
         collision=[[2830, 1760], [3200, 1640], [3560, 1720], [3380, 2070], [3280, 2080], [2880, 1930]]),
    dict(id='side_table', kind='object', exclude=['lava_lamp'], fillexcl=60, clipshape=[('rect', (3440, 1690, 4100, 2300))], shape=[('poly', [(3445, 1810), (3560, 1755), (3830, 1712), (3995, 1795), (3995, 2145), (3955, 2155),
                                                                         (3770, 2270), (3685, 2265), (3675, 2195), (3505, 2170), (3450, 2080)])], sortY=2260,
         collision=[[3460, 2060], [3760, 1960], [3990, 2130], [3760, 2265], [3480, 2165]]),
    dict(id='lava_lamp', kind='object', T=80, shape=[('poly', [(3690, 1355), (3752, 1355), (3800, 1500), (3842, 1680), (3802, 1740), (3818, 1855),
                                                          (3622, 1855), (3638, 1740), (3598, 1680), (3640, 1500)])], sortY=2261,
         note='stands on side_table (draw right after it)'),
    dict(id='lava_blobs', kind='object', parent='lava_lamp', maskfn=red_blobs([(3700, 1395), (3742, 1395), (3792, 1680), (3650, 1680)]),
         note='animate (bob/scale) inside the glass; clip to the glass if moved far'),
    dict(id='records', kind='object', shape=[('poly', [(3085, 2210), (3225, 2125), (3400, 2115), (3535, 2185), (3545, 2310), (3420, 2425),
                                                        (3330, 2445), (3175, 2395), (3085, 2320)])], sortY=2440,
         collision=[[3100, 2250], [3300, 2160], [3530, 2240], [3320, 2420]]),
    dict(id='rug', kind='object', floor=True, exclude=['armchair', 'records', 'side_table'], shape=[('ellipse', (2752, 2128, 722, 420))],
         srcfn=rug_mirror, sortY=0),
], lights_fn=radio_lights, shell_tr=dict(color_precision=8, layer_difference=6), manifest=dict(
    walkable=[[[540, 1310], [3900, 1310], [3900, 1010], [4780, 1010], [4780, 1310], [4960, 1310], [5400, 2800], [3245, 2800],
               [3245, 3060], [2260, 3060], [2260, 2800], [100, 2800]]],
    doors=[dict(id='left', side='left', x=220, y=930, w=240, h=1000), dict(id='right', side='right', x=5044, y=930, w=240, h=1000),
           dict(id='bottom', side='bottom', x=2260, y=2800, w=985, h=272)],
    anchors=dict(station_alcove=[4340, 1180], vents=[[1550, 2600], [4700, 2450]],
                 seats=[[3200, 1780]]),
))


BRIDGE = dict(room='bridge', src='09_ROOM_BRIDGE.png', layers=[
    dict(id='space', kind='space', maskfn=window_mask((2700, 500), (720, 140, 4800, 1030)), padout=120, scale=2, ms=None, cands=[dict(qtrace=48), dict(color_precision=8, layer_difference=5, filter_speckle=4), dict(color_precision=8, layer_difference=8, filter_speckle=4), dict(color_precision=8, layer_difference=6, filter_speckle=8)],
         note='nebula, stars and ringed planet behind the panoramic window; drift slowly (padded 120 px)'),
    dict(id='console', kind='object', exclude=['chair'], fillexcl=120, shape=[('poly', [(1450, 1060), (1560, 975), (1900, 920), (2560, 895), (2610, 868), (2940, 868),
                                                                         (2990, 895), (3600, 920), (3950, 975), (4068, 1060), (4072, 1712), (3820, 1712),
                                                                         (3600, 1590), (3200, 1490), (2700, 1455), (2200, 1490), (1800, 1590),
                                                                         (1620, 1712), (1448, 1712)])], sortY=1712,
         collision=[[1450, 1400], [4070, 1400], [4070, 1715], [3820, 1715], [3500, 1600], [2700, 1505], [1900, 1600], [1630, 1715], [1450, 1715]]),
    dict(id='screens', kind='object', parent='console', maskfn=green_screens, note='glowing CRT faces; pulse with bridge_lights_glow.svg'),
    dict(id='chair', kind='object', shape=[('poly', [(2530, 1185), (2595, 1125), (2875, 1125), (2925, 1200), (2925, 1410), (3010, 1445), (3130, 1445), (3155, 1530),
                                                      (3100, 1600), (3080, 1710), (2990, 1775), (3005, 1860), (2910, 1925), (2690, 1925), (2580, 1865),
                                                      (2585, 1790), (2505, 1720), (2500, 1575), (2455, 1535), (2465, 1445), (2505, 1425)])], pivot=(2780, 1830), sortY=1895,
         collision=[[2620, 1800], [2780, 1770], [2950, 1800], [2950, 1880], [2780, 1905], [2620, 1880]],
         note='captain chair; swivel = small rotate / flipX around pivot (base centre)'),
    dict(id='thermos', kind='object', shape=[('rect', (3175, 1575, 3365, 1910))], sortY=1900,
         collision=[[3190, 1850], [3330, 1850], [3330, 1905], [3190, 1905]]),
    dict(id='star_table', kind='object', refine=False, shape=[('ellipse', (1360, 2272, 495, 278)), ('ellipse', (1360, 2305, 495, 278)), ('rect', (1105, 2300, 1604, 2642)), ('ellipse', (1354, 2640, 250, 46))],
         sortY=2690, collision=[[1090, 2560], [1355, 2520], [1620, 2560], [1620, 2680], [1355, 2720], [1090, 2680]]),
    dict(id='chart_disc', kind='object', parent='star_table', refine=False, shape=[('ellipse', (1358, 2269, 447, 241))], pivot=(1358, 2269),
         unproject=(1358, 2269, 0.539), note='hologram chart; rotate group #chart_disc_spin (already inside the perspective squash)'),
    dict(id='plant', kind='object', shape=[('rect', (1825, 2275, 2225, 2785))], sortY=2765,
         collision=[[1930, 2690], [2120, 2690], [2120, 2765], [1930, 2765]]),
], shell_cands=[dict(color_precision=8, layer_difference=4, repair_T=10, repair_k=24), dict(color_precision=8, layer_difference=5, repair_T=10, repair_k=24)],
    lights=[dict(x=520, y=2130, poly=[(390, 1940), (1080, 1940), (1080, 2318), (262, 2318)], grad=(300, 1080), color='#FF3815',
                 stops=[(0, .31), (.23, .3), (.44, .24), (.64, .16), (.8, .11), (1, 0)], baked=False, id='door_spill_left'),
            dict(x=1362, y=2262, radius=700, ry=430, color='#8FF0C8', stops=[(0, .5), (.5, .4), (.6, .32), (.7, .2), (.8, .11), (.9, .045), (1, 0)], baked=False, id='star_chart_pool'),
            dict(x=1362, y=2272, radius=640, ry=380, color='#8FF0C8', a=.45, id='star_chart'),
           dict(x=2236, y=1076, radius=170, color='#8FF0C8', a=.5, id='screen_left'),
           dict(x=2750, y=1030, radius=240, color='#8FF0C8', a=.5, id='screen_main'),
           dict(x=3260, y=1076, radius=170, color='#8FF0C8', a=.5, id='screen_right')],
    manifest=dict(
    walkable=[[[470, 1700], [745, 1700], [745, 1410], [1370, 1410], [1370, 1700], [1630, 1700], [1900, 1580], [2700, 1480], [3500, 1580],
               [3820, 1700], [4140, 1700], [4140, 1410], [4775, 1410], [4775, 1700], [5030, 1700], [5400, 2800], [3245, 2800],
               [3245, 3060], [2260, 3060], [2260, 2800], [100, 2800]]],
    doors=[dict(id='left', side='left', x=220, y=930, w=240, h=1000), dict(id='bottom', side='bottom', x=2260, y=2800, w=985, h=272)],
    anchors=dict(station_alcove_left=[1050, 1550], station_alcove_right=[4460, 1550], helm=[2780, 1640], vents=[[4400, 2500]]),
))
