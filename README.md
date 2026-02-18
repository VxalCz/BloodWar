# BloodWar

Vampire Survivors clone in Python.

## Install

```bash
pip install pygame-ce
```

## Run

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| **WASD** | Move player |
| **1 / 2 / 3** | Choose upgrade on level-up screen |
| **R** | Restart (after game over) |
| **G** | Toggle debug grid |

## Features

- Scrollable world (6400×4800 px) with camera tracking
- Enemy spawning at screen edges with progressive difficulty
  - Spawn rate increases every 10 seconds
  - Enemy speed scales with survival time
- Magic Wand auto-shooting toward nearest enemy
- Multishot support (spreads projectiles in a fan)
- Experience gems with magnetic pickup
- XP & level-up system — pause + choose 1 of 3 upgrades:
  - Speed boost
  - Faster fire rate
  - Wider magnet range
  - Extra projectile
- Y-sorted rendering for depth perception
- Score (survival time) + kills tracker

## Tech

- Python + pygame-ce
- Modular architecture (`src/`)
- World-space coordinates with camera offset rendering
