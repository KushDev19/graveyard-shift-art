"""Room specs for job J. Coordinates are in 2000 px ref space (x K -> source px).
Objects are listed front-most first: earlier objects claim overlapping pixels."""
import math
from jlib import box

SICKBAY = dict(
    room='sickbay', src='35_ROOM_SICKBAY.png',
    objects=[
        *[dict(id=f'lamp_{i + 1}', region=box(bx - 49, 100, bx + 50, 216), wall=True,
               add=[box(bx - 20, 186, bx + 20, 210)]) for i, bx in enumerate([392, 812, 1187, 1606])],
        dict(id='curtain_front', region=box(1672, 592, 1918, 1012), depth=30, pivot='top'),
        dict(id='bed_lower', region=box(1448, 782, 1712, 1004), depth=150),
        dict(id='bed_upper', region=box(1428, 432, 1818, 662), depth=150),
        dict(id='curtain_back', region=box(1382, 228, 1768, 528), depth=30, pivot='top'),
        dict(id='cart', region=box(886, 352, 1118, 555), depth=60),
        dict(id='monitor', region=box(1180, 238, 1348, 404), wall=True,
             split=[('monitor_line', 'green_glow')]),
        dict(id='cabinet_tall', region=box(202, 198, 448, 552), depth=80,
             add=[[(223, 262), (227, 228), (241, 214), (262, 211), (420, 211), (435, 219), (441, 240), (441, 262)]]),
        dict(id='counter', region=box(438, 356, 848, 552), depth=80),
        dict(id='cabinet_wall', region=box(438, 118, 848, 350), wall=True),
        dict(id='eye_chart', region=box(930, 162, 1068, 342), wall=True),
        dict(id='scanner_pad', region=box(372, 618, 822, 893), floor=True),
    ],
)

def cone(bx, by=180, w0=40, w1=170, y1=480, w2=240, y2=620):
    return [(bx - w0, by), (bx + w0, by), (bx + w1, y1), (bx + w2, y2), (bx - w2, y2), (bx - w1, y1)]

SICKBAY['glows'] = [dict(id=f'light_{i + 1}', poly=cone(bx), bulb=(bx, 198))
                    for i, bx in enumerate([392, 812, 1187, 1606])]

PLANES = dict(
    back=[(222, 36), (1778, 36), (1778, 478), (222, 478)],
    left=[(36, 440), (222, 36), (222, 478), (36, 1024)],
    right=[(1778, 36), (1964, 440), (1964, 1024), (1778, 478)],
    floor=[(222, 478), (1778, 478), (1964, 1024), (36, 1024)],
)
SICKBAY['planes'] = PLANES
SICKBAY['refx'] = dict(back=[(232, 330), (470, 760), (1360, 1380), (1660, 1770)])

