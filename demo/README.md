# GRAVEYARD SHIFT: Wizard-of-Oz demo

A click-through, presenter-driven HTML demo that **fakes the finished feature** with the real art (SVG crew puppet, painted rooms, task panels, Meeting Tablet, emergency button). Nothing here talks to a server: every beat is scripted with GSAP so a ~5 minute run always looks professional.

Stack: Vite + vanilla JS (ES modules) + GSAP 3. No React, no Phaser.

## Run

```bash
cd demo
npm i
npm run dev        # http://localhost:5173
npm run build      # static site in demo/dist (about 12 MB)
npm run preview    # serve dist locally
```

Deploy: Vercel or Netlify, **root directory `demo/`**, build command `npm run build`, output `dist`. Asset paths are relative (`base: './'`), so it also works from a subfolder. Fonts (Bungee, Space Grotesk, VT323) are self-hosted in `public/fonts`, so the demo works offline.

Refresh the staged art (only needed if `art-jobs/out` changes): `python3 tools/stage_assets.py` (needs Pillow).

## Controls

| Key | Action |
|---|---|
| `→` / `Space` / `Enter` | next beat (finishes the running beat first, so it can never stall) |
| `←` | previous beat (replays the scene up to the previous beat) |
| `1`-`9`, `0` | jump to scene 1-9 / title (scene 0) |
| `W` | scene 10, Crew wins ending |
| `I` | scene 10, alternate ending: **Impostors win** (living crew <= impostors) |
| `P` | presenter notes: the acceptance criteria the current scene demonstrates |
| `C` | toggle captions |
| `M` | mute / unmute the background music (a soft lo-fi loop generated in the browser; starts on your first key press or click. To use a real track instead, drop it at `public/assets/audio/music.mp3`) |
| `R` | restart the current scene |
| `A` | autoplay (advances beats by itself) |
| `F` | fullscreen |

Interactive beats (keypad, wiring, vote, Use / Report / Eliminate, CLOCK IN) can be **done by hand** or left alone: each shows an `auto in Ns` hint and completes itself. A slim chapter bar at the bottom shows `INTRO / US3 / US1 / US2 / EDGE / END` and the current scene. POV switches show a large banner (`IMPOSTOR VIEW`, `GHOST VIEW`, `CREWMATE VIEW`).

The stage is a fixed 1920x1080 scene, letterboxed and scaled to the window (checked at 1920x1080 and 1280x720).

## Scenes (~5:00)

Crew: **You = Mint**. Impostors = **Grape** and **Cobalt**. Others: Tomato, Tangerine, Mustard, Lime, Sky, Bubblegum, Cream. Several wear hats / visors / toppers (`art-jobs/out/M_cos_hats`, `N_cos_rest`).

