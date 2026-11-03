## What changed versus v1

1. **Doorways.** Each opening is one rotated rectangle, 60 map px thick. The search is the v1 rule (open boundary samples at least 40 px from a wall and within 30 px of a neighbour), done per neighbour. Fragments that touch the same neighbour and lie within 120 px of each other are merged (fragments of different neighbours only when they overlap). The direction comes from the merged samples, snapped to exactly horizontal or vertical within 3 degrees. Each end is then moved outward to the wall, up to 50 px, so the length is the wall-to-wall gap. The centre line is moved onto the cleaned boundary edge that carries it. The Lobby door is now one plain rectangle (door width, from the Lobby bottom edge to the bottom of the door polygon), used in LOCKER, GALLEY and SHIP. On SHIP, rectangles found from both sides of the same opening are merged (centres within 70 px, similar direction), so the count falls from 45 to 22 + the lobby door.
2. **Back-wall band.** Edge based: every edge of the cleaned room polygon whose outward normal has y < -0.3 and that is not inside a doorway rectangle is extruded inward along its own normal by min(0.22 x room height, 260 map px), clipped to the polygon, and the pieces are unioned. Side and bottom edges get none.
3. **Straight edges.** Every one of the 22 polygons is simplified (Douglas-Peucker, 25 px) and every edge within 3 degrees of horizontal or vertical is snapped to exactly horizontal or vertical (vertex coordinates averaged per snapped chain). If the area change reached 2 percent the tolerance was lowered until it was under 2 percent (the `tol` used is in `check/clean.json`). The crop (`mapRect`), props and station assignment still come from the original polygons, so crops are identical to v1 (checked in the table). `roomPolygon` in the JSON is the cleaned polygon that is drawn.
4. **Cache.** Doorway search results are stored in `check/doorway_cache.json` (keyed by a hash of the geometry file and the parameters). A re-run with a warm cache takes about 15 seconds for the setup plus a few seconds per guide; a cold run is about 30 seconds more.

The bounding-box check is the same as v1: footprint (light + mid + cyan + seafoam + amber pixels inside the polygon) against the polygon drawn from the JSON, limit 2 px.

## Known flaws

- The band extrusion follows the spec literally, so the end of a band on a short slanted edge is square: a small uncovered wedge (a "V") appears where a slanted edge meets a vertical side edge (DEFLECTOR upper left, HYDRO left, SICKBAY upper left).
- Band stubs beside doorways: where a hall neck enters from the top, the short edge pieces beside the doorway rectangle are outside it and get their own band, so a mid-grey block sits just under or beside the amber rectangle (SICKBAY, RADIO, LOWER, DEFLECTOR). LOCKER has a tiny notch in the band at the top right for the same reason (a very short upper edge).
- At a convex roof peak the two extruded bands meet in an inverted-V notch on their lower edge (WATCH, REACTOR upper left); a literal union of the extrusions does that.
- Doorway rectangles sit on the cleaned boundary but are not clipped to the room shape, so on slanted walls the rectangle's end can poke a few px past the wall line.
- Cleaning moves boundaries by up to the "max boundary dev" column (25 px tolerance), so room edges can be that far from the original polygon; doorways still straddle the boundary because they are 60 px thick.
- The Storage furniture blob and the hall stubs at crop edges from v1 are unchanged.
- Not yet tried with the image model.

## Rating versus v1

v2 is better than v1: 7.5 out of 10 overall (v1 was 7). Doorways are 9 out of 10: one clean rectangle each, the doubled strips are gone, and all 16 guides pass the size, palette (0 off-palette pixels) and bounding-box checks. Room edges are straight (largest vertex shift 13.9 px, area change at most 0.34 percent). The band follows slanted walls but is only about 6.5 out of 10: square ends, wedges, small stubs beside doorways and the peak notches listed above, all caused by the specified extrusion rule. Closing the wedges with a mitre fill and trimming stubs beside doorways would be the next fix.
