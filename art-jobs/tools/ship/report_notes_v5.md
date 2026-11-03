## What changed versus v4

Everything geometric is rebuilt from the collision polygons in `ship_geometry.json`; the palette, IDs, output sizes, crop rule (still taken from the room polygon bounding box, so `mapRect` is identical to v1 to v4) and JSON fields are unchanged except `"polished": 5`. `roomPolygon` in each JSON is still the coarse room polygon (rounded to 0.1 px); the true floor outline is the shapely result and is not stored in the JSON.

1. **Walls and furniture.** Wall masses are ShipRight, ShipLeft, InteriorLeft, UpperSecurityWall, MedBayWall, ReactorUpperWall and the unnamed 56-point polygon, treated as filled areas (three of them are slightly self-intersecting; `make_valid` keeps their area within 0.01 percent of the raster fill). All other collision polygons are furniture.
2. **Floor.** Floor = room polygon minus wall masses, at full precision (coordinates rounded to 0.1 px, no simplifying, no straightening, no snapping). Furniture of the room is drawn cyan inside the floor. Neighbour floor (dark grey) = every other polygon minus the wall masses; solid (black) is everything else.
3. **Stray slivers.** Floor pieces smaller than 300 px2 or thinner than 6 px (2 x area / perimeter) are dropped: one in Storage (35 x 13 px at the bottom edge) and one in Navigation. This is the only edit to the floor outline. It is the reason the CARGO bounding-box check shows 45 output px (about 24 map px) at the bottom edge: the check compares against the raw polygon minus walls.
4. **Doorways.** For every pair of floors, the part of one floor boundary that is not next to a wall mass (within 6 px) and lies within 16 px of the other floor is a contact line (16 px because some room and hall polygons are up to 13 px apart; the previous 6 px missed O2 and Reactor). Contact lines of one pair within 120 px of each other are merged. Each result is one rotated rectangle, 60 px thick, oriented along the lines (snapped to horizontal or vertical within 3 degrees), length = extent of the contact lines. The Lobby door stays the plain rectangle from v2 to v4. Doorway counts changed because they now follow the real openings (see table).
5. **Band.** The v4 mitred band method with the 180 px and 300 px rules, run on the new floor edges: the floor outline is smoothed with a 12 px tolerance for the band only, the band is extruded inward by min(0.22 x floor height, 260) map px, clipped to this room's floor, and kept off doorways, furniture and station dots. The closing radius is 12 px.
6. **Stations.** All 20 station centroids already lie on floor, so none were moved and none were left out (the table lists each station).

## Known flaws

- The new floors are jagged, so the band is noisier than in v4: several separate blocks in SICKBAY, WATCH and SWITCH, and in LOWER and UPPER the narrow arms are almost all band because the band is as thick as the arm (min(0.22 x height, 260) px).
- BRIDGE has a tilted wedge of band across the floor between the two chairs, from the smoothed slanted upper-right edge; it follows the geometry but looks odd.
- Some dark grey neighbour fragments are tiny and odd-shaped (GALLEY corners, BRIDGE lower right), because neighbour floors are also cut by the wall masses.
- A doorway can be short where the contact is short (HYDRO), and the rectangle follows a tilted contact line (DEFLECTOR top, CARGO top), so it is not always horizontal or vertical.
- The 12 px band smoothing is for the band only, so a band edge can sit up to 12 px away from the true floor edge; the closing step covers most of the resulting hairline gaps.
- `shapely` is now required (`pip install shapely`, tested with 2.2).
- Not yet tried with the image model.

## Rating versus v4

8 out of 10 as layout guides, against 6.5 for v4 once its shape error is counted. v4 was tidy but wrong: up to 50 percent of a room's area lay inside wall masses (O2 49.7, LowerEngine 38.9, Weapons 37.8, UpperEngine 36.9, Shields 34.4, Reactor 28.6, Communications 28.5, Navigation 26.0 percent). v5 follows the true contours (engine bays, T-shaped Weapons, ragged Communications), passes the size, palette (0 off-palette pixels) and bounding-box checks, and keeps the crops. It loses points for the heavier, jagged bands and for the odd BRIDGE wedge.
