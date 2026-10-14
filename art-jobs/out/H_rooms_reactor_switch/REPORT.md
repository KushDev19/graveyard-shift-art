# Job H: Reactor + Switchboard (layered SVG)

Sources: `raw_originals/06_ROOM_REACTOR.png`, `raw_originals/07_ROOM_SWITCHBOARD.png` (5508x3072; all coordinates are in that space).

## How it was made
Faithful conversion, not a redraw. Each object was segmented from the original with seeded GrabCut / colour rules inside hand-placed shapes (`src/rooms.py`), traced with vtracer (flat colour regions, spline paths), and wrapped in named `<g id>` groups. Large objects are traced at half source resolution (paths scaled x2); small ones (valves, extinguisher, tool rack, phone, mug, lamp) at full resolution. Every SVG uses source-pixel units, has no rasters, no scripts and no CSS `var()`.

The shell is the original with every object and the steam puffs removed. The holes are repainted zone by zone (back wall, floor, hazard bands, and the rest), so walls never bleed into the floor. Hazard stripes are refilled by copying along their own repeat period, which works for the diagonal side-wall strips too. Big holes get a smooth push-pull fill and the edges get Telea. The shell is then traced after a Lab k-means posterise (48 colours), so the soft painted glows survive as colour bands.

Rebuild everything with `cd src && python build.py REACTOR && python build.py SWITCH && python preview.py` (needs `vtracer cairosvg opencv-python-headless pillow numpy`).

## Files
- `reactor_shell.svg` (1.13 MB), `switchboard_shell.svg` (0.70 MB): floor, walls, wall decor, doorways, frame.
- `reactor_lights.svg`, `switchboard_lights.svg`: additive light pools (one `<circle id="light_*">` each).
- `reactor.json`, `switchboard.json`: manifests in the BRIEFS2 schema. They add `layer` (`wall` = always behind players, `floor` = walk-over, `sorted` = depth-sort on `sortY`), `pivot`, `layers`, `glow_box`, `lamps`, `attach`, `sprites` and per-object `mae`.
- `objects/`: one SVG per object.
  - **Reactor:** `reactor_core.svg` is housing + sphere + cage combined. The core is also delivered as separate layer files `reactor_core_housing.svg`, `reactor_core_sphere.svg` and `reactor_core_cage.svg`, plus `reactor_core_glow.svg` (a radial-gradient glow to pulse). The other reactor objects are `pipes_wall`, `pipes_floor_left/right`, `valve_wall`, `valve_floor_left/right` (each with `data-pivot`/`pivot` at the wheel hub), `tool_rack`, `extinguisher` and `floor_grates`. `steam_puff.svg` is the particle sprite (with a clean outline; the jet streak was removed).
  - **Switchboard:** `switchboard_switchboard.svg` (body + lit lamps), `switchboard_switchboard_body.svg` (lamps unlit) and `switchboard_switchboard_lamps.svg` (21 bulbs + 1 lit dial as `lamp_01`..`lamp_22` groups; bounding boxes and centres are in the manifest under `lamps`). The other switchboard objects are `fuse_box`, `breaker_toggle`, `meter_box`, `knife_switch_box`, `cables_wall`, `tray_upper`, `tray_lower`, `spool_stack`, `spool_single`, `desk` (desk top repainted under its props), `phone`, `mug`, `bankers_lamp` and `switchboard_bankers_lamp_glow.svg`.
- `png/`: every SVG rendered at half source scale (RGBA).
- `check/`: `<room>_<object>_side_by_side.png` (original | rebuilt composite) and `<room>_<object>_onion.png` (object at 50% over the original) for every object. There is also `<room>_room_side_by_side.png`, `<room>_composite.png` and `<room>_manifest_debug.png` (walkable green, collisions red, sortY blue, anchors yellow, doors magenta, light radii orange).
- `PREVIEW.png`: both rebuilt rooms plus every piece, labelled.

Anchors: reactor `keypad_alcove` (1150,1000) with its floor mark, `vents` and `steam_emitters` (where the painted puffs were). Switchboard `patch_station_alcove` (3960,900) with its floor mark, `vents` and `desk_seat`.

## MAE (mean abs error /255, 4x downscale, object region, object composited over the traced shell; target <= 12)
| Reactor | MAE | Switchboard | MAE |
|---|---|---|---|
| core (housing+sphere+cage) | 6.47 | switchboard (lamps lit) | 7.15 |
| pipes_wall | 8.04 | cables_wall | 6.91 |
| pipes_floor_left | 6.11 | fuse_box | 6.10 |
| pipes_floor_right | 5.44 | breaker_toggle | 5.92 |
| valve_wall | 11.12 | meter_box | 6.31 |
| valve_floor_left | 8.03 | knife_switch_box | 6.69 |
| valve_floor_right | 8.26 | tray_upper | 5.92 |
| tool_rack | 4.64 | tray_lower | 5.19 |
| extinguisher | 5.23 | spool_stack | 5.06 |
| floor_grates | 11.41 | spool_single | 4.57 |
| | | desk | 5.82 |
| | | bankers_lamp | 9.12 |
| | | phone | 9.33 |
| | | mug | 8.56 |
| **shell (visible areas)** | **3.94** | **shell (visible areas)** | **3.12** |
| **whole room** | **5.18** | **whole room** | **4.29** |

Every object is under 12. The highest scores are on the thinnest objects (small valve and grate bars), where edge anti-aliasing dominates the error. Outlines line up because every path is traced from the source pixels.

## Deviations and known flaws
- **No gauges in the Reactor painting.** The brief lists them, but there is nothing to trace, so the valves stand in as the interactive dials.
- **Painted glows stay in the shell.** The floor glow in front of the core, the desk-lamp light cone and the switchboard halo are still painted in, so an "off" lamp still leaves its floor or wall light. The glow sprites are meant to be added on top (additive, opacity 0 to 0.6) to pulse or flicker.
- **Repaint behind big objects is plausible, not detailed.** The shell behind the core and grates is a smooth wall/floor colour with no tile seams. It is never visible, because those objects never move.
- **Colour banding.** The soft glows come out as visible colour bands rather than smooth gradients (most noticeable on the wall around the core). Painterly speckle and grain are simplified.
- **Unlit console bulbs are made up.** The painting has no off state, so the dim teal glass and the halo pulled back to panel teal were generated, not traced. The second centre dial is not lit, so it stays in the body.
- **The desk includes the shaded floor between its legs.** It is fine for depth sorting at the desk's sortY.
- **Walkable areas, collisions, anchors and doors were placed by eye.** They come from the painting; tune them in Phaser.
- **Check images are rendered at half source scale.** This keeps the repo light (`check/` is 15 MB).

## Honest rating
About 8/10 for fidelity. At game scale the rebuilt rooms read the same as the paintings: same shapes, colours, outlines and props, with every interactive piece separated, named and placed by the manifest. The weak points are the banding on soft glows and the generated unlit-lamp state.
