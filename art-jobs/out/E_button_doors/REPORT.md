# Job E: Emergency button and doors

**Units:** every SVG, PNG and rig coordinate uses pixels of the 5504 px room paintings, and PNGs are exported 1:1. To draw them in a room shown at width `Wd`, scale by `Wd / 5504`. The button base is 390 px wide, about 1.3x the Galley table pedestal. The front doorway opening is 580 px wide, about twice a crew member's width.

## Files
| File | What it is |
|---|---|
| `emergency_button.svg` | Master SVG in the idle state with every named part: `base`, `glow_ring`, `flash_ring`, `dome_back`, `button`, `dome_front`, `padlock` (hidden). Parts have `data-pivot` set. |
| `emergency_button_{idle,open,pressed,disabled}.svg/.png` | The four states (570x530 canvas). |
| `parts/*.png` | Cropped engine layers: base, glow_ring_off/on/bright, button_idle/lit/pressed/disabled, padlock. `rect` in the rig gives each layer's position in the canvas. |
| `parts/dome_back_strip.png`, `parts/dome_front_strip.png` | The dome flip pre-rendered at 0 to 120 degrees, 13 frames in 10 degree steps. |
| `emergency_button_rig.json` | Pivots, part rects, draw order (switches when the dome angle passes 30 degrees), flash ring spec, the full tween timeline in ms, and the door slide vectors and masks. |
| `emergency_demo.html` | Self-contained demo (inline SVG and vanilla JS) with Play all, Open, Press, Lock, Reset, slow-mo, a timeline scrubber, and an open/close toggle for the doors. |
| `door_front_{closed,open}.svg/.png` | Front bulkhead door (860x900). Groups: `doorway`, `halves` (`door_left`, `door_right`, clipped to the opening), `frame` (with `lamp`). |
| `door_side_{closed,open}.svg/.png` | The same door on the left wall as a skewed slab with visible thickness (260x1340). |
| `door_side_r_{closed,open}.png` | Pre-mirrored versions for the right wall. |
| `parts/door_front_*.png`, `parts/door_side_*.png` | Full-canvas aligned door layers (offset 0,0) for the slide animation. |
| `PREVIEW.png` | Every deliverable, labelled. |
| `build/` | `build_e.py` rebuilds everything. `emergency_core.js` is the shared geometry. `doors.py` builds the doors. `verify_demo.py` writes a contact sheet of animation frames. `make_preview.py` builds the preview. |

## How to use
- **Button in Phaser:** stack the layers in the rig's `draw_order`, positioned by their `rect`. Animate the dome by stepping the strip frame (`round(angle / 10)`), and run the other tweens from `tweens_ms`. Draw the flash ring as a Graphics ellipse stroke (spec in the rig). For the press, scale `button` around its pivot, then swap to `button_pressed`.
- **Doors:** place `doorway`, then the two halves, then `frame`. Mask both halves with the opening (`opening` for the front door, `opening_polygon` for the side door), then tween each half by its `slide` vector over 550 ms. In the SVG, the halves already carry `data-slide`.
- **Rebuild after edits:** `pip install playwright pillow`, then `python art-jobs/out/E_button_doors/build/build_e.py`.

## Verification
I loaded `emergency_demo.html` in headless Chromium (playwright) and captured frames at 0, 250, 480, 650, 960, 1000, 1100, 1300, 2000, 2350, 2650, 2850, 3000, 3450 and 4000 ms, plus a real-time playback and the door toggle. The page threw no errors. The frames show:
- The dome opens and overshoots to about 115 degrees, then settles at 110.
- The button squashes, then rebounds.
- Two coral rings expand and fade.
- The button dims to plum and the dome slams shut with a 7 degree bounce.
- The padlock drops, bounces and swings to rest.

## Deviations
- **Dome hinge:** the hinge is at the **back-left** of the rim (azimuth 235 degrees), not dead back. With this camera, a pure back hinge made the open dome look like a floating bubble. A back-left hinge reads clearly as a lid, matching the Gemini ref. The flip is a real 3D rotation, which a 2D sprite rotation cannot reproduce. That is why the engine gets a pre-rendered **frame strip** instead of a single rotate-around-pivot sprite. The `data-pivot` on the dome is the hinge point.
- **Dome is two layers:** the dome is split into `dome_back` and `dome_front` so the closed glass can sit both behind and in front of the button.
- **Side doors:** I drew only the left-wall door. The right-wall door is a mirror image (PNG provided, no separate SVG).
- **Live geometry:** the demo rebuilds the SVG every frame from the shared JS core. It does not tween the static SVG's groups.

## Known flaws
- On very dark backgrounds the closed glass reads a little grey. On the Galley's cream table it reads seafoam, as in the preview.
- The doors are cleaner and plainer than the painted locker-room door, which has a hexagon interlock and a big beacon. The seam is a simple stepped interlock.
- The doorway interior is a generic dark tunnel. Hide `doorway` if the room painting already shows what is behind the door.
- PNGs are 1:1 in painting pixels, not a fixed 2x of a display size, because the room display scale is not fixed yet.

## Honest rating
- **Button: 8/10.** It is a clean, polished sibling of the Gemini prop, and the animation feels snappy and readable.
- **Doors: 7/10.** They are consistent and animatable, but less detailed than the painted door slabs.
