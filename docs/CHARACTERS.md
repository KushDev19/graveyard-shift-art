# GRAVEYARD SHIFT: Characters and Prompt Book

> **For:** the teammate generating the crew character art and cosmetics (Nano Banana Pro).
> **Goal:** produce every character asset the game needs, in a form that can be cut up and animated in code.
> **Bigger picture:** [ART_DIRECTION_RESEARCH.md](ART_DIRECTION_RESEARCH.md) (whole art direction) · [USER_STORIES.md](USER_STORIES.md) (what the game does).
> **UPDATE:** the **walking puppet** is **SVG**, traced from the approved model sheet (sheet 03 is no longer generated). Master: `frontend/public/assets/ship/crew/crew_puppet.svg`; built outputs: `crew_parts.png/.json` (Phaser atlas) and `crew_rig.json` (offsets, pivots, tint flags, draw order); rebuild with `py -3.12 art/work/build_crew.py`. Live animation reference (idle/walk/run/ghost/impostor/hop, 10 colors): open `frontend/public/assets/ship/crew/puppet_demo.html`.
> **Poses** (reveal, meeting, win, knocked-out, ghost, ejected, sneak) are full **Gemini illustrations** (prompts 04A–04E in PROMPT_BOOK.md), keyed with `art/work/key_poses.py` into `poses/pose_<name>.png` + `_suit.png` (tint layer) + `_fixed.png`. The design rules below still describe the look.
>
> **RENDERING RULE (decided):** whenever a *specific player* is on screen, they are drawn from the **SVG puppet** so their color **and cosmetics** always show: in-game (side view), role reveal lineup (front view: local player centered and larger, others beside; crewmate screen shows everyone, impostor screen shows only the impostor team with coral visors and the smug half-lid visor), meeting vote cards (front head-and-shoulders), ejection (tumbling puppet), win/lose lineups (front view, arms up), ghosts (puppet ghost mode, cosmetics kept). The knocked-out map marker uses the tinted Gemini pose. Gemini poses are otherwise **flavor art only** (title, loading, how-to-play, lobby posters). Cosmetics therefore need side + front views (prompts 43A, 43B, 44N, 45N).
>
> **Deadline context:** the Wizard-of-Oz demo is **Fri Oct 16**. Tier 1 (sections 7.1–7.3) is needed for it. Cosmetics (7.4–7.6) are a stretch goal.

---

## 1. The 60-second brief

- **Game:** *GRAVEYARD SHIFT*, an Among Us-style social deduction game inside Covey.Town. The crew works the 3 a.m. shift on the **Nightjar**, a cozy 1970s retro-future cargo ship. Some of the crew are Impostors.
- **Style:** clean 2D cartoon, flat 2-tone cel shading, dark plum outlines, cozy and funny, not scary.
- **The crew:** a squat, goofy little astronaut with a giant fishbowl helmet and a glowing amber visor for a face. **Our own design**: funny like Among Us crewmates, but clearly not a copy.
- **How it's animated:** we do **not** draw animation frames. You generate the character **once, as separate body parts**, and the game assembles and animates them in code (waddle, wobble, squash, ghost float). So the job is **clean, consistent parts**, not drawings in motion.
- **How you generate:** many items per image (**batch sheets**) in a grid on a flat chroma-key background. They get sliced automatically afterwards. You never cut anything out by hand.

---

## 2. Golden rules (read before generating anything)

1. **Grey = tintable.** The suit is drawn in **neutral grey (no color tint at all)**. The game recolors grey pixels into each player's color, and everything that isn't neutral grey keeps its own color. So:
   - Suit, arms, legs, backpack body: **neutral grey** (white to mid grey, shaded with darker neutral grey).
   - Visor, stripe, outlines, helmet interior, cosmetics: **real colors**, never neutral grey.
   - Cosmetics must **avoid neutral grey** (use warm or cool tinted greys instead), or they'll get recolored too.
