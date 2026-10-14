# Job B: UI frames and the Meeting Tablet kit

All art comes from one generator, `src/build.py` (cairosvg + fontTools + Pillow). Fonts are the real Google Fonts files (Bungee, VT323, Space Grotesk instanced at weights 500 and 700), taken from github.com/google/fonts. Set `GS_FONTS` to the folder that holds them. Run `python src/build.py` to rebuild every SVG, PNG, `nineslice.json`, `PREVIEW.png` and `meeting_mock.png`.

## Files (SVG in this folder; `png/<name>@1x.png` and `@2x.png`, transparent)
| Piece | Files | 1x size |
|---|---|---|
| Large CRT panel (nine-slice) | `panel_crt_lg` | 480x320 |
| Small CRT panel (nine-slice) | `panel_crt_sm` | 240x160 |
| Toast banner, cream pill with amber lamp (3-slice) | `toast_banner` | 360x64 |
| Speech bubble, tail bottom-left (nine-slice) | `speech_bubble` | 280x150 |
| Pill button: idle, pressed, disabled, danger (3-slice) | `btn_pill_{idle,pressed,disabled,danger}` | 200x64 |
| Progress bar trough, fill, fill tile | `progress_trough`, `progress_fill`, `progress_fill_tile` | 400x40, 380x20, 24x20 |
| Timer dial layers | `timer_dial_ring`, `timer_dial_arc`, `timer_dial_center` | 112x112 each |
| Chat button, unread dot, chat drawer (nine-slice) | `chat_button`, `chat_unread_dot`, `chat_drawer` | 64, 24, 360x540 |
| Meeting Tablet frame, header title (paths) | `tablet_frame`, `tablet_title` | 1280x720 canvas, 640x56 |
| Vote plates | `plate_{alive,you,selected,voted,caller,eliminated,disconnected}` | 552x94 (536x78 body + 8 px glow margin) |
| Vote confirm/cancel mini buttons (extra) | `btn_vote_confirm`, `btn_vote_cancel` | 40x40 |
| `nineslice.json` | insets for every frame, plus the tablet layout (screen rect, the 10 plate slots, SKIP, timer, chat), plate anchors (portrait well, name baseline, status area, badge socket, button slots) and timer arc geometry | |
| `PREVIEW.png` | every piece labeled, plus a **stretch test** that re-slices the @2x PNGs with the JSON insets | |
| `meeting_mock.png` | 1280x720 mock over the dimmed Galley painting | |

## How to use (Phaser 3)
- Frames: `this.add.nineslice(x, y, key, null, w, h, left, right, top, bottom)` with the insets from `nineslice.json` (1x px; double them for @2x textures). `top/bottom = 0` means 3-slice, so the height stays fixed.
- Button labels are live text: Bungee 22, colors listed in the JSON. On the pressed state the whole shape sits 3 px lower, so nudge the label too.
- Progress: put `progress_fill` at offset (10,10) in the trough and `setCrop` it to the progress width, or use the tile as a TileSprite. Never scale the stripes.
- Timer: stack ring, then an arc drawn with Graphics (r 37, width 8, start at -90°, clockwise), then center. Arc colors: seafoam for discuss, amber for voting, coral for the last 10 s. VT323 digits go beside the dial.
- Tablet: place it at (0,0) over a 60% dim layer and tween y from 720 to 0. Plates go at `meeting_tablet.plates[i]`. Portraits come from the crew puppet in code, clipped to `portrait_well`.

## Honest quality rating: 7.5/10
Strong: the family is coherent (cream bevelled plastic, plum outlines, indigo CRT glass with a teal edge glow, screws, the cream-amber-coral stripe). Every frame passes the stretch test cleanly. The mock reads well at 1280x720: 25 px names, a 42 px title, VT323 timer.
Weaker: the glow is faked with stacked translucent strokes (no blur filter, so cairosvg renders it), so it looks a little banded up close. The plates are flat compared with the painted rooms. Mock portraits are simple helmet discs, not the puppet.

## Deviations and notes
- Tablet frame and plates are **fixed size**, not nine-slice (they are laid out for exactly 1280x720). Plate SVGs include an 8 px margin so `plate_selected`'s glow fits and every state stays the same size.
- The unread dot is nebula pink, not coral, because coral is reserved for danger and Impostor.
- Extras: vote confirm/cancel buttons, a progress fill tile, `tablet_title` as paths.
- The VOTED stamp and the megaphone badge in the mock are mock-only stand-ins; Job A provides the real ones. `plate_voted` has a seafoam "has voted" lamp and leaves the status area clear for the stamp. `plate_caller` has an amber badge socket. `plate_disconnected` has an unplugged-cable glyph.
- The mock shows "VOTING 1:42" (some players have already voted); "DISCUSS 0:15" is the same layout with a seafoam arc.
- Fonts are not committed. Fetch them as described above.
