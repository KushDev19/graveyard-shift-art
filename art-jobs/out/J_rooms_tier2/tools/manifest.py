"""Stage 3: manifests, data-pivots, half-scale PNG exports, debug overlays.
usage: python manifest.py <room>"""
import sys, json, re, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from jlib import *
from rooms import ROOMS

S = lambda p: [round(v * K) for v in p]
FLOOR = [(222, 478), (1778, 478), (1964, 1022), (1155, 1022), (1155, 1086), (845, 1086), (845, 1022), (36, 1022)]
DOORS = [dict(id='left', side='left', box=(78, 336, 166, 882)),
         dict(id='right', side='right', box=(1834, 336, 1922, 882)),
         dict(id='bottom', side='bottom', box=(845, 1022, 1155, 1086))]
ANCHORS = {
    'sickbay': {'scanner_pad': (597, 755), 'vent': (1010, 955), 'heart_monitor': (1265, 320), 'med_cabinet': (325, 380)},
    'hydroponics': {'tape_station_alcove': (637, 470), 'tape_station_mat': (637, 535), 'vent': (1700, 930),
                    'water_plants': (1090, 790), 'porthole': (1295, 225)},
    'cargo': {'door_keypad': (453, 313), 'loading_door': (727, 470), 'vent': (1000, 950), 'fuel_tank': (1555, 325), 'cargo_net': (1167, 312)},
}

def build(room):
    spec = ROOMS[room]; H, W = 3072, 5504
    meta = json.load(open(OUT / 'work' / f'{room}_objmeta.json'))
    M = dict(np.load(OUT / 'work' / f'{room}_masks_final.npz'))
    rd = OUT / room
    objs = []
    order = {o['id']: o for o in spec['objects']}
    for oid, b in meta.items():
        o = order.get(oid) or order[b['parent']]
        m = M[oid]
        ys, xs = np.nonzero(m)
        bottom = int(ys.max())
        e = dict(id=oid, file=f'objects/{room}_{oid}.svg', png=f'png/objects/{room}_{oid}.png',
                 x=b['x'], y=b['y'], w=b['w'], h=b['h'])
        if 'parent' in b:
            e['parent'] = b['parent']
        if o.get('floor'):
            e['layer'] = 'floor'; e['sortY'] = 0
        elif o.get('wall'):
            e['layer'] = 'wall'; e['sortY'] = round(478 * K)
        else:
            e['layer'] = 'depth'; e['sortY'] = bottom
            if o.get('collision', True) and 'parent' not in b:
                # footprint follows the floor-contact profile: lowest mask pixel per column, extruded back by depth
                d = round(o.get('depth', 60) * K)
                cols = np.nonzero(m.any(0))[0]
                x0, x1 = int(cols.min()), int(cols.max())
                xs_ = list(range(x0, x1, 40)) + [x1]
                yb = [int(np.nonzero(m[:, x])[0].max()) if m[:, x].any() else bottom for x in xs_]
                yb = ndi.maximum_filter1d(np.array(yb), 3)
                e['collision'] = [[x, int(y) - d] for x, y in zip(xs_, yb)] + [[x, int(y)] for x, y in zip(xs_[::-1], yb[::-1])]
        piv = o.get('pivot')
        if piv and 'parent' not in b:
            if piv == 'top':
                tx = np.nonzero(m[ys.min():ys.min() + 30].any(0))[0]
                pv = [int(tx.mean()), int(ys.min())]
            else:
                pv = S(piv)
            e['pivot'] = pv
            f = rd / e['file']
            t = f.read_text()
            t = re.sub(rf'<g id="{oid}"( data-pivot="[^"]*")?>', f'<g id="{oid}" data-pivot="{pv[0] - b["x"]},{pv[1] - b["y"]}">', t, count=1)
            f.write_text(t)
        objs.append(e)
    glows = json.load(open(OUT / 'work' / f'{room}_glows.json'))
    man = dict(room=room, source=f"raw_originals/{spec['src']}", size=[W, H],
               shell=f'{room}_shell.svg', lights_file=f'{room}_lights.svg',
               lights_blend='ADD (lights and mist add light: dst + src.rgb * src.alpha)',
               objects=objs,
               walkable=[S(p) for p in FLOOR],
               doors=[dict(id=d['id'], side=d['side'], x=S(d['box'][:2])[0], y=S(d['box'][:2])[1],
                           w=round((d['box'][2] - d['box'][0]) * K), h=round((d['box'][3] - d['box'][1]) * K)) for d in DOORS],
               anchors={k: S(v) for k, v in ANCHORS[room].items()})
    man['lights'] = [dict(id=g['id'], x=round(g['bulb'][0] * K), y=round(g['bulb'][1] * K),
                          radius=round(g.get('w', 150) * K * 1.4), color=g['color']) for g in glows]
    if (rd / f'{room}_mist.svg').exists():
        man['mist'] = f'{room}_mist.svg'
    json.dump(man, open(rd / f'{room}.json', 'w'), indent=1)
    # PNG exports at half source scale
    (rd / 'png' / 'objects').mkdir(parents=True, exist_ok=True)
    for e in objs:
        Image.fromarray(render(rd / e['file'], max(1, e['w'] // 2), max(1, e['h'] // 2))).save(rd / e['png'], optimize=True)
    for n in ['shell', 'lights', 'mist']:
        f = rd / f'{room}_{n}.svg'
        if f.exists():
            Image.fromarray(render(f, W // 2, H // 2)).save(rd / 'png' / f'{room}_{n}.png', optimize=True)
    # debug overlay on the composite (half res)
    im = Image.open(rd / f'{room}_composite.png').convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    h = lambda p: [(x / 2, y / 2) for x, y in p]
    d.polygon(h(man['walkable']), fill=(60, 220, 90, 60), outline=(60, 220, 90, 255))
    for e in objs:
        if 'collision' in e:
            d.polygon(h(e['collision']), fill=(230, 60, 60, 90), outline=(230, 60, 60, 255))
        if e['layer'] == 'depth':
            d.line([(e['x'] / 2, e['sortY'] / 2), ((e['x'] + e['w']) / 2, e['sortY'] / 2)], fill=(60, 120, 255, 255), width=3)
        if 'pivot' in e:
            px, py = e['pivot']; d.ellipse([px / 2 - 6, py / 2 - 6, px / 2 + 6, py / 2 + 6], outline=(255, 255, 255, 255), width=2)
    for dr in man['doors']:
        d.rectangle([dr['x'] / 2, dr['y'] / 2, (dr['x'] + dr['w']) / 2, (dr['y'] + dr['h']) / 2], outline=(255, 160, 0, 255), width=3)
    for k, (x, y) in man['anchors'].items():
        d.ellipse([x / 2 - 10, y / 2 - 10, x / 2 + 10, y / 2 + 10], fill=(255, 230, 40, 255)); d.text((x / 2 + 12, y / 2 - 6), k, fill=(255, 240, 120, 255))
    for l in man['lights']:
        d.ellipse([l['x'] / 2 - 8, l['y'] / 2 - 8, l['x'] / 2 + 8, l['y'] / 2 + 8], outline=(255, 120, 200, 255), width=3)
    Image.alpha_composite(im, ov).convert('RGB').save(rd / 'check' / f'{room}_manifest_debug.png', optimize=True)
    print(room, 'manifest ok', len(objs), 'objects')

if __name__ == '__main__':
    for r in sys.argv[1:]:
        build(r)
