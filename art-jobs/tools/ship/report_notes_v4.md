## What changed versus v3 (bands only)

Doorways, room polygons, crops, props, stations and the mitred band construction are the v3 code unchanged. Two additions:

1. **Doorway frame blocks.** A band piece shorter than 300 map px that touches a doorway (within 20 px) is dropped. It is the doorway's own frame wall, which read as a loose block beside the door. This fires for exactly one piece each in WATCH (the block with the station dot beside the left door) and REACTOR (the neck top wall beside the right door); the "dropped near doorway" column shows where. The values I measured before choosing the rule: those two pieces are 259 and 273 px long and touch the door, while every other piece is either at least 300 px long (RADIO 510, DEFLECTOR 375 and 285, HYDRO 412, LOWER 377 and 310) or at least 44 px from the doorway (SICKBAY side pieces 222 and 277 px at 64 and 44 px). The earlier 180 px rule is unchanged, and no hard 120 px empty margin was added.
2. **Sliver closing.** The band mask is closed with an 8 map px square (outside the room polygon counts as filled, so slivers between a band and a wall close too), then clipped to the room polygon and the doorway, furniture and station masks are subtracted as before. This straightens small kinks and removes hairline light gaps at tilted wall ends. The "band px outside room polygon" column stays 0.

## Known flaws

- Short band pieces that are not touching a doorway stay: REACTOR keeps a small block on the step wall above the neck (286 px, 344 px from the door), and SICKBAY keeps its two side pieces beside the neck (222 and 277 px, 64 and 44 px from the door). They read as normal back wall, but if you want them gone, raise `DOOR_PIECE` or `TOUCH_DOOR` in `make_guides_v4.py`.
- LOWER's top-right band piece (a short tilted wall, 310 px) has a slanted, slightly kinked lower end; it follows the polygon but looks less tidy than the other bands.
- Where a band end is cut along a tilted neck wall (RADIO left piece, DEFLECTOR) the end is slanted, as the wall is; this is the wall's real shape, not a gap.
- Under a top doorway the floor shows as a light strip through the band (GALLEY, DEFLECTOR, SICKBAY) by design (the band never covers a doorway).
- The closing is a square window, so it rounds nothing; it only fills gaps under 16 map px wide.
- Not yet tried with the image model.

## Rating versus v3

8.5 out of 10 overall (v3 was 8). The two blocks next to doorways that I flagged in v3 are gone and the thin light slivers are closed; nothing else moved. The remaining points: the slanted band ends at tilted walls, the small step-wall block in REACTOR, and the untested step with the image model.
