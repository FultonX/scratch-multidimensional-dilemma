# Project Brief: The Multidirectional Dilemma — Scratch-to-Pygame Port

## Codex assignment

Build a complete, playable Pygame port of the supplied Scratch 3 project:

`TheMultidirectionalDilemma.sb3`

Treat the `.sb3` file and its `project.json` as the source of truth. Do not make a generic platformer inspired by the Scratch game, do not implement a Scratch interpreter, and do not stop after scaffolding. Rebuild the game as clean, maintainable Python while preserving the original levels, movement, wraparound mechanic, collisions, art, animation, audio, dialogue, transitions, and ending.

The finished game must run locally with:

```bash
python main.py
```

after installing the documented requirements.

## Product summary

The Multidirectional Dilemma is a 14-level pixel-art platform game set in a mechanical facility. The player is a small robot/test subject. The defining mechanic is multidirectional screen wrapping: moving through the left or right edge enters from the opposite side, and moving through the top or bottom does the same vertically.

The game contains:

- 14 level layouts.
- Pixel-perfect terrain and hazard collisions derived from level costume alpha masks.
- Horizontal and vertical screen wrapping.
- Animated player movement, jumping, falling, and death.
- A rotating goal used to advance through levels 1–13.
- Spikes and rotating/moving saw hazards.
- Keys in levels 7, 10, and 13 that change which platforms are active.
- An assistant robot that appears for voiced dialogue.
- A CEO/boss-screen sequence in level 14.
- A scripted ending with seven final text cards.
- Background music, voice acting, and sound effects from the original project.

The source contains 17 Scratch targets, 106 PNG costume references, 59 SVG costume references, and 73 WAV sound references. Preserve the original assets rather than replacing them with approximations.

## Primary goals

1. Reproduce the original gameplay closely enough that every level can be completed using the same routes and mechanics as the Scratch version.
2. Preserve the original pixel art, voice lines, music, timing, dialogue text, and ending.
3. Make the implementation understandable and maintainable instead of directly mirroring every Scratch block.
4. Use data-driven level, dialogue, and asset definitions where practical.
5. Keep runtime dependencies minimal and make setup reliable on Windows.

## Non-goals for the first release

- Do not redesign levels.
- Do not rewrite dialogue.
- Do not replace original graphics or audio.
- Do not add combat, inventories, scoring, checkpoints, or mechanics not present in the Scratch project.
- Do not “improve” movement values until a faithful baseline is playable.
- Do not require the Scratch website or an internet connection at runtime.
- Do not build a general-purpose `.sb3` execution engine.

## Technical baseline

- Language: Python 3.11 or newer.
- Framework: Pygame.
- Logical game resolution: exactly 480 × 360, matching the Scratch stage.
- Default display: 960 × 720, displaying the logical canvas at 2× scale.
- Window should be resizable while retaining the 4:3 aspect ratio with integer scaling when possible and letterboxing otherwise.
- Use nearest-neighbor scaling for the pixel-art game canvas.
- Physics/update rate: fixed 30 updates per second to approximate Scratch timing.
- Render rate: 60 frames per second or display refresh rate, with interpolation optional but not required.
- Audio and dialogue timers should use elapsed real time, not frame counts.

## Required repository structure

A structure similar to the following is preferred. Reasonable refinements are allowed, but keep responsibilities separated.

```text
TheMultidirectionalDilemma/
├── main.py
├── requirements.txt
├── README.md
├── source/
│   └── TheMultidirectionalDilemma.sb3
├── game/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── states.py
│   ├── assets.py
│   ├── audio.py
│   ├── coordinates.py
│   ├── level.py
│   ├── player.py
│   ├── entities.py
│   ├── dialogue.py
│   ├── transition.py
│   └── finale.py
├── data/
│   ├── levels.json
│   ├── dialogue.json
│   └── asset_manifest.json
├── assets/
│   ├── generated/
│   │   ├── images/
│   │   └── audio/
│   └── README.md
├── tools/
│   ├── extract_sb3.py
│   └── validate_assets.py
└── tests/
    ├── test_coordinates.py
    ├── test_level_data.py
    ├── test_player_physics.py
    ├── test_wrapping.py
    └── test_smoke.py
```

