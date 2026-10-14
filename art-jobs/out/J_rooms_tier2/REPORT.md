# Job J: Sick Bay + Hydroponics + Cargo (layered SVG)

Sources: `raw_originals/35_ROOM_SICKBAY.png`, `36_ROOM_HYDROPONICS.png`, `37_ROOM_CARGO.png` (5504 x 3072). All coordinates (SVG placement, manifests) are in that source pixel space.

## Files (per room folder `sickbay/`, `hydroponics/`, `cargo/`)

| file | what |
|---|---|
| `<room>_shell.svg` | floor, walls, wall decor that never occludes players, frame, bottom notch. Lamp light is **removed** from it (de-lit) so the lights layer can flicker. Areas behind objects are repainted (no holes). |
| `<room>_lights.svg` | one `<g id="light_n">` (or `grow_light_*`) per lamp: cone trapezoids, floor pool and bulb halo as SVG gradients. Draw with **ADD** blend over the shell, under the objects. Shell + lights reproduces the painting. |
| `hydroponics/hydroponics_mist.svg` | floor mist (`<g id="mist">`, stacked flat-opacity contours of one lavender). ADD blend, between shell and objects; can drift/fade. |
| `objects/<room>_<id>.svg` | one file per object, one root `<g id>`, viewBox = its own box; place at manifest `x,y`. Animated pieces carry `data-pivot` (local units). |
| `<room>.json` | manifest (schema from BRIEFS2): objects with `x,y,w,h,sortY,layer,collision,pivot`, `walkable`, `doors`, `anchors`, `lights`, plus `shell`, `lights_file`, `mist`. |
| `png/` | every SVG exported at half source scale, RGBA. |
| `<room>_composite.png` | shell + lights (+ mist) + all objects, half scale. |
| `check/` | per object `<id>_side_by_side.png` (original, then SVG over the original) and `<id>_onion.png` (SVG at 50 % over the original), full source resolution; room-level `<room>_side_by_side.png`, `<room>_onion.png`, `<room>_shell_only.png`; `<room>_manifest_debug.png` (walkable green, collisions red, sortY blue, anchors yellow, doors orange, pivots white, lights pink). Check PNGs are palette-quantized to keep the repo small. |
| `tools/` | the full pipeline (re-runnable): `run_all.sh <room>`, then `manifest.py`, `preview.py`. |

Manifest `layer`: `wall` = mounted on the back wall (always behind players, sortY = wall base), `floor` = floor decal (scanner pad, always under players), `depth` = depth-sorted by `sortY` (floor contact line), with a `collision` polygon that follows the floor-contact profile of the object or cluster. Children (`monitor_line`, `loading_door_left/right`) sit on top of their parent.

## Method

Faithful trace, not redraw: every object is segmented from the original (dark-plum outline detection, closed regions inside a hand-placed loose box, pockets that match the nearby wall dropped), then vectorized with VTracer at full source resolution (colors sampled from the painting, spline paths). Lamp glow was measured (painting minus a row-interpolated unlit estimate), fitted with non-negative least squares to a few gradient shapes per lamp, written as `<room>_lights.svg`, and subtracted from the shell before tracing. Hidden wall/floor behind objects is repainted per plane (back wall, side walls, floor) by row interpolation that eases into the plane's row median; back-wall panel seams are continued through the repaint, and Cargo's diagonal hazard bands are repainted by copying whole stripe periods (212 / 224 px). The shell is traced at half resolution (scaled x2).

## Verification

MAE = mean absolute error /255 on a 4x box downscale, SVG render composited over the original, measured over the object's mask (dilated 6 px). Target <= 12: **every object passes (worst 7.26, monitor)**. Room MAE = full composite (shell + lights + mist + objects) vs the original over the whole image. Outline alignment: at least 95 % of the original's outline pixels fall on an outline pixel of the composite (checked at half scale, so within 2 px at full res); the 6 px target is met.

### sickbay  (room MAE 2.84, shell-only region 2.29)

Shell `sickbay_shell.svg` 735 KB, lights `sickbay_lights.svg` 3 KB

| object | MAE /255 | SVG KB | layer | notes |
|---|---|---|---|---|
| lamp_1 | 5.51 | 43 | wall |  |
| lamp_2 | 6.42 | 45 | wall |  |
| lamp_3 | 6.26 | 40 | wall |  |
| lamp_4 | 5.98 | 43 | wall |  |
| curtain_front | 4.5 | 188 | depth | pivot [4920, 1645] |
| bed_lower | 2.54 | 109 | depth |  |
| bed_upper | 3.54 | 244 | depth |  |
| curtain_back | 4.82 | 371 | depth | pivot [4340, 636] |
| cart | 5.0 | 307 | depth |  |
| monitor | 7.26 | 180 | wall |  |
| monitor_line | 5.82 | 45 | wall | child of monitor |
| cabinet_tall | 3.81 | 208 | depth |  |
| counter | 3.41 | 229 | depth |  |
| cabinet_wall | 3.69 | 273 | wall |  |
| eye_chart | 4.3 | 84 | wall |  |
| scanner_pad | 2.42 | 272 | floor |  |

### hydroponics  (room MAE 3.39, shell-only region 2.87)

Shell `hydroponics_shell.svg` 1215 KB, lights `hydroponics_lights.svg` 2 KB, mist `hydroponics_mist.svg` 24 KB