| # | Scene | ~Time | Story / criteria shown |
|---|---|---|---|
| 0 | Title | 0:10 | Logo, "CLOCK IN" pulse. Overview of the three stories |
| 1 | Town and arcade | 0:25 | **US3** walk to the glowing pixel arcade; prompt "SHIFT IN PROGRESS" (edge: no join), then "3/10 crew clocked in" and CLOCK IN; players in town and in a match cannot see or hear each other; CRT power-on into the ship |
| 2 | Locker Room lobby | 0:30 | **US3** crew arrive 3/10 to 6/10, first is host (crown); non-host hovers Start: disabled "Only the host can start, needs 4+" (error); host leaves: crown passes on (edge); a player leaves back to town (edge); host presses the time clock, bulkhead door slides shut, beacon spins |
| 3 | Crew reveal | 0:20 | **US3** "SHHH...", CREWMATE screen: you centred and larger, the whole crew each in their own colour and cosmetics, "There are 2 Impostors among us"; each player receives only their own role |
| 4 | Impostor view | 0:15 | **US3** POV switch: IMPOSTOR screen with the Impostor team only, coral visors, smug half-lid visor |
| 5 | Completing tasks | 1:00 | **US1** task list with rooms, shared team bar (20%); station with no task: "No task here" (edge); keypad (1-10 in order, one wrong press shakes and resets); server confirms, team bar rises for everyone; wiring started then walk away: "Task reset: no credit" (edge); wiring completed (drag 4 plugs) |
| 6 | Impostor eliminates | 0:30 | **US3** IMPOSTOR VIEW: fake task list never moves the bar; Eliminate lights near a lone Tomato, fallen marker + cooldown ring; second click "On cooldown" (error); race: only one of two simultaneous strikes counts |
| 7 | Crew finds the body | 0:15 | **US2** Mint walks in, Report lights, BODY REPORTED splash |
| 8 | Meeting and voting | 1:00 | **US2** everyone teleports to the Galley, Meeting Tablet ("Mint reported Tomato", Tomato eliminated), discussion 0:15 (vote disabled), vote Grape: select, confirm, locked ("Vote locked" if changed), others show VOTED (who, not whom), timer expiry (non-voters count as no vote), tie: "No one was ejected"; emergency button slam (meetings left 1 to 0), EMERGENCY MEETING splash, second vote ejects Grape ("1 Impostor remains"); table disabled once your meetings are used (edge) |
| 9 | Ghost view | 0:15 | **US1/US2/US3** GHOST VIEW: desaturated world, ghost floats through a wall to finish a task, living view shows no ghost |
| 10 | Win | 0:20 | **US1/US2/US3** task bar 100% (or last Impostor ejected): CREW WINS, cheering lineup with every role revealed, "Returning to lobby..." back to the Locker Room. `I`: IMPOSTORS WIN |

Not shown (Medium or Low priority in the revised plan, or future work): vision fog, vents, sabotage, two-room tasks, completed-station map indicator, ghosts watching the vote, anonymous voting, ghost-only chat and voice, cosmetics wardrobe UI, security cameras.

Scope note: press `P` for the presenter notes. A criterion tagged **Medium** (for example `[US2 error Medium]`) is Medium priority in the revised plan: it is built in Sprints 4 and 5 only after the required work is merged. Untagged criteria are High priority.

## Code map

```
src/main.js              boot (preloads cosmetics, fonts), builds the Director
src/core/stage.js        fixed 1920x1080 stage, letterbox + scale, layers
src/core/context.js      shared ctx: play/wait/interactive helpers, splash, pov, flash, room/puppet factories
src/core/director.js     scene list, next/prev/jump/restart, chapter bar, presenter notes, autoplay
src/core/puppet.js       inline crew SVG: colour, cosmetics, side/front view, idle/walk/run/cheer/wave, ghost, fallen, blink, coral/smug visor, moveTo
src/core/room.js         painted room (webp) + manifest anchors + sorted actors/occluders
src/core/hud.js          task list, team bar, Use/Report/Eliminate (+ cooldown ring), meetings-left, toasts
src/core/captions.js     caption bar
src/core/taskpanel.js    keypad and wiring mini-games (job C panels)
src/core/meeting.js      Meeting Tablet (plates, timers, two-step vote, voter chips, banner)
src/core/ebutton.js      emergency button rig (job E parts)
src/core/station.js      task stations with idle / highlight / done layers (job K)
src/core/town.js         pixel town from the Tuxmon tileset + procedural pixel avatar
src/scenes/sNN_*.js      one module per scene: { id, title, chapter, story, criteria[], enter(ctx), steps[] }
tools/stage_assets.py    copies / converts art from art-jobs/out into public/assets
```

A step is `{ label, run(ctx) }`. All motion goes through `ctx.play(timeline)` / `ctx.wait()` / `ctx.interactive()`, which is what lets "next" finish a beat instantly and lets "back" replay a scene.

## Known issues

- Room paintings are the composited Gemini art (WebP); only the pieces that must move or sort (table, stations, door leaves, button, puppets) are SVG layers.
- `locker_door_open` has square doorway corners (known from the job G report); the bulkhead closes over it.
- The pixel avatar in the town is procedural; the real Covey.Town atlas is not in this repo.
- Seated meeting puppets stand at the stool anchors (no sitting pose).
