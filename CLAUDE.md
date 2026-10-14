# CLAUDE.md: GRAVEYARD SHIFT art repo (read this first)

## HARD RULES
1. **Never add "Co-Authored-By" trailers, "Generated with Claude Code" lines, or any Claude attribution** to commits, PRs or files. Commits are authored by the user only.
2. Push only to branches named `job/<letter>-<name>`. Never force-push. Never delete or overwrite the user's files in `raw_originals/`.
3. **Token economy matters** (the user's budget is limited): do not re-read the same big file twice; never open 5504 px originals (use `art-jobs/refs/`, 2000 px); render an SVG once per iteration and look at that one PNG; no long narration; do not spawn extra agents unless this file says to.
4. Judge by LOOKING (render to PNG, open with the Read tool), not by reading SVG code. First drafts are never good enough: compare side by side with refs, iterate, then stop.
5. No image-generation services. Original designs only (no copying Among Us art).

## What this project is
**GRAVEYARD SHIFT**: an Among Us-style social deduction game (4 to 10 players) for the NJIT CS 490 Team 11 project, built into Covey.Town (Phaser 3 + Twilio + Socket.IO; the game code lives in a different, class repo: this repo is ART ONLY). Players enter from an arcade cabinet in the pixel-art town and play on the cozy 1970s retro-futurist cargo ship **Nightjar** (night-shift mood, cream/amber/coral racing stripe). **Wizard-of-Oz demo is due Fri Oct 16, 2026 5:30pm EDT** (a faked but professional-looking 5-minute demo showing all user stories: join from arcade, tasks, meetings and voting, secret roles). After the art, a new chat will build a detailed HTML/Phaser prototype from these assets.

## Art system (decided)
- **Hybrid.** Gemini "Nano Banana Pro" (the user runs it) paints rooms, screens, props sheets, key art, poses, logo. **Claude builds in SVG/code**: crew puppet, UI, HUD icons, task panels, minimap, doors, emergency button, emblem, pixel arcade. Everything that animates, tints or must hit exact coordinates is SVG.
- **Rendering rule:** any time a *specific player* appears on screen they are drawn from the SVG puppet so their color AND cosmetics always show (in-game side view; front view on role reveal, vote cards, win lineups). Gemini poses are flavor/title art only.
- **Style:** clean 2D cartoon, flat two-tone cel shading, uniform dark-plum outlines `#2A1E35` (never black), chunky rounded shapes. Palette: indigo `#1B1830`, plum `#3D2A4F`, teal `#2F6F73`, seafoam `#7FC8B8`, amber `#F5A54A`, cream `#F4E6C8`, coral `#E8574A` (danger/Impostor only), pink `#D9738C`. Fonts: Bungee, Space Grotesk, VT323.
- **Crew:** squat round astronaut, huge fishbowl helmet (dark indigo interior), amber visor as the only face, antenna, mitten hands; suit is grey and tinted per player (10 colors: tomato E4483C, tangerine F28A2E, mustard E9C046, lime A6D64A, mint 6FD6B0, sky 6EC3F0, cobalt 3F5FD9, grape 8E5AC8, bubblegum F07BB5, cream F4E6C8).
- **Rooms** are painted diorama cutaways with a dark plum frame, doors only on left/right walls and a bottom notch. Hallways are tileable SVG pieces (done).
- Full specs: `docs/ART_DIRECTION_RESEARCH.md` (incl. §11 meeting tablet, Among Us lessons, vision/fog), `docs/CHARACTERS.md`, `docs/PROMPT_BOOK.md`, `docs/USER_STORIES.md`.

## Status (updated Oct 14)
**PHASE 2 (current): convert all usable art to layered SVG.** Briefs: `art-jobs/BRIEFS2.md` (jobs G-O: rooms G H I J, props K L, cosmetics M N, brand/screens O). Phase 1 jobs A-F are DONE and merged in `art-jobs/out/`. All Gemini art is now in `raw_originals/` (00-15, 23, 26-38, 43A-45N) with 2000 px refs in `art-jobs/refs/`.

**(Phase 1 notes below, kept for history.)**
**Approved Gemini art** (originals in `raw_originals/`, 2000 px refs in `art-jobs/refs/`): 00 crew model, 01 Galley, 02 key art, 04A-E poses, 05 Locker Room, 06 Reactor, 07 Switchboard, 08 Radio, 09 Bridge, 10 painted hall, 14 task stations, 15 ship props (emergency button, vents, time clock; its doors are unusable). Also approved by the user but not yet in this repo: 23 logo, 27 title screen, 28 and 29 role-reveal stages.
**Built SVG/code (done):** `frontend/public/assets/ship/crew/` (traced puppet SVG with 32 parts, Phaser atlas, rig JSON, `puppet_demo.html`, keyed pose PNGs with tint layers), `frontend/public/assets/ship/hall/` (tileable hall_h, hall_v, two corners). Scripts in `tools/` (Windows/Edge based; cloud sessions should use `art-jobs/tools/render.py`).
**Still to do (the cloud jobs):** A HUD icons+badges, B UI frames + Meeting Tablet kit, C task panels (keypad, switchboard, tape) + parts, D tier-2 panels + minimap, E animated emergency button + doors, F emblem + 32x64 pixel arcade cabinet (logo is DONE, skip F1). Briefs: `art-jobs/BRIEFS.md`; shared rules: `art-jobs/README.md`.
**Gemini still to generate (user does this):** 26 HD arcade cabinet, 30-34 splash/eject/win screens, 35-38 tier-2 rooms and props, 43A-45N cosmetics (stretch).

## How to run a job
1. Read this file, `art-jobs/README.md`, and ONLY your job's section in `art-jobs/BRIEFS.md`. Look at the refs you need.
2. Create branch `job/<letter>-<name>` from `main`. Output goes to `art-jobs/out/<LETTER>_<name>/` (SVGs, 2x PNGs, `PREVIEW.png`, `REPORT.md`).
3. Install a renderer once (`pip install cairosvg`, or playwright chromium); `python art-jobs/tools/render.py in.svg out.png [width]`.
4. Iterate until the work genuinely matches the refs, commit in small steps (no attribution trailers), push the branch, finish with a short report: files, honest quality rating, deviations. The user's local Claude session reviews and merges approved output.
