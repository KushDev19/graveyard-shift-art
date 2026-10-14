"""Room configs for Job G. Polygons are in quarter-scale px (x4 = source px).
Objects are listed FRONT TO BACK: earlier objects claim overlapping pixels first.
fill: how the shell is repainted behind the object ('h' = blend along rows, 'v' = along columns)."""

def stool(i, cx, top, bottom, w=34):
    return dict(id=f"stool_{i:02d}", file=f"objects/galley_stool_{i:02d}.svg",
                poly=[(cx - w, top), (cx + w, bottom)])

GALLEY = dict(
    room="galley", source="01_ROOM_GALLEY.png", barrier=55,
    objects=[
        *[stool(i + 1, cx, 540, 628) for i, cx in enumerate([480, 583, 688, 792, 897])],
        stool(6, 350, 474, 560, 36), stool(7, 1026, 474, 560, 36),
        dict(id="table", file="objects/galley_table.svg", poly=[(384, 432), (628, 432), (628, 405), (748, 405), (748, 432), (990, 432), (990, 584), (384, 584)],
             parts=[dict(id="pedestal", poly=[(628, 405), (748, 500)])],
             add=[[(421, 518), (956, 518), (956, 570), (950, 577), (427, 577), (421, 570)]]),
        *[dict(id=f"stool_{i + 8:02d}", file=f"objects/galley_stool_{i + 8:02d}.svg", poly=[(cx - 34, 408), (cx + 34, 448)],
             add=[[(cx - 28, 437), (cx - 26, 423), (cx - 17, 415), (cx, 413), (cx + 17, 415), (cx + 26, 423), (cx + 28, 437)]], open_r=0)
          for i, cx in enumerate([487, 588, 787, 887])],
        dict(id="mug_1", file="objects/galley_mugs.svg", poly=[(596, 252), (638, 293)]),
        dict(id="mug_2", file="objects/galley_mugs.svg", poly=[(654, 244), (752, 299)]),
        dict(id="coffee_drip", file="objects/galley_coffee_drip.svg", poly=[(460, 184), (524, 302)]),
        dict(id="espresso_machine", file="objects/galley_espresso_machine.svg", poly=[(528, 190), (652, 304)]),
        dict(id="coffee_counter", file="objects/galley_coffee_counter.svg", poly=[(436, 254), (776, 380)],
             add=[[(452, 265), (760, 265), (766, 272), (766, 305), (760, 312), (452, 312), (446, 305), (446, 272)]]),
        dict(id="plant_1", file="objects/galley_plant_1.svg", poly=[(778, 230), (880, 362)], open_r=4),
        dict(id="plant_2", file="objects/galley_plant_2.svg", poly=[(1155, 226), (1238, 364)], open_r=4),
        dict(id="vending_machine", file="objects/galley_vending_machine.svg", poly=[(155, 163), (301, 374)], side="right"),
        dict(id="fridge", file="objects/galley_fridge.svg", poly=[(300, 174), (422, 374)], side="right"),
        dict(id="cork_board", file="objects/galley_cork_board.svg", poly=[(1028, 160), (1190, 278)], wall=True,
             add=[[(1040, 167), (1180, 167), (1185, 172), (1185, 266), (1180, 271), (1040, 271), (1035, 266), (1035, 172)]]),
        *[dict(id=f"lamp_{i + 1}", file=f"objects/galley_lamp_{i + 1}.svg", poly=[(cx - 36, 18), (cx + 36, 144)], wall=True,
                 add=[[(cx - 14, 116), (cx + 14, 116), (cx + 12, 127), (cx + 6, 133), (cx - 6, 133), (cx - 12, 127)]])
          for i, cx in enumerate([270, 558, 817, 1105])],
    ],
    shell_parts=[
        *[dict(id=f"porthole_{i + 1}", poly=[(cx - 66, 50), (cx + 66, 184)], quant=40, speckle=2) for i, cx in enumerate([441, 688, 934])],
        dict(id="door_left", poly=[(50, 226), (114, 608)]),
        dict(id="door_right", poly=[(1260, 226), (1326, 608)]),
    ],
    lights=[*[dict(id=f"light_lamp_{i + 1}", x=cx, y=128) for i, cx in enumerate([270, 558, 817, 1105])],
            dict(id="light_vending", x=228, y=330), dict(id="light_door_left", x=70, y=520),
            dict(id="light_door_right", x=1300, y=520)],
    interior=[(153, 24), (1222, 24), (1352, 300), (1352, 702), (798, 702), (798, 746), (582, 746), (582, 702),
              (24, 702), (24, 300)],
    no_light=[[(cx - 52, 64), (cx + 52, 170)] for cx in [441, 688, 934]],
)


def lamp(i, cx, prefix):
    return dict(id=f"lamp_{i}", file=f"objects/{prefix}_lamp_{i}.svg", poly=[(cx - 36, 18), (cx + 36, 144)], wall=True,
                add=[[(cx - 14, 116), (cx + 14, 116), (cx + 12, 127), (cx + 6, 133), (cx - 6, 133), (cx - 12, 127)]])


