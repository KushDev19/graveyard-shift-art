# GRAVEYARD SHIFT: Art Direction Research

> **Team 11 · CS 490 · AU26** · Among Us-style social deduction game in Covey.Town
> Living research document for the art direction of our feature, written to guide (1) asset generation with Nano Banana Pro and (2) the Wizard-of-Oz prototype that comes after.
>
> **Status legend:** ✅ Decided · 📝 Draft proposal (not yet reviewed) · ❓ Open question

---

## Table of Contents

1. [Context: Where We Are](#1-context-where-we-are)
2. [Toolchain and Who Does What](#2-toolchain-and-who-does-what)
3. [Decision Log](#3-decision-log)
4. [Research: Current Covey.Town Art](#4-research-current-coveytown-art)
5. [Research: What Nano Banana Pro Is Good and Bad At](#5-research-what-nano-banana-pro-is-good-and-bad-at)
6. [Research: Engine Constraints (Phaser and Tiled)](#6-research-engine-constraints-phaser-and-tiled)
7. [Art Direction Bible](#7-art-direction-bible)
8. [The Ship: Nightjar Layout and Rooms](#8-the-ship-nightjar-layout-and-rooms)
9. [The Crew: Character Design and Puppet Rig](#9-the-crew-character-design-and-puppet-rig)
10. [Props, Task Stations and Task Mini-Games](#10-props-task-stations-and-task-mini-games)
11. [UI and Screens](#11-ui-and-screens)
12. [User Story to Screen/Asset Coverage](#12-user-story-to-screenasset-coverage)
13. [Asset Manifest (Tiered)](#13-asset-manifest-tiered)
14. [Production Pipeline](#14-production-pipeline)
15. [Prompting Playbook for Nano Banana Pro](#15-prompting-playbook-for-nano-banana-pro)
16. [Handoff: Wizard-of-Oz Prototype (Next Chat)](#16-handoff-wizard-of-oz-prototype-next-chat)
17. [Risks](#17-risks)
18. [Open Questions](#18-open-questions)

---

## 1. Context: Where We Are

### 1.1 The project

An in-world social deduction game for **4 to 10 players**, inspired by Among Us, inside Covey.Town. Players walk up to an **arcade machine** in the town, join a lobby, and get moved onto a **spaceship map** in their own Phaser scene. Crewmates complete tasks; Impostors eliminate crewmates; everyone meets and votes. Full research and architecture: [AMONG_US_ARCHITECTURE.md](AMONG_US_ARCHITECTURE.md). Final user stories: [USER_STORIES.md](USER_STORIES.md).

### 1.2 Course milestones (from the [project demos page](https://kelloggm.github.io/cs-490-website/projects/project-demos.html))

| Milestone | Due | Weight | What it needs |
|---|---|---|---|
| Deployment Demo | Oct 2, 2026 | — | ✅ Done |
| Preliminary Project Plan | Oct 7, 2026 | — | ✅ Submitted (plan files removed from repo; user stories kept in `USER_STORIES.md`) |
| **Wizard-of-Oz Demo** | **Fri Oct 16, 2026, 5:30pm EDT** | 25 pts, weight 2 | Finished project, **faked**. No working code needed. |
| Preliminary Demo 1 (mentor) | Fri Oct 30, 2026 | 20 pts, weight 2 | Real working code for ≥1 user story, code-reviewed |
| Preliminary Demo 2 (instructor) | Fri Nov 20, 2026 | 40 pts, weight 4 | ≥1 user story substantially complete, no crashes |
| Final Demo | see deliverables page | weight 10 | Full feature |

### 1.3 Wizard-of-Oz rubric (verbatim criteria)

**Satisfactory:**
- Demo materials are professional in appearance
- Demo is about five minutes long
- Demo showcases **all user stories** from the preliminary project plan (deviations permitted based on feedback)
- Demo incorporates all feedback received on the preliminary project plan
- Feature(s) demonstrated are **plausible to implement**

**Minimum:** 3 to 7 minutes, at least two user stories.

Key instruction from the course: *"convince the course staff that you've thought through how your feature will behave in enough detail to implement it."* Suggested tools: Figma, slideshows, animation tools, paper prototypes.

**Implication for art:** the art must look professional **and** be something we can really ship in Phaser. Everything below is chosen so the same assets carry straight from the Wizard-of-Oz prototype into the real implementation.

### 1.4 Goal of this session vs. the next one

| Session | Goal | Output |
|---|---|---|
| **This one (art)** | Research and lock the art direction, then generate and process the assets | This document, a locked style, generated and processed assets |
| **Next chat (build)** | Build a full, detailed, deployable Wizard-of-Oz version of the final game | An HTML prototype that looks and behaves as close to the final as possible |

---

## 2. Toolchain and Who Does What

✅ Decided.

| Tool | Role |
|---|---|
| **Nano Banana Pro** (Gemini image model) | Generates **all** image assets: key art, characters, rooms, props, UI art, task panels. 4K output available. |
| **Claude Opus 5.5** | "The brain": writes every Nano Banana prompt, lore, task copy, UI text, reviews generated images, and runs Python processing scripts (chroma key, cut, trim, resize, WebP export, sprite atlases). Replaces an image editor. |
| **Code (Phaser / CSS)** | **All animation**: walking, waddle, squash and stretch, ghost float, eliminations, ejections, screen transitions, lighting flicker, UI motion. |
| Audio | ❓ Out of scope for now; the team will sort it out later. |
| Video tools (Veo, etc.) | Not used. Animation is done in code. |
| Image editor (Photoshop, etc.) | Not used. Claude scripts handle processing. |

---

## 3. Decision Log

| # | Question | Decision | Why |
|---|---|---|---|
| D1 | Scope of new art | ✅ **Ship + arcade only.** The town stays Tuxemon pixel art. | Smallest scope. Entering the arcade feels like entering a different world, and our plan already uses a separate Phaser scene for the ship (task 1.C1). |
| D2 | Ship visual style | ✅ **Clean 2D cartoon**, with a well-thought-out theme and a **moody but good-vibes** feel | Nano Banana's strongest style; consistent across generations; tints cleanly for player colors; readable at a distance |
| D3 | Theme / setting | ✅ **Retro-future night shift**: a '70s retro-futurist cargo ship on the late shift | Cozy and nostalgic with a touch of mystery; fits the arcade-cabinet entry point |
| D4 | Crew look | ✅ **Funny-looking like Among Us crew, but not a copy**, matched to the retro-future vibe | Comedy from silhouette and motion; avoids IP lookalike problems |
| D5 | Character animation method | ✅ **Puppet parts + code**: separate body parts, assembled and animated in Phaser, side views only and mirrored | AI frames drift; parts never drift; per-part tinting; comedy is easy to tune in code |
| D6 | Map build method | ✅ **Painted rooms + prop sprites**: one 4K painted image per room; anything interactive or stateful is a separate sprite; light overlay on top; Tiled supplies collisions and object points | Plays to Nano Banana's strengths; fixing one room never touches another; plausible in Phaser |
| D7 | Production order | ✅ **Style lock first** (3 anchor images), then Tier 1 demo-critical assets, then Tier 2 final-game assets, then Tier 3 cosmetics if time allows | Keeps 60+ assets cohesive; makes sure the demo is never blocked |
| D8 | Art direction bible (§7) | ✅ Approved: palette, lighting, shape language, fonts | — |
| D9 | Names | ✅ Arcade game **GRAVEYARD SHIFT**, ship **Nightjar** | "Night shift, but people keep disappearing." Darkly funny, not gory. |
| D10 | Browser visual companion | Declined (save tokens); all discussion stays in chat | — |
| D11 | Room list and layout (§8) | ✅ Approved as drafted | — |
| D12 | Crew colors | ✅ **10 colors, no more.** The lobby is capped at 10 players. | One color per player |
| D13 | **Batch sheets** | ✅ Small assets are generated **many per image** on a flat chroma background in a fixed grid; Claude crops, keys out the background, trims, names, and packs them | Cuts the number of generations by about 3x; one sheet also keeps every item in it stylistically identical (§14.5) |
| D14 | **Character customization** | ✅ **Stretch goal (Tier 3).** Cosmetic layers (hats, antenna toppers, backpacks, visor styles, suit decals) on top of the same puppet rig; purely visual (§9.4) | Adds personality and replay value; costs only a few batch sheets because the rig already supports layers |
| D15 | Fallen-crew marker | ✅ Dedicated generated art, included in the props batch (code deformation is the fallback) | Better-looking and a faster build |
| D16 | Raw 4K storage | ✅ Local `art/` folder, **not in git** (shared drive for the team if needed) | Repo stays small |

---

## 4. Research: Current Covey.Town Art

What exists in `frontend/public/assets/` today:

| Asset | Details | Fate |
|---|---|---|
| `tilesets/tuxmon-sample-32px-extruded.png` | Tuxemon/Pokémon-style 32px pixel tiles (grass, buildings, fences, fountain) | **Kept**. The town stays as it is (D1). |
| `atlas/atlas.png` + `atlas.json` | "misa" character atlas (blonde girl with headphones, 4-direction walk). Physics body 30×40. | Kept for the town. Replaced inside the ship by the crew puppet. |
| `tilesets/Room_Builder_32x32.png`, `1_Generic`, `5_Classroom_and_library`, `12_Kitchen`, `13_Conference_Hall`, `14_Basement`, `16_Grocery_store`, `22_Museum` (32×32) | LimeZu Modern Interiors-style pixel interiors used by `indoors.json` | Kept for the town. |
| `tilemaps/indoors.json` | 120×45 tiles at 32px; hardcoded map loaded by both server and client | The town map. The arcade cabinet object is added here. |
| `roguelike*_transparent.png`, `super-mario-*`, `catastrophi_*` | Starter leftovers | Unused by us. |

**Important consequence:** the **arcade cabinet itself sits in the pixel town**, so its in-world sprite must be **32px-grid pixel art matching Tuxemon** (about 32×64 or 64×64). Only its join prompt (a React modal) and everything after it uses the new cartoon style. That one asset needs pixel-art handling (see §5.3).

---

## 5. Research: What Nano Banana Pro Is Good and Bad At

> Capabilities as we understand them at time of writing; verify in your Gemini UI.

### 5.1 Strengths we use

- **High resolution:** up to 4K output, so room paintings and key art stay crisp.
- **Multiple reference images per prompt:** the basis of our style lock. Every prompt attaches the anchor images.
- **Aspect ratio control** (1:1, 16:9, 21:9, 9:16, 4:3, and others): pick per room shape.
- **Good with text in images:** usable for signage on walls ("GALLEY", "REACTOR"), but **we keep all gameplay text in code** so it can change and be translated.
- **Clean, flat cartoon styles** stay consistent across many generations.
- **Editing by conversation:** "same image, make the lamp warmer" works well for iterating on one asset.

### 5.2 Weaknesses and how we handle each

| Weakness | Mitigation |
|---|---|
| **No real transparency.** Asking for "transparent background" often produces a *fake checkerboard* painted into the image. | Never ask for transparency. Generate on a **flat chroma background** (§14.3) and key it out with a script. |
| **Frame-to-frame drift** (sizes, line weight, details change between generations) | Puppet rig (D5): each part is generated **once**. |
| **Fake pixel art** (blurry, off-grid pixels) | Only the arcade cabinet is pixel art. Process it: downscale to the true grid with nearest-neighbour, then reduce it to a fixed palette. |
| **Tiles rarely line up seamlessly** | No tilesets for the ship (D6). Rooms are whole paintings; hallways are separate painted strips with matching edge colors. |
| **Perspective inconsistency** between generations | Every room prompt states the same camera: *"top-down 3/4 view, camera tilted ~35°, orthographic, no vanishing points."* The room anchor image is always attached. |
| **Props baked into rooms can't change state** | Room prompts say "empty console alcove" or "empty floor spot" where interactive props go; props are generated separately. |
| **Small text is garbled** | No small text in art. UI text is rendered by code. |
| **Watermarks:** generated images carry an invisible SynthID watermark; some tiers add a visible mark | Invisible: harmless. Visible: crop or regenerate. Check corners of every export. |

### 5.3 Pixel-art cleanup (arcade cabinet only)

1. Generate at large size with the prompt "pixel art, 32-pixel grid, limited palette, Tuxemon / Pokémon GBA style", with a screenshot of the town attached as a reference.
2. Script: detect the effective pixel size, downscale with nearest-neighbour to the true resolution (for example 32×64), quantize to the Tuxemon palette sampled from `tuxmon-sample-32px.png`, and key out the background.
3. Place it in Tiled on the town map.

---

## 6. Research: Engine Constraints (Phaser and Tiled)

### 6.1 Facts from the codebase

- The town is a Phaser scene (`TownGameScene.ts`) driven by a Tiled JSON map; tiles are 32px.
- Interactable areas come from Tiled object layers; `GameAreaFactory` picks the class from the object's `type`.
- Player colors are planned as `sprite.setTint(color)`. **Tint multiplies**, so tintable art must be **light grey or white with flat shading**; dark or saturated art tints badly.
- The ship is its own Phaser scene (plan task 1.C1), so it can use its **own world scale** without affecting the town.

### 6.2 Texture limits

- WebGL maximum texture size is often 4096px on integrated or older GPUs (8192 or more on most modern ones). **Rule: no single texture over 4096px on its longest side.** 3840×2160 (4K 16:9) is safe.
- Rooms bigger than one 4K image are split into two images placed side by side.
- Ship web exports use **WebP** (quality ~85), which is much smaller than PNG for paintings. Character and prop sprites go into a texture atlas.

### 6.3 Proposed ship world scale 📝

| Thing | Value |
|---|---|
| World unit | 1 world px = 1 px of the room painting |
| Standard room painting | 3840×2160 (16:9). Large rooms: 21:9 or two images. |
| Camera zoom at 1080p | 0.5, so a standard room is about 1 screen wide (Among Us-like framing). Zoom scales with window height. |
| Crew character height | **256 world px** (about 128 px on screen at 1080p, roughly 1/8 of screen height) |
| Tiled grid for the ship | 64 world px (collision drawn as polygons, so rooms don't need to align to the grid) |
| Character physics body | Roughly the feet ellipse, about 120×60 world px |
| Gameplay distances | The architecture doc's distances (kill range 72px etc.) were at Covey scale. **Rescale ×4** for the ship world (for example, kill range about 288 world px). |

### 6.4 How painted rooms map to Tiled 📝

Ship map `nightjar.tmx` / `nightjar.json`:

| Layer | Type | Contents |
|---|---|---|
| `Rooms` | Image layers (one per room/hallway) | Room paintings, positioned in world space |
| `Collision` | Object layer (polygons) | Walls and furniture footprints |
| `Objects` | Object layer (points/rects) | Task stations, vents, emergency table, doors, meeting seats, spawn seats, room bounds (for "which room am I in") |
| `Props` | Object layer | Placement of prop sprites (with depth-sort Y) |
| `Lights` | Object layer | Light positions, color, and radius for the lighting overlay |

Object names follow the existing architecture doc (§14 there): `TaskStation`, `Vent`, `EmergencyButton`, `MeetingSeat`, `SpawnSeat`, `Door`, `Room`.

---

## 7. Art Direction Bible

✅ Approved (D8).

### 7.1 Names

- **Arcade game:** GRAVEYARD SHIFT
- **Ship:** the **Nightjar**, a '70s retro-future cargo hauler (a nightjar is a nocturnal bird, so it fits the night-shift idea).
- **Tagline idea:** *"Clock in. Trust no one. Clock out (if you can)."*

### 7.2 Mood

It's 3 a.m. on a cozy '70s retro-future freighter: warm lamps, humming CRTs, a nebula sunset through the windows. **Calm and inviting, with something slightly off.** Funny, not scary. Eliminations are slapstick, not gore.

**Mood words:** cozy · nostalgic · late-night · lo-fi · warm-on-cool · playful suspicion
**Not:** horror, grimy, gory, neon-cyberpunk, sterile white sci-fi, pixel art (inside the ship)

**Reference touchstones (for feel, never copied):** '70s NASA/retro-futurist interiors and Syd Mead-era soft industrial design, cozy lo-fi "night" illustrations, Among Us (readability, character comedy), Cult of the Lamb / Night in the Woods (cute-but-dark tone), Outer Wilds (warm campfire-in-space feeling).

### 7.3 Palette

| Role | Name | Hex |
|---|---|---|
| Deep shadow / space | Midnight indigo | `#1B1830` |
| Shadow tint | Plum | `#3D2A4F` |
| **Outline** (never pure black) | Dark plum | `#2A1E35` |
| Metal / walls | Teal steel | `#2F6F73` |
| Highlights / screens | Seafoam | `#7FC8B8` |
| **Primary accent**, lamp light | Amber | `#F5A54A` |
| Panels, paper, UI text | Cream | `#F4E6C8` |
| Danger, emergency, Impostor | Coral | `#E8574A` |
| Sky accent | Nebula pink | `#D9738C` |

**Ratio guide:** about 60% cool darks (indigo, plum, teal), 30% mid tones (teal steel, seafoam, cream), 10% hot accents (amber, coral, pink). Coral is reserved for **danger and Impostor meaning**; don't use it as decoration.

### 7.4 Lighting rules

- **Ambient light:** cool teal-indigo.
- **Light sources:** warm amber pools around lamps, consoles, and doorways.
- **Signature glow per room** (players tell rooms apart at a glance): see §8.2.
- **Windows:** nebula sunset (pink, violet, amber) with stars.
- Lighting is painted softly into the rooms; **dynamic light** (flicker, the lights-out sabotage, glows that react to the player) comes from a code overlay layer.

### 7.5 Shape language and rendering

- **Rounded rectangles everywhere**: chunky bevels, pill-shaped buttons, rounded window frames.
- **Signature motif:** the **'70s triple racing stripe** (cream, amber, coral) running along walls, on the arcade cabinet, the crew suits, and UI headers.
- **Outlines:** uniform dark plum `#2A1E35`, medium weight, slightly thicker on silhouettes.
- **Shading:** flat 2-tone cel shading plus soft glows. No texture noise, no photo-real materials, no heavy gradients.
- **Detail density:** low on floors (gameplay space has to read clearly), medium on walls, high only on hero props.

### 7.6 Crew colors (10)

Tomato · Tangerine · Mustard · Lime · Mint · Sky · Cobalt · Grape · Bubblegum · Cream
All read clearly against teal and indigo. Exact hex values are set when the character anchor is locked (they're tint multipliers over a light-grey base, so they'll be tuned by eye in-engine). ❓ Possibly add an 11th or 12th later.

### 7.7 UI style

- **CRT terminal panels:** dark indigo screens, amber and cream text, rounded bezels in teal steel or cream plastic, faint scanlines, a slight screen glow.
- **Buttons:** chunky pill shapes with a bottom bevel ("press-able"), with the racing stripe on primary actions.
- **Fonts (Google Fonts):** **Bungee** for headings and signage, **Space Grotesk** for body and UI text, **VT323** for terminal readouts, timers, and the task list.
- **Icons:** thick rounded line icons in cream, matching the outline weight.

---

## 8. The Ship: Nightjar Layout and Rooms

✅ Approved (D11). Rooms are re-themed from The Skeld into our own setting. About 8 rooms plus the lobby, matching plan task 2.C1.

### 8.1 Schematic

```
                 ┌──────────────┐        ┌───────────────────┐        ┌──────────┐
                 │ HYDROPONICS  │════════│      GALLEY       │════════│  BRIDGE  │
                 │ (grow-green) │        │ (meeting table,   │        │ (nebula  │
                 └──────┬───────┘        │  big red button)  │        │ windshield)
                        ║                └─────────┬─────────┘        └────┬─────┘
   ┌────────────┐  ┌────┴──────┐                   ║                       ║
   │  REACTOR   │══│ SICK BAY  │             ┌─────┴──────┐          ┌─────┴──────┐
   │  (coral)   │  │ (seafoam) │             │ RADIO ROOM │══════════│ CARGO HOLD │
   └─────┬──────┘  └───────────┘             │  (amber)   │          │  (dim)     │
         ║                                   └─────┬──────┘          └────────────┘
   ┌─────┴───────────┐                             ║
   │  SWITCHBOARD    │═════════════════════════════╝
   │ (electric blue) │
   └─────────────────┘
        ┌───────────────────────┐
        │  LOCKER ROOM (lobby)  │  ← spawn from arcade; door seals when the shift starts
        └───────────────────────┘
```

### 8.2 Rooms

| Room | Skeld equivalent | Signature glow | Look | Gameplay |
|---|---|---|---|---|
| **Locker Room** (lobby) | Dropship | Warm amber | Lockers with name tags, bench, a "TIME CLOCK" punch-card machine (the host's Start console), coffee machine, shift-schedule board | Lobby, 3/10 count, host starts |
| **Galley** | Cafeteria | Amber + coral button | Long diner-style table with a **big coral button under a glass dome**, vending machine, retro fridge, round porthole windows | Meeting seats, emergency button, spawn after meetings |
| **Bridge** | Navigation | Seafoam + nebula | Wide windshield with the nebula sunset, captain's swivel chair, chunky console banks | Chart Course, Download Data |
| **Reactor** ("the Furnace") | Reactor | **Coral** | Glowing core behind a grille, pipes, pressure gauges | **Unlock Manifolds keypad** (essential task) |
| **Switchboard** | Electrical | Electric blue | Wall of retro telephone-style patch panels, fuse boxes, cable spaghetti | **Fix Wiring / patch cables** (essential task); lights fix (extension) |
| **Sick Bay** | MedBay | Seafoam | Retro med pod, curtain, tiny plant | Submit Scan (extension, visual task) |
| **Radio Room** | Comms | Amber | Reel-to-reel tape decks, big radio dish window, cassette shelves | **Upload Data** half of the two-room task (desirable); comms fix (extension) |
| **Hydroponics** | (new) | Grow-light green | Hanging planters, mist, a watering can, a cozy hammock | Download Data, Water Plants (extension) |
| **Cargo Hold** | Storage | Dim, with hazard stripes | Crates, forklift, cargo net, loading door | Fuel task (extension); good hiding/kill spot |
| Hallways | — | Ambient teal | Painted strips with racing stripes and floor lights | Movement; vent locations |

### 8.3 Vents 📝

Retro floor grates with a small "louvered" lid that pops open (prop sprite with states). Two networks (desirable feature):
- **West:** Reactor ↔ Switchboard ↔ Sick Bay
- **East:** Galley ↔ Bridge ↔ Cargo Hold

---

## 9. The Crew: Character Design and Puppet Rig

✅ Direction decided (D4, D5).

> **Source of truth:** [CHARACTERS.md](CHARACTERS.md) is the final character spec and prompt book (handed off to the teammate generating characters). Where it differs from this section, **CHARACTERS.md wins**. Notable updates there: the helmet dome has a solid dark indigo interior (no see-through glass on chroma), the "grey = tintable" rule (the slicer splits tintable and untinted pixels by saturation, so poses can be tinted too), the 16-part SH-CREW sheet with visor expressions (blink, surprised, coral, ghost), and the fallen marker split into suit + helmet.

### 9.1 Design

- **Silhouette:** short, **squat, round-bottomed** suit (a gumdrop or thermos shape, clearly not the Among Us bean), **stubby legs**, about 2 heads tall.
- **Helmet:** **oversized fishbowl dome** with an **amber visor glow** (the face is just the visor; no facial features, which keeps it funny and anonymous).
- **Back:** tiny boxy '70s backpack with a racing stripe.
- **Top:** a **bobbly antenna** with a little ball on the end that wobbles when walking (a cheap comedy win in code).
- **Suit:** light grey base with flat shading so player colors **tint** it (§6.1). Visor, outline, and stripe are separate non-tinted parts.
- **Comedy comes from motion:** waddle, squash and stretch, antenna wobble, overshoot when stopping.

### 9.2 Puppet parts (generated once, side view)

| Part | Tinted? | Notes |
|---|---|---|
| `body` | ✅ player color | Torso and lower suit, light grey |
| `body_shade` | ✅ (darker multiply) | Optional shade overlay for depth |
| `helmet_glass` | ❌ | Semi-transparent dome. The glass highlight is a separate layer for alpha. |
| `visor` | ❌ (amber; coral for Impostor-only views) | The "face" |
| `leg_front`, `leg_back` | ✅ | Pivots at the hip |
| `arm_front`, `arm_back` | ✅ | Tiny stubby mitten arms, pivot at the shoulder. Swing on walk; used for wave, point ("sus!"), and cheer poses |
| `backpack` | ✅ slightly darker | With racing stripe |
| `antenna` | ❌ | Pivot at base; ball wobbles |
| `stripe` | ❌ | Cream, amber, and coral stripe decal on the suit |
| `shadow` | ❌ | Soft ellipse under the feet (can be drawn in code) |

### 9.3 States (all animated in code from the same parts)

| State | How it looks |
|---|---|
| Idle | Slow breathing scale bob, antenna sway |
| Walk | Waddle: body rocks ±6°, legs alternate, antenna lags behind |
| Eliminated ("fallen" marker) | **Slapstick and PG:** the suit deflates flat with the helmet rolled off to the side and little stars or Zs. ❓ Needs a dedicated generated asset or a code deformation; decide when testing. |
| Ghost | Same parts, 50% alpha, legs replaced by a wispy tail (one extra part, `ghost_tail`), floating bob, slight halo |
| Ejected | Tumbles through the airlock into the nebula (code rotation along a path) |
| Role reveal pose | Front-facing hero pose (one extra **front-view** generation for the reveal and win screens only) |

### 9.4 Character customization (Tier 3 stretch) ✅

Cosmetics are **extra layers on the same puppet rig**. They are purely visual, chosen in the Locker Room lobby, and never affect gameplay.

| Slot | Attaches to | Examples (retro night-shift themed) | Tinted? |
|---|---|---|---|
| `hat` | Top of the helmet dome | Trucker cap, paper diner hat, hard hat, beanie, cowboy hat, chef toque, sleep cap with pom, tiny party hat, headphones, flower crown, '70s afro wig, propeller beanie | ❌ (own colors) |
| `antenna_topper` | Antenna ball | Star, heart, tiny moon, cherry, lightbulb, eyeball, satellite dish | ❌ |
| `backpack` | Back | Default box, jetpack, thermos, lunchbox, cassette player, mini plant pot | ✅ or ❌ per item |
| `visor` | Helmet front | Default amber, aviator shades, heart visor, sleepy half-lid, star visor | ❌ |
| `decal` | Suit front | Racing stripe (default), name patch, lightning bolt, smiley, flames, "NIGHT CREW" badge | ❌ |

**Rules:**
- Every cosmetic is generated **side view, facing right**, at the same scale as the crew parts sheet (the crew sheet is attached as a reference so sizes match).
- Each cosmetic gets an **anchor offset** in `cosmetics.json` (x/y relative to its slot pivot), tuned once by eye in-engine.
- Cosmetics must stay readable as decoration and **never cover the visor** (players need to read the "face").
- Ghosts keep their hat (funny), at ghost alpha.

---

## 10. Props, Task Stations and Task Mini-Games

📝 Draft.

### 10.1 Stateful prop sprites (separate from room paintings)

| Prop | States | Notes |
|---|---|---|
| Task console (generic, plus room variants) | idle · highlighted (player is near and has a task) · done (green check glow) | The "done" state covers the desirable "visual indicator" criterion |
| Emergency button under glass dome | idle · pressed · disabled (used up or sabotage) | Hero prop in the Galley |
| Vent grate | closed · open | Pop animation in code |
| Doors | open · closed | Extension (door sabotage) |
| Time clock (lobby start console) | idle · ready (≥4 players) | Host only |
| Fallen crew marker | — | See §9.3 |
| Med pod scanner | idle · scanning | Extension |

### 10.2 Task mini-games (full-screen panel art, retro themed)

| Task (our name) | Mechanic | Story priority | Panel art |
|---|---|---|---|
| **Reactor Override** (Unlock Manifolds) | Press keys 1–10 in order on a shuffled chunky keypad | **Essential** | Big cream keypad, amber LED numerals, coral "pressure" gauge |
| **Patch the Switchboard** (Fix Wiring) | Drag 4 colored patch cables to matching jacks (old telephone-switchboard style) | **Essential** | Wood-and-metal panel, coiled cables, brass jacks |
| **Tape Transfer** (Download → Upload) | Download in Bridge/Hydroponics (reel-to-reel spin progress), upload in Radio Room | Desirable (two-room task) | Reel-to-reel deck, VU meters |
| Align Thrusters | Slider alignment | Extension | — |
| Calibrate Gyro | Timing | Extension | — |
| Pattern Memory (Start Reactor) | Simon-says lights | Extension | — |

Panel art is generated as **static backgrounds plus separate moving parts** (keys, cable ends, reels, needles). Interaction and animation are code.

---

## 11. UI and Screens

📝 Draft. The full screen list the prototype (and the final game) needs.

| # | Screen / UI | Style notes |
|---|---|---|
| S1 | **Arcade cabinet in town** (pixel sprite) + **join prompt modal** ("GRAVEYARD SHIFT · 3/10 crew clocked in · [Clock in]") | Cabinet is Tuxemon pixel; the modal is CRT style |
| S2 | Cabinet "full" / "shift in progress" prompt states | Coral warning text |
| S3 | Transition: town to ship (CRT power-on / tube-zoom effect) | Code effect |
| S4 | **Locker Room lobby HUD**: crew list with host badge, 3/10 count, host-only "Start Shift" (disabled under 4), Leave button | — |
| S5 | **Role reveal**: "SHHH…" then **CREWMATE** (cream/amber) or **IMPOSTOR** (coral). Lineup of the actual players built from the SVG puppet (front view) with each player's color and cosmetics: local player centered and larger; crewmate screen shows everyone, impostor screen shows only the impostor team (coral visors, smug half-lid visor) | Puppet front view on the reveal stage background (28/29) |
| S6 | **In-game HUD**: task list with room names (VT323), team task bar, action buttons (Use, Report, Eliminate with cooldown ring, Vent), meetings-left counter | — |
| S7 | Toasts: "No task here", cooldown, "Can't do that during a meeting" | — |
| S8 | **Meeting called splash**: "EMERGENCY MEETING" vs "BODY REPORTED" | Big Bungee type, coral |
| S9 | **Meeting / voting panel**: crew tiles (alive/eliminated, "caller" badge, "I voted" stamp), Skip, discussion and voting timers, chat | CRT panel |
| S10 | Vote reveal + **ejection** cutscene ("Mint was not the Impostor. 1 Impostor remains.") | Nebula airlock background |
| S11 | Ghost view: desaturated world, ghost-only chat tint | Code filter |
| S12 | **Win/lose screens**: CREW CLOCKS OUT SAFE (crew victory) / THE NIGHT SHIFT CLAIMS ANOTHER CREW (Impostor victory), with all roles revealed | Key art style |
| S13 | Task panels (see §10.2) | — |
| S14 | Viewing-radius vignette (desirable) | Code mask |

### 11.1 Meeting screen spec ✅

**Background = the live game, no new art.** When a meeting starts, every living player is moved to a Galley meeting seat (US2), so the real scene already shows everyone **seated around the table as their own puppet, with color and cosmetics**. During the meeting that scene stays visible behind the UI, **dimmed (about 55%) and slightly blurred**. Ghosts float near the walls at ghost opacity (only ghosts can see them).

**Foreground = the "Meeting Tablet"**, a chunky CRT panel in our style (cream bezel, dark indigo screen) that slides up from the bottom:

| Zone | Contents |
|---|---|
| Header | "WHO'S THE IMPOSTOR?" (Bungee) + a caller line: "📣 Mint called an emergency meeting" or "📣 Mint reported Tomato" |
| Player grid | 10 **vote plates** in 2 columns × 5 rows. Each plate shows a **portrait** (front-view puppet, head and shoulders, **with cosmetics**), the name, and the status |
| Plate states | **alive** (normal) · **you** (amber outline) · **selected** (glowing bezel + ✓ confirm / ✗ cancel buttons on the plate) · **voted** ("VOTED" stamp: shows *that* they voted, never *for whom*) · **caller** (megaphone badge) · **eliminated** (plate dimmed, portrait greyed with X tape over the visor; not clickable) · **disconnected** (greyed, "left") |
| Bottom-left | **SKIP** button (same ✓ / ✗ confirm) |
| Bottom-right | Timer dial: "DISCUSS 0:15" (vote buttons disabled) then "VOTING 2:00" |
| Top-right | Chat button with an unread dot; chat drawer slides in. Ghost messages are seafoam-tinted and only ghosts see them |
| Results | When everyone has voted or time runs out: small **voter chips** (mini helmets in the voter's color) stack under each plate, skip votes stack beside SKIP, then **ejection** (puppet tumbles across 32) or "No one was ejected (tie / skip)" |
| Ghost view | Same tablet, plates not clickable, banner: "Ghosts can't vote" |

UI assets needed (my SVG list, 20–22): tablet frame, plate (normal/selected/you/dead), ✓ and ✗ round buttons, VOTED stamp, megaphone badge, X-tape eliminated badge, SKIP button, timer dial, chat button + drawer, voter chip. Portraits come from the puppet (front view crop).

### 11.2 Lessons from Among Us's interface (what to copy, what to avoid) ✅

**Copy the conventions (players already know them):**
1. Vote secrecy: show only **who has voted** until the reveal; then show voter icons under each plate (with an "anonymous votes" option graying them out).
2. **Two-step voting** (select → ✓ confirm, ✗ cancel); once confirmed it's locked.
3. Discussion phase first with the vote buttons disabled, a timer always visible, and SKIP as a first-class option.
4. Dead players stay listed but are clearly marked, can't be voted for, and can't vote.
5. The caller/reporter is marked with a megaphone.
6. Portraits show **color + hat/visor**, and names are always shown. Never rely on color alone (color-blind players; tomato vs coral).
7. Role intro: "Shhh!" → role title → lineup with the **local player in front/center** and others fanned behind; the Impostor screen shows only the Impostor team; the Crewmate screen shows everyone plus "There is 1 Impostor among us".
8. HUD: actions in the **bottom-right** (Use, Report; Impostors also get Eliminate/Sabotage/Vent above them), the task list + team task bar **top-left**, settings/map/chat **top-right**. Context buttons light up only when usable (near a station, body, vent or target) and show cooldown rings.
9. Recoloring: Among Us recolors players with a **channel mask** (main color, shadow color, visor). Our grey-base + shade/back/light variables do the same thing, and are why every cosmetic must avoid neutral grey unless it's meant to take the player color.
10. Wraparound cosmetics (headphones, flower crown) need a **back layer** (drawn behind the dome) and a **front layer**, or they look pasted on.

**Avoid (mistakes / IP):**
- Don't copy Among Us's exact UI art (its tablet look, fonts, "Who Is The Impostor?" plate styling, bean shapes). Same *conventions*, our *style*: CRT/retro panels, Bungee/Space Grotesk/VT323, cream-amber-coral palette.
- Don't put story text inside images. All UI text is live text, so it can change and be translated.
- Don't leak information: no vote targets before the reveal, no roles in any data sent to non-Impostors, and no ghost visibility for the living.
- Don't make plates rely on color alone or tiny text; the plates must work at 1280×720.

### 11.3 Vision and fog ✅ (US3 desirable; walls and lights-out are extensions)

**Rules (ship world scale, crew height 256 world px):**

| Who / when | Vision radius | Notes |
|---|---|---|
| Crewmate | **640 px** (2.5 crew heights) | Default |
| Impostor | **960 px** (1.5x crew) | Sees farther; this is part of the role's advantage |
| Lights sabotage (extension) | Crew **160 px**; Impostor unchanged | Everyone gets a coral alarm pulse; fixed at the Switchboard |
| Ghost | **Unlimited** | World slightly desaturated (about 60%); ghosts are invisible to the living |
| Meeting / voting | No fog | The scene is dimmed behind the Meeting Tablet instead |

**Fairness and anti-cheat:** visibility is decided on the **server** (VisibilityPolicy): the server only sends positions of players inside the sender's radius (plus a small margin), so a modified client can't "wall-hack". The fog on screen is purely visual.

**Rendering (all code, no generated art):**
1. A full-screen overlay in midnight indigo `#1B1830` at about 92% opacity, with a soft-edged circular hole centered on the local player: fully clear out to 70% of the radius, then fading to opaque at 100%. In Phaser: a RenderTexture that is refilled each frame and has a pre-rendered radial-gradient sprite ERASEd out of it at the player's position (cheap, and the soft edge is baked into the sprite).
2. Players and props outside the radius simply aren't drawn (server filter), so nothing pops in at the edge: the fade hides the entry.
3. **Never a hard-edged circle** (it reads as a flashlight cutout); never fog over the HUD, minimap or meeting UI.
4. **Walls block line of sight (extension):** compute a visibility polygon each frame by raycasting from the player against the Tiled `Collision` polygons, then use that polygon (intersected with the circle) as the hole. Rooms seen through a doorway show as a wedge.
5. **Lights out (extension):** the same hole shrinks to 160 px with a slow flicker; the overlay goes to 97%, and a coral vignette pulses at the screen edges.
6. Must stay readable by brightness alone (color-blind safe) and at 1280x720.

**Assets I produce:** `fog_soft.png` (radial gradient hole sprite, 1024 px), `vignette_coral.png`, and the ghost desaturation filter. For the Wizard-of-Oz prototype: the vision circle follows the player; other players fade out as they leave it; the presenter hotkey triggers lights-out.

---

## 12. User Story to Screen/Asset Coverage

Checks that the Wizard-of-Oz demo can show **every** story (rubric requirement). Full criteria: [USER_STORIES.md](USER_STORIES.md).

| Story | Key criteria | Screens / assets |
|---|---|---|
| **US1 Completing tasks** | Task list with rooms; station opens task UI; "no task here" message; server-confirmed completion updates the team bar; abandoning resets; Impostor fake tasks; ghosts do tasks; keypad + wiring mini-games; 100% → crew wins. *Desirable:* done indicator, two-room task. | S6, S7, S13 (Reactor Override, Patch the Switchboard, Tape Transfer), console props with **done** state, S11, S12 |
| **US2 Meetings and voting** | Trigger by button or report; meetings-left limit; freeze, clear bodies, gather in Galley; meeting audio for everyone; participant panel with status and caller; one vote or skip; timer expiry; plurality ejection; tie/skip → no ejection; disconnect handling; ghosts can't vote and have ghost-only chat; last Impostor ejected → crew wins. *Desirable:* ghosts watch. | Emergency button prop, fallen marker, S8, S9, S10, S11, S12, Galley room and meeting seats |
| **US3 Join and secret role** | Arcade prompt with count; lobby 4–10, host, host migration; leave; full / in-progress states; host-only start at ≥4; private role reveal with Impostor partners; real-time movement; town and ship separated; Eliminate with range and cooldown; ghosts hidden from the living; no Impostor-on-Impostor kills; parity → Impostors win; disconnects. *Desirable:* viewing radius, vents. | S1–S5, S6 (Eliminate button + cooldown), fallen marker, ghost rig, vent props, S12, S14 |

---

## 13. Asset Manifest (Tiered)

📝 Draft. **Tier 0** locks the style. **Tier 1** is everything the Wizard-of-Oz demo shows. **Tier 2** completes the final game.

### Tier 0: Style anchors (generate first, iterate until right)

| ID | Asset | Format |
|---|---|---|
| A0.1 | **Key art**: crew in the Galley at night, nebula window, big button, one shifty crewmate | 16:9, 4K |
| A0.2 | **Character sheet**: crew side view + front view, several colors, on a flat chroma background | 16:9, 4K |
| A0.3 | **Room anchor**: the Galley, top-down 3/4, no characters | 16:9, 4K |

### Tier 1: Wizard-of-Oz demo critical

| ID | Asset | Format |
|---|---|---|
| T1.1 | Crew puppet parts (side view), one sheet on chroma, cut by script | 1:1, 4K |
| T1.2 | Crew front-view hero pose (reveal / win screens) | 1:1, 4K |
| T1.3 | Ghost tail part + fallen-crew marker | 1:1, 4K |
| T1.4 | Rooms: Locker Room, Galley, Reactor, Switchboard, Radio Room, Bridge | 16:9, 4K each |
| T1.5 | Hallway strips (horizontal + vertical) | 21:9 / 9:16 |
| T1.6 | Props: task console (3 states), emergency button (3 states), vent (2 states), time clock | 1:1 sheets on chroma |
| T1.7 | Task panels: Reactor Override keypad, Patch the Switchboard, Tape Transfer | 16:9 backgrounds + parts sheet |
| T1.8 | Ejection background (airlock + nebula) | 21:9 |
| T1.9 | Role reveal backgrounds (Crewmate / Impostor) | 16:9 |
| T1.10 | Win / lose backgrounds | 16:9 |
| T1.11 | Arcade cabinet: pixel sprite for the town + high-res cartoon version for the modal | pixel 32×64 (via cleanup) + 1:1 |
| T1.12 | GRAVEYARD SHIFT logo (wordmark) | 16:9 on chroma |
| T1.13 | UI kit: CRT panel frame, pill buttons, icons (Use, Report, Eliminate, Vent, Chat, Settings), "I voted" stamp, host badge | 1:1 sheets on chroma |

### Tier 2: Final game completion

| ID | Asset |
|---|---|
| T2.1 | Rooms: Sick Bay, Hydroponics, Cargo Hold |
| T2.2 | Door props (open/closed); med pod scanner (idle/scanning) |
| T2.3 | Extension task panels: Align Thrusters, Calibrate Gyro, Pattern Memory |
| T2.4 | Sabotage UI: lights-out, alarm overlays |
| T2.5 | Security camera console + camera feed frames |
| T2.6 | Minimap art (stylized ship blueprint) |
| T2.7 | Loading screen / arcade attract-mode art |

### Tier 3: Cosmetics (stretch, only if time allows)

| ID | Asset |
|---|---|
| T3.1 | Hats sheet (12) |
| T3.2 | Antenna toppers + visors sheet (12) |
| T3.3 | Backpacks + suit decals sheet (12) |
| T3.4 | Lobby wardrobe UI (locker mirror panel, slot tabs) |

**Rough count (with batch sheets, §14.5):** Tier 0 = 3 images · Tier 1 ≈ 22 generations · Tier 2 ≈ 10 · Tier 3 = 4. Iterations probably double that. Fits in a day.

---

## 14. Production Pipeline

📝 Draft.

### 14.1 Loop per asset

1. Claude writes the prompt (style block + asset block + constraints, §15) and lists which anchor images to attach.
2. You generate in Nano Banana Pro (usually 2–4 variants) and save the raw output into `art/raw/<id>/`.
3. Claude reviews it (style match, palette, perspective, artifacts) and either approves it or writes a corrective follow-up prompt.
4. Claude runs scripts: chroma key + despill, trim, part cut-out, resize, WebP/PNG export, atlas packing.
5. Approved exports go to `art/export/` and then into the game folder.

### 14.2 Folders and naming 📝

```
art/                         ← NOT in git (4K raws are 5–15 MB each)
  anchors/                   ← locked Tier 0 anchors (attach to every prompt)
  raw/<asset-id>/            ← untouched Nano Banana outputs, v1, v2, ...
  work/                      ← script intermediates
  prompts/<asset-id>.md      ← the exact prompt used (reproducibility)
frontend/public/assets/ship/ ← processed, web-ready (in git)
  rooms/   room_galley.webp
  crew/    crew_parts.png + crew_parts.json (atlas)
  props/   props.png + props.json (atlas)
  ui/      ui.png + ui.json, logo_graveyard_shift.png
  tasks/   task_reactor_override_bg.webp, task_parts.png/json
```

Naming: `snake_case`, `<category>_<name>_<state>`, for example `prop_vent_open`, `prop_console_done`.
❓ Whether raws are kept in Git LFS or a shared drive: team decision.

### 14.3 Chroma backgrounds

- **Characters, UI, most props:** flat **pure green `#00FF00`** (the crew base is grey, so nothing green in them).
- **Green things** (Hydroponics props, lime-colored items): flat **magenta `#FF00FF`**.
- Prompt must say: *"isolated on a perfectly flat, uniform #00FF00 background, no shadows on the background, no gradient, no floor."*
- The script uses color-distance keying with a tolerance, then **despill** (removes the green fringe from edges), then trims.

### 14.4 Processing scripts Claude will write (Python, Pillow/NumPy)

| Script | Does |
|---|---|
| `key.py` | Chroma key + despill + alpha feather |
| `cut_parts.py` | Splits a sheet into parts by connected regions, names them, sets pivot points |
| `pack_atlas.py` | Packs sprites into a Phaser-compatible JSON atlas |
| `export_web.py` | Resizes and exports WebP/PNG at game scale |
| `pixelize.py` | Pixel-art cleanup for the arcade cabinet (§5.3) |
| `palette_check.py` | Reports how far an image drifts from the palette |
| `slice_sheet.py` | Batch-sheet slicer: finds each item, crops, keys, trims, names it from the sheet's layout spec, and writes PNGs + a contact sheet for review (§14.5) |

### 14.5 Batch sheets (many assets per generation) ✅

Small assets (props, icons, UI pieces, task parts, cosmetics) are **never generated one by one**. Each generation is a **sheet**: many items laid out in a grid on a flat chroma background. Claude slices it.

**Why it works:**
- About 3x fewer generations.
- Items in one sheet come out in **the same style, line weight, and lighting**, which is better consistency than separate generations.
- **States of one prop in the same sheet** (idle / highlighted / done) come out matching each other.

**Sheet rules (put in every sheet prompt):**
1. **Fixed grid:** "arranged in a neat grid of N columns × M rows, one item per cell, each item centered in its cell."
2. **Wide gutters:** "generous empty space between items; no item touches or overlaps another; nothing crosses cell boundaries."
3. **Flat chroma:** "on a perfectly flat, uniform #00FF00 background; no shadows, no floor, no gradient, no vignette" (magenta `#FF00FF` for sheets with green items).
4. **No labels:** no text, numbers, or captions under items (they come out garbled and are harder to remove). Claude identifies items by **grid position** from the prompt's ordered list.
5. **Same view and scale:** "all items in the same top-down 3/4 view (or side view), same scale, same lighting from the top-left."
6. **Size budget:** a 4K 16:9 sheet (3840×2160) in a 4×3 grid gives about 900×700 px per cell, plenty for props shown at 128–256 px on screen. **Keep it to at most about 16 items per sheet**; past that, items shrink and details turn to mush.
7. **States in one row:** e.g. row 1 = console idle, console highlighted, console done.

**Slicing (`slice_sheet.py`):**
1. Key out the chroma color (tolerance + despill).
2. Find items as connected alpha regions (small specks are dropped; parts that belong together, such as a glow halo plus its object, are merged by grid cell).
3. Map each region to its grid cell and give it the name from the sheet's layout list.
4. Trim to content, add 4px of padding, save as `<category>_<name>_<state>.png`.
5. Generate a **contact sheet** (all cut items on a checkerboard, labeled) so the user can check every cut at a glance.
6. Pack approved items into the Phaser atlas with `pack_atlas.py`.

**What stays one-per-image:** room paintings, hallway strips, full-screen backgrounds (role reveal, ejection, win/lose), key art, and the logo. These need full resolution.

### 14.6 Batch plan 📝

| Sheet | Grid | Contents (row by row) | Chroma |
|---|---|---|---|
| **SH-CREW** | 4×4 | Crew puppet parts + visor expressions (full list in [CHARACTERS.md](CHARACTERS.md) §7.2) | Green |
| **SH-CREW-POSES** | 4×2 | Hero, smug, wave, point, shrug, cheer, fallen suit, rolled helmet ([CHARACTERS.md](CHARACTERS.md) §7.3) | Green |
| **SH-PROPS-1** | 4×3 | Row 1: task console idle / highlighted / done / generic small wall panel · Row 2: emergency button idle / pressed / disabled / time clock · Row 3: vent closed / vent open / time clock ready / meeting stool | Green |
| **SH-PROPS-2** (Tier 2) | 4×3 | Door open / closed (×2 orientations), med pod idle / scanning, crates, plant pots, coffee mug, lamp, etc. | Magenta |
| **SH-UI-ICONS** | 4×3 | Use, Report, Eliminate, Vent, Chat, Settings, Map, Leave, Host crown, "I voted" stamp, Skip, Ghost | Green |
| **SH-UI-FRAMES** | 3×3 | CRT panel frame (large), CRT panel (small), pill button idle / pressed / disabled, progress bar frame + fill, timer dial, toast frame | Green |
| **SH-TASK-PARTS** | 4×3 | Keypad keys (blank, pressed), patch cables ×4 colors + jack, reel (full/empty), VU needle, slider knob | Magenta |
| **SH-COSMETIC-1/2/3** (Tier 3) | 4×3 each | See §9.4 | Green |

**Effect:** Tier 1 drops from about 30 generations to about 22, and all small assets come from about 6 sheets.

---

## 15. Prompting Playbook for Nano Banana Pro

📝 Draft. Final prompts are written per asset during production.

### 15.1 Prompt structure

```
[STYLE BLOCK]      same text in every prompt (below)
[ASSET BLOCK]      what this image is, its composition, camera, contents
[CONSTRAINTS]      background, framing, what NOT to include
[REFERENCES]       "Match the style of the attached reference images exactly."
```

### 15.2 Master style block (draft)

> Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

### 15.3 Rules

- Always attach the locked anchors (A0.1–A0.3) once they exist.
- Room prompts: *"top-down 3/4 view, camera tilted about 35 degrees, orthographic, no vanishing points, no characters, floor area kept clear and readable, empty alcoves where consoles go."*
- Character prompts: *"side view facing right, full body, neutral pose, separated parts laid out apart from each other"* (for the puppet sheet).
- Never ask for transparency, small text, or UI text inside the art.
- Never use "Among Us" or "Innersloth" in prompts, to avoid lookalike outputs.
- One asset per prompt; iterate conversationally on the best variant.
- Save every final prompt to `art/prompts/`.

---

## 16. Handoff: Wizard-of-Oz Prototype (Next Chat)

📝 Draft recommendation; final decisions happen in the next chat.

- **Build the prototype in Phaser 3 (one HTML page)**, the same engine as Covey.Town, so it is visibly "plausible to implement" and every asset and animation carries over to the real code.
- **Literal Wizard-of-Oz:** a hidden **director panel** (hotkeys) lets the presenter puppet the fake players and server: add players to the lobby, start the game, trigger an elimination, call a meeting, cast bot votes, finish tasks, end in either win state.
- **Fake multiplayer:** scripted bot crew walking pre-recorded paths.
- **Demo script (about 5 minutes):** town → arcade (US3) → lobby + host start → role reveal → tasks: keypad + wiring + "no task here" + team bar (US1) → Impostor elimination + cooldown → report → meeting + vote + eject (US2) → ghost view → final win screen.
- Inputs it needs from this session: the locked palette and fonts (§7), processed assets (§13), atlas JSONs, and the world scale (§6.3).

---

## 17. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Style drift across 50+ generations | Looks unprofessional | Style lock with anchors attached to every prompt; Claude reviews every output |
| Demo is due in 3 days | Not enough assets | Tier 1 only for the demo; code placeholders (colored shapes) for anything missing |
| Perspective mismatch between rooms | Map looks stitched together | Fixed camera language; room anchor attached; hallways hide the seams |
| Chroma fringe on edges | Ugly halos | Despill + 1px alpha erode in `key.py` |
| Large file sizes | Slow load, repo bloat | WebP exports; raws outside git |
| Lookalike to Among Us IP | Professionalism, legal | Own silhouette (squat suit + fishbowl dome + antenna); never name Among Us in prompts |
| Pixel cabinet looks off in the town | Breaks immersion | Palette-match to Tuxemon via `pixelize.py`; test in the town map |

---

## 18. Open Questions

1. ✅ Art direction bible approved (D8).
2. ✅ Room list and layout approved (D11).
3. ✅ Fallen-crew marker: generated art in a batch sheet (D15).
4. ✅ 10 crew colors (D12).
5. ✅ Raw 4K generations stay local in `art/`, not in git (D16).
6. ✅ "GRAVEYARD SHIFT" approved (D9).
7. ❓ Audio direction (deferred).
