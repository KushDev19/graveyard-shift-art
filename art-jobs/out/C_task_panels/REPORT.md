# Job C: Task panels (Tier 1) and moving parts

## Files
| File | What |
|---|---|
| `panel_keypad.svg/.png` | Reactor Override: cream bezel, top racing stripe, semicircle gauge (coral zone, blank ticks), speaker grille, unlit amber LED window, plum well with 2x5 empty key sockets, coral hazard stripes, amber lamp socket |
| `panel_switchboard.svg/.png` | Patch the Switchboard: wood frame with grain, brass corner caps and screws, 4 output jacks (left) and 4 input jacks (right), unlit lamps (left: red, yellow, blue, green; right: green, red, blue, yellow), stitched plum felt center, amber power lamp |
| `panel_tape.svg/.png` | Tape Transfer: cream trim, brushed teal faceplate, 2 reel recesses with spindles, tape head and guide rollers, VU window (amber-to-coral arc), empty progress window, big button socket, 3 toggles, power lamp |
| `panels.json` | Every socket (center x,y and w,h in 2048x1536 px), its kind, default part, scale, pivots; plus every part's size and anchor |
| `task_parts/*.svg/.png` | 25 parts: `key_idle/pressed/correct/wrong`, `plug_red/yellow/blue/green`, `cable_seg_*` (4), `lamp_lit_red/yellow/blue/green/amber`, `lamp_unlit`, `reel_full`, `reel_empty`, `vu_needle`, `btn_big_amber(_pressed)`, `slider_knob`, `jack_ring` |
| `debug/*_debug.png` | Socket rectangles from `panels.json` drawn on each panel (magenta; green cross = center; circles for round sockets; line from pivot for needles) |
| `debug/*_assembled.png` | Parts placed purely from `panels.json` (demo: some keys pressed/correct/wrong, one yellow cable patched) |
| `PREVIEW.png` | Assembled panels and all parts, labeled, on cream |
| `src/build.py`, `src/verify.py` | Generator (sockets defined once, written to both SVG and JSON) and verifier/renderer |

Panel SVGs are 15 to 17 KB each; all parts together are 100 KB. Panel PNGs are native 2048x1536. Part PNGs are 2x the panel-space size (when the panel is shown at 1024 px wide they are 4x).

## How to use
- Draw the panel, then for each socket put the part's `anchor` on the socket's `x,y` and scale by `socket.scale` times `displayWidth/2048`. Parts are drawn at panel scale, so scale is 1.0 unless a value is given.
- **Needles** (`vu_needle`, also used for the keypad gauge): origin = `parts.vu_needle.pivot` (30,280), rotate around it. The keypad gauge sweeps -88 to +88 deg (coral zone +58 to +88). The VU sweeps -50 to +50 deg (coral +16 to +50).
- **Switchboard**: at rest each plug sits with its tip anchor (340,62) on its `jack_out_i`, body to the left. While dragging, draw the cable from the out jack to the plug's `cable_attach` (10,64). Use a Phaser Graphics stroke: 50 px `#2A1E35`, then 34 px cable color, with a sagging quadratic curve (see `verify.py`). You can also stretch `cable_seg_<color>` along the vector. Once a plug lands on its matching `jack_in_i`, draw `jack_ring` on top of the tip and swap that jack's lamp (and the matching out lamp) to `lamp_lit_<color>`.
- **Tape**: rotate `reel_full`/`reel_empty` around their centers and swap them (or crossfade) as the tape moves. Fill `progress` with an amber rect (rx 14). Show `btn_big_amber_pressed` while the button is held.
- **Text** (keypad `display`): live VT323 text in amber `#F5A54A`. The art has no text or numbers anywhere.

## Verification
`verify.py` reads `panels.json` on its own and draws every socket. I checked all three overlays at full scale and with 1:1 crops (key socket, jack, lamp): every rectangle or circle sits exactly on its recess. Coordinates come from the same constants as the art, so the match is by construction, and the overlays confirm it. The assembled previews show the parts fit their sockets at the right scale.

## Deviations
- **Switchboard lamps are to the right of every jack.** At rest a plug's body points left out of the jack, and left-side lamps would be hidden under it. The colors and order follow the brief.
- **At rest the left plugs' coiled stubs hang about 10 px past the panel's left edge.** It reads as cables entering from outside, Among Us style. Crop or mask if needed.
- No separate gauge-needle part: the keypad gauge reuses `vu_needle` at scale 0.714 (given in `panels.json`).
- Extra pieces I added: the keypad speaker grille, `btn_big_amber_pressed`, colored `lamp_lit_*` variants (the brief asked only for `lamp_lit`/`lamp_unlit`), and stitched felt on the switchboard.
- The lit lamps and the correct/wrong keys use a soft radial glow, as the brief allows. Everything else is flat two-tone.

## Known flaws and honest rating
- **7.5/10 against `14_stations.jpg`.** The materials match well: cream plastic with a shadow band, wood with grain, brass jacks, teal steel, plum outlines, triple stripe. The panels are clean and readable, and they sit with the room art.
- They are flatter and more geometric than the painted refs: no painted wear, and the wood grain is minimal.
- The toggles on the tape deck are small for the panel size.
- `key_pressed` is just a darker idle key with no glow (intended).
- The slider knob is generic. It works on the progress bar, but no socket uses it by default.
