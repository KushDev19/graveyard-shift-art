# Job briefs (A to F)

Shared rules are in [README.md](README.md). Each job: one output folder, PNG + SVG, `PREVIEW.png`, `REPORT.md`, own branch.

---

## Job A: HUD action buttons and badges  (out: `A_icons`)

**Display sizes:** action buttons 96 px, badges 64 px. Export PNG at 2x (192 and 128 px) plus a 256 px version of each button. Everything must read instantly at those sizes: bold, simple, high contrast, thick outlines.

### A1. Eight big circular action buttons
Common base: chunky circular badge with a **thick cream beveled ring** (**coral ring** for dangerous actions) around a **dark midnight-indigo inner disc**, with a bold, simple, full-color illustrated icon inside. Same overall size and outline weight for all.

| id | Icon | Ring |
|---|---|---|
| `btn_use` | grey mitten hand pressing a chunky amber button | cream |
| `btn_report` | cream megaphone with amber sound waves | cream |
| `btn_eliminate` | playful: a big cartoon safety pin next to a small deflating balloon with a "pop" burst (funny, not violent) | coral |
| `btn_vent` | teal floor grate with an amber upward arrow and a small puff | coral |
| `btn_sabotage` | wrench with small sparks | coral |
| `btn_emergency` | big coral button under a glass dome | cream |
| `btn_map` | folded seafoam blueprint map | cream |
| `btn_chat` | cream speech bubble with three amber dots | cream |

For each button provide **normal** and **disabled** (desaturated, dim) versions, and one shared `cooldown_ring.svg` (a track ring and a separate arc layer meant to be drawn by code; document how the arc is parameterized, e.g. stroke-dasharray).

### A2. Twelve small badges / icons (64 px)
`badge_host_crown` (chunky amber crown, three cream gems), `badge_voted_stamp` (round coral rubber-stamp mark with a bold check, slightly tilted), `badge_skip` (round cream badge, curved amber arrow hopping a line), `badge_ghost` (seafoam ghost built from the fishbowl helmet with a wispy tail), `badge_caller` (small cream megaphone with amber ring), `badge_eliminated` (small helmet icon with an X of plum tape across its visor), `badge_settings` (chunky cream gear), `badge_leave` (teal door with amber arrow out), `badge_mic_on`, `badge_mic_muted` (same mic with a coral slash), `badge_task_done` (seafoam circle with bold cream check), `badge_warning` (amber rounded triangle, plum exclamation mark).

