# The Multidirectional Dilemma — Pygame port

A faithful, offline Pygame rebuild of the supplied Scratch project. It uses the
original 14 level paintings, collision geometry, character animation, dialogue
cards, voices, sound effects, and music. The 480×360 Scratch stage is presented
with nearest-neighbour scaling and 4:3 letterboxing.

## Setup and launch

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

No Scratch installation or network connection is used at runtime.

## Controls

* **A/D** or **Left/Right** — move
* **W**, **Up**, or mouse above stage centre — jump
* Hold the mouse left/right of centre — move
* **F11** — toggle fullscreen
* **Escape** — quit
* **R/Enter** — restart after the final card

Move through any stage edge to wrap to its opposite edge. Reach each rotating
goal. Keys in levels 7, 10, and 13 reveal otherwise intangible platforms.

## Source assets and reproducibility

`source/TheMultidirectionalDilemma.sb3` remains the source of truth. To keep the
Git patch text-only, generated PNG and WAV files are distributed separately in
`TheMultidirectionalDilemma-binary-assets.zip`. Extract that archive **at the
repository root** before launching. It contains paths beginning with
`assets/generated/`, so no manual file rearrangement is needed.

```bash
# Run this from the repository root, adjusting the archive path if necessary.
python -m zipfile -e ../TheMultidirectionalDilemma-binary-assets.zip .
python tools/validate_assets.py
python main.py
```

The text-only `data/asset_manifest.json` records every logical reference,
including duplicates, with original names, hashes, rotation centres, bitmap
resolutions, dimensions, and target defaults.

Alternatively, regenerate all binary files deterministically from the checked-in
SB3 with:

```bash
python tools/extract_sb3.py
python tools/validate_assets.py
```

Modern Pygame builds load the source SVG costumes through SDL_image; PNG pixel
art and WAV audio remain byte-for-byte copies. No SVG Python package is needed.

## Tests

```bash
python -m pytest
python -m compileall -q main.py game tools
```

For CI/headless launch checks, set `SDL_VIDEODRIVER=dummy` and
`SDL_AUDIODRIVER=dummy`. A full playthrough includes eight assistant sequences,
all 14 stages, the CEO confrontation, and seven timed final cards.

## Parity notes

The port deliberately uses fixed 30 Hz physics and elapsed-time audio/dialogue.
Scratch's move-then-retreat pixel-mask collision order and four-edge wrap values
are retained. Resizable presentation is permitted to use fractional scaling when
the window cannot fit an integer multiple, while gameplay always remains at the
original logical resolution.
