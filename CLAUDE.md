# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

- **Project Name**: BloodWar
- **License**: MIT License (Copyright 2026 ValCz)
- **Status**: Vampire Survivors clone in development
- **Main File**: `game.py` (~185 lines)

## Development

```bash
# Install dependencies
pip install pygame-ce

# Run game
python main.py
```

## Architecture

- Modular structure with `game.py` delegating to `src/` modules
- OOP approach with classes: `Game`, `Player`, `Enemy`, `Projectile`, `ExperienceGem`, `Tree`
- All game objects inherit from `pygame.sprite.Sprite`
- Movement uses `pygame.math.Vector2` with delta time for FPS-independent movement
- **World-space coordinates**: all object positions are in world space; renderer applies camera offset

### Source Modules

| Module | Responsibility |
|--------|----------------|
| `src/input_handler.py` | Keyboard input (WASD), debug grid toggle, restart, level-up choice |
| `src/spawner.py` | Enemy spawning at camera-relative screen edges (world-space) |
| `src/combat.py` | Targeting nearest enemy, shooting (supports multishot with spread) |
| `src/collision.py` | Collision detection, XP collection, level-up trigger |
| `src/renderer.py` | Drawing with camera offset, Y-sorting, HUD, level-up overlay, debug grid |

## Game Controls

- **WASD**: Move player
- **1 / 2 / 3**: Select upgrade on level-up screen
- **G**: Toggle debug grid (shows tile coordinates)
- **R**: Restart after game over

## Key Classes

| Class | Purpose |
|-------|---------|
| `Player` | Hero with sprite sheet animation (4 directions, 4 frames); mutable stats: `speed`, `magnet_radius`, `projectile_count`, `proj_size`, `proj_speed`, `proj_lifetime`, `pierce`, `xp_bonus`, `gem_speed_mult`, `heal_on_kill`, `adrenalin`, `has_explosion`, `aura_radius`, `orbital_count` |
| `Enemy` | Slime sprite chasing player; speed scales with elapsed time; accepts `slow_factor` |
| `FastEnemy` | 2× speed, smaller sprite |
| `TankEnemy` | 3 HP, 0.5× speed, larger sprite, drops 3 gems |
| `Projectile` | Yellow projectile from Magic Wand; mutable `speed`, `size`, `lifetime`, `pierce_remaining` |
| `OrbitalProjectile` | Purple orb orbiting player at ORBIT_RADIUS; 0.5s per-enemy hit cooldown |
| `ExperienceGem` | Green ring dropped by enemies; magnetic pickup, respects `gem_speed_mult` |
| `Tree` | Decorative obstacle with hitbox in lower third |
| `Game` | Main game loop, state management, camera, upgrades, `orbital_projectiles` group |

## Graphics

- Hero: `image/hero_sheet.png` (4x4 sprite grid)
- Enemy: `image/slime.png` (2-frame horizontal sheet)
- Tileset: `image/tileset.png` (16x16 grid, scaled 3x)
- Tile size: 48x48 pixels (16 * 3)

## Tileset Constants

Located in `constants.py`:
```python
TILE_SIZE = 16             # Original tile size
TILESET_SCALE = 3          # Scale factor
TILE_GRASS = (2, 3)        # Background tile
TILE_TREE = (6, 20, 2, 3)  # Large tree (col, row, w, h)
```

## Game Mechanics

- World size: **6400×4800 px** (8× the screen); camera follows player
- Player starts at world center, moves with WASD
- Enemies spawn at camera-relative screen edges every N frames
- **Spawn interval**: starts at 60 frames, decreases by 5 every 10s (minimum 10)
- **Enemy speed**: starts at 100 px/s, increases by 100% every 2 minutes
- Magic Wand shoots every `wand_cooldown_frames` toward nearest enemy (default 60)
- Killing enemy drops ExperienceGem (+10 XP)
- Gems attracted when within `player.magnet_radius` px (default 100)
- Game over on enemy collision; press R to restart
- Score = survival time in seconds (separate from XP)

## XP & Level-up System

- XP accumulates separately from score
- Thresholds (total XP): `[20, 50, 90, 140, 200, 270, 350, 440, 540, 650, ...]`
- On level-up: game pauses, overlay shows 3 random upgrade choices
- `UPGRADES` list defined in `game.py` (17 entries total)

| ID | Effect |
|----|--------|
| `speed` | player.speed += 50 |
| `firerate` | wand_cooldown_frames -= 10 (min 10) |
| `magnet` | player.magnet_radius += 60 |
| `multishot` | player.projectile_count += 1 (spread 15°) |
| `health` | player.hp += 1 (up to max) |
| `armor` | player.max_hp += 1, player.hp += 1 |
| `proj_size` | player.proj_size += 6 |
| `proj_speed` | player.proj_speed += 80 |
| `proj_range` | player.proj_lifetime += 0.5s |
| `xp_boost` | player.xp_bonus += 5 (added to GEM_VALUE per pickup) |
| `vampire` | player.heal_on_kill += 0.25 (accumulates → +HP) |
| `pierce` | player.pierce += 1 (projectile passes through N enemies) |
| `adrenalin` | player.adrenalin = True (+150 px/s at HP ≤ 1) |
| `gem_speed` | player.gem_speed_mult += 0.5 |
| `explosion` | player.has_explosion = True (AoE r=80px on kill, chain kills) |
| `aura` | player.aura_radius = 150 (enemies in range → 40% speed) |
| `orbital` | player.orbital_count += 1 (rotating orb, 0.5s hit cooldown per enemy) |

## Debug Features

- **G key**: Toggle debug grid showing (col, row) tile coordinates
- Debug grid useful for finding correct tile positions in tileset.png

## Notes

- The .gitignore includes Cursor and VSCode-specific entries
- Do NOT use Co-Authored-By Claude in git commits