2. **Flat chroma background.** Crew sheets use pure green **#00FF00**; cosmetics sheets use pure magenta **#FF00FF**. Perfectly flat, no shadow under feet, no floor, no gradient.
3. **No see-through anything.** The background must never show through an object. The helmet dome has a **dark indigo interior** (that's how it reads as glass, plus a white highlight), not clear glass.
4. **Grid, gutters, no touching.** One item per grid cell, centered, with wide empty space around it. Items never touch or cross into another cell.
5. **No text.** No labels, numbers, captions, or letters anywhere. Items are identified by grid position.
6. **Side view faces RIGHT.** The game mirrors it for left. Everything in the parts and cosmetics sheets is in **side view facing right**, unless the prompt says otherwise.
7. **Same scale, same light.** Every item in a sheet at the same scale, lit from the top-left.
8. **Attach the references.** Once the model sheet (A0.2) is approved, **attach it to every later prompt**. That's what keeps everything consistent.
9. **4K, 2–4 variants, pick the best, then fix by chatting.** Use Nano Banana Pro at 4K. If a variant is 90% right, don't re-roll; reply in the same chat: "Keep everything identical, but …".

---

## 3. Character design spec

### 3.1 Design

| Feature | Spec |
|---|---|
| **Body** | Short, **squat, round-bottomed**, shaped like a gumdrop or thermos. Chunky and huggable. About **2 heads tall** including the helmet. **Not** a bean or capsule. |
| **Legs** | Two short stubby legs with rounded boots |
| **Arms** | Two tiny stubby **mitten** arms, held close to the body by default |
| **Helmet** | **Oversized fishbowl dome** on top of the body, with a chunky rounded rim/collar where it meets the suit. The inside of the dome is **dark midnight indigo** (not see-through), with a soft white curved glass highlight on the upper left. |
| **Face** | A big smooth **glowing amber visor** (rounded rectangle) floating inside the dark dome. **No eyes, no mouth, no face**: the visor is the face. Expressions come from visor shape variants (blink, surprise). |
| **Antenna** | Thin stalk out of the top of the dome with a small round ball on the tip. It wobbles in-game. |
| **Backpack** | Small boxy 1970s backpack on the back |
| **Stripe** | Cream, amber, and coral **triple racing stripe** across the chest (and repeated on the backpack) |
| **Personality** | Goofy, lovable, a bit clumsy. Comedy comes from **proportions** (tiny legs, huge helmet) and **motion** (waddle). |
| **Avoid** | Bean shape, a visor set directly into the body, realistic proportions, a human face, black outlines, gradients, texture noise |

### 3.2 Palette

| Role | Hex |
|---|---|
| Outline (all outlines, never black) | `#2A1E35` dark plum |
| Helmet interior | `#1B1830` midnight indigo |
| Visor (default) | `#F5A54A` amber, with a lighter inner glow |
| Visor (Impostor partner view) | `#E8574A` coral |
| Stripe | cream `#F4E6C8` · amber `#F5A54A` · coral `#E8574A` |
| Glass highlight | white / cream |
| Suit base | **neutral grey** (light, about `#E6E6E6`, shaded to about `#A0A0A0`) |

### 3.3 Crew colors (10, applied by the game as tints)

These are the **target** look in-game. You only draw grey; the hex values tell you what the bottom-row color previews in the model sheet should look like.

| Color | Target hex | Color | Target hex |
|---|---|---|---|
| Tomato | `#E4483C` | Sky | `#6EC3F0` |
| Tangerine | `#F28A2E` | Cobalt | `#3F5FD9` |
| Mustard | `#E9C046` | Grape | `#8E5AC8` |
| Lime | `#A6D64A` | Bubblegum | `#F07BB5` |
| Mint | `#6FD6B0` | Cream | `#F4E6C8` |

### 3.4 In-game size

The character is about **256 px tall in the game world** (about 128 px on a 1080p screen). Sheets are generated at 4K, so each part comes out much larger than needed. That's intentional: it's downscaled cleanly.

---

## 4. How the puppet works (why the parts matter)

The game stacks the parts like paper cut-outs (back to front):

```
back arm → back leg → backpack → body → stripe → front leg → front arm → helmet dome → visor → glass highlight → antenna → (hat)
```

Code then animates them:

| State | What code does with the parts |
|---|---|
| Idle | Slow breathing bob; visor blinks now and then (visor swaps to `visor_blink`) |
| Walk | Body rocks ±6°, legs swing alternately, arms swing opposite, antenna lags and wobbles |
| Surprised (meeting called) | Visor swaps to `visor_surprised`, little hop |
| Ghost | Legs are swapped for `ghost_tail`, everything at 50% opacity, slow float |
| Eliminated | The `fallen_suit` + `fallen_helmet` props are left on the floor |
| Ejected | Whole puppet tumbles out of the airlock (rotation along a path) |
| Impostor partner view | Visor swaps to `visor_coral` (only Impostors see this on each other) |

**This means each part must be drawn COMPLETE**, including the bits that are normally hidden behind other parts (the top of a leg that goes under the body, the part of the antenna inside the dome rim). Hidden overlap areas get covered in-game; missing ones leave holes.

---

## 5. Cosmetics system (stretch goal)

Players pick cosmetics in the Locker Room (lobby). Purely visual, no gameplay effect.

| Slot | Attaches to | Notes |
|---|---|---|
| `hat` | Top of the helmet dome | Equipping a hat **hides the antenna**, so hats are drawn without an antenna |
| `antenna_topper` | Replaces the antenna ball | Only visible when no hat is worn |
| `backpack` | Back (replaces the default backpack) | Grey areas get the player color |
| `visor` | Replaces the default visor inside the dome | Same size and position as the default visor |
| `decal` | Chest (replaces the racing stripe) | Flat graphic on the suit |

**Cosmetic rules:**
- Side view facing right, sized to fit the character in the attached model sheet.
- Hats and toppers must **not cover the visor**.
- Avoid neutral grey (it would get tinted), except backpack bodies, which should be grey so they match the suit.
- Avoid pure magenta or hot pink, which would be keyed out on the magenta background (use coral or bubblegum-ish warm pinks instead).

---

## 6. Workflow and delivery

1. Generate in this order: **A0.2 → SH-CREW → SH-CREW-POSES →** (stretch) **SH-COS-1 → SH-COS-2 → SH-COS-3**.
2. **A0.2 must be approved by the team first.** It is the design lock, and every later prompt attaches it.
3. For each sheet, run the prompt, generate 2–4 variants, and pick the best. Fix small issues by chatting in the same thread.
4. Before sending, run the **review checklist** (§8).
5. **Deliver** the full-resolution PNG (**never a screenshot or a compressed copy**) to the shared drive / team chat, named:
   `<SHEET-ID>_v<N>.png` (e.g. `SH-CREW_v2.png`)
   They go into `art/raw/<SHEET-ID>/` and get sliced by script. You'll get back a contact sheet of every cut part to double-check.
6. Paste the **exact final prompt** you used (including any follow-up edits) next to the image (`<SHEET-ID>_v<N>.txt`), so it can be regenerated later.

---

## 7. Prompt Book

> ⚠️ **Superseded by [PROMPT_BOOK.md](PROMPT_BOOK.md)** (IDs 00, 03, 04, 43–45). Those versions add the "glows stay inside outlines" rule and the file naming. Use them; this section is kept only for reference.

Every prompt below is **complete and copy-paste ready** (the style block is already inside). Settings for all of them: **Nano Banana Pro, 4K**, aspect ratio as listed.

### 7.1 A0.2: Model sheet (DESIGN LOCK) · 16:9 · attach: nothing

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. 1970s retro-future spaceship aesthetic: rounded rectangles, chunky bevels, cream-amber-coral triple racing stripes. Flat two-tone cel shading with soft glows, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no texture noise, no photorealism. Palette: midnight indigo #1B1830, plum #3D2A4F, teal steel #2F6F73, seafoam #7FC8B8, amber #F5A54A, cream #F4E6C8, coral #E8574A. Cozy, playful, slightly mysterious; not horror.

Character model sheet for one original mascot character: a crew member of a cozy 1970s retro-future cargo spaceship. The same character is shown 6 times in a neat grid of 3 columns × 2 rows, each figure centered in its cell with generous empty space between figures; no figure touches another.

Top row, all with a plain NEUTRAL LIGHT GREY suit (pure grey, no color tint, shaded with darker neutral grey): (1) side view facing right, standing neutral; (2) front view, standing neutral; (3) three-quarter view, standing neutral.
Bottom row, side view facing right, mid-waddle with one leg forward: (4) tomato-red suit, (5) mint suit, (6) mustard-yellow suit.

Character design: a short, squat, round-bottomed body shaped like a gumdrop or a thermos, about two heads tall, chunky and huggable. Two short stubby legs with rounded boots. Two tiny stubby mitten arms held close to the body. An oversized fishbowl dome helmet sits on top with a chunky rounded rim collar where it meets the suit; the inside of the dome is solid dark midnight indigo (#1B1830), not see-through, with a soft white curved glass highlight on the upper left. Floating inside the dark dome is a big smooth glowing AMBER visor shaped like a rounded rectangle. No eyes, no mouth, no face: the visor IS the face. A thin antenna sticks up from the top of the dome with a small round ball on the tip. A small boxy 1970s backpack on the back. A cream-amber-coral triple racing stripe runs across the chest. Goofy, lovable, funny proportions: tiny legs, huge helmet. An original design: not a bean or capsule shape, not a visor set directly into the body.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no gradient, no vignette. Nothing is transparent or see-through. All six figures at exactly the same scale, same lighting from the top-left. No text, no labels, no numbers, no captions.
```

**Approve when:** the silhouette reads instantly at thumbnail size, it's clearly *not* a bean, the top-row suit is truly grey, and it's funny. Save the approved one as the anchor; it gets attached to everything after.

---

### 7.2 SH-CREW: Puppet parts · 1:1 · attach: approved A0.2

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise. Palette: midnight indigo #1B1830, amber #F5A54A, cream #F4E6C8, coral #E8574A, seafoam #7FC8B8.

A game sprite parts sheet ("exploded view") of the crew character in the attached model sheet, for cut-out puppet animation. Match the attached character's design, proportions, outline weight and shading EXACTLY. Every part in side view facing right, at the same scale as if the character were assembled, each part drawn COMPLETE including areas that would normally be hidden behind other parts. All suit parts in NEUTRAL LIGHT GREY (pure grey, no color tint), shaded with darker neutral grey.

Arrange 16 separate parts in a neat grid of 4 columns × 4 rows, one part centered per cell, with generous empty space between parts; no part touches another.
Row 1: (1) body: torso and round bottom only, no arms, no legs, no helmet, no stripe; (2) chest racing stripe decal only, cream-amber-coral, shaped to the chest curve; (3) backpack: boxy, grey, with a small cream-amber-coral stripe; (4) antenna: thin stalk with round ball tip.
Row 2: (5) helmet dome: fishbowl dome with chunky rim collar, solid dark midnight indigo interior, no visor, no highlight; (6) visor: glowing amber rounded rectangle; (7) the same visor in glowing coral red; (8) glass highlight only: the soft white curved shine shape for the dome.
Row 3: (9) front arm: tiny stubby mitten arm; (10) back arm: same but slightly darker grey; (11) front leg: stubby leg with rounded boot; (12) back leg: same but slightly darker grey.
Row 4: (13) ghost tail: a soft wispy rounded tail shape that replaces the legs for a ghost, light grey; (14) visor variant: glowing pale seafoam (ghost visor); (15) visor variant: amber, squinted half-closed (blink); (16) visor variant: amber, round "O" shape (surprised).

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no gradient. Nothing transparent or see-through. No text, no labels, no numbers.
```

**Approve when:** all 16 parts are separate and complete, the suit parts are neutral grey, the visors match in size, and the parts would plausibly fit back together into the model-sheet character.

---

### 7.3 SH-CREW-POSES: Full-body poses and fallen marker · 16:9 · attach: approved A0.2 (+ SH-CREW)

These are used on the role-reveal, meeting, and win/lose screens, and as the "fallen" marker on the map.

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise. Palette: midnight indigo #1B1830, amber #F5A54A, cream #F4E6C8, coral #E8574A.

A pose sheet of the crew character in the attached references. Match the design, proportions, outline weight and shading EXACTLY. The suit is NEUTRAL LIGHT GREY (pure grey, no color tint) in every pose; the helmet interior stays dark midnight indigo with the glowing amber visor; the chest keeps its cream-amber-coral stripe.

Arrange 8 items in a neat grid of 4 columns × 2 rows, one item centered per cell, generous empty space between items, nothing touching.
Row 1: (1) front view hero pose, standing proud with mitten fists on hips; (2) three-quarter view, arms crossed, smug and confident (the impostor-reveal pose); (3) side view facing right, waving one mitten hand cheerfully; (4) side view facing right, pointing forward accusingly with one mitten arm, leaning in, "it was them!"
Row 2: (5) front view, shrugging with both arms out, "who, me?"; (6) front view, jumping and cheering with both arms up; (7) the FALLEN SUIT: the empty grey suit deflated flat on the ground like a sad balloon, seen from the side, with the backpack and stripe still visible, no helmet, a few small cartoon stars above it; slapstick and funny, not gory, no blood; (8) the fishbowl helmet alone, rolled over onto its side, visor dimmed, with a tiny dizzy swirl.

Isolated on a perfectly flat, uniform pure green #00FF00 background: no shadows, no floor, no gradient. No text, no labels, no numbers.
```

**Approve when:** every pose is clearly the same character, the suits are grey, the fallen marker is funny and PG, and items 7 and 8 are separate.

---

### 7.4 SH-COS-1: Hats (stretch) · 16:9 · attach: approved A0.2

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients, no texture noise. Warm 1970s palette: amber #F5A54A, cream #F4E6C8, coral #E8574A, teal #2F6F73, seafoam #7FC8B8, plum #3D2A4F, mustard, tomato red, cobalt blue.

A sheet of 12 cosmetic HATS for the crew character in the attached model sheet. Each hat drawn ALONE (no character), in side view facing right, sized to sit on top of that character's fishbowl dome helmet, matching its outline weight and shading exactly. Hats use real colors only; avoid plain neutral grey and avoid magenta or hot pink.

Arrange in a neat grid of 4 columns × 3 rows, one hat centered per cell, generous empty space between hats, nothing touching.
Row 1: (1) retro trucker cap with a tiny rocket patch; (2) 1950s paper diner hat; (3) yellow hard hat; (4) knitted beanie with a pom-pom.
Row 2: (5) cowboy hat; (6) tall chef toque; (7) striped sleepy nightcap with a bobble; (8) tiny cone party hat with a tassel.
Row 3: (9) big chunky retro headphones; (10) flower crown with small daisies and leaves; (11) fluffy 1970s afro wig; (12) propeller beanie.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no gradient. No text, no labels, no numbers.
```

---

### 7.5 SH-COS-2: Antenna toppers and visors (stretch) · 16:9 · attach: approved A0.2 + SH-CREW

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients. Warm 1970s palette: amber #F5A54A, cream #F4E6C8, coral #E8574A, seafoam #7FC8B8, mustard, cobalt, plum.

A sheet of 12 cosmetic items for the crew character in the attached references, each drawn ALONE in side view facing right, matching the references' outline weight and shading exactly. Avoid plain neutral grey and avoid magenta or hot pink.

Arrange in a neat grid of 4 columns × 3 rows, one item centered per cell, generous empty space, nothing touching.
Row 1, ANTENNA TOPPERS (each replaces the small ball on the tip of the antenna, same size as that ball, slightly bigger is fine): (1) a little yellow star; (2) a red heart; (3) a crescent moon; (4) a pair of cherries.
Row 2, more ANTENNA TOPPERS: (5) a glowing lightbulb; (6) a googly eyeball; (7) a tiny satellite dish; (8) a little ringed planet.
Row 3, VISORS (each replaces the glowing amber visor inside the dark dome; same size and shape footprint as the visor in the attached parts sheet): (9) dark aviator sunglasses visor with a shine; (10) glowing heart-shaped visor; (11) glowing star-shaped visor; (12) glowing pixel-grid "retro LED" visor showing a smiling pattern.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no gradient. No text, no labels, no numbers.
```

---

### 7.6 SH-COS-3: Backpacks and chest decals (stretch) · 16:9 · attach: approved A0.2 + SH-CREW

```
Clean 2D cartoon illustration for a cozy retro-futurist sci-fi video game. Flat two-tone cel shading, uniform medium-weight dark plum outlines (#2A1E35), no black outlines, no gradients. Warm 1970s palette: amber #F5A54A, cream #F4E6C8, coral #E8574A, seafoam #7FC8B8, teal #2F6F73, mustard, cobalt.

A sheet of 12 cosmetic items for the crew character in the attached references, each drawn ALONE in side view facing right, matching the references' outline weight and shading exactly.

Arrange in a neat grid of 4 columns × 3 rows, one item centered per cell, generous empty space, nothing touching.
Row 1, BACKPACKS (each replaces the default boxy backpack, same size, same attachment side; main body in NEUTRAL LIGHT GREY so it takes the player's color, details in real colors): (1) a retro jetpack with two little thrusters and amber flame tips; (2) a big thermos; (3) a metal lunchbox with a cream-amber-coral stripe; (4) a chunky cassette player with orange headphones wire.
Row 2, more BACKPACKS: (5) a tiny potted plant in a backpack pot (leaves real green); (6) a mini space-heater with glowing coils; (7) a parachute pack with straps; (8) a toolbox with a wrench sticking out.
Row 3, CHEST DECALS (flat graphics that replace the chest racing stripe, curved to the chest, real colors, no grey): (9) a cream name-tag patch shape (blank, no text); (10) an amber lightning bolt; (11) a mustard smiley face; (12) coral and amber hot-rod flames.

Isolated on a perfectly flat, uniform pure magenta #FF00FF background: no shadows, no gradient. No text, no labels, no numbers.
```

---

## 8. Review checklist (before sending a sheet)

- [ ] Background is **flat** pure green (crew) or pure magenta (cosmetics), with no shadows, gradient, or floor
- [ ] **Nothing is see-through**: the dome interior is solid dark indigo
- [ ] Every item is **separate**, centered in its cell, and touches nothing else
- [ ] The **count and order** match the prompt's list (row by row, left to right)
- [ ] **No text**, numbers, or labels anywhere
- [ ] Suit parts are **neutral grey** with no color tint (zoom in: no blue or beige cast)
- [ ] Cosmetics have **no neutral grey** (except backpack bodies) and no magenta or hot pink
- [ ] Outlines are **dark plum, not black**, and the same weight everywhere
- [ ] **Side views face right**
- [ ] Matches the A0.2 model sheet (proportions, helmet size, visor shape)
- [ ] No visible watermark in the corners
- [ ] Saved as a **full-resolution PNG**, with the prompt text next to it

---

## 9. Fix-it phrases (reply in the same chat)

| Problem | Say this |
|---|---|
| Body came out bean-shaped | "Keep everything else identical, but make the body a short squat gumdrop shape with a wide round bottom, much shorter, with clearly separate stubby legs." |
| Dome is see-through / shows green | "Keep everything identical, but fill the inside of the helmet dome with solid dark midnight indigo #1B1830. Nothing may be see-through." |
| Suit is tinted (bluish or beige) | "Keep everything identical, but make all suit parts pure neutral grey with no color tint at all." |
| Eyes or a face appeared | "Remove the eyes and mouth. The face is only the smooth glowing amber visor shape, nothing else." |
| Black outlines | "Change all outlines to dark plum #2A1E35, same weight everywhere." |
| Shadows or a floor under items | "Remove all shadows and any floor. The background must be a single perfectly flat #00FF00 color." |
| Items touching or overlapping | "Spread the items out so each sits alone in the center of its grid cell with wide empty space around it." |
| Labels or text appeared | "Remove all text, labels and numbers." |
| Wrong number of items | "There must be exactly N items in a 4 × M grid, in this order: …" (paste the row list again) |
| Style drifted from the model sheet | "Match the attached model sheet exactly: same proportions, same outline weight, same flat shading, same helmet size." |
| Parts incomplete (hidden areas missing) | "Draw each part complete as a standalone cut-out, including the areas that would be hidden behind other parts." |
| Gradients or a painterly look | "Use flat two-tone cel shading only: one base color and one shadow color per area, no gradients." |

---

## 10. What happens after delivery (for context)

1. The sheet is sliced by script: background removed, green fringe cleaned, each item cropped, trimmed, and named by grid position (`crew_body`, `crew_visor_blink`, `cos_hat_cowboy`, …).
2. You get back a **contact sheet** (every cut item on a checkerboard with its name) to confirm nothing was mis-cut.
3. Parts are packed into a sprite atlas and assembled into the puppet in Phaser; pivots and cosmetic anchor offsets are tuned in-engine.
4. If a part doesn't line up when assembled, you may be asked for a targeted re-generation of just that part (same chat, "Keep everything identical, but …").

| Sheet | Tier | Needed for |
|---|---|---|
| A0.2 | 0 (design lock) | Everything |
| SH-CREW | 1 | In-game character, ghosts, Impostor partner view |
| SH-CREW-POSES | 1 | Role reveal, meeting, win/lose screens, fallen marker |
| SH-COS-1/2/3 | 3 (stretch) | Locker Room wardrobe customization |
