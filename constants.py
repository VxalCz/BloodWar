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
GEM_VALUE = 5               # XP za gem
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

# Celkové XP potřebné k dosažení levelu `level + 1`.
# Kvadratický růst s monotónně rostoucími přírůstky.
# L0=20, L5=240, L10=660, L15=1280, L20=2100
def xp_threshold(level: int) -> int:
    """Celkové XP potřebné pro level-up z úrovně `level`."""
    return (level + 1) * (20 + level * 4)

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

# Jezírko (3×3 dlaždice)
POND_TILE_X = 6
POND_TILE_Y = 7
POND_SIZE = 3

# Dům
TILE_HOUSE_X = 0
TILE_HOUSE_Y = 12
HOUSE_WIDTH = 5
HOUSE_HEIGHT = 5

# ==============================================================================
# HRÁČ - HP
# ==============================================================================

PLAYER_MAX_HP = 30
PLAYER_INVINCIBILITY_TIME = 0.75  # sekundy neranitelnosti po zásahu (bylo 1.5)
LEVELUP_INVINCIBILITY_TIME = 1.5  # sekundy neranitelnosti po level-up výběru
VAMPIRE_HEAL_CAP = 7.5            # max heal_on_kill (3 upgrady po 2.5)

# ==============================================================================
# NEPŘÁTELÉ - TYPY A SEPARACE
# ==============================================================================

ENEMY_SEPARATION_DIST = 30        # px — minimální vzdálenost mezi nepřáteli

FAST_ENEMY_SPEED_MULT = 2.0       # 2× rychlejší než base
FAST_ENEMY_SCALE = 2              # menší sprite (oproti ENEMY_ANIM_SCALE = 3)

TANK_ENEMY_HP = 50                # počet životů (×10)
TANK_ENEMY_SCALE = 4              # větší sprite
TANK_ENEMY_SPEED_MULT = 0.5       # poloviční rychlost
TANK_ENEMY_GEM_COUNT = 3          # počet gemů po smrti
TANK_ENEMY_CONTACT_DMG = 20       # base kontaktní poškození tanku (×10)

# Barevné fáze dle obtížnosti (elapsed_seconds → tint)
DANGER_TINTS = [
    (0,   (150, 255, 150)),   # zelená
    (90,  (200, 255, 100)),   # žlutozelená
    (180, (255, 255,  50)),   # žlutá
    (270, (255, 160,  50)),   # oranžová
    (360, (255,  60,  60)),   # červená
    (450, (220,  50, 255)),   # fialová
]

# ZPŮSOB ZVÝŠENÍ OBTÍŽNOSTI
ENEMY_BASE_HP = 20                # základní HP nepřátel
ENEMY_HP_SCALE_INTERVAL = 30      # každých 30 sekund HP × faktor
ENEMY_HP_SCALE_FACTOR = 1.35      # násobitel HP za interval (exponenciální růst)
ENEMY_SPEED_SCALE_INTERVAL = 60   # každých 60 sekund +25% rychlost (bylo 90)
ENEMY_CONTACT_DMG_INTERVAL = 90   # každých 90 sekund +10 kontaktní poškození (bylo 180)

# POŠKOZENÍ PROJEKTILŮ A VÝBUCHU
PROJECTILE_DAMAGE = 10            # damage za jeden zásah projektilu / orbitálu
EXPLOSION_DAMAGE = 5              # damage výbuchu v AoE (není instant kill)

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

# ==============================================================================
# UPGRADES - seznam dostupných upgradů
# ==============================================================================

UPGRADES = [
    {"id": "speed",      "name": "Rychlost",    "desc": "+50 rychlost"},
    {"id": "firerate",   "name": "Kadence",     "desc": "-10 cooldown",       "combat": True},
    {"id": "magnet",     "name": "Magnet",      "desc": "+60 dosah sběru"},
    {"id": "multishot",  "name": "Multishot",   "desc": "+1 projektil",       "combat": True},
    {"id": "damage",     "name": "Síla útoku",  "desc": "+1 damage",          "combat": True},
    {"id": "health",     "name": "Regenerace",  "desc": "+10 HP, +regen"},
    {"id": "armor",      "name": "Pancíř",      "desc": "+10 max HP"},
    {"id": "proj_size",  "name": "Větší střela", "desc": "+10 velikost",      "combat": True},
    {"id": "proj_speed", "name": "Rychlá střela", "desc": "+80 rychlost",     "combat": True},
    {"id": "proj_range", "name": "Delší dosah", "desc": "+0.5s dolet",        "combat": True},
    {"id": "xp_boost",   "name": "XP Bonus",    "desc": "+1 XP za gem"},
    {"id": "vampire",    "name": "Vampirismus",  "desc": "+2.5 heal/kill",    "combat": True},
    {"id": "pierce",     "name": "Průraz",       "desc": "+1 průchod",        "combat": True},
    {"id": "adrenalin",  "name": "Adrenalin",    "desc": "Buff při <30% HP",  "combat": True},
    {"id": "gem_speed",  "name": "Sběr gemů",   "desc": "+rychlost, +magnet"},
    {"id": "explosion",  "name": "Exploze",      "desc": "AoE při zabití",    "combat": True},
    {"id": "aura",       "name": "Ledová aura",  "desc": "Zpomalí nepřátele", "combat": True},
    {"id": "orbital",    "name": "Orbitál",      "desc": "+1 orbitál",        "combat": True},
]

# Prvních N levelů nabízet jen bojové upgrady
COMBAT_ONLY_UNTIL_LEVEL = 5
