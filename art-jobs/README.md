# Art jobs: SVG assets for GRAVEYARD SHIFT

Read this whole file, then your job section in [BRIEFS.md](BRIEFS.md). You are one of several parallel agents; each owns one job letter (A to F).

## The project

**GRAVEYARD SHIFT** is an Among Us-style social deduction game (4 to 10 players) built into Covey.Town (Phaser 3 + Twilio). Players join from an arcade cabinet in the pixel-art town and play on a cozy 1970s retro-futurist cargo ship, the **Nightjar**: Crewmates do tasks, Impostors eliminate them, everyone meets and votes. The art is a hybrid: rooms and screens are painted by an AI image tool (see `refs/`); **characters, UI, task panels, icons and anything that must animate or tint are clean SVG made by you.** The course demo is due in 3 days, so quality AND speed matter: deliver a good complete set first, then polish.

## Style rules (apply to everything)

- Clean 2D cartoon. Flat two-tone cel shading: one base color and one shadow color per area. **Uniform dark-plum outlines `#2A1E35`, never black.** Chunky, rounded shapes, bevels. No gradients (except a soft glow or light pool where a brief asks), no texture noise, no photorealism.
- Palette: midnight indigo `#1B1830`, plum `#3D2A4F`, outline plum `#2A1E35`, teal steel `#2F6F73`, seafoam `#7FC8B8`, amber `#F5A54A`, cream `#F4E6C8`, coral `#E8574A`, nebula pink `#D9738C`. Coral is reserved for danger and Impostor meaning. Darker/lighter tints of these are fine.
- Retro-70s vocabulary: cream plastic, brushed teal metal, chunky screws, amber lamps, CRT screens, and the **cream-amber-coral triple racing stripe** motif.
- Mood: cozy, playful, slightly mysterious. Funny, never scary or gory.
- UI fonts (Google Fonts): **Bungee** (headings), **Space Grotesk** (body), **VT323** (terminal readouts). In delivered SVGs convert any lettering to paths unless the brief says live text is expected.
- Original designs only. Among Us conventions (layouts, button roles) are fine to follow; its art, shapes and logos must not be copied.

## Reference images (`art-jobs/refs/`, Read them with the Read tool)

| File | What it is |
|---|---|
| `00_crew_model.jpg` | The approved crew character: chunky round astronaut, huge fishbowl helmet (thick light blue-grey rim, dark indigo interior, big white glass highlight), glowing amber visor as its only face, antenna with ball, mitten hands, grey suit with vertical striped chest tab |
| `crew_svg_lineup.png` | The same crew already built as SVG (side/front, colors, ghost): shows the SVG style target |
| `01_galley.jpg` ... `09_bridge.jpg` | The painted rooms: your style target for materials, outline weight, flatness, lighting |
| `10_hall.jpg` | Painted corridor |
| `14_stations.jpg`, `15_props_ship.jpg` | Painted props (task stations, emergency button, vents, time clock, doors) |
| `02_keyart.jpg` | Key art (mood) |
| `crew_rig.png` | The SVG puppet side + front views on green (scale reference) |

The real files are larger than they look: refs are 2000 px wide copies of 5504 px originals (x2.75).

## SVG conventions

- Set `viewBox`; keep each SVG under about 500 KB. No external references, no scripts, no raster images embedded.
- Every logical piece is a named `<g id="...">`. Parts that animate get a `data-pivot="x,y"` attribute (joint position in viewBox units).
- Colors that the game must recolor use CSS variables with defaults, e.g. `fill: var(--suit, #CDCCD4)`; **cairosvg does not support `var()`**, so keep variables out of anything you must render with cairosvg, or substitute defaults when exporting PNGs.
- XML comments must not contain two consecutive dashes.
- Name files `snake_case`, like `btn_use.svg`, `panel_keypad.svg`.

## You cannot judge by reading code: render and LOOK

1. Install a renderer (cloud Linux): try `pip install cairosvg` (if it fails: `apt-get install -y libcairo2` first); alternatives: `rsvg-convert`, `inkscape`, or `pip install playwright && playwright install chromium`. `art-jobs/tools/render.py` wraps whichever works: `python art-jobs/tools/render.py in.svg out.png [width]`.
2. Render every iteration to PNG and open it with the Read tool. Put it next to the matching reference at the same scale. Be critical: the first pass is never good enough. Check outline weight, flatness, palette, proportions, readability at the real display size (small icons must read at 64 px).

## Deliverables and git

- Output folder: `art-jobs/out/<LETTER>_<name>/` containing: final SVGs, PNG exports (transparent, 2x of the in-game display size), `PREVIEW.png` (all pieces labeled on a cream `#F4E6C8` background), and `REPORT.md` (files, sizes, how to use, known flaws, honest quality rating versus the references).
- Git: create branch `job/<letter>-<name>` from `main`, commit in small steps, **push that branch**. Do not touch files outside your output folder. Never push to `main`.
- Do not use any image-generation service. Do not stop at the first draft.