### A3. Meeting extras
`btn_confirm` (round seafoam with bold check) and `btn_cancel` (round coral with bold X) as small round buttons (48 px), `dot_unread` (coral dot), `badge_disconnected`, and `icon_helmet_front` (the crew's front-view helmet head as a small icon; **recolorable**: the suit/collar uses `var(--suit, #CDCCD4)`; this is used as the "voter chip" in vote results, so also export a 32 px version).

**Acceptance:** all icons consistent as one family; ring/disc construction identical across buttons; legible at display size; no text inside any icon.

---

## Job B: UI frames and the Meeting Tablet kit  (out: `B_ui_frames`)

Design target: CRT-terminal panels: dark indigo screens, cream plastic bezels with chunky screws and the racing stripe, rounded corners, a faint screen glow (inside the screen only). Panels are **nine-slice friendly**: uniform border thickness, symmetric rounded corners, a flat uniform center (no pattern in the stretchable middle). Also provide a `nineslice.json` with the slice insets (px) for every frame.

### B1. Frames and controls (SVG + PNG, each at 1x and 2x)
Large CRT panel, small CRT panel, toast banner (pill, cream), speech bubble (cream, tail bottom-left), **pill button** in 4 states (idle amber with darker bottom bevel, pressed, disabled plum-grey, danger coral), **progress bar** trough (dark indigo, cream bezel) and fill (seafoam/amber diagonal candy stripes, sized to fit), timer dial (ring + center; the arc layer separate), chat button + unread dot, chat drawer frame.

### B2. The Meeting Tablet
A chunky CRT tablet frame, 1280x720 safe area, that slides up from the bottom over a dimmed game scene. Zones: header "WHO'S THE IMPOSTOR?" (Bungee) with a caller line "Mint reported Tomato"; **player grid 2 columns x 5 rows of vote plates**; bottom-left SKIP button; bottom-right timer ("DISCUSS 0:15" then "VOTING 2:00"); top-right chat button.
**Vote plate states** (each its own SVG, same size, nine-slice or fixed): `plate_alive`, `plate_you` (amber outline), `plate_selected` (glowing amber bezel; room for the confirm/cancel buttons), `plate_voted` (leaves space for a "VOTED" stamp that Job A provides), `plate_caller` (room for a megaphone badge), `plate_eliminated` (dimmed), `plate_disconnected` (greyed). Each plate: circular portrait well on the left (portrait is added by code), name line, status area. Must stay readable at 1280x720.

### B3. Mock
Compose `meeting_mock.png` (1280x720): dim teal-indigo background, the tablet, 10 plates with fake names and simple colored helmet portraits (circles with a dark dome and amber visor is enough), different plate states, SKIP, timer. Use the real fonts if you can fetch them from Google Fonts or a font package; else a close system font, and say so in the report.

**Acceptance:** looks like one coherent retro-CRT family; frames stretch cleanly; the mock is attractive and clearly readable.

---

## Job C: Task panels (Tier 1) and their moving parts  (out: `C_task_panels`)

Three full-screen mini-game panels, **perfectly straight-on front view**, flat, each 2048x1536 (4:3), the panel face IS the image. Moving parts are separate SVG/PNG files placed by code, so the panels must have **EMPTY sockets at exact coordinates**, which you must write to `panels.json` (pixel centers and sizes in the 2048x1536 space).

1. **`panel_keypad` "Reactor Override"**: thick rounded cream plastic bezel with chunky corner screws and the racing stripe along the top. Top area: left, a horizontal semicircular pressure gauge with a coral danger zone and blank tick marks (no numbers, no needle: needle is a separate part), right, a small dark rectangular amber LED display window, empty and unlit. Lower 65%: a recessed dark plum well with a grid of **2 rows x 5 columns** of empty square key sockets (shallow rounded recesses, evenly spaced). Coral warning stripes along the bottom edge, a tiny amber indicator lamp.
2. **`panel_switchboard` "Patch the Switchboard"**: vintage telephone-operator switchboard: warm wooden frame with brass corner caps, racing stripe on top. **Left column: 4 empty brass output jacks** stacked and evenly spaced, each with a small unlit colored indicator lamp beside it (tomato red `#E4483C`, mustard `#E9C046`, cobalt `#3F5FD9`, mint `#6FD6B0`, top to bottom). **Right column: 4 empty brass input jacks**, each with an unlit lamp, in the shuffled color order mint, tomato, cobalt, mustard (top to bottom). Center: wide empty dark plum felt area (cables drawn by code). Brass screws, a tiny amber power lamp.
3. **`panel_tape` "Tape Transfer"**: chunky 1970s reel-to-reel deck face: brushed teal metal faceplate, cream plastic trim, racing stripe. Upper half: two **empty reel spindle hubs** left and right, each on a large circular recess; between them a small tape-head assembly. Lower half: left, a rounded VU-meter window with cream dial face and an amber-to-coral arc of blank tick marks (needle separate); middle, a long horizontal empty dark progress window; right, an **empty round recessed socket for a big button**. Chunky toggle switches and a tiny amber power lamp.

### Moving parts (`task_parts`, individual SVG+PNG, tight crop, transparent)
Keypad keys: `key_idle` (chunky cream rounded-square, bevel), `key_pressed`, `key_correct` (seafoam glow, glow inside outline), `key_wrong` (coral); **patch cable plugs** (chunky brass-tipped plug with a short stub of thick coiled cable, pointing right) in the 4 colors; `reel_full` (cream reel, three holes, dark tape) and `reel_empty`; `vu_needle` (thin plum needle, round pivot cap at the bottom, pointing straight up, `data-pivot`); `btn_big_amber` (big chunky round push button); `slider_knob`; `lamp_lit` and `lamp_unlit`; `jack_ring`. Also a cable segment piece or a note on how to stretch a cable between plug and jack.

**No text, letters or numbers anywhere** on panels or parts (the game overlays live text). Write `panels.json` carefully and **verify it by rendering a debug image with the socket rectangles drawn on top of each panel**: every rectangle must sit exactly on its socket.

**Acceptance:** panels look like they belong to the same ship as the refs (compare with `14_stations.jpg` for materials); sockets sit exactly where `panels.json` says; parts fit their sockets at the right scale.

---

## Job D: Tier 2 task panels and the minimap  (out: `D_panels2_minimap`)

### D1. Three more panels, 2048x1536, same construction rules as Job C panels (cream bezel with screws and racing stripe, front view, empty sockets listed in `panels2.json` with a verified debug overlay):
- `panel_thrusters` "Align Thrusters": left two-thirds a dark indigo CRT screen showing a simple seafoam line diagram of a rocket thruster nozzle in side view with a horizontal dashed amber target line across the middle; right third a tall vertical recessed slider track (empty slot, knob is a separate part) with blank tick marks.
- `panel_gyro` "Calibrate Gyro": a large round dark dial face with three concentric empty circular grooves, each groove with one small seafoam target notch at a different angle; below the dial an empty round recessed socket for a big push button flanked by two tiny amber indicator lamps.
- `panel_memory` "Pattern Memory": left half a dark CRT area with a 3x3 grid of empty round lamp sockets; right half a teal metal plate with a matching 3x3 grid of empty square button sockets; a row of five small unlit progress lamps along the bottom.
Plus any moving parts these need (slider knob, round lamp lit/unlit, square button idle/pressed). No text.

### D2. Minimap blueprint (`minimap.svg`, 1600x900)
Flat plan view (from directly above, not angled): midnight-indigo background, seafoam and cream line work, amber accents. Rooms are rounded rectangles with thick seafoam outlines and a subtle lighter fill; corridors are thinner double lines; the ship's rounded outer hull outlined in cream. Layout on a 3-row grid:
- TOP: HYDROPONICS (small, top-left), GALLEY (largest, top-center), BRIDGE (top-right, rounded nose front).
- MIDDLE: REACTOR (far left), SICK BAY (left-center, under Hydroponics), RADIO ROOM (center, under the Galley), CARGO HOLD (large, right, under the Bridge).
- BOTTOM: SWITCHBOARD (bottom-left, under the Reactor) and a LOCKER ROOM (bottom-center) that is separate and **not connected** to anything.
- Corridors: Hydroponics-Galley, Galley-Bridge, Hydroponics-Sick Bay, Sick Bay-Reactor, Galley-Radio Room, Radio Room-Cargo Hold, Bridge-Cargo Hold, Reactor-Switchboard, Switchboard-Radio Room (long corridor along the bottom).
- Each room has one simple amber icon in its center: Galley a button, Bridge a steering wheel, Reactor an atom, Switchboard a lightning bolt, Radio Room a satellite dish, Cargo Hold a crate, Sick Bay a heart, Hydroponics a leaf, Locker Room a clock.
Every room is its own `<g id="room_<name>">` (so code can highlight rooms and place player dots) and you also export `minimap_rooms.json` with each room's center and bounding box. No text labels in the art. Also export a small 320x180 version.

**Acceptance:** the panels share one construction language with Job C (follow the same spec text); the minimap is clean, balanced and readable at 320x180.

---

## Job E: Emergency button and doors  (out: `E_button_doors`)

The emergency button is the hero prop of the meeting story: it must **animate**. Style target: `15_props_ship.jpg` (row 1) for shapes, `01_galley.jpg` for orientation: draw it **front-facing three-quarter view like the Galley's furniture** (front face toward the viewer, top surface slightly visible), sitting on the round pedestal in the middle of the Galley table (measure the pedestal in `01_galley.jpg`; scale the prop to fit it, about 1.3x the pedestal's width).