Commit the generated runtime assets so that a normal player does not need SVG-conversion tooling. The extraction tool must remain available so the generated assets can be reproduced from the original `.sb3`.

## SB3 extraction requirements

An `.sb3` file is a ZIP archive. `tools/extract_sb3.py` must:

1. Open `source/TheMultidirectionalDilemma.sb3` with Python's `zipfile` module.
2. Read `project.json`.
3. Extract every referenced costume and sound.
4. Give generated files stable, human-readable names based on target, costume/sound name, and index.
5. Preserve the following metadata in `data/asset_manifest.json`:
   - Scratch target name.
   - Asset kind: costume or sound.
   - Original costume/sound name.
   - Original index.
   - Original `md5ext`.
   - Data format.
   - Bitmap resolution.
   - Rotation center X and Y.
   - Source image dimensions.
   - Default sprite size, direction, rotation style, visibility, and layer order where relevant.
6. Convert SVG costumes to PNG during asset generation. Use a dependable development-time SVG rasterizer, then commit the rasterized results. The shipped game must not need an SVG library.
7. Preserve alpha exactly enough for collision-mask use.
8. Copy WAV files without lossy recompression unless a format issue makes conversion necessary.
9. Avoid collisions between sanitized filenames.
10. Be idempotent: running the extractor twice produces the same output paths and manifest.

Some source assets are duplicated under different logical names. The manifest must preserve every logical reference even if physical files are deduplicated.

## Scratch coordinate and costume conversion

Keep all gameplay internally in Scratch logical coordinates where practical:

- Scratch X increases to the right and is centered at zero.
- Scratch Y increases upward and is centered at zero.
- Screen X = `240 + scratch_x`.
- Screen Y = `180 - scratch_y`.

For bitmap costumes:

```text
render_scale = sprite_size_percent / 100 / bitmapResolution
render_left = screen_x - rotationCenterX * render_scale
render_top  = screen_y - rotationCenterY * render_scale
```

Scale pixel-art assets with nearest-neighbor interpolation. Rotation and flipping must occur around the Scratch rotation center, not merely the image rectangle center, when that distinction affects visible alignment.

SVG costumes use bitmap resolution 1. Rasterize them at sufficient resolution to retain the original appearance at their largest in-game scale.

## Core game states

Use an explicit state machine. Suggested states:

- `BOOT`
- `PLAYING`
- `DIALOGUE`
- `DYING`
- `LEVEL_TRANSITION`
- `FINALE_DIALOGUE`
- `FINAL_CARDS`
- `COMPLETE`
- `PAUSED` only if a user pause feature is added

Do not represent all pauses with scattered booleans. The original Scratch `pause` variable controls player physics while dialogue, death, and transitions continue; express this cleanly in the state machine.

## Player controls

Required controls:

- Left arrow or A: move left.
- Right arrow or D: move right.
- Up arrow or W: jump.
- Escape: quit or open a minimal pause/quit overlay.
- F11: toggle fullscreen.

Preserve the original optional mouse control if practical:

- While left mouse is held, cursor right of stage center moves right.
- Cursor left of stage center moves left.
- Cursor above stage center requests a jump.

Additional controller support is welcome after the faithful keyboard implementation, but it must not delay completion.

## Player physics: preserve order and values

The original movement is frame-based. Reproduce it at a fixed 30 Hz update rate.

Per physics update, preserve this operation order:

1. Select the dedicated `Hitbox` costume/mask for solid collision.
2. Apply gravity: `sy -= 1`.
3. Clamp fall speed: if `sy < -20`, set `sy = -20`.
4. If jump is held, the player is grounded, and `sy > -2`:
   - Play `jump (1)`.
   - Set `sy = 13`.
   - Mark the player airborne.
5. Move vertically by `sy`.
6. Resolve vertical terrain collision.
7. Apply vertical screen wrapping.
8. Apply horizontal input:
   - Right input contributes `+1.2`.
   - Left input contributes `-1.2`.
