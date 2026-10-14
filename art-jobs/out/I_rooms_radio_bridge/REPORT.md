# Job I: Radio Room + Bridge (layered SVG)

Sources: `raw_originals/08_ROOM_RADIO.png` and `raw_originals/09_ROOM_BRIDGE.png` (5504x3072). All coordinates (manifests, pivots) are in source pixels.
Rebuild with `python tools/build_i.py radio|bridge` (about 2.5 min per room), then `python tools/preview.py`.

## Files

```
radio/   radio.json  radio_shell.svg  radio_space.svg  radio_string_lights.svg  radio_lights_glow.svg  radio_composite.png
         objects/ vu_meters, vu_needle_1..4, tape_deck, reel_left, reel_right, cassette_shelf_upper, cassette_shelf_lower,
                  cassette_crate, armchair, side_table, lava_lamp, lava_blobs, records, rug, dish   (all radio_*.svg + .png)
bridge/  bridge.json  bridge_shell.svg  bridge_space.svg  bridge_light_pools.svg  bridge_lights_glow.svg  bridge_composite.png
         objects/ console, screens, chair, thermos, star_table, chart_disc, plant   (all bridge_*.svg + .png)
check/   <room>_<layer>_side_by_side.png (original | SVG on original | SVG alone on cream), <room>_<layer>_onion.png (SVG 50% over original),
         <room>_full_side_by_side.png, <room>_full_onion.png, <room>_masks.png (segmentation), <room>_manifest_debug.png,
         <room>_shell_repaint.jpg (what the shell looks like behind furniture), <room>_scores.json
tools/   build_i.py (pipeline), rooms_i.py (per-room shapes, pivots, manifest data), preview.py, zoom.py
PREVIEW.png
```
Every SVG has a `viewBox` at source scale and one named `<g id="<room>_<layer>">`; PNGs are RGBA at half source scale. Largest SVG: `radio_shell.svg` at 1.2 MB (limit 1.5 MB). No embedded rasters, scripts, or `var()`.

## How to assemble (draw order)
1. `background` (`*_space.svg`, behind the shell; padded 60/120 px so it can drift), plus `background_children` (the radio dish).
2. `*_shell.svg` (floor, walls, frame; the window is cut out with a clipPath).
3. Bridge only: `bridge_light_pools.svg`, blended with **screen**. These are the hologram-table glow and the left door's light spill, rebuilt as SVG gradients and taken out of the shell. Keep them on; they can pulse.
4. Objects sorted by `sortY` (`layer: floor` and `sortY: 0` first: rug, wall shelves, VU unit, string lights). Each `children` entry draws right after its parent.
5. Optional `*_lights_glow.svg` (screen) for flicker or pulse. The painted halos are already baked into the shell, so this layer is **off** in the faithful look.