| object | MAE /255 | SVG KB | layer | notes |
|---|---|---|---|---|
| gnome | 6.11 | 166 | depth |  |
| watering_can | 4.68 | 64 | depth |  |
| hammock_post | 5.13 | 26 | depth |  |
| hammock | 6.0 | 351 | depth | pivot [182, 1970] |
| planter_greens | 3.19 | 844 | depth |  |
| planter_tomato | 3.43 | 1027 | depth |  |
| pipe_mid | 4.1 | 17 | depth |  |
| planter_lettuce | 4.25 | 603 | depth |  |
| planter_sunflower | 4.38 | 892 | depth |  |
| grow_light_1 | 3.91 | 66 | wall |  |
| grow_light_2 | 4.19 | 49 | wall |  |
| grow_light_3 | 3.72 | 44 | wall |  |
| vines_ceiling | 5.7 | 247 | wall | pivot [1881, 91] |
| hanging_plants_left | 5.16 | 596 | wall | pivot [966, 362] |
| hanging_plants_mid | 5.49 | 832 | wall | pivot [2682, 362] |
| hanging_plants_right | 5.28 | 807 | wall | pivot [4430, 362] |
| porthole | 5.59 | 213 | wall |  |

### cargo  (room MAE 2.6, shell-only region 2.03)

Shell `cargo_shell.svg` 1047 KB, lights `cargo_lights.svg` 3 KB

| object | MAE /255 | SVG KB | layer | notes |
|---|---|---|---|---|
| lamp_1 | 5.97 | 41 | wall |  |
| lamp_2 | 6.36 | 42 | wall |  |
| lamp_3 | 5.98 | 38 | wall |  |
| crates_front_right | 3.08 | 273 | depth |  |
| barrel_front | 3.51 | 78 | depth |  |
| cloth_pile | 3.76 | 110 | depth |  |
| crates_front_left | 3.1 | 493 | depth |  |
| crates_right | 3.07 | 467 | depth |  |
| pallet_jack | 4.02 | 109 | depth |  |
| crates_center | 3.24 | 645 | depth |  |
| forklift | 3.98 | 318 | depth |  |
| barrels_back | 4.08 | 223 | depth |  |
| crate_teal_back | 3.49 | 138 | depth |  |
| wall_keypad | 4.6 | 42 | wall |  |
| crates_back_left | 6.43 | 584 | depth |  |
| cargo_net | 4.35 | 596 | wall |  |
| fuel_tank | 4.1 | 187 | wall |  |
| loading_door | 4.23 | 123 | wall |  |
| loading_door_left | 1.83 | 166 | wall | child of loading_door |
| loading_door_right | 1.51 | 141 | wall | child of loading_door |

## Deviations and known flaws

- **Traced, so it inherits the painting.** Soft painted gradients become a few flat bands (VTracer color quantization). It reads as flat cel shading at game scale but is visible when zoomed in. SVGs are large-ish (objects 40 to 830 KB, shells 0.7 to 1.2 MB) because the paths follow painted detail. All are under 1.5 MB.
- **Occluded parts are not invented.** An object hidden behind a front object (planter ends behind the gnome, watering can and pipe; the barrel behind the front crate; the bed foot behind the curtain) is cut where the front object starts. This is fine while the props stay put. If you move a front prop you will see the cut.
- **Repainted hidden areas are plausible, not perfect.** They are flat wall or floor with continued horizontal stripes and vertical panel seams. Rivets and slanted floor seams are not continued, and contact shadows smear a little under big furniture. You only see this if an object is hidden.
- **Lights are an approximation.** The cones are simple trapezoids, ellipses and gradients fitted to the glow. The fitted residual stays baked in the shell, so shell + lights matches the painting, but lights-off is "mostly de-lit", not perfectly dark. Sick Bay lamp 4 fitted mostly to its halo. The Hydroponics grow-light glow on the plants and planters stays baked into those objects.
- **The mist is an estimate.** It is the floor brightening above a per-row 30th-percentile floor colour. Faint mist below that threshold stays in the shell.
- **Pocket filtering.** In the Hydroponics hanging plants and ceiling vines, wall pockets enclosed by strings or vines were returned to the shell. A few tiny pockets remain inside the vines. They move with the vines if you sway them.
- **Clusters.** Crate stacks and clusters (Cargo) are one object each with one sortY. A player walking *between* crates of the same cluster sorts against the whole cluster.
- **Loading door leaves.** They are split along the painted seam into `loading_door_left/right`. Nothing is painted behind them, so an opening animation needs a dark interior shape added in code.
- Brief items: Sick Bay heart-monitor line is separate (`monitor_line`), curtains have top pivots, the scanner pad is a floor object and the anchor `scanner_pad`. Hydroponics: planters with their pipes, hanging plant groups (pivot top), ceiling vines, hammock (pivot at the wall hook) plus post, gnome, watering can, mist layer, anchor `tape_station_alcove` (the recess stays in the shell, the mat is anchor `tape_station_mat`). Cargo: crate stacks, forklift, pallet jack, barrels, net, fuel tank, loading door (frame plus 2 leaves), cloth pile, wall keypad. Hanging plants are grouped by wall column, not one file per pot.
- The eye chart, porthole and grow-light bars were split out as wall objects (not required) so their fine detail is traced at full resolution.

## Honest rating

**8 / 10 for fidelity, 7 / 10 as game layers.** At display size the composites are very hard to tell from the paintings (room MAE 2.6 to 3.4). Every object is its own correctly named, placed and verified file, and the lights and mist really separate. What holds it back: traced banding instead of hand-built clean shapes, cut-off occluded edges, and approximate repaints behind furniture.