9. Apply horizontal damping: `sx *= 0.8`.
10. Move horizontally by `sx`.
11. Resolve horizontal terrain collision.
12. Apply horizontal screen wrapping.
13. Select the visible animation frame.
14. Check goal and hazard overlaps.
15. Advance the animation frame counter.

Use floating-point position and velocity but reproduce Scratch's collision feel.

### Solid collision algorithm

The original game moves by the full velocity, then steps the player backward one logical pixel at a time until the hitbox no longer overlaps a solid mask.

- On downward vertical collision, mark the player grounded and set `sy = 0`.
- On upward vertical collision, set `sy = 0` without marking grounded.
- On horizontal collision, set `sx = 0`.
- Safely handle zero velocity; never divide by zero.

Use pixel masks, not only broad rectangles, because the level geometry is authored as irregular costume art.

### Screen wrapping

Preserve the defining mechanic:

- Crossing the right edge wraps to approximately X = -245.
- Crossing the left edge wraps to approximately X = +245.
- Crossing the top or bottom wraps to the opposite Y at approximately ±182.

The Scratch script checks around `abs(x) == 240` and `abs(y) > 182`. Implement robust crossing detection so a large fractional step cannot skip the wrap.

After wrapping, if the player overlaps active solid terrain at the destination, resolve or cancel movement in the same spirit as the source and zero the corresponding velocity.

## Player animation

The player target contains these relevant costumes:

- `Hitbox`
- `idle 1` through `idle 4`
- `run 1` through `run 8`
- `jump`
- `fall`
- `die 1` through `die 11`, with intentionally blank frames among them
- `broken bot`

Required behavior:

- Face right for rightward input and left for leftward input.
- Use left-right flipping rather than free rotation.
- Use `jump` while `sy > 0`.
- Use `fall` while `sy <= 0` and airborne.
- While grounded and moving, cycle the eight run frames using the source frame cadence.
- While grounded and idle, cycle the four idle frames using the source frame cadence.
- Preserve the death flash/animation timing closely:
  - Begin with `die 1`.
  - Advance through the next five costume steps at 0.1-second intervals.
  - Flash visible/invisible three times at 0.2-second intervals.
  - Hide for 0.5 seconds.
  - Respawn.

The original checks hazards with the visible costume after terrain resolution, so hazard/goal overlap may be slightly larger than the solid hitbox. Preserve that distinction by using either the current visual sprite mask or a separately tuned trigger mask for goals and hazards.

## Level data

Store level definitions in `data/levels.json`. Do not hard-code a long nested `if` chain.

Every level entry should reference:

- Background costume.
- Ground costume/mask.
- Spike costume/mask.
- Invisible-platform costume/mask.
- Disappearing-platform costume/mask.
- Player spawn position and facing.
- Goal position, or no goal for level 14.
- Optional key position.
- Optional saw definitions.
- Optional assistant position and dialogue sequence.
- Initial platform visibility/state.

### Player spawn table

| Level | X | Y | Facing | Initial movement state |
|---:|---:|---:|---|---|
| 1 | -200 | -140 | right | playing |
| 2 | 210 | -34 | left | dialogue-paused |
| 3 | -97 | -141 | right | dialogue-paused |
| 4 | -200 | -141 | right | dialogue-paused |
| 5 | -200 | -141 | right | dialogue-paused |
| 6 | 155 | -141 | left | dialogue-paused |
| 7 | 132 | -29 | left | dialogue-paused |
| 8 | 214 | -141 | left | playing |
| 9 | -205 | -11 | right | playing |
| 10 | 205 | -74 | left | dialogue-paused |
| 11 | -180 | 73 | right | dialogue-paused |
| 12 | -190 | 142 | right | playing |
| 13 | -89 | 80 | right | playing |
| 14 | -143 | -139 | right | finale-paused |

On every spawn:

- Reset horizontal and vertical velocity to zero.
- Reset animation frame to the appropriate state.
- Reset grounded/moving flags as in the source.
- Reset the player ghost/opacity effect.
- Place the player near the front, but behind dialogue/transition overlays.

### Goal table

The goal rotates clockwise by 2 degrees per physics update and uses 10% ghost/transparency in the source.

