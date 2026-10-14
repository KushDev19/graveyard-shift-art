# Job M: Hats (12 cosmetics, side + front, fitted to the SVG puppet)

## Files
| Path | What |
|---|---|
| `svg/hat_<id>_<view>.svg` | 18 single-layer hats (trucker, diner, hardhat, beanie, cowboy, chef, nightcap, party, propeller) |
| `svg/hat_<id>_<view>_back.svg` / `_front.svg` | wraparound items: afro (side+front), flowercrown (side+front), headphones side; headphones front is `hat_headphones_front.svg` (front only, see deviations) |
| `png/*@2x.png` | RGBA exports at 2x puppet scale |
| `cosmetics.json` | `{id, name, slot, side:{file,x,y,pivot,back?}, front:{...}, hidesAntenna, layers:{back,front}}` |
| `wardrobe_preview.png` | puppet side + front in tomato / sky / mint wearing every hat |
| `PREVIEW.png` | every SVG labelled on cream |
| `check/side_by_side.png`, `check/mae.json` | original crop vs SVG trace, error numbers |
| `tools/` | reproducible pipeline (`extract.py` → `build.py` → `final.py`; placements in `place.json`) |

29 SVGs, 812 KB total (largest 68 KB). All under the 1.5 MB limit; no rasters, scripts or external refs.

## How to use
- Every file is drawn at **puppet scale** (viewBox 640x800 units). Draw it with its top-left at `(x, y)` in puppet units.
- `pivot` = the dome centre (320,300) in file-local units: parent the hat to the head and bob/rotate it around this point.
- Side view faces right; mirror the whole puppet + hat for left-facing.
- Z-order: `back` file before `#dome` (side) / before `#f_leg_l` (front, so hair sits behind the body too). The main/front file goes after `#collar`, before `#arm_front` (side) / before `#f_arm_l` (front).
- `hidesAntenna: true` for every hat except headphones and flower crown (antenna pokes through those).
- Hats keep their own fixed colours. None of them has a neutral-grey part, so none use `var(--suit)` (the propeller blades are a fixed lavender-grey as painted).

## Method
1. Keyed the magenta off the 5504 px originals and cut the 24 views. For 43B (hats drawn on helmets), the helmet was removed by colour: the indigo interior plus the light-blue rim band within reach of it. The helmet outline was kept only where it touches hat colour, because there it is the hat's bottom edge.
2. Quantized each hat to its own palette sampled from the original (k-means, 6 to 10 colours). Every outline was snapped to the puppet outline `#2D1E3A`, and antialias speckles were mode-filtered out.
3. Vectorized with vtracer (spline, stacked) and snapped every fill to the sampled palette.
4. Fitting. **43B hats**: the source helmet's rim box (width and top; top estimated from the 0.866 height/width ratio where the hat hides it) maps onto the puppet rim (404 wide, top y=109), so each hat sits on the dome exactly as Gemini drew it. **43A hats**: scale and seat height were tuned by eye on the wardrobe render (`tools/place.json`).

## Fidelity (MAE /255, SVG vs original, 4x downscale, hat pixels only; target ≤ 12)
| hat | side | front |
|---|---|---|
| trucker | 5.5 | 7.2 |
| diner | 6.4 | 6.8 |
| hardhat | 5.7 | 4.7 |
| beanie | 6.2 | 5.1 |
| cowboy | 6.9 | 6.0 |
| chef | 7.2 | 4.9 |
| nightcap | 8.6 | 9.2 |
| party | 8.3 | 8.2 |
| headphones | 8.2 | 9.0 |
| flowercrown | 11.2 | 10.0 |
| afro | 1.7 | 2.5 |
| propeller | 8.1 | 8.4 |

All 24 are under target. The flower crown is the highest because of its many tiny petals; it is traced at 0.8 source scale, the others at 0.5.

## Deviations
- **Outline colour:** the paintings use `#3F1945`; it was snapped to the puppet's `#2D1E3A` so hats match the body linework.
- **Back layers:**
  - afro: a dark-brown filled hair mass behind the dome, so no background shows if the dome and source helmet differ slightly.
  - headphones side: the far ear cup peeking behind the dome, as painted.
  - flower crown: a darkened, raised copy of the crown standing in for the far side of the ring. Most of it is hidden by the dome, and only the ends peek out.
  - headphones front: has no back layer, because in the painting everything sits in front of the helmet (`layers.back.front` is absent).
- The **chef toque and beanie side** show their inner opening, as painted. It reads fine on the dome.
- The 43A seat heights are judgment calls: hats sit on the crown of the dome like the 43B ones.

## Known flaws
- Small leftover rim/outline slivers along the bottom edge of the nightcap brim, the propeller front brim, and the inner edge of the headphones side band. At game size they sit on the dome outline and hardly show; a hand clean-up pass would remove them.
- The traced paths come from vectorizing, not clean hand-built Béziers. They are faithful and smooth at game size, but harder to hand-edit than hand-drawn SVG.

## Honest rating
**8/10.** Faithful to the originals (all MAE ≤ 11.2), consistent outline weight, and every hat fits the puppet in both views and all colours (see `wardrobe_preview.png`). It loses points for the small brim slivers above and for having no animation split (propeller blades are not a separate rotating part).
