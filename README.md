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
- 3 enemy types: Normal, Fast, Tank
- Magic Wand auto-shooting toward nearest enemy
- Multishot support (spreads projectiles in a fan)
- Experience gems with magnetic pickup
- XP & level-up system — pause + choose 1 of 3 upgrades (17 total):
  - Movement & combat: speed, fire rate, multishot, projectile size/speed/range, pierce
  - Survival: HP heal, armor, vampirism, adrenalin (speed burst at 1 HP)
  - Collection: magnet range, gem pickup speed, XP bonus per gem
  - Special: explosion on kill (AoE chain), ice aura (slows nearby enemies), orbital projectile
- Y-sorted rendering for depth perception
- Score (survival time) + kills tracker

## Tech

- Python + pygame-ce
- Modular architecture (`src/`)
- World-space coordinates with camera offset rendering
