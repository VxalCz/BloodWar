"""BloodWar - konstanty a nastavení hry."""

import pygame

# ==============================================================================
# OBRAZOVKA A FPS
# ==============================================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# ==============================================================================
# BARVY
# ==============================================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)       # Hráč
RED = (255, 50, 50)         # Nepřítel
YELLOW = (255, 255, 50)     # Projektil
GREEN = (50, 255, 50)       # Experience Gem

# ==============================================================================
# HERNÍ NASTAVENÍ - HRÁČ
# ==============================================================================

PLAYER_SPEED = 300          # pixels per second
PLAYER_SIZE = 32
ANIMATION_SCALE = 3         # zvětšení sprite
ANIMATION_SPEED = 0.15      # sekundy mezi snímky

# ==============================================================================
# HERNÍ NASTAVENÍ - NEPŘÍTEL
# ==============================================================================

ENEMY_SIZE = 24
ENEMY_SPEED = 100           # pixels per second
ENEMY_SPAWN_INTERVAL = 60   # frames
ENEMY_ANIM_SCALE = 3        # zvětšení sprite
ENEMY_ANIM_SPEED = 0.3      # sekundy mezi snímky (pomalejší než hráč)
ENEMY_ANIM_SCALE = 3        # zvětšení sprite
ENEMY_ANIM_SPEED = 0.3      # sekundy mezi snímky

# ==============================================================================
# HERNÍ NASTAVENÍ - PROJEKTIL
# ==============================================================================

PROJECTILE_SPEED = 400      # pixels per second
PROJECTILE_SIZE = 12
WAND_COOLDOWN = 60          # frames (1 sekunda při 60 FPS)

# ==============================================================================
# HERNÍ NASTAVENÍ - EXPERIENCE GEM
# ==============================================================================

GEM_SIZE = 10
GEM_VALUE = 10              # XP za gem
MAGNET_RADIUS = 100        # pixelů - vzdálenost pro magnet efekt
GEM_SPEED = 200             # pixels per second - rychlost gemu k hráči

# ==============================================================================
# TILESET KONSTANTY
# ==============================================================================

TILE_SIZE = 16              # velikost jedné dlaždice v tilesetu
TILESET_SCALE = 3           # zvětšení dlaždic (16 -> 48)

# Tráva
GRASS_TILE_COL = 2
GRASS_TILE_ROW = 3

# Strom
TILE_TREE_X = 6
TILE_TREE_Y = 20
TREE_WIDTH = 2
TREE_HEIGHT = 3

# Keř
TILE_BUSH_X = 2
TILE_BUSH_Y = 0

# Dům
TILE_HOUSE_X = 0
TILE_HOUSE_Y = 12
HOUSE_WIDTH = 5
HOUSE_HEIGHT = 5

# ==============================================================================
# CACHING
# ==============================================================================

_tileset_cache: dict[tuple, pygame.Surface] = {}
