# Job G: Galley + Locker Room (layered SVG)

Sources: `raw_originals/01_ROOM_GALLEY.png`, `raw_originals/05_ROOM_LOCKER.png` (5504 x 3072). Every SVG uses source-pixel coordinates. Objects use their own `viewBox` and sit at `x,y` from the manifest.

## Files

| File | What it is |
|---|---|
| `galley_shell.svg`, `locker_shell.svg` | Floor, walls, wall decor and frame, with every object removed and the area behind it repainted. Groups: `base`, `porthole_1..3`, `door_left/right` (galley), `hazard_mat`, `timeclock_alcove` (locker), `shade` (soft painted shadows, blurred). |
| `galley_lights.svg`, `locker_lights.svg` | The painted lamp cones, glow pools and beacon glow as blurred shapes, one `<g id="light_*">` per source (`light_lamp_1..4`, `light_vending`, `light_door_left/right`; `light_lamp_1..3`, `light_beacon`, `light_alcove`). Draw it over the shell and the wall objects, under the floor objects. Animate group opacity to flicker. Shell alone = lights off (useful for a blackout sabotage). |
| `objects/galley_*.svg` (25) | vending_machine, fridge, coffee_counter, coffee_drip, espresso_machine, mugs (groups `mug_1`, `mug_2`), plant_1, plant_2, cork_board, table (group `pedestal`), stool_01..11 (one file per stool, for sorting), lamp_1..4 |
| `objects/locker_*.svg` (27) | lockers_row, open_04 (cabinet + swung door), open_06, door_frame, door_leaf_left/right, door_closed, door_open, beacon, clock (face without hands), clock_hand_hour, clock_hand_minute, bench_left, bench_right, bench_side, rug, coffee_counter, coffee_machine, mugs, water_cooler, coat_rack_1, coat_rack_2, plant, cork_board, lamp_1..3 |
| `galley.json`, `locker.json` | Manifests (brief schema). Also `layer` (`wall` / `floor` / `sorted`), `draw_order`, `lights_layer`, plus `sliding_door` and `clock_hands` blocks in `locker.json`. |
| `*.png` | Every SVG exported at half source scale (RGBA). `*_room.png` = full composite. Shell and lights PNGs are rendered with Chromium, because the blur filter needs it. |
| `PREVIEW.png` | Both rooms (composite, shell, lights) and every object, labeled with its MAE, on cream. |
| `check/` | `<obj>_side_by_side.png` (original \| SVG over the original), `<obj>_onion.png` (SVG at 50 %), `<room>_room_side_by_side.png` / `_onion.png`, `<room>_manifest_debug.png` (walkable = green, collision = red, sortY = blue, anchors = yellow, doors = white, light radii = orange), `<room>_maskmap.png`, `<room>_shell_repaint.png`. |
| `build/` | Reproducible pipeline: `segment_room.py` → `build_room.py` (trace, shell, light fit, compose) → `finalize.py` (hands, door states, manifest, exports) → `preview.py`. Polygons live in `rooms.py`. Needs `pip install cairosvg vtracer opencv-python-headless scipy playwright`, and Chromium at `/opt/pw-browsers/chromium`. |

## Using it in Phaser

Draw order: shell → `layer:"wall"` objects (lamps, boards, clock, beacon, door frame/leaves) → lights layer → `layer:"floor"` objects (the rug) → `layer:"sorted"` objects and players sorted by `sortY`. Collision polygons sit at the floor footprint (they are the convex hull of the bottom band of each object). Stools have small base footprints only. Anchors:
- Galley: `emergency_pedestal` (center of the table pedestal, for the Job E button), 10 `seats` (4 back stools, 2 end stools, 4 front stools; the middle front stool is left free so the camera can see the button), 2 `vents`, 3 doors (left, right, bottom notch).
- Locker: `timeclock_alcove`, 1 vent (the teal floor hatch), 10 seats (benches and rug), doors `bulkhead` (back wall, sliding) and `bottom`.

Sliding door: the leaves slide by their own width (`slide_px`) inside the `clip` rect, under `door_frame`. The shell has a dark doorway behind them. `door_closed.svg` and `door_open.svg` are ready-made assembled states. Clock: rotate the `hour` and `minute` files about `pivot` (the painted time is 3:00).

## MAE per object (0-255, 4x downscale, over the object's own pixels; target ≤ 12)

**Galley** (room composite **3.85**, shell outside objects 5.49)

| object | MAE | KB | object | MAE | KB |
|---|---|---|---|---|---|
| vending_machine | 6.16 | 296 | stool_01 | 4.23 | 67 |
| fridge | 3.88 | 121 | stool_02 | 4.19 | 63 |
| coffee_counter | 4.00 | 233 | stool_03 | 4.15 | 61 |
| coffee_drip | 7.03 | 77 | stool_04 | 4.00 | 62 |
| espresso_machine | 4.33 | 88 | stool_05 | 4.20 | 67 |
| mugs | 6.68 | 64 | stool_06 | 4.13 | 50 |
| plant_1 | 4.18 | 134 | stool_07 | 4.15 | 56 |
| plant_2 | 4.68 | 135 | stool_08 | 3.79 | 21 |
| cork_board | 4.00 | 139 | stool_09 | 3.57 | 24 |
| table (+pedestal) | 3.29 | 512 | stool_10 | 4.39 | 20 |
| lamp_1 / 2 / 3 / 4 | 3.54 / 3.85 / 3.97 / 3.80 | ~30 | stool_11 | 3.36 | 22 |