| Level | Goal X | Goal Y |
|---:|---:|---:|
| 1 | 200 | -130 |
| 2 | -181 | -130 |
| 3 | 129 | 3 |
| 4 | -180 | 80 |
| 5 | -180 | 80 |
| 6 | -180 | 80 |
| 7 | 165 | 130 |
| 8 | -175 | -172 |
| 9 | 190 | -145 |
| 10 | -30 | 2 |
| 11 | 121 | 154 |
| 12 | 190 | -135 |
| 13 | -205 | 111 |
| 14 | none | none |

Touching the goal must:

1. Freeze player physics.
2. Begin the transition overlay.
3. Remove current saw instances.
4. Reset key/platform state for the next level.
5. Increment the level only during the transition, matching the original sequence.
6. Respawn into the next level.

## Level-specific mechanics

### Keys and revealed platforms

Keys appear only in:

| Level | Key X | Key Y |
|---:|---:|---:|
| 7 | -140 | -130 |
| 10 | -205 | -131 |
| 13 | 82 | 120 |

The key:

- Is rendered at 200% Scratch size.
- Slowly oscillates its rotation around roughly 80 degrees using the original sine motion.
- Plays `pickupCoin (1)` when collected.
- Hides immediately after collection.

On collection:

- Enable and reveal the level's invisible-platform mask.
- Fade the platform brightness from bright to normal over roughly 20 source steps.
- In level 13, also fade out and disable the disappearing-platform mask.

On death/respawn in levels 7, 10, and 13:

- Restore the key.
- Hide and disable the revealed invisible platforms.
- Restore the disappearing platforms where applicable.

The source variable `Keys Collected` is reset but not meaningfully used. Do not invent a collectible counter.

### Moving saws

Saws begin in levels 11–13. They rotate clockwise by 7 degrees per update. Each saw can also oscillate between its initial position and an endpoint determined by `movement_x` and `movement_y`.

Preserve the source interpretation:

- First move from the starting position by `-movement_x`, `-movement_y` over 10 increments.
- Pause for 1 second.
- Move back to the starting position over 10 increments.
- Pause for 1 second.
- Repeat.

Use a short smooth duration approximating the original 10 Scratch loop iterations rather than teleporting.

Saw definitions:

#### Level 11

| X | Y | Size % | movement_y | movement_x |
|---:|---:|---:|---:|---:|
| 240 | 155 | 700 | 0 | 0 |
| 240 | 90 | 700 | 0 | 0 |
| -177 | 35 | 350 | 0 | -280 |
| -123 | -157 | 750 | 0 | 0 |

#### Level 12

| X | Y | Size % | movement_y | movement_x |
|---:|---:|---:|---:|---:|
| -135 | -115 | 600 | -280 | -320 |
| 5 | 122 | 315 | 0 | 0 |
| 233 | -38 | 650 | 0 | 0 |

#### Level 13

| X | Y | Size % | movement_y | movement_x |
|---:|---:|---:|---:|---:|
| 117 | -15 | 350 | 0 | -130 |
| -27 | -130 | 425 | 55 | 0 |

Destroy all saws on level transition so they do not leak into the next level.

## Terrain and hazard masks

The Scratch targets named below provide one costume per level and are placed at Scratch position `(0, 0)`:

- `background`, rendered at 350% with 30% ghost/transparency in the source.
- `Ground`, rendered at 350% and used as a solid mask.
- `spikes`, rendered at 350% and used as a lethal mask.
- `Invisible platforms`, rendered at 350%, initially disabled unless revealed.
- `disappearing platforms`, rendered at 350%, mainly relevant to level 13.

Build full-stage masks for each level at load time. Cache them; do not rescale and recreate masks every frame.

Blank 1×1 costumes represent absence of geometry and must be handled without errors.

## Dialogue system

Implement dialogue as data, not as one giant hard-coded coroutine.

The assistant appears at the positions below, faces the player using left-right flipping, animates between `costume1` and `costume2` every 0.7 seconds, and has a subtle floating motion.

