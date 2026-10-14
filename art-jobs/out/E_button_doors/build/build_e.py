"""Builds every Job E deliverable into the parent folder.
Usage (from repo root): python art-jobs/out/E_button_doors/build/build_e.py
Needs: pip install playwright pillow (uses the pre-installed Chromium; set CHROME to override)."""
import io
import json
import os
import pathlib
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent
sys.path.insert(0, str(HERE))
import doors as D  # noqa: E402

CHROME = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
CORE = (HERE / 'emergency_core.js').read_text(encoding='utf-8')
STATES = ['idle', 'open', 'pressed', 'disabled']
DOME_ANGLES = list(range(0, 121, 10))


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        pg = b.new_page(viewport={'width': 1400, 'height': 1400})
        pg.set_content(f'<body style="margin:0;background:transparent"><div id="h"></div><script>{CORE}</script></body>')

        def eb(state, opts=None):
            return pg.evaluate('([s,o]) => EB.svg(typeof s === "string" ? EB.STATES[s] : s, o || {})', [state, opts])

        def shot(svg):
            pg.evaluate('s => document.getElementById("h").innerHTML = s', svg)
            return Image.open(io.BytesIO(pg.query_selector('#h svg').screenshot(omit_background=True))).convert('RGBA')

        rig_parts, files = {}, []

        def save(img, name):
            img.save(OUT / name, optimize=True)
            files.append(name)

        def crop_save(img, name, pad=4):
            x0, y0, x1, y1 = img.getbbox()
            x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
            x1, y1 = min(img.width, x1 + pad), min(img.height, y1 + pad)
            save(img.crop((x0, y0, x1, y1)), name)
            return [x0, y0, x1 - x0, y1 - y0]

        # 1. master SVG (idle state, every part present; padlock and flash hidden) + state SVG/PNGs
        master = eb('idle').replace('<g id="padlock"', '<g id="padlock" display="none"', 1)
        (OUT / 'emergency_button.svg').write_text(master, encoding='utf-8'); files.append('emergency_button.svg')
        for s in STATES:
            svg = eb(s)
            (OUT / f'emergency_button_{s}.svg').write_text(svg, encoding='utf-8'); files.append(f'emergency_button_{s}.svg')
            save(shot(svg), f'emergency_button_{s}.png')

        # 2. part layers for the game engine (cropped; offset = top-left in the 570x530 canvas)
        pdir = 'parts/'
        (OUT / 'parts').mkdir(exist_ok=True)
        layer_specs = {
            'base': ('idle', ['base']),
            'glow_ring_off': ('idle', ['glow_ring']),
            'glow_ring_on': ('open', ['glow_ring']),
            'glow_ring_bright': ('pressed', ['glow_ring']),
            'button_idle': ('idle', ['button']),
            'button_lit': ('open', ['button']),
            'button_pressed': ('pressed', ['button']),
            'button_disabled': ('disabled', ['button']),
            'padlock': ('disabled', ['padlock']),
        }
        for name, (st, only) in layer_specs.items():
            rig_parts[name] = {'file': pdir + name + '.png', 'rect': crop_save(shot(eb(st, {'only': only})), pdir + name + '.png')}

        # 3. dome flip strips (3D hinge motion is pre-rendered: back layer + front layer per angle)
        for layer in ['dome_back', 'dome_front']:
            frames = [shot(eb({'theta': a}, {'only': [layer]})) for a in DOME_ANGLES]
            box = [min(f.getbbox()[i] for f in frames) if i < 2 else max(f.getbbox()[i] for f in frames) for i in range(4)]
            box = [box[0] - 4, max(0, box[1] - 4), box[2] + 4, box[3] + 4]
            fw, fh = box[2] - box[0], box[3] - box[1]
            strip = Image.new('RGBA', (fw * len(frames), fh))
            for i, f in enumerate(frames):
                strip.paste(f.crop(box), (i * fw, 0))
            save(strip, pdir + layer + '_strip.png')
            rig_parts[layer] = {'file': pdir + layer + '_strip.png', 'rect': [box[0], box[1], fw, fh],
                                'frameWidth': fw, 'frameHeight': fh, 'angles': DOME_ANGLES}

        # 4. doors
        door_svgs = {
            'door_front_closed': D.svg_front(False), 'door_front_open': D.svg_front(True),
            'door_side_closed': D.svg_side(False), 'door_side_open': D.svg_side(True),
        }
        for n, svg in door_svgs.items():
            (OUT / f'{n}.svg').write_text(svg, encoding='utf-8'); files.append(f'{n}.svg')
            save(shot(svg), f'{n}.png')
        for n in ['door_side_closed', 'door_side_open']:
            save(shot(D.svg_side(n.endswith('open'), mirror=True)), n.replace('side', 'side_r') + '.png')
        door_parts = {}
        for part in ['doorway', 'door_left', 'door_right', 'frame']:
            save(shot(D.svg_front(False, only=[part])), f'{pdir}door_front_{part}.png')
            door_parts.setdefault('front', {})[part] = f'{pdir}door_front_{part}.png'
        for part in ['slab', 'doorway', 'door_left', 'door_right', 'frame']:
            save(shot(D.svg_side(False, only=[part])), f'{pdir}door_side_{part}.png')
            door_parts.setdefault('side', {})[part] = f'{pdir}door_side_{part}.png'

        # 5. demo page (core inlined + doors inlined)
        demo = (HERE / 'demo_template.html').read_text(encoding='utf-8')
        demo = demo.replace('/*CORE*/', CORE).replace('<!--DOORS-->', D.svg_front(False, P='qf') + '\n' + D.svg_side(False, P='qs'))
        (OUT / 'emergency_demo.html').write_text(demo, encoding='utf-8'); files.append('emergency_demo.html')

        # 6. rig
        hinge = pg.evaluate('EB.HINGE')
        a, bk = D.SKEW
        rig = {
            'units': 'pixels of the 5504 px wide room paintings (scale by roomDisplayWidth / 5504)',
            'emergency_button': {
                'canvas': [570, 530],
                'anchor': {'base_top_center': [330, 380], 'floor_contact': [330, 450],
                           'note': 'place base_top_center on the Galley table pedestal top (about 1.3x pedestal width)'},
                'pivots': {'base': [330, 380], 'button': [330, 386], 'dome': [round(hinge[0], 1), round(hinge[1], 1)],
                           'padlock': [462, 420], 'glow_ring': [330, 382], 'flash_ring': [330, 374]},
                'parts': rig_parts,
                'draw_order': {'dome_angle_le_30': ['base', 'glow_ring', 'flash_ring', 'dome_back', 'button', 'dome_front', 'padlock'],
                               'dome_angle_gt_30': ['base', 'glow_ring', 'flash_ring', 'dome_back', 'dome_front', 'button', 'padlock']},
                'dome': {'hinge': 'back-left of the rim (azimuth 235 deg), real 3D flip', 'open_angle': 110,
                         'how': 'set strip frame = round(angle/10); angles above 110 are for the overshoot'},
                'button': {'press_depth': 14, 'squash': {'scaleX': 1.12, 'scaleY': 0.78, 'pivot': 'button'}},
                'flash_ring': {'shape': 'ellipse stroke #E8574A, ry = rx * 0.336', 'rx_from': 90, 'rx_to': 240,
                               'stroke_from': 16, 'stroke_to': 4, 'alpha_from': 1, 'alpha_to': 0, 'duration_ms': 650,
                               'second_ring_delay_ms': 120},
                'states': {s: f'emergency_button_{s}.png' for s in STATES},
                'tweens_ms': [
                    {'at': 0, 'dur': 650, 'target': 'dome', 'prop': 'angle', 'from': 0, 'to': 110, 'ease': 'Back.easeOut(1.25)', 'note': 'peaks near 117 deg'},
                    {'at': 300, 'dur': 350, 'target': 'glow_ring', 'swap': 'glow_ring_off -> glow_ring_on', 'ease': 'Sine.easeInOut'},
                    {'at': 200, 'dur': 300, 'target': 'button', 'swap': 'button_idle -> button_lit (crossfade)'},
                    {'at': 900, 'dur': 100, 'target': 'button', 'props': {'y': '+18', 'scaleX': 1.12, 'scaleY': 0.78}, 'ease': 'Cubic.easeIn'},
                    {'at': 1000, 'dur': 180, 'target': 'button', 'props': {'y': '-4', 'scaleX': 1, 'scaleY': 1}, 'ease': 'Back.easeOut(2)', 'swap': 'button_pressed'},
                    {'at': 950, 'dur': 650, 'target': 'flash_ring', 'note': 'see flash_ring'},
                    {'at': 950, 'dur': 100, 'target': 'glow_ring', 'swap': 'glow_ring_bright'},
                    {'at': 1900, 'dur': 500, 'target': 'button', 'swap': 'button_lit -> button_disabled (crossfade)', 'props': {'y': 0}},
                    {'at': 1900, 'dur': 500, 'target': 'glow_ring', 'swap': 'glow_ring_off (crossfade)'},
                    {'at': 2100, 'dur': 450, 'target': 'dome', 'prop': 'angle', 'from': 110, 'to': 0, 'ease': 'Cubic.easeIn'},
                    {'at': 2550, 'dur': 200, 'target': 'dome', 'prop': 'angle', 'yoyo': 7, 'ease': 'Sine.easeOut'},
                    {'at': 2750, 'dur': 500, 'target': 'padlock', 'props': {'y': 'from -150', 'alpha': 'from 0'}, 'ease': 'Bounce.easeOut'},
                    {'at': 3150, 'dur': 750, 'target': 'padlock', 'prop': 'angle', 'note': 'damped swing 14*exp(-4t)*sin(5*pi*t)'},
                ],
            },
            'doors': {
                'front': {'canvas': [D.FW, D.FH], 'opening': [D.OX0, D.OY0, D.OX1, D.OY1], 'opening_top_radius': D.ORAD,
                          'mask': 'mask both halves with the opening (rounded-top rect) so they vanish into the frame',
                          'halves': {'door_left': {'slide': [-D.SLIDE, 0]}, 'door_right': {'slide': [D.SLIDE, 0]}},
                          'draw_order': ['doorway', 'door_left', 'door_right', 'frame'], 'parts': door_parts['front'],
                          'tween': {'dur_ms': 550, 'ease': 'Cubic.easeInOut'}, 'floor_line_y': 872},
                'side_left_wall': {'canvas': [D.SW, D.SH], 'skew_matrix': [a, bk, 0, 1, D.STX, D.STY],
                                   'opening_polygon': [D.side_pt(D.OX0, D.OY1), D.side_pt(D.OX0, D.OY0), D.side_pt(D.OX1, D.OY0), D.side_pt(D.OX1, D.OY1)],
                                   'halves': {'door_left': {'slide': [round(-D.SLIDE * a, 1), round(-D.SLIDE * bk, 1)]},
                                              'door_right': {'slide': [round(D.SLIDE * a, 1), round(D.SLIDE * bk, 1)]}},
                                   'draw_order': ['slab', 'doorway', 'door_left', 'door_right', 'frame'], 'parts': door_parts['side'],
                                   'tween': {'dur_ms': 550, 'ease': 'Cubic.easeInOut'}},
                'side_right_wall': {'note': 'mirror the left-wall door horizontally (door_side_r_*.png are pre-mirrored)'},
            },
        }
        (OUT / 'emergency_button_rig.json').write_text(json.dumps(rig, indent=1), encoding='utf-8'); files.append('emergency_button_rig.json')
        b.close()
    print('\n'.join(files))


if __name__ == '__main__':
    main()