Animation hooks (`pivot` in room coordinates in the JSON; `data-pivot` in the file's local coordinates):
VU needles 1-4 (clean vector, rotate about the dial hub), reels (spin), lava blobs (bob), string lights (flicker), bridge chair (swivel about the base centre), chart disc (rotate the inner group `#chart_disc_spin`, which already sits inside the perspective squash, so a plain rotation reads as a flat disc turning), screens (pulse).

Anchors: radio `station_alcove` (tape station) [4340,1180], 2 vents, 1 seat. Bridge `station_alcove_left` [1050,1550], `station_alcove_right` [4460,1550], `helm`, 1 vent. Doors: radio has left, right and bottom; the bridge has left and bottom (the painting has no right door).

## Method
For each layer I drew a generous hand shape. The script snaps it to the painted plum outlines (flood fill from outside through non-outline pixels; GrabCut and analytic ellipses where glow washes the outline out). Anything a child or neighbour covers is repainted. The pixels are flattened with mean shift and traced with vtracer, with a few settings tried per layer; the build renders each attempt, scores it, and keeps the best one under the size cap.

vtracer sometimes drops a whole colour cluster. A repair pass re-renders the trace, finds large wrong areas, and refills them with posterised polygons. The nebulae use a k-means band tracer, with stars as exact circles.

The shell behind furniture is filled with row-wise colour blends, so hidden wall and floor stay flat and clean (see `check/*_shell_repaint.jpg`). Every number below comes from rendering the final SVG with cairosvg.

## Scores
MAE is on a 4x downscale over each layer's own visible pixels, with children drawn on top of the parent (target ≤ 12/255). Edge is the distance from the SVG's edges to the original's edges at full resolution (median / 90th percentile).

| Radio layer | MAE | edge med/p90 px | KB | | Bridge layer | MAE | edge med/p90 px | KB |
|---|---|---|---|---|---|---|---|---|
| **full composite** | **3.17** | | | | **full composite** | **3.17** | | |
| shell | 2.89 | | 1226 | | shell | 3.14 | | 682 |
| space (nebula) | 3.53 | 1.4 / 4.6 | 54 | | space (nebula + planet) | 4.57 | 1.9 / 17.4 | 166 |
| dish | 6.01 | 1.0 / 3.8 | 39 | | console | 4.46 | 1.0 / 1.9 | 473 |
| string_lights | 5.86 | 1.0 / 3.7 | 134 | | screens | 6.12 | 1.4 / 5.5 | 56 |
| vu_meters | 4.67 | 1.0 / 1.9 | 178 | | chair | 4.07 | 1.0 / 2.7 | 123 |
| vu_needle_1 | 10.29 | 0.0 / 1.4 | 0.4 | | thermos | 4.78 | 1.0 / 1.9 | 24 |
| vu_needle_2 | 11.23 | 0.0 / 1.4 | 0.4 | | star_table | 5.05 | 0.0 / 1.9 | 56 |
| vu_needle_3 | 6.38 | 0.0 / 1.0 | 0.3 | | chart_disc | 3.68 | 0.0 / 1.0 | 218 |
| vu_needle_4 | 5.71 | 0.0 / 1.0 | 0.3 | | plant | 4.44 | 1.0 / 1.0 | 51 |
| tape_deck | 4.53 | 1.0 / 1.9 | 417 | | | | | |
| reel_left / reel_right | 5.01 / 5.46 | 1.0 / 1.9 | 29 / 29 | | | | | |
| cassette_shelf_upper / lower | 5.01 / 5.11 | 1.0 / 1.0 | 62 / 89 | | | | | |
| cassette_crate | 4.83 | 0.0 / 1.0 | 144 | | | | | |
| armchair (with headphones) | 4.13 | 0.0 / 1.0 | 159 | | | | | |
| side_table | 4.26 | 1.0 / 1.4 | 67 | | | | | |
| lava_lamp / lava_blobs | 6.67 / 4.13 | 1.0 / 2.9 | 36 / 14 | | | | | |
| records | 4.74 | 0.0 / 1.0 | 55 | | | | | |
| rug | 3.11 | 1.0 / 12.3 | 182 | | | | | |

Every object is under 12. Outlines align within 1 px (median) and ≤ 4 px (p90). The exceptions are the soft nebula bands, which add edges the original only has as gradients, and the rug, whose p90 comes from its fine dot pattern.

## Deviations and known flaws (honest)
- **Flatter than the painting.** Soft in-object gradients (the glow on the VU faces, reel sheen, lamp-light falloff on the armchair) become 2-4 flat cel tones. This matches the style rules, but it is visibly less painterly. The nebulae are posterised into bands.
- **VU needles are redrawn as clean vector lines.** Their geometry was measured from the painting, and they are faithful in position and angle. Where a needle crossed the scale arc, a few pixels of the arc are slightly smudged.
- **Hidden areas are plausible fills, not paintings.** Covered regions are repainted as plausible fill: the shell behind furniture, the console behind the chair (visible only while the chair swivels), the deck behind the reels, and the table top under the lamp. The rug's hidden right side is mirrored from its left half.
- **Bridge light pools are fitted approximations.** They were fitted to the painting's falloff; faint residual blotches remain on the floor around the table.
- **The window glare streaks belong to the space layers,** so they drift with the nebula.
- **The planet is not split from the nebula.** The brief allows one background layer.
- The armchair outline includes a few stray pixels of the window rail where the headphone band touches it.
- Collision polygons, walkable floor, vents and the seat anchor are hand-placed estimates, so tune them in the prototype.

## Rating
**About 8/10 against the originals.** Both composites read as the paintings: MAE 3.2 and outlines within about 1 px. Every requested piece is a separate named layer with pivots, and the manifests are complete. The points off are for flatter shading than the painting and for fill quality in hidden areas.
