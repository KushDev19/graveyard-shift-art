# Job D: Tier 2 task panels and minimap

## Files
| File | What |
|---|---|
| `panel_thrusters.svg/.png` | Align Thrusters, 2048x1536. CRT with a seafoam nozzle diagram and a dashed amber target line; vertical slider track with blank ticks (the amber tick marks the target) |
| `panel_gyro.svg/.png` | Calibrate Gyro. Dark dial with 3 grooves (r 392/282/172, 46 px wide), each with a seafoam notch (38°, 150°, 262°); big button socket and 2 lamp sockets below it |
| `panel_memory.svg/.png` | Pattern Memory. CRT with a 3x3 grid of round lamp sockets, a teal plate with a 3x3 grid of square button sockets, and 5 progress lamp sockets |
| `panels2.json` | Every socket in 2048x1536 pixels (rects: x,y,w,h,cx,cy; circles: cx,cy,r; gyro rings: cx,cy,r,width,notch angle; slider and marker travel paths), plus each part's size |
| `parts/*.svg/.png` | 15 moving parts at 1:1 panel scale, centered: `slider_knob`, `thrust_marker`, `gyro_bead`, `gyro_bead_locked`, `btn_big_round_idle/_pressed`, `lamp_small_unlit/_lit_amber/_lit_seafoam`, `lamp_round_unlit/_lit`, `btn_square_idle/_pressed/_correct/_wrong` |
| `minimap.svg/.png` (1600x900), `minimap_320.png` | Blueprint plan view. 9 `<g id="room_<name>">` groups, corridors in `<g id="corridors">` (`corr_<a>__<b>`) |
| `minimap_rooms.json` | Center and bbox of each room, plus corridor polylines (1600x900 space; multiply by 0.2 for the 320 version) |
| `debug/*_sockets.png` | The JSON sockets drawn in magenta over each panel (drawn from the JSON file, not from the drawing code) |
| `debug/*_assembled.png` | Parts pasted at their JSON positions (mixed states) to show fit and scale |
| `debug/minimap_rooms_overlay.png` | Room bboxes from JSON over the minimap |
| `PREVIEW.png` | Everything labeled on cream |
| `src/build.py` | Generator that rebuilds all of the above (`pip install cairosvg pillow`, then run from the repo root) |

The SVGs are 11 to 16 KB each. They contain no text, no `var()`, no rasters and no scripts.

## How to use
- Draw the panel at any scale `k` (for example 1024x768 means k = 0.5). Put each part's center at `socket.(cx,cy) * k` and scale the part by `k` too, since parts are drawn at panel scale.
- **Thrusters:** move `slider_knob` along `slider_knob_path` (x fixed, y1 to y2) and map the same fraction to `thrust_marker` on `thrust_marker_path`. The puzzle is solved when the marker's y equals `target_line.y` (794).
- **Gyro:** place a bead at `(cx + r·sin a, cy − r·cos a)`, with a measured clockwise from straight up. Once it reaches `notch_angle_deg`, switch it to `gyro_bead_locked`. `btn_big_round_*` goes on `button_big`, and `lamp_small_*` goes on `lamp_left` and `lamp_right`.
- **Memory:** `lamp_round_*` goes on `lamp_RC` and `btn_square_*` goes on `button_RC` (R = row, C = column). `lamp_small_unlit/_lit_seafoam` goes on `progress_0..4`.
- All 3 panels share a `power_lamp` socket in the bottom-right corner.
- **Minimap:** tint or stroke the room's `<rect>`/`<path>` inside `room_<name>` to highlight it. Place player dots near `cx,cy`. `locker_room` has `connected: false`.

## Verification
I rendered every socket from `panels2.json` on top of its panel, and each one sits exactly on its socket. I also pasted every part at its JSON position, and they all fit their sockets at the right scale.

## Deviations and known flaws
- I couldn't find the Job C output in the repo, so I followed the Job C spec text for the construction: cream two-tone bezel, 4 slotted corner screws, a cream/amber/coral racing stripe across the top, plum 10 px outlines and a bottom vent. Compare the two side by side before merging; if Job C made different choices (stripe height or position, screw style), copy C's `frame()` values into `src/build.py` and rerun it.
- **Additions not in the brief:**
  - `thrust_marker`, so the thruster screen has something to move.
  - `gyro_bead` and its locked state, as the gyro's moving parts.
  - My own big button, so this job doesn't depend on C's `btn_big_amber`.
  - Static toggles and a vent on the gyro panel to fill the empty sides.
  - Engine nubs on the minimap hull.
- The minimap's bottom-right corner below the Cargo Hold is a bit empty. At 320 px the galley button icon is small and could be mistaken for a hat.
- The lit glows use radial gradients, which the brief allows for glow.

## Honest rating
- **Panels: 8/10.** They're clean, consistent and readable, and the materials match `14_stations.jpg`: cream plastic, teal metal and dark CRTs. They're flatter and plainer than the painted refs and lack the painted refs' small wear details.
- **Parts: 8/10.**
- **Minimap: 8/10.** It's balanced and reads well at 320x180.