### E1. Emergency button (`emergency_button.svg` with named parts, plus per-state PNGs and a rig file)
Parts (each a `<g>` with a `data-pivot` where it moves): `base` (round chrome-and-cream base with a coral stripe), `button` (glossy coral button), `dome` (glass dome in pale seafoam with white highlights; **hinged at the back**, pivot at the hinge), `padlock` (small chunky padlock), `glow_ring` (amber ring that lights when pressed or active).
States: **idle** (dome closed, coral button), **open** (dome flipped open about 110 degrees on its hinge, button visible and lit), **pressed** (dome open, button pushed down about 14 px, brighter glow), **disabled** (dome closed, button dull dark plum, padlock on the base).
Deliver `emergency_button_rig.json` (part offsets, pivots, draw order, tween suggestions) and **`emergency_demo.html`**: a self-contained page (inline SVG + vanilla JS) with buttons that play: dome lifts open (ease-out, small overshoot), button presses with a squash, a coral flash ring expands, then it locks into the disabled state with the padlock dropping on. Open it in a headless browser (playwright) and screenshot several frames to verify.

### E2. Doors (front-facing, same camera as the Galley)
Study the door slabs on the left/right walls of `01_galley.jpg` and the bulkhead double door in `05_room_locker.jpg`. Draw: `door_front_closed` and `door_front_open` (rounded sliding bulkhead door, teal steel, yellow-plum hazard stripes at the bottom, small amber lamp; open = door halves slid into the frame leaving the empty frame), and `door_side_closed` / `door_side_open` (the same design seen as a thick vertical slab in a side wall, as the Galley's side wall doors). Provide the door as **two separate sliding halves plus frame** (named groups with slide distance in the rig file) so code can animate it opening. Keep consistent scale with the rooms (a doorway is about twice a crew member's width; a crew member is about 650 px tall in the 5504 px wide room paintings).