HYDRO = dict(
    room='hydroponics', src='36_ROOM_HYDROPONICS.png', planes=PLANES,
    objects=[
        dict(id='gnome', region=box(1406, 720, 1502, 880), depth=25),
        dict(id='watering_can', region=box(876, 778, 1024, 874), depth=30),
        dict(id='hammock_post', region=box(558, 783, 620, 1030), depth=20),
        dict(id='hammock', region=box(48, 692, 562, 978), pivot=(66, 716), collision=False),
        dict(id='planter_greens', region=box(522, 622, 1044, 832), depth=110),
        dict(id='planter_tomato', region=box(1044, 552, 1584, 832), depth=110),
        dict(id='pipe_mid', region=box(1256, 524, 1312, 610), depth=20),
        dict(id='planter_lettuce', region=box(893, 410, 1364, 580), depth=100),
        dict(id='planter_sunflower', region=box(1383, 352, 1798, 614), depth=100),
        dict(id='grow_light_1', region=box(248, 62, 564, 114), wall=True),
        dict(id='grow_light_2', region=box(798, 62, 1114, 114), wall=True),
        dict(id='grow_light_3', region=box(1443, 62, 1759, 114), wall=True),
        dict(id='vines_ceiling', wall_tol=22, region=box(566, 30, 802, 198), wall=True, pivot='top', keep=0.002),
        dict(id='hanging_plants_left', wall_tol=22, region=box(252, 124, 448, 440), wall=True, pivot='top', keep=0.002),
        dict(id='hanging_plants_mid', wall_tol=22, region=box(848, 124, 1114, 410), wall=True, pivot='top', keep=0.002),
        dict(id='hanging_plants_right', wall_tol=22, region=box(1482, 124, 1750, 404), wall=True, pivot='top', keep=0.002),
        dict(id='porthole', region=[(1295 + 146 * math.cos(t / 16 * math.pi), 225 + 146 * math.sin(t / 16 * math.pi)) for t in range(32)], wall=True),
    ],
    glows=[dict(id='grow_light_pink', bulb=(406, 104), top=150, w=200, core=110, pool_y=560, pool_rx=260, halo=(170, 40)),
           dict(id='grow_light_green_1', bulb=(956, 104), top=150, w=200, core=110, pool_y=560, pool_rx=260, halo=(170, 40)),
           dict(id='grow_light_green_2', bulb=(1601, 104), top=150, w=200, core=110, pool_y=560, pool_rx=260, halo=(170, 40))],
    mist=dict(region=[(222, 478), (1778, 478), (1964, 1024), (36, 1024)], color='#C9BFDC'),
    refx=dict(back=[(232, 250), (450, 490), (805, 850), (1115, 1150), (1440, 1480), (1750, 1775)]),
)
for g in HYDRO['glows']:
    g['poly'] = cone(g['bulb'][0], 100, 160, 230, 480, 300, 620)

CARGO = dict(
    room='cargo', src='37_ROOM_CARGO.png', planes=PLANES,
    objects=[
        *[dict(id=f'lamp_{i + 1}', region=box(bx - 49, 100, bx + 50, 216), wall=True,
               add=[box(bx - 20, 186, bx + 20, 210)]) for i, bx in enumerate([392, 1187, 1606])],
        dict(id='crates_front_right', region=box(1763, 773, 1940, 1024), depth=150),
        dict(id='barrel_front', region=box(1710, 878, 1797, 1018), depth=45),
        dict(id='cloth_pile', region=box(1533, 870, 1714, 1020), depth=80),
        dict(id='crates_front_left', region=box(63, 783, 444, 1024), depth=150),
        dict(id='crates_right', region=box(1106, 603, 1480, 877), depth=170),
        dict(id='pallet_jack', region=box(1476, 616, 1684, 807), depth=60),
        dict(id='crates_center', region=box(543, 551, 922, 864), depth=190),
        dict(id='forklift', region=box(1160, 413, 1434, 617), depth=110),
        dict(id='barrels_back', region=box(1626, 391, 1802, 562), depth=90),
        dict(id='crate_teal_back', region=box(978, 398, 1097, 547), depth=70),
        dict(id='wall_keypad', region=box(426, 273, 480, 354), wall=True),
        dict(id='crates_back_left', region=box(198, 273, 480, 582), depth=120),
        dict(id='cargo_net', region=box(993, 218, 1342, 407), wall=True),
        dict(id='fuel_tank', region=box(1376, 226, 1732, 422), wall=True),
        dict(id='loading_door', region=box(486, 103, 970, 494), wall=True,
             split=[('loading_door_left', ('poly', [(528, 146), (737, 146), (737, 252), (707, 274), (707, 362), (737, 382), (737, 474), (528, 474)])),
                    ('loading_door_right', ('poly', [(737, 146), (940, 146), (940, 474), (737, 474), (737, 382), (707, 362), (707, 274), (737, 252)]))]),
    ],
    refx=dict(back=[(232, 330), (480, 490), (970, 990), (1345, 1375), (1735, 1775)]),
)
CARGO['periodic'] = [dict(poly=box(222, 474, 1778, 552), period=212),
                      dict(poly=[(40, 955), (1960, 955), (1960, 1024), (40, 1024)], period=224)]
CARGO['glows'] = [dict(id=f'light_{i + 1}', poly=cone(bx), bulb=(bx, 198)) for i, bx in enumerate([392, 1187, 1606])]

ROOMS = {'sickbay': SICKBAY, 'hydroponics': HYDRO, 'cargo': CARGO}