LOCKER = dict(
    room="locker", source="05_ROOM_LOCKER.png", barrier=55,
    objects=[
        dict(id="water_cooler", file="objects/locker_water_cooler.svg", poly=[(1243, 508), (1340, 710)]),
        dict(id="coffee_machine", file="objects/locker_coffee_machine.svg", poly=[(1086, 532), (1224, 650)]),
        dict(id="mugs", file="objects/locker_mugs.svg", poly=[(982, 580), (1088, 657)]),
        dict(id="coffee_counter", file="objects/locker_coffee_counter.svg", poly=[(970, 594), (1246, 710)],
             add=[[(982, 603), (1236, 603), (1242, 612), (1242, 660), (1236, 668), (982, 668), (976, 660), (976, 612)]]),
        dict(id="plant", file="objects/locker_plant.svg", poly=[(38, 556), (126, 710)], open_r=6),
        dict(id="coat_rack_2", file="objects/locker_coat_rack_2.svg", poly=[(128, 486), (194, 704)], open_r=3),
        dict(id="bench_side", file="objects/locker_bench_side.svg", poly=[(62, 406), (190, 594)],
             add=[[(110, 420), (172, 420), (172, 468), (165, 502), (146, 548), (80, 548), (72, 505), (88, 462)]]),
        dict(id="bench_left", file="objects/locker_bench_left.svg", poly=[(362, 452), (630, 564)]),
        dict(id="bench_right", file="objects/locker_bench_right.svg", poly=[(747, 452), (1014, 564)]),
        dict(id="rug", file="objects/locker_rug.svg", poly=[(486, 398), (892, 678)], floor=True, trace=dict(quant=10, filter_speckle=20),
             add=[[(878, 538), (875, 560), (867, 581), (853, 601), (834, 619), (810, 635), (783, 647), (753, 656), (721, 662), (688, 664), (655, 662), (623, 656), (593, 647), (566, 635), (542, 619), (523, 601), (509, 581), (501, 560), (498, 538), (501, 516), (509, 495), (523, 475), (542, 457), (566, 441), (593, 429), (623, 420), (655, 414), (688, 412), (721, 414), (753, 420), (783, 429), (810, 441), (834, 457), (853, 475), (867, 495), (875, 516)]]),
        dict(id="coat_rack_1", file="objects/locker_coat_rack_1.svg", poly=[(156, 198), (232, 378)], open_r=5),
        dict(id="locker_04_door", file="objects/locker_open_04.svg", poly=[(741, 204), (796, 222), (796, 394), (741, 394)]),
        dict(id="locker_04", file="objects/locker_open_04.svg", poly=[(687, 164), (748, 390)], add=[[(691, 170), (745, 170), (745, 378), (691, 378)]]),
        dict(id="locker_06", file="objects/locker_open_06.svg", poly=[(808, 164), (870, 390)], add=[[(811, 170), (867, 170), (867, 378), (811, 378)]]),
        dict(id="lockers", file="objects/locker_lockers_row.svg", poly=[(484, 160), (1008, 392)], add=[[(492, 170), (1002, 170), (1002, 378), (492, 378)]]),
        dict(id="door_leaf_left", file="objects/locker_door_leaf_left.svg", poly=[(272, 175), (351, 334)], mode="poly"),
        dict(id="door_leaf_right", file="objects/locker_door_leaf_right.svg", poly=[(351, 175), (434, 334)], mode="poly"),
        dict(id="beacon", file="objects/locker_beacon.svg", poly=[(325, 88), (377, 145)], wall=True, open_r=0),
        dict(id="door_frame", file="objects/locker_door_frame.svg", poly=[(238, 116), (466, 344)], wall=True,
             add=[[(243, 150), (250, 135), (262, 126), (280, 122), (425, 122), (442, 126), (454, 135), (461, 150), (461, 340), (243, 340)]]),
        dict(id="clock", file="objects/locker_clock.svg", poly=[(628, 36), (750, 156)], wall=True, open_r=0,
             erase=[dict(poly=[(684, 66), (693, 66), (693, 95), (684, 95)], fill="h"),
                    dict(poly=[(692, 93), (717, 93), (717, 105), (692, 105)], fill="v")]),
        dict(id="cork_board", file="objects/locker_cork_board.svg", poly=[(34, 206), (136, 528)], wall=True,
             add=[[(118, 212), (131, 218), (131, 320), (66, 520), (42, 524), (38, 352)]]),
        *[lamp(i + 1, cx, "locker") for i, cx in enumerate([558, 817, 1105])],
    ],
    repaint=[dict(poly=[(272, 175), (434, 334)], color=(46, 30, 52))],
    overlays=[("objects/locker_clock_hand_hour.svg", "locker_clock"), ("objects/locker_clock_hand_minute.svg", "locker_clock")],
    shell_parts=[
        dict(id="hazard_mat", poly=[(266, 330), (436, 384)]),
        dict(id="timeclock_alcove", poly=[(1020, 166), (1192, 334)]),
    ],
    lights=[*[dict(id=f"light_lamp_{i + 1}", x=cx, y=128) for i, cx in enumerate([558, 817, 1105])],
            dict(id="light_beacon", x=350, y=112), dict(id="light_alcove", x=1110, y=300)],
    interior=[(153, 24), (1222, 24), (1352, 300), (1352, 702), (798, 702), (798, 746), (582, 746), (582, 702),
              (24, 702), (24, 300)],
    no_light=[],
)