**Locker Room** (room composite **5.68**, shell outside objects 7.85)

| object | MAE | KB | object | MAE | KB |
|---|---|---|---|---|---|
| lockers_row | 4.45 | 653 | bench_left | 3.32 | 181 |
| open_04 | 3.46 | 246 | bench_right | 3.46 | 205 |
| open_06 | 3.97 | 144 | bench_side | 3.76 | 117 |
| door_frame | 3.79 | 199 | rug | 3.58 | 835 |
| door_leaf_left | 2.15 | 168 | coffee_counter | 3.36 | 124 |
| door_leaf_right | 2.07 | 190 | coffee_machine | 2.62 | 111 |
| beacon | 5.13 | 29 | mugs | 6.38 | 74 |
| clock face | 7.48 | 136 | water_cooler | 4.24 | 107 |
| clock face + hands | 5.26 | | coat_rack_1 | 4.07 | 142 |
| cork_board | 5.16 | 219 | coat_rack_2 | 4.85 | 158 |
| plant | 3.88 | 149 | lamp_1 / 2 / 3 | 3.87 / 3.65 / 3.48 | ~29 |

The clock face score is measured with the hands erased, so it is higher than the assembled clock score. All SVGs are under 1.5 MB. The largest is `galley_shell.svg` at 1.3 MB.

## Method (how faithfulness was reached)

1. **Segmentation.** Each object was segmented by flood fill inside a hand-placed polygon, stopped by the plum outlines. Outlines were detected as dark green channel OR a morphological black-hat, which catches outlines brightened by the painted lamp light. Thin wall seams glued to outlines were trimmed by an opening. A few lit areas with gaps in the outline (the lockers, the frame top, the rug, the counter tops, the side bench) got explicit add-polygons. Front objects claim pixels first.
2. **Tracing.** Each object was traced with a bilateral filter, then a 24-color k-means palette, then vtracer (spline). This gives flat cel regions with clean edges. Masks with holes get an even-odd clipPath.
3. **Shell.**
   - The holes left by removed objects were repainted by row-wise blending from the surrounding wall and floor.
   - Soft painted lighting was flattened: regions between real color edges take their median color. The flat result was traced at half resolution.
   - The soft lighting was then re-fitted as blurred blobs (`feGaussianBlur`, σ = 12 px) with a least-squares color and opacity per blob. Positive blobs go to the lights layer and negative blobs to `shade`. This is what makes the lamp cones, the vending glow and the floor pools look painted rather than banded.

## Deviations / known flaws (honest)

- **Not hand-drawn vector art.** The SVGs are faithful traces: shapes, colors and outline weights come from the painting. Edges are slightly wobblier than a hand-built SVG, and gradients inside objects become 2-4 flat cel bands. Up close, outlines are a little irregular in places (cork boards, the coffee drip glass, mugs). At game scale it reads like the painting.
- **Blur needs a browser renderer.** The shell `shade` group and the lights layer use `feGaussianBlur`. Chromium and Phaser (via the browser) render it. cairosvg ignores it and shows hard-edged blobs.
- **Repainted shell areas** (behind the vending machine, the fridge, the left-wall objects and the door) are plausible fills, not redrawn art. Streaks are visible only if an object is removed. The side-wall fills (behind the cork board, bench and racks on the slanted left wall) are the weakest.
- **Wall-mounted, static objects keep some wall pixels.** Lockers, the door frame and the cork boards include a few px of wall at rounded corners (from the add-polygons). This is invisible in place.
- **Objects that sit on others leave notches.** Counter tops have notches under the machines and mugs that sit on them, so draw them together. Mugs are one file per cluster, with groups `mug_1` / `mug_2` in the galley.
- **Clock and door details.**
  - The clock hands are clean redrawn shapes, not traced. They match the painted ones (assembled MAE 5.26).
  - The bulkhead door leaves are cut on a straight rectangle, and the dark doorway has square corners inside the rounded inner frame.
- **Painted lamp bulbs.** The bulb glow is included in the lamp objects and the lights layer. Its bright core is a little dimmer than in the painting.
- **Lockers 4 and 6.** Locker 6 is drawn open without a door in the painting, and it stays that way. Locker 5 is mostly hidden behind the swung door of locker 4, and the hidden part is not reconstructed.
- **Seat anchors** are my placements: 10 per room. In the galley, the middle front stool is skipped.

**Rating:** Galley 8/10 and Locker Room 7.5/10 versus the paintings. The composites are close to the originals (MAE 3.9 / 5.7, every object well under 12). The light layer and the separate parts (stools, door, clock hands, open lockers) make them game-usable. Points lost for traced, slightly wobbly edges and for the side-wall repaint quality behind objects.