**Acceptance:** the button looks like a more polished sibling of the Gemini one in `15_props_ship.jpg` but cleaner, and the demo animation feels good; doors match the room door slabs.

---

## Job F: Logo, emblem and the pixel arcade cabinet  (out: `F_brand_arcade`)

### F1. Logo: SKIP (already generated and approved from the image tool). Do only F2 and F3.

### F2. Emblem `emblem.svg`
Round badge (app icon / loading spinner): circular badge with a thick cream rim bearing the triple racing stripe as a ring; inside a midnight-indigo night sky with a few stars and a big cream crescent moon on the right; in front, the crew's fishbowl helmet (see `00_crew_model.jpg`: dark indigo dome, glowing amber visor, antenna) peeking up from the bottom of the circle. Bold and simple, still readable at 32 px. Export 512, 128, 32.

### F3. Pixel arcade cabinet (hand-placed pixels, NOT a smoothed image)
The cabinet stands in the pixel-art town, so it must match the town's Tuxemon/Pokemon-GBA pixel style: look at `frontend/public/assets/tilesets/tuxmon-sample-32px-extruded.png` in this repo (same pixel density, dark outline, slightly-from-above front perspective, limited palette).
- Sprite size exactly **32 x 64 px** (one tile wide, two tall), written with a Python script that places pixels from an ASCII map and a palette of **at most 16 colors** (pick the dark outline and tones to sit naturally next to the tileset's colors).
- Design: dark plum cabinet body with a cream-amber-coral stripe running down its side, a small glowing coral marquee (no letters) on top, a glowing amber screen showing a tiny pixel spaceship and stars, a control deck with a tiny joystick and two round buttons (amber, coral), a small coin slot at the bottom. It should read as "fun thing to walk up to".
- Deliver: `arcade_32x64.png` (1x), `arcade_32x64_x8.png` (nearest-neighbor 8x for inspection), an **idle/active 2-frame sheet** (`arcade_sheet_64x64.png`: frame 1 screen dim, frame 2 screen bright and marquee glowing), the generator script `make_arcade.py`, and a **composite test** (`arcade_in_town.png`) placing the sprite at 2x scale on a crop of the tileset image so the match can be judged.

**Acceptance:** wordmark spelling is perfect and looks like retro arcade signage; emblem is bold; the pixel cabinet is clean (no stray anti-aliased pixels) and plausibly belongs in the Tuxemon town.