| Level | Assistant X | Assistant Y | Sequence |
|---:|---:|---:|---:|
| 2 | 0 | 0 | 1 |
| 3 | 0 | 0 | 2 |
| 4 | 0 | -43 | 3 |
| 5 | 0 | -100 | 4 |
| 6 | 64 | 40 | 5 |
| 7 | -33 | 0 | 6 |
| 10 | 40 | -115 | 7 |
| 11 | 95 | -68 | 8 |
| 14 | 15 | -120 | 9/finale |

On normal dialogue sequences:

1. Freeze player movement.
2. Fade the assistant in from high brightness to normal.
3. Position each text-card costume approximately 30 Scratch units above the assistant.
4. Fade the text in.
5. Play the matching voice line to completion.
6. Wait 0.5 seconds between most lines.
7. Apply any special hide/show timing encoded by the original blocks.
8. Fade text out.
9. Fade/hide the assistant.
10. Resume player movement.

### Normal sequence mappings

The text costume and sound arrays must remain in this exact order:

- Sequence 1, level 2:
  - Text `1 1`…`1 6`
  - Sounds: `Woah there`, `Be lost`, `Terminate you`, `i wasn't upgraded`, `with no violence`, `Kind of`
- Sequence 2, level 3:
  - Text `2 1`…`2 4`
  - Sounds: `look at that`, `that jump is impossible`, `patiently wait give up`, `mission accomplished`
- Sequence 3, level 4:
  - Text `3 1`…`3 4`
  - Sounds: `ok wow`, `who told you, looping mech`, `Speak up`, `silence is fine too`
- Sequence 4, level 5:
  - Text `4 1`…`4 6`
  - Sounds: `Getting on my nerves`, `maybe im malfunctioning`, `error`, `dididididi`, `reset complete`, `buddy boy`
- Sequence 5, level 6:
  - Text `5 1`…`5 6`
  - Sounds: `Ok`, `Why does the mechanism`, `What other secrets`, `He runs this place`, `I was given orders`, `I think you know`
- Sequence 6, level 7:
  - Text `6 1`…`6 4`
  - Sounds: `i know this room`, `Something missing`, `i wonder why it's different`, `I must leave now`
- Sequence 7, level 10:
  - Text `7 1`…`7 3`
  - Sounds: `This place`, `Sensed it before`, `Grave danger, so am I`
- Sequence 8, level 11:
  - Text `8 1`…`8 3`
  - Sounds: `Countless before me`, `Countless test subjects like you`, `Endless cycle`

Extract the exact displayed dialogue from the SVG costumes. Do not retype or spell-correct it; the original wording and intentional quirks are part of the game.

### Special dialogue timing

Preserve special beats found in `project.json`, including:

- Sequence 3 hiding the text after `Speak up`, waiting about 3.5 seconds, then showing `3 4`.
- Sequence 4's error/reset visibility interruptions.
- Sequence 5 and 6 visibility interruptions between selected lines.

Represent these as data-driven actions such as `show_card`, `hide_card`, `play_sound`, `wait`, `broadcast/action`, and `fade`.

## Level 14 scripted finale

Level 14 has no goal. Player movement begins frozen. After roughly 1.5 seconds, run sequence 9.

Required action order:

1. Play `Im going to help you out`.
2. Wait 0.5 seconds.
3. Play `decrepid building`.
4. Wait 0.5 seconds.
5. Play `i cannot suport this org`.
6. Wait 0.5 seconds.
7. Reveal the CEO screen using the `calm` costume and a brightness fade.
8. Wait about 1.5 seconds.
9. Play `deep voice 1`.
10. Wait 0.5 seconds.
11. Play `our visitor is right here`.
12. Wait 0.5 seconds.
13. Play `deep voice 2`.
14. Wait 0.5 seconds.
15. Play `no I wont`.
16. Wait 0.5 seconds.
17. Switch the CEO to the angry presentation:
    - Play `Vine Boom Sound Effect (Longer Verison For Real)`.
    - Move CEO to `(0, 0)`.
    - Set size to 525%.
    - Switch costume to `angy`.
