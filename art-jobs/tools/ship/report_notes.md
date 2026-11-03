## How the rules were interpreted

- **Crop:** the room bounding box grows by 12 percent of its own width on the left and right and 12 percent of its own height on top and bottom, then the shorter side grows about the center to the target aspect. Outside the map stays black. `scale` is the same on x and y; `crewHeightPct` = 130 / mapRect height x 100.
- **Hull and wall collision shapes are treated as outlines, not filled areas.** `ShipRight`, `ShipLeft`, the big unnamed shape, `InteriorLeft` and the three `*Wall` shapes overlap room polygons heavily (for example 50 percent of O2), so they cannot be solid fills. They are used only as wall lines for the "within 40 px of a wall" test. A closing segment is added only when the last point is within 120 px of the first.
- **Props** = `Table*`, `AdminTable`, `Chair`, and unnamed shapes that lie at least 80 percent inside one room and are under 800 px across (two shapes: one in Weapons, one in Storage). A prop belongs to the room that contains its centroid. The Storage one is the big cyan blob in CARGO; it is 705 x 620 px, so it may really be a wall mass. Check it against the painting.
- **Doorways:** the boundary of each of the 22 polygons is sampled every 4 px. A sample is open if it is at least 40 px from every wall line and within 30 px of another room or hall polygon. Open stretches of at least 40 px become one doorway each, drawn as a 60 px strip centered on the boundary. The lobby `door` polygon counts as one doorway of the Lobby and the Cafeteria; a small bridge rectangle from the Lobby bottom edge to the door polygon is added because the door sits about 90 px below the Lobby polygon.
- **Back-wall band:** per column, the first `min(0.22 x room height, 260)` map px below the topmost polygon pixel, on the room's own polygon only; columns whose top pixel is amber are skipped.
- **Stations** are placed by polygon centroid and drawn only in the room whose polygon contains it. A station whose centroid is only in a hallway does not appear in any room guide (it does appear on SHIP).
- **bbox check:** the light-grey area alone can never match the polygon bounding box, because the mid-grey band always covers the top rows and doorway strips cover edge rows. The check therefore uses the room footprint rebuilt from the PNG: light + mid + cyan + seafoam + amber pixels that fall inside the polygon. It is compared with the polygon rasterised from `roomPolygon`, `mapRect` and `scale` in the json. The table shows the largest difference per side in px (limit 2).

## Rooms where a rule was changed

Only the Lobby door bridge above. No rule gave a clearly wrong result that I fixed per room, and nothing was hand-edited.

## Known flaws

- Hallway polygons overlap several rooms by 50 to 100 px. Where that happens the doorway comes out as a strip with a small second or tilted piece (visible in DEFLECTOR left side, DISPATCH left side, SWITCH bottom, SICKBAY top, SICKBAY and WATCH corners) and the back-wall band is notched at the doorway. The positions are right; the strips are not tidy.
- Neighbouring hallway floor shows as dark grey only where the hall polygon is inside the crop; some hall stubs end abruptly at the crop edge.
- The furniture shapes come straight from the data: the cafeteria tables have notched "bat wing" outlines.
- Doorway detection takes about 90 seconds per run (all 22 polygons are tested each time).
- Not yet tried with the image model: whether it keeps to these guides.

## Quality rating

7 out of 10 as layout guides. Shapes, doorways, props and stations are in the right places and recognisable in `PREVIEW.png`, all 16 files have exactly the seven colors and exact sizes, and the numeric check passes for every room. Points off for the untidy doubled doorway strips and the unverified Storage prop.
