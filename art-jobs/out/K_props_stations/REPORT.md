# Job K: Task stations + ship props

Sources: `raw_originals/14_PROPS_STATIONS.png` (4 stations x idle / highlight / done) and `raw_originals/15_PROPS_SHIP.png` (vent closed/open, time clock idle/ready, table clutter). The doors and the emergency button on sheet 15 were skipped, as the brief says (Job E has them).

## Files

| File | What | Groups (ids) |
|---|---|---|
| `station_keypad_{orig,front}.svg` | keypad terminal | `body`, `state_idle`, `state_highlight`, `state_done` |
| `station_switchboard_{orig,front}.svg` | patch-cable switchboard | same |
| `station_tape_{orig,front}.svg` | reel-to-reel tape deck | same |
| `station_scope_{orig,front}.svg` | round CRT scope console | same |
| `timeclock_{orig,front}.svg` | punch time clock | `body`, `state_idle` (`screen_idle`, `card_slot_idle*`), `state_ready` (`screen_ready`, `card_slot_glow*`) |
| `vent_frame_{orig,front}.svg` | floor vent frame (hole under the lid repainted) | `vent_frame` |
| `vent_lid_{orig,front}.svg` | hinged lid, same viewBox as its frame | `lid_closed` (default), `lid_open`; both carry `data-pivot`, `lid_open` has `data-hinge` |
| `table_clutter_{orig,front}.svg` | 3 mugs + donut box | `mug_teal`, `donut_box`, `mug_cream`, `mug_red` (painter's order) |
| `png/*.png` | RGBA exports at half source scale, one per state (`*_orig_idle.png`, `*_front_done.png`, `vent_orig_open.png`, ...) | |
| `check/*_side_by_side.png`, `check/*_onion.png` | original vs SVG, and the SVG at 50% over the original (every `*_orig` state) | |
| `PREVIEW.png` | all exports labeled on cream | |
| `tools/` | `trace.py` (tracer), `build_orig.py`, `build_ship.py`, `build_front.py`, `outline_check.py`, `preview.py`, plus JSON logs | |

SVG sizes: 18 to 775 KB (switchboard is the largest because of its wood grain and cables). Nothing is embedded, there are no scripts, and the only gradients are radial ones for the glows.

## How to use

- **States:** exactly one of `state_idle` / `state_highlight` / `state_done` (time clock: `state_idle` / `state_ready`) is visible at a time. Flip the `display` attribute. `body` is shared and always on. The beacon and its glow live inside `state_done`.
- **Vent:** stack `vent_frame_*` with `vent_lid_*` (both use the same viewBox). Then show `lid_closed` or `lid_open`. In this 3/4 view the lid can't swing as a plain 2D rotation, so swap the two groups (or tween `scaleY` about `data-pivot`, which sits on the hinge line).
- **Coordinates:** the `*_orig` viewBoxes are in the sheet's own pixel coordinates (for example, the keypad is `viewBox="186 0 1066 1096"`), as shared trace rule 1 requires. Every state layer is registered to its body. The `*_front` files use the same pixel scale.
- Everything renders in cairosvg (no `var()`, no filters).

## Verification of the `*_orig` traces (MAE on a 4x downscale over the object region, 0 to 255; target is 12 or lower)

| Object | idle | highlight / ready / open | done / closed |
|---|---|---|---|
| station_keypad | 4.78 | 5.77 | 6.15 |
| station_switchboard | 6.50 | 8.28 | 10.68 |
| station_tape | 5.55 | 8.51 | 5.58 |
| station_scope | 3.82 | 5.44 | 6.74 |
| timeclock | 5.91 | 8.19 (ready) | |
| vent | | 5.78 (open) | 6.70 (closed trace), 4.49 (closed lid placed on frame) |
| table_clutter | 6.30 | | |

Every state of every object is under 12. **Outline alignment** (`tools/log_outline.json`, idle drawings): 95% of the SVG's outline pixels fall on the original's outline (0 px). Going the other way, 95% of the original's outline pixels are within 1.0 px of the SVG outline, which is well inside the 6 px tolerance.

Method: each sprite is color-quantized in Lab with the plum outline excluded (outline pixels come from a luminance and local-contrast test and are traced as their own layer on top, in up to 3 sampled outline colors). Fill clusters are grown under the outlines and stacked by area, so the layers never leave gaps. Soft painted gradients were merged into flat cel zones. States are separated by aligning each state drawing to idle (phase correlation) and keeping only the outline-bounded cells that changed (screens, keys, lamps, reels, the beacon). Soft glows become radial gradients.

## The `*_front` versions

These are built from the same traced paths with a piecewise-affine mesh: the corners of each iso face (front, top, side), read off the sheet, are moved to a front-facing 3/4 layout like the Galley fridge. The front face is flat, the top shows as a band, and the side is a narrow strip (on the left for the time clock, whose cream side is on the left). All ids, states and colors are unchanged. The floor vent uses true projective maps: the frame becomes a straight-on floor rectangle and the open lid stands up on the hinge. In the clutter, the mugs were already front-facing and stay as drawn, and the donut box is sheared so its front face is level. The meshes are in `tools/build_front.py`, so they're easy to tweak.

## Deviations and known flaws

1. **`*_front` versions are re-projections, not hand redraws.** Round parts (gauges, reels, the scope CRT) become slightly skewed ellipses, the outline gets thinner or thicker on compressed faces, and top bands are thin. They read well at in-game size, but they're the weakest part of the job.
2. `table_clutter_front`: the corner of the box hidden behind the red mug has no source art. It was inpainted, and a small flat orange patch shows beside the red mug's rim.
3. `station_keypad` highlight recolors the whole body, so `state_highlight` there is a full re-trace that covers the body instead of a small delta layer (detected automatically, logged in `tools/log_orig.json`).
4. Painted glows (the highlight halo around the keypad and tape deck, the time clock's warm haze) are approximated with radial gradients. They're the main source of the higher MAE on highlight/ready (about 8). The switchboard done state (10.7) is its fine wood grain, flattened into cel zones.
5. The vent: the frame behind the open lid was repainted from the closed drawing's rim (affine fit, corner residual 6.9 px). `lid_closed` is the closed drawing placed on the frame by a `matrix()` transform (`*_orig`) or with the coordinates baked in (`*_front`).
6. Lettering: none in these props.

## Honest rating

- `*_orig`: **8.5/10.** Faithful to the sheets (MAE 3.8 to 10.7, outlines within 1 px) and cleanly layered, with real state toggles. Painted soft shading has been flattened into cel zones, which suits the style guide.
- `*_front`: **6.5/10.** Usable and consistent with the originals in every detail and state. The tape deck, switchboard, keypad and time clock look good; the scope's rounded hood, the vent and the donut box show warp artifacts. If any front view becomes a hero prop, a hand-tuned redraw would beat this.
