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
BASE_ENEMY_SPEED = 100      # pixels per second (základ, roste s časem)
ENEMY_SPEED = 100           # alias pro zpětnou kompatibilitu
ENEMY_SPAWN_INTERVAL = 60   # frames (základ, klesá s časem)
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
# MAPA
# ==============================================================================

WORLD_WIDTH = 6400          # šířka světa v pixelech
WORLD_HEIGHT = 4800         # výška světa v pixelech

# ==============================================================================
# XP A LEVEL-UP
# ==============================================================================

# XP potřebné pro každý level (index = aktuální level, hodnota = XP do dalšího)
XP_THRESHOLDS = [
    20, 50, 90, 140, 200, 270, 350, 440, 540, 650,
    780, 930, 1100, 1300, 1530, 1790, 2080, 2400, 2750, 3130,
]

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
# HRÁČ - HP
# ==============================================================================

PLAYER_MAX_HP = 3
PLAYER_INVINCIBILITY_TIME = 1.5   # sekundy neranitelnosti po zásahu

# ==============================================================================
# NEPŘÁTELÉ - TYPY A SEPARACE
# ==============================================================================

ENEMY_SEPARATION_DIST = 30        # px — minimální vzdálenost mezi nepřáteli

FAST_ENEMY_SPEED_MULT = 2.0       # 2× rychlejší než base
FAST_ENEMY_SCALE = 2              # menší sprite (oproti ENEMY_ANIM_SCALE = 3)

TANK_ENEMY_HP = 3                 # počet životů
TANK_ENEMY_SCALE = 4              # větší sprite
TANK_ENEMY_SPEED_MULT = 0.5       # poloviční rychlost
TANK_ENEMY_GEM_COUNT = 3          # počet gemů po smrti

# ==============================================================================
# ORBITÁLNÍ PROJEKTIL A VÝBUCH
# ==============================================================================

ORBIT_RADIUS = 80
ORBIT_SPEED = 2.5       # rad/s
EXPLOSION_RADIUS = 80

# ==============================================================================
# LEDOVÁ AURA
# ==============================================================================

AURA_RADIUS = 150
AURA_SLOW = 0.4         # násobič rychlosti při aure

# ==============================================================================
# CACHING
# ==============================================================================

_tileset_cache: dict[tuple, pygame.Surface] = {}
