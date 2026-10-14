# Job L: Extra props (sheet 38) report

Source: `raw_originals/38_PROPS_EXTRA.png` (5504 x 3072, magenta key). 12 sprites → 10 props (the med scanner and security desk each come in two states on the sheet).

## Files

| Prop | `*_orig.svg` (traced) | `*_front.svg` (room camera) | Layers (`<g id>`) |
|---|---|---|---|
| med_scanner | 125 KB | 23 KB | `base`, `arch_back`, `scan_ring` (`scan_light`, `scan_ring_glow`, `scan_ring_core`; `data-pivot`), `arch_front` (front: `base`, `arch`, `scan_ring`) |
| security_desk | 268 KB | 8 KB | `body`, `screens_off`, `screens_on` |
| floor_lamp | 26 KB | 26 KB | `body` (unlit), `glow` (`glow_shade`, `glow_bulb`, `glow_halo` hidden) |
| plant, crate_stack, water_cooler, locker, toolbox, mop_bucket, cactus | 31-102 KB | 1-50 KB | one named group per prop (crate front: `crate_left/right/top`, cooler front: `bottle`) |

- `png/`: every SVG at **half source scale**, RGBA, rendered in Chromium (the SVG blur glows need it). Alternate states: `*_idle.png` (scanner, ring hidden), `*_off.png` (desk screens off, lamp unlit).
- `layers/`: the animated or stateful layers as standalone SVGs with the **same viewBox** as their parent, so they overlay 1:1: `med_scanner_scan_ring_*`, `security_desk_screens_on_*`, `floor_lamp_glow_*`.
- `check/`: `<name>_side_by_side.png` (original | SVG over magenta) and `<name>_onion.png` (50/50) for every traced object and state.
- `PREVIEW.png`: all props, both views, both states, labeled, on cream.
- `src/`: the reproducible pipeline (`segment.py`, `common.py`, `build_decor.py`, `build_lamp.py`, `build_desk.py`, `scanner_masks.py`, `build_scanner.py`, `build_front.py`, `export.py`). Run from this folder with `PYTHONPATH=src`. Needs vtracer, cairosvg, scipy and playwright.

Coordinates are in source pixels. `viewBox="0 0 w h"` is the sprite crop (16 px margin), and `data-src-box="x,y,w,h"` gives where that crop sits on the sheet.

## MAE (4x downscale, object region, Chromium render composited on magenta; target ≤ 12/255)

| Object | MAE |
|---|---|
| locker | 2.94 |
| toolbox | 3.47 |
| security_desk (screens off) | 3.94 |
| water_cooler | 4.28 |
| cactus | 4.96 |
| floor_lamp (glow on) | 4.99 |
| plant | 5.02 |
| crate_stack | 5.76 |
| med_scanner (idle) | 5.81 |
| mop_bucket | 6.42 |
| security_desk (screens on, vs the "on" sprite) | 6.70 |
| med_scanner (scanning, vs the "active" sprite) | 7.96 |

All are within target. Outlines align within 1-3 px, because the shapes are traced from the source.

## How it was made
1. Key the magenta by unmixing against the sheet's plum outline (#4E1648, not #2A1E35 on this sheet) and decontaminate the edge pixels.
2. Flatten colours per prop with a median filter, k-means (near-duplicate clusters merged), and a majority filter. Small accents that would otherwise be lost (cooler tap caps, lamp rim line) were added as extra colour centres.
3. Trace with vtracer (stacked splines) and wrap the result in named groups.
4. Special layers:
   - **Med scanner.** The arch was split from the base by teal-component topology. The base under the arch was **repainted** from fitted ellipses, so it has no holes. The ring was extracted from the active sprite by differencing it against the idle sprite (aligned +2 px), and its cut ends were extended 60 px under the left pillar so it can bob vertically without gaps. Layer order is `base` < `arch_back` < `scan_ring` < `arch_front`, which matches the painting: the ring passes in front of the back pillar and behind the front one.
   - **Security desk.** The glass mask comes from the off sprite. `screens_on` is the on-sprite content (aligned −4 px), clipped to the glass and softly blurred.
   - **Floor lamp.** The body is traced *unlit*: the shade's light zones are flattened to the rim colour and the bulb is dimmed. `glow` re-adds the cel-shaded light zones (soft blur, clipped to the shade) and the bulb. `glow_halo` is an optional soft halo, hidden by default (there is none on the sheet).

## Front versions
- **Redrawn** for the room's top-down 3/4 front camera (front face + visible top face, two-tone, sheet outline colour, 14 px stroke, sampled colours): med scanner (the arch now spans left-right across the pad, three stacked scan rings; the base reuses the round traced base), security desk (straight desk, two pedestals, drawers, four monitors slightly angled inward, same three state layers), crate stack, water cooler (body redrawn; the round bottle reuses the trace), locker, toolbox.
- **Same artwork as orig** for the four round props (plant, cactus, floor lamp, mop bucket). They are rotationally symmetric, so the sheet view already matches the room camera, and a redraw would have the same silhouette. The file only gets `data-view="front ..."`.
- There is no MAE for the fronts (no source exists). They were checked visually next to the originals.

## Usage notes
- Scanner: toggle `#scan_ring` (`display`) for idle/scanning. Animate it with `translateY` (about ±40 px) and an opacity pulse around `data-pivot`.
- Desk: show `#screens_on` or hide it (when hidden, `#screens_off` shows through). Lamp: toggle `#glow`.
- Use the `layers/` files if the game composites states as separate sprites.

## Deviations and known flaws
- The **orig traces keep the sheet's own colours**, including the magenta-leaning outline #4E1648. They do not snap to the house #2A1E35, by the "faithful" rule. The fronts use the same outline so the two views match.
- Painterly texture is posterised into flat zones. The leaf bases on the plant and some cream areas show slight blotches, and the lamp's inner rim line is thinner in places.
- The scanning state's pink haze over the magenta is approximated by the blurred ring glow plus a `scan_light` ellipse. The scanner ring and the desk screen content come from the *other* sprite on the sheet, so those states inherit small differences between Gemini's two paintings (that is why they score 6.7-8.0).
- The orig desk SVG is the largest file (268 KB, all under the 1.5 MB limit).
- Front redraws are simpler than the paintings: no painterly highlights, and the crate fronts are plainer.

## Honest rating
- **orig: 8.5/10.** Visually near-identical to the sheet at game scale, and every object is well under the MAE target. The layers are genuinely usable (repainted base, extended ring, unlit lamp body).
- **front: 7/10.** Clean and consistent with the room furniture, and they read well at game size. They are more geometric and less painterly than the originals, and the locker and crates are the plainest.
