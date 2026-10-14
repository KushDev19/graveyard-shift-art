# Job N: toppers, backpacks, visors, decals

24 cosmetics traced from `raw_originals/44N_COS_TOPPERS_PACKS.png` and `45N_COS_VISORS_DECALS.png`, fitted to `frontend/public/assets/ship/crew/crew_puppet.svg`.

## Files
| What | Files |
|---|---|
| 8 antenna toppers (side + front) | `top_{star,heart,moon,cherries,bulb,eyeball,dish,planet}_{side,front}.svg` |
| 8 backpacks (side only, front hides the pack) | `pack_{jetpack,thermos,lunchbox,walkman,plant,heater,bedroll,toolbox}_side.svg` |
| 4 visors (side + front) | `visor_{aviator,heart,star,led}_{side,front}.svg` |
| 4 decals (side + front) | `decal_{nametag,bolt,smiley,flames}_{side,front}.svg` |
| Manifest | `cosmetics.json` |
| PNG exports (1x puppet units, default grey, RGBA) | `png/` (40 files) |
| Fit sheet: every item on the puppet, side + front, tomato / cobalt / mint | `wardrobe_preview.png` |
| Labelled overview | `PREVIEW.png` |
| Faithful traces in SOURCE pixel space (5504 px sheets) | `src/*_trace.svg` |
| Verification: original vs SVG, onion skin | `check/*_side_by_side.png`, `check/*_onion.png` (stored at half size) |
| Rebuild scripts | `build/` (`trace44.py`, `domes.py`, `extract45.py`, `build.py`, `wardrobe.py`, `export.py`; Chromium via Playwright) |

The largest SVG is 190 KB (bedroll); most are 10-60 KB.

## How to use (`cosmetics.json`)
- Every cosmetic SVG's `viewBox` is in **puppet units** (the 640x800 space of `crew_puppet.svg`). Draw the file at `(x, y)` with size `(w, h)` in puppet space and it lines up. For inline SVG you can drop the file's contents straight into the puppet.
- `replaces`: puppet groups to hide per view. Toppers hide `antenna` / `f_antenna` (the file carries its own stalk and nub, tinted). Backpacks hide `backpack`. Visors hide `visor` + `visor_glow` (and the `f_` pair). Decals hide `stripe` / `f_stripe`.
- `z`: the puppet group to insert after, so stacking stays correct (backpack stays behind the body; decals stay under `arm_front`).
- `pivot`: toppers rotate with the antenna (300,104 side / 320,108 front). Visors use the visor pivot (416,314).
- `hidesAntenna: true` on toppers means they replace it. `front: null` on backpacks means the front view shows no pack.
- `layers`: none of these items wrap around the dome. `back: true` marks the backpack slot (drawn behind the body).
- Tint: grey parts of all backpacks and the topper stalks use `var(--suit|--suit-shade|--suit-back|--suit-light, <sampled grey>)`, the same variables as the puppet, so `styleFor()` in `puppet_demo.html` colours them.

## Method
1. **Sheet 44N** (icons drawn on their own): magenta is keyed out, colours are clustered with k-means++ (the darkest cluster is forced to the house outline `#2A1E35`), a median filter removes paint speckle, and vtracer traces stacked layers in source pixels. The bulb's painted halo becomes a radial gradient.
2. **Sheet 45N** (drawn ON characters): each box is classified against a fixed background palette (helmet glass, rim, highlight, suit greys, magenta, glow halo) plus item colours. Background is removed. Outside the glass only saturated item pixels survive, which drops the helmet-rim arcs. The LED smiles are rebuilt as exact circles (33 and 57 dots) from detected dot centroids.
3. **Fit:** each source helmet's glass ellipse was measured (`build/domes.json`) and mapped onto the puppet's glass (centre 320,300, rx 196). Visors and decals keep the size and position they have relative to the helmet. Toppers sit on the stalk tip (max 118 tall x 150 wide). Backpacks are up to 236 tall x 196 wide, tucked 25 units behind the body edge. Decals are clipped to the body outline.

## MAE (0-255, 4x downscale, object region; target <= 12)
| Item | MAE | Item | MAE | Item | MAE |
|---|---|---|---|---|---|
| top_star | 3.25 | pack_jetpack | 8.45 | visor_aviator (side src) | 9.78 |
| top_heart | 2.23 | pack_thermos | 4.85 | visor_heart (side src) | 6.08 |
| top_moon | 3.85 | pack_lunchbox | 5.40 | visor_star (front src) | 6.21 |
| top_cherries | 6.59 | pack_walkman | 8.30 | visor_led side / front | **14.56** / **12.79** |
| top_bulb | 10.46 | pack_plant | 6.34 | decal_nametag side / front | **16.07** / 4.69 |
| top_eyeball | 3.61 | pack_heater | 9.29 | decal_bolt (side src) | 6.78 |
| top_dish | 4.93 | pack_bedroll | 8.50 | decal_smiley (src) | 4.88 |
| top_planet | 4.05 | pack_toolbox | 4.86 | decal_flames side / front | **15.01** / 9.68 |

For the 45N items the SVG is composited on a *flat* glass or suit colour, so anything missing counts as error. The four items over 12 are not tracing faults:
- **LED:** the painted glow has a different falloff from the SVG blur.
- **nametag side, flames side:** the box includes the painted body outline and arm, which are deliberately not part of the decal.

The decals themselves match visually (see `check/`).

## Deviations (honest)
- **Views Gemini did not draw are derived:**
  - Aviator front = the near lens plus its mirror over the puppet's amber visor.
  - Heart front = the same heart, centred.
  - Star side = the front pair foreshortened with the scale and offset measured between the two LED views.
  - Bolt front and smiley side/front come from the one view of each in the sheet.
- **Ignored as Gemini mix-ups on sheet 45N:**
  - the cream rectangles on the name-tag helmets
  - the lightning bolt and smiley painted on helmets
  - the second aviator pose. It is traced (`src/visor_aviator_s2_trace.svg`) but not used.
- The aviator temple arm is hand-drawn, because it is the same value as the helmet glass and cannot be keyed out.
- Backpacks are the sheet's front-facing icons stuck to the back. There is no true side redraw, but they read fine at game scale.
- Topper sizes, backpack sizes and decal scale factors (`build/decal_fit.json`) are judgement calls. The brief gave no target sizes.
- Visors replace the expression variants (`visor_blink`, `visor_surprised`, `visor_coral`). The game should keep the cosmetic visor and skip those swaps, or fall back to them for Impostor and ghost states.
- The jetpack flames are not a separate group, so they cannot be animated without splitting them out.

## Rating
- **Toppers and backpacks: 8.5/10.** They are faithful to the sheet (MAE 2-10), clean outlines, and tint correctly.
- **Visors: 7/10.**
  - LED and star read well.
  - The heart edge is a bit soft from the traced glow band.
  - The aviator front is derived and looks busier than the side.
- **Decals: 7.5/10.** They are faithful. Small sizes are tuned by eye.
