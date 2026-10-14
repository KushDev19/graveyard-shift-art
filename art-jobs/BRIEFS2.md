# Phase 2 briefs: convert ALL usable art to layered SVG

Phase 1 (jobs A-F: icons, UI kit, task panels, minimap, button, doors, emblem, pixel arcade) is done and merged in `art-jobs/out/`. Phase 2 converts the Gemini paintings into **layered, game-usable SVG**. Read `CLAUDE.md`, `art-jobs/README.md`, the shared rules below, then ONLY your job section.

## Shared trace rules (every phase-2 job)

1. **Source of truth = the original** in `raw_originals/` (5504 px wide, keep coordinates in that space). Use `art-jobs/refs/` (2000 px) only for quick looks.
2. **Faithful, not reinvented.** Each SVG must match its source painting: same shapes, proportions, colors (sample them with Pillow from the original), outline weight, shading zones, highlights. Soft painted glows/gradients may become SVG gradients or a blur filter.
3. **Verify numerically AND visually, every object:**
   - render the SVG at source size, composite on the source background, and save `check/<name>_side_by_side.png` (original | SVG) and `check/<name>_onion.png` (SVG at 50% over the original);
   - compute mean absolute error over the object's region on a 4x downscale; **target <= 12/255**, outlines aligned within ~6 px at full res. Put the number in REPORT.md. Iterate on the worst objects first.
4. **Layered and named.** One `<g id>` per logical object; objects that move or change state are separate files with a `data-pivot` where they rotate. Untouched areas behind removed objects must be repainted in the shell (no holes).
5. **Camera angle.** Rooms use a front-facing top-down 3/4 diorama camera. Props that Gemini drew in a diagonal/isometric angle (sheets 14, 15, 38) get **two versions**: `*_orig` (faithful to the sheet) and `*_front` (redrawn front-facing like the room furniture, e.g. the fridge in the Galley, same height, same materials). Study the room furniture to infer the front view; keep every detail consistent with the original.
6. **Exports:** each SVG + PNG at half source scale (RGBA), `PREVIEW.png` (labeled, cream background), `REPORT.md` (files, MAE per object, deviations, honest rating). Keep SVGs lean (merge identical shapes, no embedded rasters; < 1.5 MB each).
7. Branch `job/<letter>-<name>` from `main`, output in `art-jobs/out/<LETTER>_<name>/`, small commits, push the branch. **No Claude attribution anywhere** (no Co-Authored-By, no "Generated with").