18. Wait 0.5 seconds.
19. Play `deep voice 3`.
20. Wait 0.5 seconds.
21. Play `i cant I wont`.
22. Wait 0.5 seconds.
23. Play `deep voice 4`.
24. Wait 0.5 seconds.
25. Play `no please!`.
26. Wait 1 second.
27. Play `manual override`.
28. Wait 0.5 seconds.
29. Play `my thrusters are controlled`.
30. Wait 0.5 seconds.
31. Send the assistant upward until it exits above the stage, then hide it.
32. Wait about 1.25 seconds.
33. Play `receiving far worse`.
34. Wait 0.5 seconds.
35. Begin the final black cover.

At the start of this sequence, change background music from looping `Hungarian Dance No` to looping `PSP Persona OST Mad Hospital 10 Disc 1`.

## Final cards

After the final black cover has faded in, show text costumes `Final 1` through `Final 7` in order at Scratch position `(0, 50)` above the cover.

For each card:

- Start at 100% size and fully transparent.
- Over about 25 steps, increase size by 1% per step while fading to opaque; the source waits 0.03 seconds per step.
- Add another 5% size.
- Hold for the source duration.
- Fade out over about 25 steps.
- Wait 0.5 seconds before the next card.

Hold durations:

| Card | Hold |
|---|---:|
| Final 1 | 1 second |
| Final 2 | 1 second |
| Final 3 | 4 seconds |
| Final 4 | 4 seconds |
| Final 5 | 2 seconds |
| Final 6 | 3 seconds |
| Final 7 | 3 seconds |

After `Final 7`, remain on a stable completion screen. Do not abruptly close the program. Allow Escape to quit and optionally R/Enter to restart from level 1.

## Music and sound

Required music behavior:

- From game start, loop `Hungarian Dance No` at approximately 20% volume.
- At the start of finale sequence 9, stop or replace that loop and begin looping `PSP Persona OST Mad Hospital 10 Disc 1`.
- `Steampunk Music - Gears and Cogs` is present but not connected to an active source script; extract it but do not invent a use for it.

Relevant effects:

- Player jump: `jump (1)`, source player volume approximately 50%.
- Player death/hit: `hitHurt (2)`.
- Key pickup: `pickupCoin (1)`.
- CEO angry impact: `Vine Boom Sound Effect (Longer Verison For Real)`.

Use separate mixer channels or a small audio manager so music, voice, and effects do not incorrectly interrupt one another. Voice lines should play to completion unless the game is quitting or restarting.

## Title and transition presentation

### Opening title

The `Title ` Scratch target contains `untilted` and `tilted` costumes. Preserve the active opening presentation:

- Display the title at the front from startup.
- Level 1 begins underneath it, as in the original.
- Hold about 4 seconds.
- Fade the title to transparent over roughly 50 source steps.

### Level transition

The `transist` target is a full-screen SVG overlay. Reproduce the source transition closely:

- Begin offscreen around Scratch `(460, 360)`.
- Move toward the center using the source's nonlinear motion, or recreate an extremely close visual equivalent.
- Cover the screen.
- Wait 0.5 seconds.
- Increment the level and respawn.
- Wait 0.25 seconds.
- Fade the overlay out over roughly 20 source steps.

The transition must prevent duplicate goal triggers.

## Rendering order

Use an explicit render order approximating the Scratch layer stack:

1. Stage/backdrop color.
2. Level background.
3. Ground.
4. Active invisible/disappearing platforms where visible.
5. Saws.
6. Key.
7. Spikes/hazard art.
8. Goal.
9. CEO screen.
10. Assistant.
11. Dialogue text.
12. Player, positioned so dialogue and transition overlays remain above it.
13. Title/final cards.
14. Transition/final black cover.

Adjust only where the source's actual layer order demands it.

## Debugging features

Development-only features may include:

- F1: toggle collision-mask visualization.
- F2: show player position and velocity.
- Page Up/Page Down: change level.
- R: respawn current level.
- A command-line `--level N` option.

These must be disabled or clearly marked as debug behavior in the normal release. The disconnected/commented Scratch X-key level-skip block must not become a hidden release shortcut.

## Save behavior

The source game does not implement saves. A save system is not required for parity.

Optionally remember only non-gameplay preferences such as window size, fullscreen state, and volume. Do not auto-unlock later levels unless explicitly documented as an optional enhancement.

## Error handling

