# Job F: emblem + pixel arcade cabinet

F1 (logo) skipped: already done and approved.

## Files
| File | What |
|---|---|
| `emblem.svg` | F2 round badge, 512 viewBox, 3.7 KB. Groups: `rim`, `screws`, `sky` > `stars`, `moon`, `helmet`. No text, no external refs. |
| `emblem_512.png`, `emblem_128.png`, `emblem_32.png` | Transparent exports (cairosvg). |
| `make_arcade.py` | F3 generator. A 32 x 64 ASCII map + one shared 15-color palette; frame-specific symbols (screen, ship, stars, marquee, sparkles) remap per frame. Asserts map size, at most 16 colors and alpha only 0/255. Run `python make_arcade.py`. |
| `arcade_32x64.png` | 1x sprite (active frame, the default "look at me" state). |
| `arcade_32x64_x8.png` | 8x nearest-neighbor inspection view. |
| `arcade_sheet_64x64.png` | 2 frames of 32 x 64: frame 0 idle (dim CRT, dark marquee), frame 1 active (bright amber CRT, glowing marquee, sparkles). |
| `arcade_in_town.png` | Sprite at true game scale (1 tile wide) on a Tuxemon tileset crop next to the shop, whole scene 2x. |
| `PREVIEW.png` | Everything labeled on cream. |

## Use
- Phaser: `this.load.spritesheet('arcade', 'arcade_sheet_64x64.png', { frameWidth: 32, frameHeight: 64 })`; idle = frame 0, swap to frame 1 (or alternate 0/1 at ~2 fps) when a player is in range. Keep `pixelArt: true` / NEAREST filtering.
- Emblem: app icon / favicon (`emblem_32.png`), loading spinner (rotate only the `rim` group if wanted; it is radially symmetric apart from the screws).

## Quality (honest)
- **Arcade: 7.5/10.** Clean (0 anti-aliased pixels, 15 colors), reads instantly as an arcade cabinet with the ship stripe, rocket on the CRT, joystick and two buttons; sits plausibly next to the Tuxemon shop at the same scale. Weaknesses: the lower body is fairly plain compared with the tileset's busier textures, and the outline (`#2B1F33`, project plum) is a bit darker than the tileset's brownish `#504040`, so the cabinet looks slightly heavier-lined than neighbouring buildings.
- **Emblem: 8/10.** Bold, palette-correct, reads at 32 px (moon + amber visor + ring stripe). At 32 px the small stars become noise; a simplified 32 px variant (no stars, no screws) would be crisper if the favicon matters.

## Deviations
- Stripe on the cabinet runs down the right edge of the front face (front-on view has no visible side panel).
- Marquee "glow" is shown with bulb dots and four solid sparkle pixels beside it in the active frame (no semi-transparent glow, to keep the sprite AA-free).
- Emblem uses one soft radial gradient for the visor glow (allowed by the "glowing" exception); otherwise flat.
