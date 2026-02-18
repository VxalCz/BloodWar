# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

- **Project Name**: BloodWar
- **License**: MIT License (Copyright 2026 ValCz)
- **Status**: Vampire Survivors clone in development
- **Main File**: `game.py` (~130 lines, refactored)

## Development

```bash
# Install dependencies
pip install pygame-ce

# Run game
python main.py
```

## Architecture

- Modular structure with `game.py` delegating to `src/` modules
- OOP approach with classes: `Game`, `Player`, `Enemy`, `Projectile`, `ExperienceGem`
- All game objects inherit from `pygame.sprite.Sprite`
- Movement uses `pygame.math.Vector2` with delta time for FPS-independent movement

### Source Modules

| Module | Responsibility |
|--------|----------------|
| `src/input_handler.py` | Keyboard input (WASD), debug grid toggle, restart |
| `src/spawner.py` | Enemy spawning at screen edges |
| `src/combat.py` | Targeting nearest enemy, shooting projectiles |
| `src/collision.py` | Collision detection (player-enemy, projectile-enemy, gems) |
| `src/renderer.py` | Drawing, Y-sorting, debug grid |

## Game Controls

- **WASD**: Move player
- **G**: Toggle debug grid (shows tile coordinates)
- **R**: Restart after game over

## Key Classes

| Class | Purpose |
|-------|---------|
| `Player` | Hero with sprite sheet animation (4 directions, 4 frames each) |
| `Enemy` | Red squares spawning from screen edges, chasing player |
| `Projectile` | Yellow projectiles from Magic Wand |
| `ExperienceGem` | Green rings dropped by enemies, magnetic pickup |
| `Game` | Main game loop, state management |

## Graphics

- Hero: `image/hero_sheet.png` (4x4 sprite grid)
- Tileset: `image/tileset.png` (16x16 grid, scaled 3x)
- Tile size: 48x48 pixels (16 * 3)

## Tileset Constants

Located in `constants.py`:
```python
TILE_SIZE = 16             # Original tile size
TILESET_SCALE = 3          # Scale factor
TILE_GRASS = (1, 1)        # Background
TILE_TREE = (0, 7, 3, 4)  # Large tree
TILE_BUSH = (2, 0)         # Small bush
TILE_HOUSE = (0, 12, 5, 5)# House
```

## Game Mechanics

- Player starts centered, moves with WASD
- Enemies spawn every 60 frames at screen edges
- Magic Wand shoots every 60 frames toward nearest enemy
- Killing enemy drops ExperienceGem (+10 XP)
- Gems have magnetic effect within 100px radius
- Game over on enemy collision
- Score = survival time + kills

## Debug Features

- **G key**: Toggle debug grid showing (col, row) tile coordinates
- Debug grid useful for finding correct tile positions in tileset.png

## Notes

- The .gitignore includes Cursor and VSCode-specific entries
- Do NOT use Co-Authored-By Claude in git commits