- Fail early with a clear message if required generated assets are missing.
- Validate all manifest references at startup or through `tools/validate_assets.py`.
- Treat blank costumes as valid assets.
- Handle an unavailable audio device by continuing silently with a warning rather than crashing.
- Keep file paths relative to the repository/package, never to the current working directory alone.
- Do not assume Windows path separators.

## Tests

At minimum, provide automated tests for:

1. Scratch-to-screen coordinate conversion.
2. Costume placement using rotation centers and bitmap resolution.
3. Parsing/extraction manifest completeness.
4. Level count and required level fields.
5. Spawn and goal tables.
6. Horizontal and vertical wrapping in both directions.
7. Player gravity, jump impulse, fall-speed clamp, and horizontal damping.
8. Death/respawn state transition without repeated death events.
9. Key/platform reset behavior for levels 7, 10, and 13.
10. Saw cleanup on level transition.
11. Dialogue sequence data references valid assets.
12. A headless smoke test that initializes Pygame, loads level 1, runs several fixed updates, and exits.

Use Pygame's dummy SDL video/audio drivers for headless tests where needed.

## README requirements

Document:

- Supported Python version.
- Virtual-environment setup.
- Dependency installation.
- How to run the game.
- Controls.
- How to run tests.
- How to regenerate assets from the `.sb3`.
- How to use debug mode.
- Known parity differences, if any.
- A statement that the original `.sb3` is the source project supplied by its owner.

## Implementation sequence

Complete the work in this order, leaving the repository runnable after each major phase:

### Phase 1: Inspect and extract

- Place the source `.sb3` under `source/`.
- Build the extractor and manifest.
- Rasterize SVG costumes.
- Validate every referenced asset.

### Phase 2: Display and level rendering

- Create the 480 × 360 logical canvas and scalable window.
- Implement coordinate conversion and costume placement.
- Render level 1 background, ground, spikes, goal, and player using original assets.

### Phase 3: Core movement

- Implement fixed-step physics.
- Implement pixel-mask terrain collision.
- Implement horizontal and vertical wrapping.
- Implement animation and sound effects.

### Phase 4: Level progression

- Create data for all 14 levels.
- Implement goals, transition, spawn logic, death, and respawn.
- Verify every level is traversable.

### Phase 5: Special mechanics

- Implement keys and platform-state changes.
- Implement moving/rotating saws.
- Implement level-specific reset behavior.

### Phase 6: Dialogue and finale

- Implement assistant behavior.
- Encode sequences 1–8.
- Implement level 14 CEO sequence.
- Implement final cover and seven final cards.

### Phase 7: Polish and verification

- Add title fade and music transitions.
- Add reliable fullscreen/resizing and optional debug overlays.
- Finish tests and README.
- Play through the complete game from level 1 to the ending.

## Definition of done

The project is complete only when all of the following are true:

- `python main.py` launches without requiring Scratch or internet access.
- The original art and audio are used.
- The game renders at a 480 × 360 logical resolution with clean nearest-neighbor scaling.
- Movement, jumping, collision, and four-edge wrapping are functional and feel close to the source.
- All 14 levels load with correct player spawns and goal positions.
- Levels 7, 10, and 13 have functioning key/platform mechanics and reset correctly after death.
- Saws appear and move correctly in levels 11–13 and are cleaned up during transitions.
- Spikes and saws kill the player once per contact and trigger the full death/respawn sequence.
- Dialogue sequences 1–8 display the correct original text assets and play the matching voice lines in order.
- The complete level 14 CEO sequence runs in the correct order.
- All seven final cards appear with the original timing and the game remains on a completion screen.
- Music changes at the finale.
- No release-only debug level skip is enabled.
- Automated tests pass.
- The README contains complete setup, run, extraction, testing, and controls instructions.
- A full manual playthrough from launch to ending has been completed and any deliberate parity differences are documented.

## Final instruction to Codex

Begin by inspecting `project.json` inside the `.sb3` and confirming the source behaviors against this brief. Then implement the complete port. When uncertain, prefer observable source-project behavior over assumptions. Keep a running checklist in the repository, but do not treat planning or scaffolding as completion; deliver and test the playable game.
