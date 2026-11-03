# Phase 3 brief: layout guides for the ship map repaint

Read `CLAUDE.md` and `art-jobs/README.md` first. This is ONE job, **Job P** (output `art-jobs/out/P_ship_guides/`).
Branch `job/P-ship-guides` from `main`. Small commits, push the branch, no attribution trailers anywhere.

## Context (short)

The game's ship map is a 8842 x 6174 px picture plus invisible walls, rooms and stations. We are repainting the
picture in our own Nightjar style, room by room, with an image model. To keep every painting lined up with the
invisible walls, each room painting is made **against a flat layout guide drawn from the map's geometry**.
Your job is to draw those guides.

## Hard rules

1. **Input is only `art-jobs/data/ship_geometry.json`** (polygons and points in map pixels, map size 8842 x 6174).
   Do not look for, open, download or use any picture of the original map, and do not copy any art from anywhere.
   The guides are plain colored diagrams.
2. Python with Pillow and NumPy (add `shapely` only if it installs cleanly; otherwise do the geometry with masks).
   Put scripts in `art-jobs/tools/ship/` (`make_guides.py`, one entry point) and write outputs to
   `art-jobs/out/P_ship_guides/`.
3. **Flat colors, hard edges, no anti-aliasing, no gradients, no text, no labels** inside the guide images.
4. Budget: the cloud credit for this job is small (about 5 dollars). Work in this order and **commit after each
   step**: (a) SHIP, GALLEY, LOCKER guides, (b) the other 13 rooms, (c) PREVIEW.png and REPORT.md. If you reach
   about 80 percent of your budget, stop, commit what you have, and write REPORT.md with what is done and what is
   not. Do not re-read big files twice. Render once per iteration and look at that one PNG.

## The guides to draw

One guide per room (15) plus the whole ship. `ID | map area name (in the json) | aspect ratio | output size`.

| ID | Area name | Ratio | Output px |
|---|---|---|---|
| LOCKER | Lobby | 1:1 | 4096 x 4096 |
| GALLEY | Cafeteria | 1:1 | 4096 x 4096 |
| TURRET | Weapons | 1:1 | 4096 x 4096 |
| HYDRO | O2 | 1:1 | 4096 x 4096 |
| BRIDGE | Navigation | 4:5 | 3277 x 4096 |
| DEFLECTOR | Shields | 1:1 | 4096 x 4096 |
| RADIO | Communications | 5:4 | 4096 x 3277 |
| CARGO | Storage | 2:3 | 2731 x 4096 |
| DISPATCH | Admin | 5:4 | 4096 x 3277 |
| SWITCH | Electrical | 3:4 | 3072 x 4096 |
| LOWER | LowerEngine | 1:1 | 4096 x 4096 |
| UPPER | UpperEngine | 1:1 | 4096 x 4096 |
| REACTOR | Reactor | 3:4 | 3072 x 4096 |
| WATCH | Security | 4:5 | 3277 x 4096 |
| SICKBAY | MedBay | 1:1 | 4096 x 4096 |
| SHIP | whole map | 3:2 | 4096 x 2731 |

### Crop rule (rooms)
Take the room polygon's bounding box, grow it by 12 percent on every side, then grow the shorter side around the
center until the box has the target aspect ratio. If the box leaves the map, fill the outside with solid structure
(black) instead of moving the box. Scale the box to the output size (uniform scale, same on x and y).
SHIP uses the whole map, padded to 3:2 with black.

### Colors (exact RGB)
| Color | RGB | Meaning |
|---|---|---|
| Light grey | 200,200,200 | Open walkable floor of THIS room (inside its polygon) |
| Mid grey | 140,140,140 | Back-wall face of this room (see band rule) |
| Dark grey | 80,80,80 | Floor of a neighbouring room or hallway (not this room) |
| Black | 0,0,0 | Solid structure and everything outside the ship |
| Amber | 245,165,74 | Doorway: an opening of this room into a neighbour |
| Cyan | 0,255,255 | Furniture footprint (collision props: Table*, AdminTable, Chair, and the small unnamed collision shapes inside the room; NOT the big hull or wall-mass shapes) |
| Seafoam | 127,200,184 | Task station spot: filled circle of radius 28 map px at each station's centroid inside this room |

For SHIP use the same colors with every room as light grey, every doorway amber, every collision prop cyan, and
stations as seafoam dots (radius 28 map px).

### Band rule (mid grey)
For every column of the room, paint the first band of floor below the room's top edge as back-wall face, band height
= min(0.22 x room height, 260 map px), except where that top edge is a doorway. Show this band only on the room's
own polygon (never over a neighbouring room).

### Doorway rule (amber)
A doorway is a stretch of the room polygon's boundary that is NOT within 40 map px of a solid structure
(collision wall shape) and that touches a neighbouring room or hallway polygon. Draw each as a strip 60 map px
thick centered on the boundary, running through to the neighbour. The lobby door (`door` in the json) counts as a
doorway of the Lobby and the Cafeteria.

If a rule above gives a clearly wrong result for a room (for example a band across a doorway, or no doorway where
two rooms obviously join), fix it in code for that room and say what you did in REPORT.md. Do not hand-edit PNGs.

## Outputs

In `art-jobs/out/P_ship_guides/`:
- `guides/<ID>.png` (exact sizes above) and `guides/<ID>.json` with
  `{ "id", "area", "mapRect": [x, y, w, h], "outSize": [w, h], "scale", "roomPolygon": [[x, y], ...], "crewHeightPct" }`
  where `crewHeightPct` = 130 / mapRect height x 100 (a character is about 130 map px tall).
- `check/<ID>_overlay.png`: the guide at half size with the room polygon, doorways and station points outlined in a
  bright color (debug only).
- `PREVIEW.png`: a contact sheet of all 16 guides on a cream (244,230,200) background with the ID under each and a
  color legend.
- `REPORT.md`: for every guide the mapRect, scale, number of doorways, number of props and stations; the result of
  this numeric check for each guide: map the room polygon through `mapRect`/`scale` into guide pixels and confirm
  that the light-grey area's bounding box matches the polygon's bounding box within 2 px; the rooms where you
  changed a rule and why; known flaws; an honest quality rating.

## Acceptance
- Every guide has exactly the colors above (no other colors), exact output size, and the check passes.
- `PREVIEW.png` shows rooms whose shapes are clearly recognizable and whose doorways and stations are where you
  would expect. Look at it once with the Read tool before finishing.
- No image of any original map was used. Nothing outside `art-jobs/out/P_ship_guides/` and
  `art-jobs/tools/ship/` was changed.
