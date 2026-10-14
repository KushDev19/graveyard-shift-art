# Job O: logo, HD arcade, screens pack, pose cutouts

All traces were made from `raw_originals/` at source size. Coordinates in every SVG and JSON file are source pixels. Checks are in `check/` (`*_side_by_side.png` shows the original on the left and the SVG on the right; `*_onion.png` is the SVG at 50% over the original; `mae.json`). MAE was computed on a 4x downscale over each object's bounding box, with the SVG composited over the keyed green background plate.

## Files

| File | Size | What |
|---|---|---|
| `logo.svg` / `logo.png` (half scale) | 470 KB / 865 KB | Layered logo, viewBox 5504x3072. Groups, back to front: `glow` (stepped cream halo made of rings, no filter), `racing_stripe`, `moon` (crescent, rod, small crescent), `letters` holding 14 groups `letter_G` … `letter_T`, each with a `data-char` (G R A V E Y A R D / S H I F T). Each letter group holds its own face, mauve line and plum extrusion. `helmet_dot` (antenna, glass, visor, collar) has `data-pivot` at the collar. Spelling verified: GRAVEYARD SHIFT. |
| `logo_mono_cream.svg` / `.png` | 57 KB | One-colour cream version. Faces and extrusion are split by transparent outline gaps; the helmet is shown as rim, visor, collar and antenna. |
| `arcade.svg` / `arcade.png` | 521 KB / 520 KB | HD arcade, viewBox 4096x4096. Groups: `cabinet`, `marquee`, `screen`, `coin_door`, `controls` (joystick and 10 buttons, pivot at the joystick base). Under the screen the cabinet carries a CRT-off dark glass, and the controls and coin door areas are repainted, so hiding any group leaves no hole. |
| `arcade_screen.svg` / `.png` | 224 KB | Screen content only. The viewBox is the screen's region in source px (`data-origin="1384,1226"`), so it can be placed or animated on its own. |
| `arcade_marquee_blank.svg` / `.png` | 31 KB | Blank lit marquee (`data-origin="1440,316"`), ready for a title overlay. |
| `screens/*_1920.webp`, `*_3840.webp` | 3.1 MB total | Screens 27 to 34 at q85, plus `27_screen_title_16x9_*` (crop x0 y1720, 4096x2304; keeps the planet ring and the whole ship). |
| `screens/30_rays.svg`, `screens/31_rays.svg` | 2.5 KB / 2.1 KB | `#backing` rect plus `#rays` group (`data-pivot` = burst centre). Each ray is one triangle, colours snapped to 3 inks. The rays in 30 run past the frame so they can spin with no gaps. The rays in 31 keep the painted flat-cut lengths. |
| `screens/30_*_fg_*.webp`, `31_*_fg_*.webp` | | Everything in front of the rays with alpha (comic panel; megaphone, sound waves, spotlight, helmet and floor). Stacking order is backing, spinning rays, then the foreground. |
| `screens.json` | | For each screen: source, size and WebP paths; the 16:9 crop rect for 27; `podium_top` ellipse and `stage_line` for 28, 29, 33 and 34; `burst` (svg, pivot, foreground) for 30 and 31. Values are given in source px and normalised 0..1. |
| `poses/pose_*.png` (10) + `poses.json` | 9.7 MB | Transparent cutouts at half source scale: reveal_hands_on_hips, reveal_arms_crossed_smug, meeting_point_accuse, meeting_shrug, win_jump_cheer, win_wave, fallen_headless (body, popped helmet and stars), ghost_halo, eject_tumble, sneak_tiptoe. `poses.json` gives each crop's sheet and source rect. |
| `src/` | | Reproducible scripts: `common.py` (green key with local plate, MAE), `tracer.py` (k-means palette → majority-filtered regions → smoothed paths), `logo.py`, `arcade.py`, `rays.py` (+ `rays_probe.py` centre search), `podiums.py`, `poses.py`, `screens.py`, `screens_json.py`, `verify.py`, `finalize.py`, `preview.py`. |

## MAE (target ≤ 12/255)

| Object | MAE |
|---|---|
| logo (whole) | 4.68 |
| logo / letters | 4.15 |
| logo / racing_stripe | 5.08 |
| logo / helmet_dot | 7.20 |
| logo / moon | 8.47 |
| arcade (whole) | 3.93 |
| arcade / marquee | 3.94 |
| arcade / screen | 5.73 |
| arcade / controls | 5.97 |
| arcade / coin_door | 7.08 |
| 30 rays (ray area, foreground excluded) | 2.05 |
| 31 rays (ray area, foreground excluded) | 2.34 |

The podium ellipses were snapped onto the dark rim line by a local search; overlays are in `check/podium_*.jpg`.

## Deviations and known flaws

- **Traced, not hand-drawn.** The SVGs are colour-region traces (each object has its own palette of 3 to 24 colours, with outlines in source coordinates). Soft painted glows (the visor glow, the marquee light, the galaxy swirl) become stepped colour bands, not gradients. You can see the banding up close in the logo's visor glow and the screen swirl; at display size it reads as cel shading.
- **Logo glow** is made of cream rings whose opacity was measured from the keyed halo. cairosvg ignores blur filters, so I used rings instead of a blur. On dark backgrounds it shows as a soft stepped halo.
- **Logo seams:** there is a faint double line where the moon tucks behind the D, and a small stripe notch next to the D. Both are only visible zoomed in.
- **Gemini artifacts kept for fidelity:** a lighter block at the top-left of the arcade's side panel (from Gemini's green background tiles). The motion-smeared mittens in fallen_headless, eject_tumble and win_jump_cheer, and the smeared left rim of sneak_tiptoe's helmet, stay semi-transparent and mottled. The green is removed (despilled) but the smear itself is in the source.
- **Rays:** the 30 foreground includes a few static ray slivers hugging the panel's lower-left edge, and the 31 foreground includes the ray pieces visible between the sound waves. When spinning, those slivers stay fixed.
- The marquee was already blank in the source. Its traced glow is banded (MAE 3.9).

## Honest rating

- Logo: **8/10**. The shapes, spelling, layering and colours match closely. The halo is stepped, not soft.
- HD arcade: **8/10**. Very close match, cleanly layered, and swapping the screen or marquee works. The swirl glow is banded.
- Screens pack: **9/10**.
- Pose cutouts: **8/10**. Edges are clean with no green fringe; the source smears remain.