### Room manifest schema (`<room>.json`, source-pixel coordinates)
```json
{
  "room": "galley", "source": "raw_originals/01_ROOM_GALLEY.png", "size": [5504, 3072],
  "shell": "galley_shell.svg",
  "objects": [{"id": "fridge", "file": "objects/galley_fridge.svg", "x": 0, "y": 0, "w": 0, "h": 0,
               "sortY": 0, "collision": [[0, 0], [0, 0], [0, 0]]}],
  "walkable": [[0, 0], [0, 0], [0, 0]],
  "doors": [{"id": "left", "side": "left", "x": 0, "y": 0, "w": 0, "h": 0}],
  "anchors": {"station_alcove": [0, 0], "emergency_pedestal": [0, 0], "seats": [[0, 0]]},
  "lights": [{"x": 0, "y": 0, "radius": 0, "color": "#F5A54A"}]
}
```
`shell` = floor, walls, wall decor, frame (everything the player always walks in front of). `objects` = furniture/props that need depth sorting (`sortY` = the y of the object's floor contact line) or that block movement (`collision` polygon on the floor). `walkable` = floor polygon. `anchors` = where interactive props go (alcoves, the Galley pedestal, meeting seats, vent spots you choose sensibly). `lights` = lamp pools so code can add flicker. Also render `check/<room>_manifest_debug.png`: the room with walkable (green), collisions (red), sortY lines (blue), anchors (yellow) drawn on top.

---

## Room jobs (each: shell + objects + lights layer + manifest + debug overlay)

### Job G: Galley + Locker Room  (out `G_rooms_galley_locker`)
Sources: `01_ROOM_GALLEY.png`, `05_ROOM_LOCKER.png`. Highest priority (demo). Galley objects: vending machine, fridge, coffee counter (+ machine, mugs), two plants, cork board, diner table, every stool (separately, for sorting), pendant lamps (light layer). Anchors: table pedestal (emergency button), 10 meeting seats, doors. Locker objects: lockers (row; the open ones separately), bulkhead door (`door_open`/`door_closed` parts so it can slide), beacon (separate, for spin/glow), wall clock with **separate hour/minute hands** (`data-pivot` at center), benches, rug, coffee counter, water cooler, coat racks, plant, cork board. Anchor: time-clock alcove.

### Job H: Reactor + Switchboard  (out `H_rooms_reactor_switch`)
Sources: `06_ROOM_REACTOR.png`, `07_ROOM_SWITCHBOARD.png`. Reactor: core as separate layered object (cage, glowing core, glow layer for pulsing), pipes, gauges, tool rack, extinguisher, floor grates, valves; **remove the painted steam puffs** from the shell and deliver one `steam_puff.svg` sprite for code particles. Anchor: keypad alcove. Switchboard: the big switchboard (lamps as a separate layer so they can blink), fuse boxes, knife switches, cable trays, cable spools, desk with phone, mug and banker's lamp (lamp glow separate). Anchor: patch-station alcove.

### Job I: Radio Room + Bridge  (out `I_rooms_radio_bridge`)
Sources: `08_ROOM_RADIO.png`, `09_ROOM_BRIDGE.png`. Radio: window (nebula + dish as a separate layer behind the frame), tape deck, cassette shelves, VU meters (needles separate), string lights (separate light layer), armchair, side table, lava lamp (blob layer separate for animation), records, rug. Anchor: tape-station alcove. Bridge: panoramic window (nebula and planet as a separate background layer so it can drift slowly), console bank (screens separate to glow), captain's chair (separate, with a swivel pivot), star-chart table (chart layer separate to slowly rotate), thermos, plant. Anchors: the two station alcoves.

### Job J: Sick Bay + Hydroponics + Cargo  (out `J_rooms_tier2`)
Sources: `35_ROOM_SICKBAY.png`, `36_ROOM_HYDROPONICS.png`, `37_ROOM_CARGO.png`. Same treatment: shell + every furniture object separately (cots, curtains, cabinets, heart monitor line separate; planters, hanging plants, hammock, gnome, mist layer; crate stacks, forklift, barrels, net, fuel tank, loading door), lights, manifests (Sick Bay anchor: scanner pad; Hydroponics anchor: tape-station alcove).

---

## Prop jobs

### Job K: Task stations + ship props  (out `K_props_stations`)
Sources: `14_PROPS_STATIONS.png` (4 stations x idle/highlight/done) and `15_PROPS_SHIP.png` (vents closed/open, time clock idle/ready, table clutter; skip its doors and emergency button, they are done in `art-jobs/out/E_button_doors/`). For every station deliver ONE layered SVG with shared body + state layers (`state_idle`, `state_highlight`, `state_done`: screen, lamps, beacon) so code toggles layers; both `*_orig` (as drawn) and `*_front` (front-facing, matching room furniture). Vent: frame + separate hinged lid with pivot. Time clock: body + screen layer + card slot glow layer.

### Job L: Extra props  (out `L_props_extra`)
Source: `38_PROPS_EXTRA.png`. Med scanner pod (base + arch + separate scan-ring layer for animation), security desk (screens as a separate layer), and the 8 decor pieces (plant, floor lamp with separate glow, crate stack, water cooler, locker, toolbox, mop and bucket, cactus). `*_orig` + `*_front` for each.

---

## Character cosmetics jobs (must fit the existing SVG puppet)

Puppet: `frontend/public/assets/ship/crew/crew_puppet.svg` and `crew_rig.json` (viewBox 640x800; side view faces right; front-view groups are prefixed `f_`). Look at `art-jobs/refs/crew_rig.png` and the puppet demo. Each cosmetic: an SVG in **side** and **front** variants drawn at puppet scale (helmet dome: center 320,300, rx 207, ry 196), plus `cosmetics.json` with `{id, slot, side:{file, x, y, pivot}, front:{file, x, y}, hidesAntenna, layers:{back, front}}`. Wraparound items (headphones, flower crown, afro) need **back** (behind the dome) and **front** layers. Neutral grey parts that must take the player color use `var(--suit, #CDCCD4)`. Deliver `wardrobe_preview.png`: the puppet (side + front, 3 crew colors) wearing every item, so fit can be judged.

### Job M: Hats  (out `M_cos_hats`)
Sources: `43A_COS_HATS_A.png` (hats drawn alone, side+front pairs) and `43B_COS_HATS_B.png` (Gemini drew these ON helmets: extract only the hat). 12 hats: trucker cap, diner hat, hard hat, beanie, cowboy hat, chef toque, nightcap, party hat, headphones, flower crown, afro, propeller beanie. Hats hide the antenna (`hidesAntenna: true`) except headphones and flower crown.

### Job N: Toppers, backpacks, visors, decals  (out `N_cos_rest`)
Sources: `44N_COS_TOPPERS_PACKS.png` (8 antenna toppers replace the antenna ball; 8 backpacks replace the backpack; side view only, front view: backpack hidden, topper same shape) and `45N_COS_VISORS_DECALS.png` (Gemini drew these on characters: extract only the visor or decal). Visors (aviator, heart, star, LED smile) replace `visor`/`f_visor` with matching footprints; decals (name tag, bolt, smiley, flames) replace `stripe`/`f_stripe`.

---

## Brand and screen job

### Job O: Logo, HD arcade, screens pack  (out `O_brand_screens`)
- `23_LOGO.png` -> faithful layered SVG (letters with outline and extrusion, helmet "dot" as a separate group, moon, racing stripe), spelling exactly GRAVEYARD SHIFT; plus a one-color cream version.
- `26_ARCADE_HD.png` -> layered SVG (screen content separate so it can animate; marquee separate, blank).
- Screens 27-34 stay **static images** (they are backgrounds). Process them: crop `27_SCREEN_TITLE` (1:1) to a 16:9 version keeping the ship and planet; export every screen as WebP at 1920 and 3840 width (quality 85) into `screens/`; for 30 and 31 also deliver the burst rays as a separate SVG layer so code can spin them; for 28, 29, 33, 34 deliver the podium top ellipse and the "stage line" (where characters stand) in `screens.json`.
- Key out the green background on the five pose sheets `04A`-`04E` cleanly (no green fringe) into transparent PNG cutouts, one per pose, named by pose.
