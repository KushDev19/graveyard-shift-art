# GRAVEYARD SHIFT: Full Prompt Book (Nano Banana Pro)

> Every image asset for the game, one copy-paste prompt each. 46 prompts in total.
> Specs behind these prompts: [ART_DIRECTION_RESEARCH.md](ART_DIRECTION_RESEARCH.md) (world, UI, pipeline) · [CHARACTERS.md](CHARACTERS.md) (crew design rules).
> This file **supersedes** the prompts in `CHARACTERS.md` §7 and `art/prompts/tier0_anchors.md`.

> **UPDATE (production split):** these assets are built by Claude as **SVG / code**, so **skip their prompts in Gemini**: **03** (done: `frontend/public/assets/ship/crew/crew_puppet.svg`, the walking puppet), **16–19**, **39–41**, **20–22**, **23** (unless the Bungee font can't be obtained), **24**, **25** (hand-placed pixels), **42**. Prompt **04** is replaced by **04A–04E** (full pose illustrations by Gemini, 2 per image). Everything else stays in Gemini. Keep doing the Gemini ones in order: 04A–04E, 05, 06, 07, ...

---

## 0. How to use this book

### 0.1 Settings for every prompt
- **Model:** Nano Banana Pro · **Resolution:** 4K · **Aspect ratio:** as listed on each prompt.
- Generate **2–4 variants**, keep the best. If a variant is 90% right, don't re-roll: reply in the same chat with *"Keep everything identical, but …"* (fix phrases in §12).
- Each code block is **one complete prompt**. Copy the whole block, nothing else.

### 0.2 Attach references (this is what keeps 46 images looking like one game)

Each prompt lists **ATTACH**. These are images *you* already generated and picked:

| Tag | File to attach |
|---|---|
| `[CREW]` | your chosen `00_CREW_MODEL.png` |
| `[GALLEY]` | your chosen `01_ROOM_GALLEY.png` |
| `[KEYART]` | your chosen `02_KEYART.png` |
| `REF_RIG` | `art/raw/REF_RIG.png` (exported SVG puppet, side + front: scale reference for cosmetics) |
| `[STATIONS]` | your chosen `14_PROPS_STATIONS.png` |
| `[TOWN]` | `frontend/public/assets/tilesets/tuxmon-sample-32px-extruded.png` from this repo |

### 0.3 Use separate Gemini chats per family
Nano Banana remembers within a chat. Use **one chat per family**: Characters (00, 04A–04E, 43A–45N) · Rooms & halls (01, 05–13, 35–37) · Props (14, 15, 38) · Brand (23 fallback, 26) · Screens (02, 27–34).

### 0.4 Where to save (so I can review everything)
- Folder: **`art/raw/`** in this project (it's git-ignored, so 4K files never bloat the repo).
- Name each chosen image **exactly by its ID**: `03_CREW_PARTS.png`. Extra variants worth keeping: `03_CREW_PARTS_alt1.png`.
- **Full-resolution PNG downloads only.** No screenshots, no compressed copies.
- If you edited a prompt in the chat, paste your final wording into `art/raw/<ID>.txt`.

### 0.5 ⚠️ Strongly recommended checkpoint
Generate **00, 01, 02 first** and drop them in `art/raw/` for a quick review **before** the rest. Every later prompt attaches them, so a problem there would repeat across 40+ images. It takes about 5 minutes and can save hours.

### 0.6 The rules baked into every prompt (so you know why they're there)
1. **Grey = tintable:** the crew suit is neutral grey; the game recolors it per player.
2. **Flat chroma background** (green `#00FF00`, or magenta `#FF00FF` for sheets containing green) on every sprite sheet. The script removes it.
3. **Nothing see-through, and glows stay inside outlines.** Anything semi-transparent or glowing past an edge mixes with the chroma color and can't be cleaned. The code adds halos and glows afterwards.
4. **Grid + gutters + no text** on sheets. Items are identified by grid position.
5. **Same camera everywhere:** top-down 3/4 for the world, straight-on front view for UI and task panels.

---

## 1. Generation checklist (in order)

| ✓ | ID | Asset | Tier | Aspect | Attach |
|---|---|---|---|---|---|
| ✅ | 00 | CREW_MODEL: crew model sheet (design lock) | 0 | 16:9 | — |
| ✅ | 01 | ROOM_GALLEY: Galley room (world-style lock) | 0 | 16:9 | [CREW] |
| ✅ | 02 | KEYART: key art | 0 | 16:9 | [CREW] [GALLEY] |
| SVG | 03 | CREW_PARTS: puppet parts sheet (built by Claude) | 1 | 1:1 | — |
| ✅ | 04A–E | POSES: reveal, meeting, win, knocked-out + ghost, ejected + sneak (2 per image) | 1 | 16:9 | [CREW] |
| ✅ | 05 | ROOM_LOCKER: Locker Room (lobby) | 1 | 16:9 | [GALLEY] [CREW] |
| ✅ | 06 | ROOM_REACTOR: Reactor | 1 | 16:9 | [GALLEY] [CREW] |
| ☐ | 07 | ROOM_SWITCHBOARD: Switchboard | 1 | 16:9 | [GALLEY] [CREW] |
| ☐ | 08 | ROOM_RADIO: Radio Room | 1 | 16:9 | [GALLEY] [CREW] |
| ☐ | 09 | ROOM_BRIDGE: Bridge | 1 | 16:9 | [GALLEY] [CREW] |
| SVG | 10 | HALL_HORIZONTAL (built by Claude: tileable) | 1 | — | — |
| SVG | 11 | HALL_VERTICAL (built by Claude: tileable) | 1 | — | — |
| SVG | 12 | HALL_CORNER_DOWN (built by Claude: tileable) | 1 | — | — |
| SVG | 13 | HALL_CORNER_UP (built by Claude: tileable) | 1 | — | — |
| ☐ | 14 | PROPS_STATIONS: task stations × 3 states | 1 | 1:1 | [GALLEY] [CREW] |
| ☐ | 15 | PROPS_SHIP: button, vents, time clock, doors | 1 | 16:9 | [GALLEY] [STATIONS] |
| SVG | 16 | TASK_KEYPAD: Reactor Override panel (built by Claude) | 1 | 4:3 | — |
| SVG | 17 | TASK_SWITCHBOARD: Patch the Switchboard panel (built by Claude) | 1 | 4:3 | — |
| SVG | 18 | TASK_TAPE: Tape Transfer panel (built by Claude) | 1 | 4:3 | — |
| SVG | 19 | TASK_PARTS: keys, plugs, reels, needles (built by Claude) | 1 | 1:1 | — |
| SVG | 20 | UI_ACTIONS: big HUD action buttons (built by Claude) | 1 | 16:9 | — |
| SVG | 21 | UI_BADGES: small icons and badges (built by Claude) | 1 | 16:9 | — |
| SVG | 22 | UI_FRAMES: CRT panels, buttons, bars (built by Claude) | 1 | 16:9 | — |
| ☐ | 23 | LOGO: GRAVEYARD SHIFT wordmark | 1 | 16:9 | [CREW] [KEYART] |
| SVG | 24 | LOGO_EMBLEM: round badge emblem (built by Claude) | 1 | 1:1 | — |
| SVG | 25 | ARCADE_PIXEL: town arcade cabinet (pixel art) (built by Claude) | 1 | 1:1 | — |
| ☐ | 26 | ARCADE_HD: cartoon arcade cabinet (join modal) | 1 | 1:1 | [CREW] + 23 |
| ☐ | 27 | SCREEN_TITLE: Nightjar exterior title screen | 1 | 16:9 | [KEYART] |
| ☐ | 28 | SCREEN_REVEAL_CREW | 1 | 16:9 | [KEYART] |
| ☐ | 29 | SCREEN_REVEAL_IMPOSTOR | 1 | 16:9 | [KEYART] + 28 |
| ☐ | 30 | SCREEN_SPLASH_EMERGENCY | 1 | 16:9 | [CREW] [KEYART] |
| ☐ | 31 | SCREEN_SPLASH_BODY | 1 | 16:9 | [CREW] + 04D, 30 |
| ☐ | 32 | SCREEN_EJECT: airlock + nebula | 1 | 21:9 | [KEYART] + 27 |
| ☐ | 33 | SCREEN_WIN_CREW | 1 | 16:9 | 05 + [KEYART] |
| ☐ | 34 | SCREEN_WIN_IMPOSTOR | 1 | 16:9 | 05 + 33 |
| ☐ | 35 | ROOM_SICKBAY | 2 | 16:9 | [GALLEY] [CREW] |
| ☐ | 36 | ROOM_HYDROPONICS | 2 | 16:9 | [GALLEY] [CREW] |
| ☐ | 37 | ROOM_CARGO | 2 | 16:9 | [GALLEY] [CREW] |
| ☐ | 38 | PROPS_EXTRA: med pod, security, decor | 2 | 16:9 | [GALLEY] [STATIONS] |
| SVG | 39 | TASK_THRUSTERS: slider panel (built by Claude) | 2 | 4:3 | — |
| SVG | 40 | TASK_GYRO: timing panel (built by Claude) | 2 | 4:3 | — |
| SVG | 41 | TASK_MEMORY: pattern panel (built by Claude) | 2 | 4:3 | — |
| SVG | 42 | MAP_BLUEPRINT: minimap (built by Claude) | 2 | 16:9 | — |
| ☐ | 43A, 43B | COS_HATS: 12 hats, side + front | 3 | 16:9 | [CREW] REF_RIG |
| ☐ | 44N | COS_TOPPERS_PACKS: toppers + backpacks, side | 3 | 16:9 | [CREW] REF_RIG |
| ☐ | 45N | COS_VISORS_DECALS: visors + decals, side + front | 3 | 16:9 | [CREW] REF_RIG |

**Tier 1 (00–34) = everything the Wizard-of-Oz demo shows.** Tier 2 completes the final game. Tier 3 is cosmetics.

---

## 2. Tier 0: Style anchors

### 00 · CREW_MODEL · 16:9 · ATTACH: nothing

```
Clean 2D cartoon game art for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded shapes, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A. Cozy, playful, slightly mysterious; not horror. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

Character model sheet for one original mascot character: a crew member of a cozy 1970s retro-future cargo spaceship working the night shift. The same character is shown 6 times in a neat grid of 3 columns × 2 rows, each figure centered in its cell with generous empty space between figures; no figure touches another.

Top row, all with a plain NEUTRAL LIGHT GREY suit (pure grey with zero color tint, shaded with darker neutral grey): (1) side view facing right, standing neutral; (2) front view, standing neutral; (3) three-quarter view, standing neutral.
Bottom row, side view facing right, mid-waddle with one leg forward and the body tilted slightly: (4) tomato-red suit, (5) mint suit, (6) mustard-yellow suit.

Character design: a short, squat, round-bottomed body shaped like a gumdrop or a thermos flask, about two heads tall, chunky and huggable, wider at the bottom. Two short stubby legs with rounded boots. Two tiny stubby mitten arms held close to the body. An oversized fishbowl dome helmet sits on top with a chunky rounded rim collar where it meets the suit; the inside of the dome is solid dark midnight indigo (#1B1830), completely opaque, with a soft white curved glass highlight on the upper left. Floating inside the dark dome is a big smooth glowing AMBER visor shaped like a wide rounded rectangle, its glow contained inside its own outline. No eyes, no mouth, no face at all: the visor IS the face. A thin antenna sticks up from the top of the dome with a small round ball on the tip. A small boxy 1970s backpack on the back. A cream-amber-coral triple racing stripe runs horizontally across the chest. Goofy, lovable, funny proportions: tiny legs, huge helmet, round bottom. An original design: not a bean or capsule shape, not a visor set directly into the body.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no gradient, no vignette, no outer glow. Nothing transparent or see-through. All six figures at exactly the same scale, same lighting from the top-left. No text, no labels, no numbers, no captions.
```

**Pick the one where:** the silhouette reads instantly at thumbnail size, it's clearly not a bean, the top-row suit is truly grey, and it makes you smile.

---

### 01 · ROOM_GALLEY · 16:9 · ATTACH: [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the GALLEY (crew mess hall) of the cargo spaceship Nightjar at 3 a.m. Camera: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points, no perspective distortion. The room fills the entire frame edge to edge with no border. The back wall runs along the top of the image and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low wall ledge along the bottom edge.

Back wall: teal steel rounded wall panels with the cream-amber-coral triple racing stripe running along it, and three round porthole windows showing a pink, violet and amber nebula sunset with stars. Warm amber pendant lamps hang from the ceiling and cast soft round pools of light on the floor. Floor: smooth dark teal-indigo panels with subtle seams, low detail, clearly readable as open walkable space.

Center: a long rounded 1970s diner-style table in cream and teal with ten round cushioned stools around it. In the exact middle of the table, an EMPTY round raised pedestal base (an object will be placed on it later). Along the walls: a retro vending machine with glowing buttons, a rounded 1970s fridge with a racing stripe, a coffee counter with a chunky coffee machine and mugs, two potted plants, a cork board with blank pinned notes. Doorway openings: one gap in the left wall (middle height), one gap in the right wall (middle height), one gap in the bottom ledge (center). Keep plenty of open walkable floor around the table and between the doorways.

Scale: match the attached character sheet; the fridge is slightly taller than the character, and each doorway is about twice the character's width. The character must look like it belongs here, so match its line style, colors and shading exactly.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

**Pick the one where:** the camera angle feels like a classic top-down RPG room, the floor is clearly walkable, it's cozy, and the empty pedestal is in the middle of the table.

---

### 02 · KEYART · 16:9 · ATTACH: [CREW] [GALLEY]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Promotional key art for a cozy social-deduction mystery game. A cinematic, slightly low eye-level view inside the Galley from the attached room reference. Six crew characters from the attached character sheet, in tomato red, mint, mustard yellow, cobalt blue, bubblegum pink and cream suits, are gathered around the long diner table, leaning in and eyeing each other suspiciously with funny, exaggerated body language: one points accusingly, one shrugs innocently, one clutches a coffee mug nervously, one peeks over a blank card. In the middle of the table, a big glowing coral-red button under a glass dome on a round pedestal. In the background, half-hidden behind the rounded fridge, a grape-purple crew member peeks out slyly, its visor glinting faintly coral. Through the round porthole windows: a huge nebula sunset in pink, violet and amber with stars. Warm amber lamp light pools on the table; cool teal and indigo shadows everywhere else.

The characters must match the attached character sheet exactly (gumdrop body, fishbowl dome helmet with dark indigo interior, glowing amber visor face, antenna with ball, mitten arms, stubby legs, racing stripe). Keep the top third of the image calmer and less detailed (wall and windows) so a logo can be placed there later. No text, no logo, no letters, no numbers.
```

---

## 3. Characters

> **03** (crew parts) is built as SVG, so there's no prompt: see `frontend/public/assets/ship/crew/crew_puppet.svg`.

### 04A–04E · Pose illustrations (REPLACE 04) · 16:9 · ATTACH: `00_CREW_MODEL.png` only

Two full-body poses per image. Generated whole by Gemini (the in-game walking puppet stays SVG). Save as `art/raw/04A_POSES_REVEAL.png`, `04B_POSES_MEETING.png`, `04C_POSES_WIN.png`, `04D_POSES_FALLEN_GHOST.png`, `04E_POSES_EJECT_SNEAK.png`.

#### 04A · Role reveal: hero (crewmate) + smug (impostor)

```
Clean 2D cartoon game art for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, amber #F5A54A, cream #F4E6C8, coral #E8574A, light blue-grey #9DBCCB. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

CHARACTER: match the attached model sheet EXACTLY (same proportions, outline weight, shading and details): the squat round-bodied crew member with an oversized fishbowl helmet (thick light blue-grey glass rim, solid opaque dark midnight-indigo interior, a big curved white glass highlight plus a small dot on the upper left), a big glowing amber rounded visor as its only face (no eyes, no mouth), a small grey dome-shaped nub on top of the helmet with a thin antenna and a round ball tip, a thick grey ring collar where the helmet meets the suit, a small vertical chest tab with cream-amber-coral stripes hanging below the collar, a boxy backpack with a round button, a slot and a pocket, stubby sleeves with cuff lines ending in mitten hands with a thumb, and short thick legs with rounded boots that have a cuff line and a light highlight. The suit is NEUTRAL LIGHT GREY (pure grey, zero color tint, shaded with darker neutral grey) in both poses.

Two poses of this same character side by side, each centered in its own half of the image with wide empty space between them; nothing touches; both at exactly the same scale, each figure about 80% of the image height, fully visible including the antenna and boots.
LEFT, "proud crewmate": front view, standing tall and proud with the chest puffed out, both mitten fists planted firmly on the hips with elbows out, feet planted apart, antenna standing perky and straight, helmet tilted up slightly with the visor bright and confident.
RIGHT, "smug impostor": three-quarter view turned slightly to the right, leaning back with the weight on one leg, both arms crossed tightly over the chest with the mittens tucked in, helmet tilted to one side, the visor narrowed into a half-closed smug squint (its top edge flattened like a lowered eyelid), antenna bent to one side mischievously.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no ground line, no gradient, no outer glow, no effects. No text, no labels, no numbers.
```

#### 04B · Meeting: accuse + innocent shrug

```
Clean 2D cartoon game art for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, amber #F5A54A, cream #F4E6C8, coral #E8574A, light blue-grey #9DBCCB. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

CHARACTER: match the attached model sheet EXACTLY (same proportions, outline weight, shading and details): the squat round-bodied crew member with an oversized fishbowl helmet (thick light blue-grey glass rim, solid opaque dark midnight-indigo interior, a big curved white glass highlight plus a small dot on the upper left), a big glowing amber rounded visor as its only face (no eyes, no mouth), a small grey dome-shaped nub on top of the helmet with a thin antenna and a round ball tip, a thick grey ring collar where the helmet meets the suit, a small vertical chest tab with cream-amber-coral stripes hanging below the collar, a boxy backpack with a round button, a slot and a pocket, stubby sleeves with cuff lines ending in mitten hands with a thumb, and short thick legs with rounded boots that have a cuff line and a light highlight. The suit is NEUTRAL LIGHT GREY (pure grey, zero color tint, shaded with darker neutral grey) in both poses.

Two poses of this same character side by side, each centered in its own half of the image with wide empty space between them; nothing touches; both at exactly the same scale, each figure about 80% of the image height, fully visible including the antenna and boots.
LEFT, "it was them!": side view facing right, leaning forward dramatically onto the front boot, one arm thrust straight out forward accusing someone with the mitten jabbing forward, the other arm pulled back in a fist, antenna bent forward with the momentum, visor wide and intense.
RIGHT, "who, me?": front view, both arms raised out to the sides at shoulder height with the mittens open palm-up, shoulders hunched up so the collar rises toward the helmet, helmet tilted to one side, one knee slightly bent inward, the visor a wide innocent rounded shape, antenna drooping sideways.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no ground line, no gradient, no outer glow, no effects. No text, no labels, no numbers.
```

#### 04C · Win screen: cheer + wave

```
Clean 2D cartoon game art for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, amber #F5A54A, cream #F4E6C8, coral #E8574A, light blue-grey #9DBCCB. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

CHARACTER: match the attached model sheet EXACTLY (same proportions, outline weight, shading and details): the squat round-bodied crew member with an oversized fishbowl helmet (thick light blue-grey glass rim, solid opaque dark midnight-indigo interior, a big curved white glass highlight plus a small dot on the upper left), a big glowing amber rounded visor as its only face (no eyes, no mouth), a small grey dome-shaped nub on top of the helmet with a thin antenna and a round ball tip, a thick grey ring collar where the helmet meets the suit, a small vertical chest tab with cream-amber-coral stripes hanging below the collar, a boxy backpack with a round button, a slot and a pocket, stubby sleeves with cuff lines ending in mitten hands with a thumb, and short thick legs with rounded boots that have a cuff line and a light highlight. The suit is NEUTRAL LIGHT GREY (pure grey, zero color tint, shaded with darker neutral grey) in both poses.

Two poses of this same character side by side, each centered in its own half of the image with wide empty space between them; nothing touches; both at exactly the same scale, each figure about 80% of the image height, fully visible including the antenna and boots.
LEFT, "we did it!": front view, jumping in celebration with both boots off the ground and the legs tucked up behind, both arms thrown straight up in victory with the mittens open, body stretched tall, antenna boinging upward, the visor tilted up joyfully.
RIGHT, "hello!": three-quarter view turned slightly to the right, standing relaxed, one arm raised high above the helmet waving hello with the mitten open, the other arm resting at its side, the body leaning slightly toward the wave, friendly and cheerful.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no ground line, no gradient, no outer glow, no effects. No text, no labels, no numbers.
```

#### 04D · Fallen marker (map) + ghost

```
Clean 2D cartoon game art for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, amber #F5A54A, cream #F4E6C8, coral #E8574A, light blue-grey #9DBCCB, seafoam #B5EAD8, mustard #E9C046. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

CHARACTER: match the attached model sheet EXACTLY (same proportions, outline weight, shading and details): the squat round-bodied crew member with an oversized fishbowl helmet (thick light blue-grey glass rim, solid opaque dark midnight-indigo interior, a big curved white glass highlight plus a small dot on the upper left), a big glowing amber rounded visor as its only face (no eyes, no mouth), a small grey dome-shaped nub on top of the helmet with a thin antenna and a round ball tip, a thick grey ring collar where the helmet meets the suit, a small vertical chest tab with cream-amber-coral stripes hanging below the collar, a boxy backpack with a round button, a slot and a pocket, stubby sleeves with cuff lines ending in mitten hands with a thumb, and short thick legs with rounded boots that have a cuff line and a light highlight. The suit is NEUTRAL LIGHT GREY (pure grey, zero color tint, shaded with darker neutral grey) in both items.

Two items side by side, each centered in its own half of the image with wide empty space between them; nothing touches; same character scale in both.
LEFT, "knocked out" (the marker left on the floor of the map): seen from a slightly top-down three-quarter view, as if lying on the floor of a top-down game room. The empty suit lies flat on its back, deflated and crumpled like a sad empty sleeping bag, the stubby arms and legs splayed out limply, the chest tab still visible, and an empty dark neck-ring opening at the collar where the helmet popped off. The fishbowl helmet has rolled a short distance away to the upper right and lies on its side, the visor dimmed to dull brownish amber, a tiny dizzy swirl above it. Three small mustard cartoon stars circle above the suit. Slapstick and funny: no blood, no injury, nothing scary. The suit and the helmet form one compact group about half the image width.
RIGHT, "ghost": front view of the same character floating peacefully as a friendly ghost: the legs are replaced by a soft wispy tail that curls to one side, the arms float loosely outward, the suit is the same neutral grey but slightly paler, the visor is a soft pale seafoam (#B5EAD8) instead of amber, and a small cream halo ring floats just above the antenna ball. Drawn fully opaque (transparency is added later in the game).

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no ground line, no gradient, no outer glow, no other effects. No text, no labels, no numbers.
```

#### 04E · Ejected tumbling + sneaky impostor

```
Clean 2D cartoon game art for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, amber #F5A54A, cream #F4E6C8, coral #E8574A, light blue-grey #9DBCCB. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

CHARACTER: match the attached model sheet EXACTLY (same proportions, outline weight, shading and details): the squat round-bodied crew member with an oversized fishbowl helmet (thick light blue-grey glass rim, solid opaque dark midnight-indigo interior, a big curved white glass highlight plus a small dot on the upper left), a big glowing amber rounded visor as its only face (no eyes, no mouth), a small grey dome-shaped nub on top of the helmet with a thin antenna and a round ball tip, a thick grey ring collar where the helmet meets the suit, a small vertical chest tab with cream-amber-coral stripes hanging below the collar, a boxy backpack with a round button, a slot and a pocket, stubby sleeves with cuff lines ending in mitten hands with a thumb, and short thick legs with rounded boots that have a cuff line and a light highlight. The suit is NEUTRAL LIGHT GREY (pure grey, zero color tint, shaded with darker neutral grey) in both poses.

Two poses of this same character side by side, each centered in its own half of the image with wide empty space between them; nothing touches; both at exactly the same scale, each figure about 75% of the image height, fully visible including the antenna and boots.
LEFT, "ejected": tumbling helplessly through empty space, the whole body rotated about 35 degrees, arms and legs flailing outward in comic panic, the antenna bent back by the spin, the backpack visible, the visor shaped like a round surprised "O". No stars or space background.
RIGHT, "sneaky impostor": side view facing right, tiptoeing in an exaggerated cartoon-burglar crouch, knees bent, body hunched forward, both mittens raised in front of the chest with the thumbs up like sneaking fingers, the visor narrowed into a sly sideways glance, the antenna tucked low behind the helmet.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no ground line, no gradient, no outer glow, no effects. No text, no labels, no numbers.
```

---

## 4. Rooms (Tier 1)

> All rooms share the Galley's camera. Door positions match the ship layout, so **keep the doorways where the prompt says**.

### 05 · ROOM_LOCKER (lobby) · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the LOCKER ROOM of the cargo spaceship Nightjar, where the night-shift crew gathers before clocking in. This is the warmest, coziest room on the ship. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall: a long row of tall rounded 1970s lockers in alternating teal and cream, a few doors slightly ajar with a scarf or jacket peeking out, small round stickers (no text); the cream-amber-coral racing stripe above the lockers; a big round wall clock with hands pointing at 3 o'clock (no numerals). On the back wall, left of center: a heavy rounded bulkhead double door, CLOSED, with an amber warning lamp above it and yellow-plum hazard stripes around its frame. On the back wall, right of center: an EMPTY rectangular wall alcove with a cream floor marking in front of it (a time-clock machine will be placed there later).
Floor: warm plum and teal floor panels with a round braided rug in the middle. Two long cushioned benches in the center of the room. Right side: a chunky coffee machine on a small counter, a water cooler, a stack of mugs. Left side: a cork shift-schedule board with blank cards, a coat rack, a potted plant. Warm amber ceiling lamps make inviting light pools. No other doorways.

Scale and style: match the attached references exactly; the lockers are about 1.5 times the character's height; leave plenty of open walkable floor for ten characters to stand around.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

### 06 · ROOM_REACTOR · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the REACTOR room (nicknamed "the Furnace") of the cargo spaceship Nightjar. Signature lighting: a warm CORAL-orange glow from the reactor core spilling across the room, contrasted with cool teal-indigo shadows in the corners. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall, center: a huge round 1970s reactor core set into the wall behind a chunky protective cream grille, glowing coral and amber, with thick rounded pipes running out from it along the wall and ceiling, round pressure gauges with blank dials, and plum-and-amber hazard stripes around its base. On the back wall, left of the core: an EMPTY rectangular wall alcove with a cream floor marking in front of it (a keypad control station will be placed there later). A small tool rack and a fire extinguisher on the back wall right side.
Floor: metal grate panels around the reactor's base, catching coral reflections, then smooth dark teal-indigo panels; keep the center and lower half open and walkable. A few low pipes run along the side walls, with tiny puffs of steam from two valves.
Doorway openings: one gap in the right wall (middle height), one gap in the bottom ledge (center-left). No other doorways.

Scale and style: match the attached references exactly; the reactor core is about three times the character's height; doorways are about twice the character's width.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

### 07 · ROOM_SWITCHBOARD · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the SWITCHBOARD room (the ship's electrical room) of the cargo spaceship Nightjar. Signature lighting: a soft ELECTRIC BLUE glow from rows of small indicator lamps, mixed with one warm amber desk lamp; a little dimmer and moodier than other rooms. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall: a wall-to-wall vintage telephone-operator switchboard in wood and teal metal with rows of brass jack holes, small glowing blue indicator lamps, and a few loose patch cords dangling in loops; chunky fuse boxes; two big knife-switch levers; thick cable bundles running along the top of the wall. In the back wall, center: an EMPTY rectangular wall alcove with a cream floor marking in front of it (a patch-panel task station will be placed there later). In the back wall, far left: a doorway opening into a corridor.
Floor: dark teal-indigo panels with two metal cable trays running across it. Lower right: a small desk with a banker's lamp glowing amber, an old rotary phone and a coffee mug. Lower left: a stack of spare cable spools.
Doorway openings: one doorway in the back wall (far left), one gap in the right wall (middle height). No other doorways. Keep the center of the room open and walkable.

Scale and style: match the attached references exactly; the switchboard is about 1.5 times the character's height; doorways are about twice the character's width.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

### 08 · ROOM_RADIO · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the RADIO ROOM (communications) of the cargo spaceship Nightjar, like a late-night radio DJ booth in space. Signature lighting: warm AMBER from glowing VU meters and string lights, against a cool nebula-lit window. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall: a big rounded window showing a large satellite radio dish outside against the pink-violet-amber nebula and stars; on both sides of it, rows of chunky reel-to-reel tape decks and shelves of colorful cassette tapes; warm amber string lights draped along the top. On the back wall, right of the window: an EMPTY rectangular wall alcove with a cream floor marking in front of it (a tape-deck task station will be placed there later).
Floor: warm plum and teal panels, a round rug, a cozy worn armchair with a pair of big headphones resting on it, a small side table with a lava lamp, a stack of records.
Doorway openings: one gap in the left wall (middle height), one gap in the right wall (middle height), one gap in the bottom ledge (center). No other doorways; the back wall has no door. Keep the center of the room open and walkable.

Scale and style: match the attached references exactly; doorways are about twice the character's width.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

### 09 · ROOM_BRIDGE · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the BRIDGE (cockpit) of the cargo spaceship Nightjar. Signature lighting: soft SEAFOAM glow from console screens plus the dramatic nebula light pouring through the windshield. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall: teal steel wall panels (like the attached Galley) framing a wide panoramic rounded windshield across almost the whole wall, showing a huge pink, violet and amber nebula sunset, stars and a large ringed planet. Below the windshield, a long curved console bank in cream and teal with chunky toggle switches, big round buttons and small round CRT screens glowing seafoam (blank screens, no text). In the center of the room, facing the windshield: a big cushioned 1970s captain's swivel chair. On the back wall: two EMPTY wall alcoves with cream floor markings in front of them, one left of center and one right of center (two task stations will be placed there later).
Floor: dark teal-indigo panels with a round star-chart table on the left (a glowing seafoam map of dots and lines, no text), and a small potted plant and a coffee thermos next to the captain's chair.
Doorway openings: one gap in the left wall (middle height), one gap in the bottom ledge (center). No other doorways; the back wall has no door. Keep the lower half of the room open and walkable.

Scale and style: match the attached references exactly; the captain's chair is about the character's height; doorways are about twice the character's width.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

---

## 5. Hallways (Tier 1)

> **10–13 are built by Claude as tileable SVG** (Gemini drew closed 3D boxes that can't tile). Output goes to `frontend/public/assets/ship/hall/`. No Gemini prompts here.

---

## 6. Props (Tier 1)

### 14 · PROPS_STATIONS · 1:1 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon game sprites for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded shapes, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A. Any glow stays strictly inside each object's outline: no outer glow, no halos, no light rays, no drop shadows.

A sprite sheet of wall-mounted TASK STATIONS for the spaceship rooms in the attached reference, drawn in the SAME top-down three-quarter camera view as the attached room (front face toward the viewer, top surface slightly visible), at a scale where each station is about as tall as the attached character. Each station is a freestanding object that will be placed in front of a wall. Every row shows the same station in three states, identical in shape and size: (left) IDLE: screen and lamps dim; (middle) HIGHLIGHTED: the same station with its screen, buttons and trim lit up bright warm amber; (right) DONE: the same station with its screen showing a big seafoam check mark symbol and a small seafoam lamp lit.

Arrange 12 items in a neat grid of 3 columns × 4 rows, one item centered per cell, generous empty space between items, nothing touching.
Row 1: REACTOR KEYPAD STATION: a chunky cream and coral control pedestal with a small square screen and a 2-by-5 grid of big chunky keys on its sloped top, a pressure gauge with a blank dial. (idle / highlighted / done)
Row 2: SWITCHBOARD PATCH STATION: a wood and teal metal cabinet with a small vintage switchboard face, brass jacks, four colored patch cords (tomato red, mustard yellow, cobalt blue, mint) and a small screen. (idle / highlighted / done)
Row 3: TAPE DECK STATION: a cream 1970s reel-to-reel tape deck console on a teal stand, with two tape reels, a VU meter and a big round button. (idle / highlighted / done)
Row 4: GENERIC CONSOLE: a rounded teal and cream computer console with a round CRT screen, chunky toggle switches and the racing stripe. (idle / highlighted / done)

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no gradient, no outer glow. Nothing transparent or see-through. No text, no letters, no numbers anywhere (keys are blank).
```

### 15 · PROPS_SHIP · 16:9 · ATTACH: [GALLEY] [STATIONS]

```
Clean 2D cartoon game sprites for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded shapes, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A. Any glow stays strictly inside each object's outline: no outer glow, no halos, no light rays, no drop shadows.

A sprite sheet of interactive ship props for the spaceship in the attached references, drawn in the SAME top-down three-quarter camera view and the same style and scale as the attached room and task stations. Every prop faces straight toward the viewer, like the fridge and vending machine in the attached Galley: front-facing, NOT rotated, NOT a diagonal isometric corner view.

Arrange 12 items in a neat grid of 4 columns × 3 rows, one item centered per cell, generous empty space between items, nothing touching.
Row 1, EMERGENCY BUTTON (sits on a round tabletop pedestal; same object in each state): (1) IDLE: a big glossy coral-red dome button under a closed glass dome drawn with solid pale seafoam glass color and white highlights (opaque, not see-through), on a round chrome and cream base with a racing stripe; (2) PRESSED: the glass dome flipped open on a hinge, the coral button pushed down and lit bright; (3) DISABLED: the glass dome closed, the button dull dark plum, a small chunky padlock on the base; (4) TABLE CLUTTER: a small group of three coffee mugs and an open box of donuts, as tabletop decoration.
Row 2: (5) FLOOR VENT CLOSED: a rounded-rectangle louvered floor grate in teal steel set flat in the floor; (6) FLOOR VENT OPEN: the same vent with its louvered lid flipped up and a dark opening below; (7) TIME CLOCK IDLE: a chunky wall-mounted 1970s punch-card time clock machine in cream and teal with a round clock face (no numerals), a card slot and a rack of blank punch cards beside it, its small screen dim; (8) TIME CLOCK READY: the same machine with its screen and card slot lit bright warm amber.
Row 3, BULKHEAD DOORS (for doorways in the rooms): (9) DOOR IN A BACK/FRONT WALL, CLOSED: a rounded sliding bulkhead door seen from the front, teal steel with yellow-plum hazard stripes and a small amber lamp; (10) the same door OPEN: the door panels slid into the frame, leaving the empty frame; (11) DOOR IN A SIDE WALL, CLOSED: the same door design seen edge-on as a thick vertical slab in a side wall, as it appears in the top-down three-quarter view; (12) the side-wall door OPEN: retracted, only the frame visible.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no gradient, no outer glow. Nothing transparent or see-through. No text, no letters, no numbers.
```

---

## 7. Task mini-games (Tier 1)

> **16–19** (task panels + moving parts) are built as **SVG by Claude**, so no Gemini prompts.

---

## 8. UI and brand (Tier 1)

> **20–22** (HUD icons, badges, frames), **24** (emblem) and **25** (pixel arcade cabinet) are built by Claude (SVG / hand-placed pixels). **23** (logo) stays here as a fallback in case the Bungee font route doesn't work out.

### 23 · LOGO (GRAVEYARD SHIFT wordmark) · 16:9 · ATTACH: [CREW] [KEYART]

```
Clean 2D cartoon logo design for a cozy retro-futurist sci-fi video game, 1970s retro-future style. Flat two-tone cel shading, uniform thick dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise. Palette: midnight indigo #1B1830, plum #3D2A4F, amber #F5A54A, cream #F4E6C8, coral #E8574A, seafoam #7FC8B8. Any glow stays strictly inside the logo's outline: no outer glow, no halos, no drop shadow onto the background.

A game title logo wordmark reading exactly "GRAVEYARD SHIFT", spelled G-R-A-V-E-Y-A-R-D on the first line and S-H-I-F-T on the second line, the second line bigger and bolder. Chunky rounded 1970s display lettering like retro diner and arcade signage, cream letters with a thick plum outline and a solid plum 3D extrusion going down and to the right. A cream-amber-coral triple racing stripe sweeps behind the letters from left to right. A small fishbowl crew helmet with a glowing amber visor and a little antenna (matching the attached character) replaces the dot above the letter I in SHIFT, and a thin cream crescent moon hangs off the end of GRAVEYARD. Playful, cozy, slightly mysterious, instantly readable.

The logo is centered with generous empty margin around it, isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no gradient, no outer glow. No other text besides "GRAVEYARD SHIFT".
```

### 26 · ARCADE_HD (join-modal art) · 1:1 · ATTACH: [CREW] + your 23

```
Clean 2D cartoon game art for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded shapes, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Any glow stays strictly inside the object's outline: no outer glow, no halos, no drop shadows.

A single retro ARCADE CABINET in front three-quarter view, standing upright, hero shot. A rounded dark plum cabinet with chunky bevels, the cream-amber-coral racing stripe sweeping down its sides, a wide blank glowing marquee panel on top (empty: the logo will be placed on it later), a large CRT screen with a curved glass bezel showing attract-mode art: a cozy pink-violet-amber nebula, a tiny chunky retro spaceship, and three little fishbowl crew helmets with glowing amber visors peeking up from the bottom of the screen. A control deck with a chunky joystick and round amber and coral buttons, a coin door with two coin slots, and small chrome feet. Inviting and fun.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no gradient, no outer glow. No text, no letters, no numbers.
```

---

## 9. Screens (Tier 1)

> Full-bleed backgrounds. **Players and text are added by code**, so the prompts keep stage areas empty.

### 27 · SCREEN_TITLE (the Nightjar exterior) · 16:9 · ATTACH: [KEYART]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo with warm amber light. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Title screen art: the cargo spaceship NIGHTJAR flying through space at night, seen from the side and slightly below, in the lower-right half of the image. The ship is a chunky, rounded 1970s retro-futurist freighter loosely shaped like a nightjar bird: a plump rounded hull, two short swept-back wings, a small beak-like cockpit with warm amber lit windows, a row of round porthole windows glowing amber along the hull, a cream hull with teal panels and the cream-amber-coral racing stripe running its full length, a small radio dish on top, and gentle glowing amber engine jets at the back. Behind it: a vast pink, violet and amber nebula sunset, scattered stars, and a big ringed planet in the lower-left distance. Calm, cozy, mysterious, beautiful.

The top 35% of the image is calm, open sky (soft nebula and stars only) so a logo can be placed there. Match the style of the attached key art. No text, no letters, no logo.
```

### 28 · SCREEN_REVEAL_CREW · 16:9 · ATTACH: [KEYART]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C.

Background for a role-reveal screen ("you are a CREWMATE"). A dark, calm midnight indigo space with soft distant stars and a faint pink-violet nebula haze at the edges. In the lower center, a round 1970s stage platform in teal steel with the cream-amber-coral racing stripe around its rim, lit from above by a warm AMBER spotlight cone, the light pooling softly on the platform. The platform is EMPTY (characters will be placed on it later) and wide enough for a row of five small characters. The upper-middle area is calm and empty (a title will be placed there). Hopeful, warm, cozy.

Match the style of the attached key art. No characters, no people, no text, no letters, no numbers.
```

### 29 · SCREEN_REVEAL_IMPOSTOR · 16:9 · ATTACH: [KEYART] + your 28

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C.

Background for a role-reveal screen ("you are an IMPOSTOR"), the same composition as the attached crew reveal but sinister-playful. The same round 1970s stage platform in the lower center, but lit from above by a CORAL-RED spotlight cone, with thin wisps of low plum smoke curling across the platform floor, deeper plum and indigo darkness all around, a few coral-tinted stars, and a faint coral rim light on the platform edge. The platform is EMPTY (characters will be placed on it later) and wide enough for a row of three small characters. The upper-middle area is calm and empty (a title will be placed there). Mischievous, not horror.

Match the style of the attached references. No characters, no people, no text, no letters, no numbers.
```

### 30 · SCREEN_SPLASH_EMERGENCY · 16:9 · ATTACH: [CREW] [KEYART]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading with soft glows, uniform thick dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, amber #F5A54A, cream #F4E6C8, coral #E8574A.

A dramatic, funny full-screen splash for the moment an emergency meeting is called. A close-up of a grey crew mitten hand (matching the attached character) SLAMMING down on a big glossy coral-red button under a flipped-open glass dome, on the right side of the image. Bold comic-book action: radiating cream and amber speed lines and a big coral burst shape exploding from the button, little motion lines, a wobbling coffee mug on the table edge. The left 55% of the image is a bold simpler area of radiating coral and amber burst rays on deep plum (a big title will be placed there).

Match the style of the attached references. No text, no letters, no numbers.
```

### 31 · SCREEN_SPLASH_BODY · 16:9 · ATTACH: [CREW] + your 04D and 30

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading with soft glows, uniform thick dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, amber #F5A54A, cream #F4E6C8, coral #E8574A.

A dramatic, funny full-screen splash for the moment a fallen crew member is reported, matching the composition and energy of the attached emergency splash. On the right side: a cream megaphone blaring toward the left with big amber sound-wave arcs, and below it, in a bright amber spotlight on the dark floor, the empty fishbowl helmet from the attached pose sheet rolled onto its side with its visor dimmed and a little dizzy swirl. Slapstick and funny, not gory, no blood. The left 55% of the image is a bold simpler area of radiating coral and amber burst rays on deep plum (a big title will be placed there).

Match the style of the attached references. No standing characters, no text, no letters, no numbers.
```

### 32 · SCREEN_EJECT · 21:9 · ATTACH: [KEYART] + your 27

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C.

A wide panoramic space background for the ejection scene. On the far left edge, part of the hull of the cargo ship from the attached title art, with a round airlock hatch flung open and a small puff of cream vapor drifting out. The rest of the image is a vast, calm, beautiful starfield with a soft pink-violet-amber nebula band flowing horizontally across the middle, a few tiny distant planets, and gentle sparkles. The horizontal middle band from left to right is clear and open (a small character will tumble across it later), and the center is calm enough for a line of text to be placed over it. Quiet, a little melancholy, funny in its emptiness.

Match the style of the attached references. No characters, no text, no letters, no numbers.
```

### 33 · SCREEN_WIN_CREW · 16:9 · ATTACH: your 05 + [KEYART]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C.

Victory background for "the crew clocks out safe": the Locker Room from the attached reference at the END of the night shift, seen from a straight-on front eye-level view. Golden morning sunrise light pours through a big round porthole window in the back wall, making long warm cream and amber light beams. The punch-card time clock on the wall with a few cards sticking out, lockers with jackets, steaming coffee mugs on a bench, floating dust sparkles in the light. Relieved, warm, triumphant, cozy. The lower center of the floor is EMPTY and evenly lit, wide enough for a row of ten small characters (they will be placed later), and the upper-middle wall area is calm (a title will be placed there).

Match the style of the attached references. No characters, no people, no text, no letters, no numbers.
```

### 34 · SCREEN_WIN_IMPOSTOR · 16:9 · ATTACH: your 05 + your 33

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, amber #F5A54A, cream #F4E6C8, coral #E8574A.

Defeat background for "the night shift claims another crew": the same Locker Room and the same straight-on composition as the attached crew-victory image, but the night never ended. Dark plum and indigo, lit only by a flashing CORAL emergency light on the back wall casting coral-red light across the room; lockers flung open; a coffee mug knocked over; punch cards scattered on the floor; the time clock's screen glowing coral; outside the porthole, deep night and a sly crescent moon. Mischievous and darkly funny, not horror, no gore. The lower center of the floor is EMPTY, wide enough for a row of three small characters (they will be placed later), and the upper-middle wall area is calm (a title will be placed there).

Match the style of the attached references. No characters, no people, no text, no letters, no numbers.
```

---

## 10. Tier 2: Final game completion

> **39–42** (extra task panels, minimap) are built as SVG by Claude.

### 35 · ROOM_SICKBAY · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the SICK BAY (medical room) of the cargo spaceship Nightjar. Signature lighting: soft calm SEAFOAM glow. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall: rounded cream medical cabinets with a seafoam heart-and-plus symbol (not a red cross), a vision chart made only of shapes (no letters), a wall-mounted retro monitor showing a seafoam heartbeat line. Two cozy medical cots with seafoam curtains half-drawn on rails on the right side. In the center-left of the floor: an EMPTY round floor platform marking with a cream ring (a medical scanner pod will be placed there later). A small rolling tray with a thermometer, a tiny potted cactus, a fishbowl with one goldfish on a shelf. In the back wall, center: a doorway opening into a corridor.
Doorway openings: one doorway in the back wall (center), one gap in the left wall (middle height). No other doorways. Keep the center open and walkable.

Scale and style: match the attached references exactly; doorways are about twice the character's width.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

### 36 · ROOM_HYDROPONICS · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the HYDROPONICS garden room of the cargo spaceship Nightjar, a little indoor jungle at night. Signature lighting: soft pink and GREEN grow lights over the plants, with a gentle mist. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall: rows of hanging planters and trailing vines under long pink-green grow-light bars, a big round porthole window with the nebula. On the back wall, left of center: an EMPTY rectangular wall alcove with a cream floor marking in front of it (a tape-deck task station will be placed there later). Floor: three long raised hydroponic trays of leafy greens, tomatoes and sunflowers in rounded cream planters with teal pipes, a watering can, a garden gnome wearing a tiny space helmet, and a cozy hammock strung in the lower left corner. Thin mist near the floor.
Doorway openings: one gap in the right wall (middle height), one gap in the bottom ledge (center-left). No other doorways. Keep walkable paths between the trays and to the doorways.

Scale and style: match the attached references exactly; doorways are about twice the character's width.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

### 37 · ROOM_CARGO · 16:9 · ATTACH: [GALLEY] [CREW]

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Night-shift mood: cool teal and indigo ambient light with warm amber lamp pools. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A, nebula pink #D9738C. Cozy, playful, slightly mysterious; not horror.

Game environment art for a cozy 2D top-down adventure game: the CARGO HOLD of the cargo spaceship Nightjar, the biggest and dimmest room, with spooky-cozy hiding spots. Signature lighting: DIM, with only a few hanging amber work lamps making small pools of light, deep indigo shadows between stacks of crates, and amber-plum hazard stripes on the floor. Camera exactly matching the attached Galley reference: top-down three-quarter view, tilted about 35 degrees, orthographic, no vanishing points. The room fills the entire frame edge to edge. The back wall runs along the top and shows its face; the left and right walls appear as thick wall tops running down the sides; the front wall is cut away, leaving only a low ledge along the bottom edge.

Back wall: a huge rounded loading bay door with hazard stripes, closed; cargo netting holding sacks; a big wall-mounted rounded fuel tank. In the back wall, left side: a doorway opening into a corridor. Floor: stacks of chunky wooden and teal metal crates in a few clusters (stamped only with a simple bird silhouette, no text), a small cartoon forklift, a pallet jack, barrels, a cozy pile of packing blankets. Leave winding walkable lanes between the crate stacks.
Doorway openings: one doorway in the back wall (left side), one gap in the left wall (middle height). No other doorways.

Scale and style: match the attached references exactly; crate stacks are about 1.5 times the character's height; doorways are about twice the character's width.

No characters, no people, no text, no letters, no numbers, no signage text anywhere.
```

### 38 · PROPS_EXTRA · 16:9 · ATTACH: [GALLEY] [STATIONS]

```
Clean 2D cartoon game sprites for a cozy retro-futurist sci-fi video game. 1970s retro-future aesthetic: rounded shapes, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A. Any glow stays strictly inside each object's outline: no outer glow, no halos, no light rays, no drop shadows.

A sprite sheet of extra ship props for the spaceship in the attached references, in the SAME top-down three-quarter camera view and the same style and scale as the attached room and task stations.

Arrange 12 items in a neat grid of 4 columns × 3 rows, one item centered per cell, generous empty space between items, nothing touching.
Row 1: (1) MED SCANNER POD IDLE: a round cream floor platform with a rounded teal arch over it, unlit; (2) MED SCANNER POD SCANNING: the same pod with seafoam scanning rings lit on the arch and platform; (3) SECURITY MONITOR DESK IDLE: a teal desk with four small round CRT monitors, screens dark; (4) SECURITY MONITOR DESK ACTIVE: the same desk with the four screens lit seafoam showing simple blurry room shapes.
Row 2, DECOR that characters can walk behind: (5) a tall potted plant with big green leaves in a cream pot; (6) a tall standing amber floor lamp with a rounded shade; (7) a stack of three chunky crates; (8) a water cooler with an opaque seafoam water jug.
Row 3, more DECOR: (9) a single tall rounded teal locker; (10) a plum and amber toolbox with a wrench on top; (11) a mop and bucket; (12) a chunky round potted cactus on a short stand.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no floor, no gradient, no outer glow. Nothing transparent or see-through. No text, no letters, no numbers.
```

---

## 11. Tier 3: Cosmetics (stretch)

> ⚠️ Every player is drawn from the SVG puppet (in-game side view; front view on the role reveal, vote cards and win screens), so hats, visors and decals need **both a side view and a front view**. Toppers and backpacks only need a side view.
> **Attach to all four:** `00_CREW_MODEL.png` **and** `art/raw/REF_RIG.png` (the puppet's exact side + front shapes, for scale). Settings: 4K, 16:9. Save as `art/raw/43A_COS_HATS_A.png`, `43B_COS_HATS_B.png`, `44N_COS_TOPPERS_PACKS.png`, `45N_COS_VISORS_DECALS.png`.

#### 43A · Hats 1–6 (side + front)

```
Clean 2D cartoon game sprites for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Warm 1970s palette: amber #F5A54A, cream #F4E6C8, coral #E8574A, teal #2F6F73, seafoam #7FC8B8, plum #3D2A4F, mustard yellow, tomato red, cobalt blue. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

A sheet of 6 cosmetic HATS for the crew character in the attached references. Each hat is drawn ALONE (no character, no helmet, no antenna) TWICE: once in SIDE VIEW facing right and once in FRONT VIEW, matching the two views of the character in the attached reference. Size every hat to sit on top of that character's big round fishbowl helmet (each hat about half the helmet's width), matching the references' outline weight and shading exactly. Real colors only: avoid plain neutral grey, avoid magenta and hot pink.

Arrange in a neat grid of 4 columns x 3 rows, one item centered per cell, generous empty space between items, nothing touching. Each row holds two hats; each hat appears as a pair (side view, then front view) next to each other.
Row 1: (1) retro trucker cap in teal and cream with a tiny rocket patch, side view; (2) the same cap, front view; (3) a 1950s cream-and-coral paper diner hat, side view; (4) the same diner hat, front view.
Row 2: (5) a mustard yellow hard hat, side view; (6) the same hard hat, front view; (7) a cobalt knitted beanie with a cream pom-pom, side view; (8) the same beanie, front view.
Row 3: (9) a tan cowboy hat with a coral band, side view; (10) the same cowboy hat, front view; (11) a tall cream chef toque, side view; (12) the same toque, front view.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no gradient, no outer glow. No text, no labels, no numbers.
```

#### 43B · Hats 7–12 (side + front)

```
Clean 2D cartoon game sprites for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Warm 1970s palette: amber #F5A54A, cream #F4E6C8, coral #E8574A, teal #2F6F73, seafoam #7FC8B8, plum #3D2A4F, mustard yellow, tomato red, cobalt blue. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

A sheet of 6 cosmetic HATS for the crew character in the attached references. Each hat is drawn ALONE (no character, no helmet, no antenna) TWICE: once in SIDE VIEW facing right and once in FRONT VIEW, matching the two views of the character in the attached reference. Size every hat to sit on top of that character's big round fishbowl helmet (each hat about half the helmet's width, the headphones and afro can be wider), matching the references' outline weight and shading exactly. Real colors only: avoid plain neutral grey, avoid magenta and hot pink.

Arrange in a neat grid of 4 columns x 3 rows, one item centered per cell, generous empty space between items, nothing touching. Each row holds two hats; each hat appears as a pair (side view, then front view) next to each other.
Row 1: (1) a striped plum-and-cream sleepy nightcap with a bobble, side view; (2) the same nightcap, front view; (3) a tiny amber cone party hat with a coral tassel, side view; (4) the same party hat, front view.
Row 2: (5) big chunky retro headphones in amber and plum that wrap over the top of the helmet, side view; (6) the same headphones, front view; (7) a flower crown with small cream daisies, coral blossoms and green leaves, side view; (8) the same flower crown, front view.
Row 3: (9) a fluffy dark-brown 1970s afro wig shaped to sit on top of the helmet, side view; (10) the same afro, front view; (11) a propeller beanie in amber, coral and teal segments, side view; (12) the same propeller beanie, front view.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no gradient, no outer glow. No text, no labels, no numbers.
```

#### 44N · Antenna toppers + backpacks (side view)

```
Clean 2D cartoon game sprites for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Warm 1970s palette: amber #F5A54A, cream #F4E6C8, coral #E8574A, teal #2F6F73, seafoam #7FC8B8, plum #3D2A4F, mustard yellow, cobalt blue. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

A sheet of 16 cosmetic items for the crew character in the attached references, each drawn ALONE in SIDE VIEW facing right, matching the references' outline weight, shading and scale exactly. Avoid magenta and hot pink.

Arrange in a neat grid of 4 columns x 4 rows, one item centered per cell, generous empty space between items, nothing touching.
Rows 1-2, ANTENNA TOPPERS (each replaces the small round ball on the tip of the antenna; about the size of that ball, up to twice as big; real colors only, no plain grey): (1) a little mustard star; (2) a coral heart; (3) a cream crescent moon; (4) a pair of red cherries; (5) a glowing amber lightbulb; (6) a googly eyeball; (7) a tiny teal satellite dish; (8) a little ringed planet in seafoam and amber.
Rows 3-4, BACKPACKS (each replaces the boxy backpack on the character's back, same size and position as in the attached reference; the main body in NEUTRAL LIGHT GREY so it takes the player's color, details in real colors): (9) a retro jetpack with two little thrusters and amber flame tips drawn inside their outlines; (10) a big thermos with a cream cap; (11) a metal lunchbox with a cream-amber-coral stripe; (12) a chunky cassette player with an orange headphone wire; (13) a tiny plant-pot backpack with real green leaves; (14) a mini space heater with glowing amber coils; (15) a parachute pack with cream straps; (16) a toolbox with a wrench sticking out.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no gradient, no outer glow. No text, no labels, no numbers.
```

#### 45N · Visors + chest decals (side + front)

```
Clean 2D cartoon game sprites for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise, no photorealism. Warm 1970s palette: amber #F5A54A, cream #F4E6C8, coral #E8574A, teal #2F6F73, seafoam #7FC8B8, plum #3D2A4F, mustard yellow, cobalt blue. Any glow stays strictly inside each object's outline: no outer glow, no halos, no drop shadows.

A sheet of 8 cosmetic items for the crew character in the attached references, each drawn ALONE TWICE: once matching the SIDE VIEW and once matching the FRONT VIEW of the character in the attached reference, at exactly the reference's scale. Real colors only: no plain neutral grey, no magenta or hot pink.

Arrange in a neat grid of 4 columns x 4 rows, one item centered per cell, generous empty space between items, nothing touching. Each item appears as a pair (side view, then front view) next to each other.
Rows 1-2, VISORS (each replaces the glowing amber visor inside the dark helmet: in side view the same tall narrow footprint as the reference's side visor, in front view the same wide rounded footprint as the reference's front visor; no eyes, no mouth): (1-2) dark plum aviator-sunglasses visor with a cream shine; (3-4) glowing coral heart-shaped visor; (5-6) glowing mustard star-shaped visor; (7-8) glowing amber retro LED-dot visor forming a simple smile pattern.
Rows 3-4, CHEST DECALS (each replaces the small vertical striped tab on the chest: in front view a flat patch the size of that tab, in side view the same patch seen edge-on as a narrow curved sliver): (9-10) a blank cream name-tag patch with a plum stitched border, no text; (11-12) an amber lightning bolt; (13-14) a mustard smiley face; (15-16) coral and amber hot-rod flames.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no gradient, no outer glow. No text, no labels, no numbers.
```

---

## 12. Fix-it phrases (reply in the same chat)

| Problem | Say this |
|---|---|
| Body came out bean-shaped | "Keep everything else identical, but make the body a short squat gumdrop with a wide round bottom, much shorter, with clearly separate stubby legs." |
| Dome is see-through / shows the background | "Keep everything identical, but fill the inside of the helmet dome with solid opaque dark midnight indigo #1B1830. Nothing may be see-through." |
| Suit has a color cast | "Keep everything identical, but make all suit parts pure neutral grey with zero color tint." |
| Eyes or a face appeared | "Remove the eyes and mouth. The face is only the smooth glowing amber visor shape." |
| Glow or halo spills past edges | "Keep everything identical, but remove every outer glow, halo and light ray. Glows must stay inside the objects' outlines." |
| Black outlines | "Change all outlines to dark plum #2A1E35, the same weight everywhere." |
| Shadows or a floor under sprites | "Remove all shadows and any floor. The background must be one perfectly flat #00FF00 color." (or #FF00FF for magenta sheets) |
| Items touching or overlapping | "Spread the items out so each sits alone in the center of its grid cell with wide empty space around it." |
| Labels or text appeared | "Remove all text, labels and numbers." |
| Wrong item count or order | "There must be exactly N items in a C × R grid, in this order: …" (paste the row list again) |
| Room camera too flat or too angled | "Keep the room identical, but match the camera angle of the attached Galley exactly: top-down three-quarter view, about 35 degrees, orthographic." |
| Doorway missing or in the wrong place | "Keep everything identical, but put the doorways exactly here: …" (paste the doorway line) |
| Room floor too cluttered | "Keep the walls identical, but clear the floor: fewer objects, larger open walkable areas." |
| Style drifted from the anchors | "Match the attached references exactly: same outline weight, same flat two-tone shading, same palette, same level of detail." |
| Gradients or a painterly look | "Use flat two-tone cel shading only: one base color and one shadow color per area, no gradients." |
| Logo misspelled | "The text must read exactly GRAVEYARD SHIFT, letter by letter: G R A V E Y A R D / S H I F T. Change nothing else." |
| Pixel art is blurry | "Use crisp hard square pixels only, no anti-aliasing, no smoothing, on a strict 32 × 64 pixel grid shown enlarged." |

---

## 13. When you're done

1. All chosen images are in **`art/raw/`**, named `NN_NAME.png`, plus any `_alt` variants and `.txt` prompt edits.
2. Tell me. I'll review every image against the art direction, flag anything that needs a regeneration (with the exact fix prompt), then slice, key, trim, and pack everything into `frontend/public/assets/ship/`.
3. You get contact sheets of every cut asset to upload to the team drive.
