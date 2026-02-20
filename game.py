"""BloodWar - main game class."""

import math
import random
import sys
from math import sqrt

import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WORLD_WIDTH, WORLD_HEIGHT,
    TILE_SIZE, TILESET_SCALE,
    ENEMY_SEPARATION_DIST,
    AURA_SLOW, AURA_RADIUS,
    VAMPIRE_HEAL_CAP,
    LEVELUP_INVINCIBILITY_TIME,
)
from tiles import get_tile, init_grass_variants
from player import Player
from items import Tree
from enemy import OrbitalProjectile

from src.input_handler import InputHandler
from src.spawner import Spawner
from src.combat import Combat
from src.collision import Collision
from src.renderer import Renderer
from src.particles import ParticleSystem
from src.spatial_grid import SpatialGrid

# Definice dostupných upgradů (neomezené stackování, diminishing returns přes _scaled)
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


class Game:
    """Main game class - game state manager."""

    def __init__(self) -> None:
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BloodWar - Vampire Survivors Clone")
        init_grass_variants()
        self.clock = pygame.time.Clock()

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
        self.orbital_projectiles = pygame.sprite.Group()
        # Vodní dlaždice — set (tile_col, tile_row) v souřadnicích světa
        self.water_tiles: set[tuple[int, int]] = set()

        # Create player in world center
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.all_sprites.add(self.player)

        # Generování vodních ploch NEJDŘÍVE — obdélníky s min. 1-tile mezerou mezi sebou
        tile_px = TILE_SIZE * TILESET_SCALE          # 48 px
        world_tw = WORLD_WIDTH // tile_px
        world_th = WORLD_HEIGHT // tile_px
        spawn_tc = (WORLD_WIDTH // 2) // tile_px
        spawn_tr = (WORLD_HEIGHT // 2) // tile_px
        rng = random.Random(42)
        size_pool = [
            (2, 2), (2, 3), (3, 2),                    # malé
            (3, 4), (4, 3), (4, 4), (5, 3), (3, 5),   # střední
            (6, 4), (4, 6), (7, 5), (5, 7),            # velká jezírka
        ]
        for _ in range(30):
            w, h = rng.choice(size_pool)
            cx = rng.randint(2, world_tw - w - 2)
            cy = rng.randint(2, world_th - h - 2)
            if abs(cx + w // 2 - spawn_tc) < 10 and abs(cy + h // 2 - spawn_tr) < 10:
                continue
            # Zkontrolovat 1-tile okraj kolem nového obdélníku — nesmí se dotýkat jiného jezera
            if any((tx, ty) in self.water_tiles
                   for ty in range(cy - 1, cy + h + 1)
                   for tx in range(cx - 1, cx + w + 1)):
                continue
            for ty in range(cy, cy + h):
                for tx in range(cx, cx + w):
                    self.water_tiles.add((tx, ty))

        # Generate 200 random trees — ne ve vodě (TREE_WIDTH=2, TREE_HEIGHT=3 tiles)
        for _ in range(200):
            x = random.randint(100, WORLD_WIDTH - 100)
            y = random.randint(100, WORLD_HEIGHT - 100)
            if self.player.position.distance_to(pygame.math.Vector2(x, y)) < 200:
                continue
            # Zkontrolovat zda plocha stromu (2×3 dlaždice) nezasahuje do vody
            tc0 = x // tile_px
            tc1 = (x + 2 * tile_px - 1) // tile_px
            tr0 = (y - 3 * tile_px) // tile_px
            tr1 = (y - 1) // tile_px
            if any((tc, tr) in self.water_tiles
                   for tr in range(tr0, tr1 + 1)
                   for tc in range(tc0, tc1 + 1)):
                continue
            tree = Tree(x, y)
            self.trees.add(tree)

        # Game state
        self.running = True
        self.game_over = False
        self.frame_count = 0
        self.score = 0      # čas přežití (frame_count // FPS)
        self.kills = 0

        # XP a level
        self.xp = 0
        self.level = 0
        self.level_up_pending = False
        self.upgrade_choices: list[dict] = []

        # Počet vzatých stacků pro každý upgrade (pro logaritmické škálování)
        self.upgrade_stacks: dict[str, int] = {}

        # Dynamická obtížnost
        self.wand_cooldown_frames = 60   # mutable — snižuje se upgradem

        # Timery (nahrazují frame_count % N)
        self.wand_timer = 0.0
        self.spawn_timer = 0.0

        # Debug
        self.show_grid = False
        self.camera_x = 0.0
        self.camera_y = 0.0

        # Grass tile for background
        self.grass_tile = get_tile(2, 3)

        # Initialize modules
        self.input_handler = InputHandler(self)
        self.spawner = Spawner(self)
        self.combat = Combat(self)
        self.collision = Collision(self)
        self.renderer = Renderer(self)
        self.particle_system = ParticleSystem()
        self._separation_grid = SpatialGrid(ENEMY_SEPARATION_DIST)

    @property
    def elapsed_seconds(self) -> float:
        return self.frame_count / FPS

    def _current_spawn_interval(self) -> int:
        """Spawn interval klesá každých 10s o 5 framů, minimum 5."""
        reduction = int(self.elapsed_seconds // 10) * 5
        return max(5, 45 - reduction)  # Základ 45 místo 60, min 5 místo 10

    def _update_camera(self) -> None:
        """Kamera sleduje hráče, clampováno na hranice světa."""
        self.camera_x = self.player.position.x - SCREEN_WIDTH / 2
        self.camera_y = self.player.position.y - SCREEN_HEIGHT / 2
        self.camera_x = max(0, min(WORLD_WIDTH - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(WORLD_HEIGHT - SCREEN_HEIGHT, self.camera_y))

    def _trigger_level_up(self) -> None:
        """Spustí level-up obrazovku s náhodnými volbami."""
        self.level_up_pending = True
        if self.level <= COMBAT_ONLY_UNTIL_LEVEL:
            pool = [u for u in UPGRADES if u.get("combat")]
        else:
            pool = UPGRADES
        self.upgrade_choices = random.sample(pool, min(3, len(pool)))
        self.particle_system.spawn_level_up(self.player.position.x, self.player.position.y)

    def _scaled(self, uid: str, base: float) -> float:
        """Vrátí škálovaný bonus: base / sqrt(stack + 1). Klesá logaritmicky s každým stackem."""
        stack = self.upgrade_stacks.get(uid, 0)
        return base / sqrt(stack + 1)

    def apply_upgrade(self, upgrade: dict) -> None:
        """Aplikuje vybraný upgrade s logaritmickým škálováním opakovaných výběrů."""
        uid = upgrade["id"]
        s = self._scaled  # zkratka

        if uid == "speed":
            self.player.speed += max(1, round(s(uid, 50)))
        elif uid == "firerate":
            self.wand_cooldown_frames = max(10, self.wand_cooldown_frames - max(1, round(s(uid, 10))))
        elif uid == "magnet":
            self.player.magnet_radius += max(1, round(s(uid, 60)))
        elif uid == "multishot":
            self.player.projectile_count += 1
        elif uid == "damage":
            self.player.bonus_damage += 1
        elif uid == "health":
            self.player.hp = min(self.player.max_hp, self.player.hp + 10)
            self.player.regen_rate += max(0.1, round(s(uid, 0.5) * 10) / 10)
        elif uid == "armor":
            bonus = max(1, round(s(uid, 10)))
            self.player.max_hp += bonus
            self.player.hp += bonus
        elif uid == "proj_size":
            self.player.proj_size += max(1, round(s(uid, 10)))
            # Každé 2 stacky +1 pierce bonus
            new_stacks = self.upgrade_stacks.get(uid, 0) + 1
            if new_stacks % 2 == 0:
                self.player.pierce += 1
        elif uid == "proj_speed":
            self.player.proj_speed += max(1, round(s(uid, 80)))
        elif uid == "proj_range":
            self.player.proj_lifetime += max(0.05, round(s(uid, 0.5) * 20) / 20)
        elif uid == "xp_boost":
            self.player.xp_bonus += max(1, round(s(uid, 1)))
        elif uid == "vampire":
            self.player.heal_on_kill = min(VAMPIRE_HEAL_CAP, self.player.heal_on_kill + max(0.1, s(uid, 2.5)))
        elif uid == "pierce":
            self.player.pierce += 1
        elif uid == "adrenalin":
            self.player.adrenalin = True
            self.player.adrenalin_damage_mult += 0.5  # +50% DMG per stack při ≤30% HP
        elif uid == "gem_speed":
            self.player.gem_speed_mult += max(0.05, round(s(uid, 0.5) * 20) / 20)
            self.player.magnet_radius += max(1, round(s(uid, 30)))
        elif uid == "explosion":
            if not self.player.has_explosion:
                self.player.has_explosion = True
            else:
                self.player.explosion_damage = round(self.player.explosion_damage * 1.2, 2)
                self.player.explosion_radius = round(self.player.explosion_radius * 1.2, 2)
        elif uid == "aura":
            if self.player.aura_radius == 0:
                self.player.aura_radius = AURA_RADIUS
                self.player.aura_slow = 0.90   # základ 10 % zpomalení
            else:
                self.player.aura_slow = max(0.10, round(self.player.aura_slow - 0.02, 2))
        elif uid == "orbital":
            self.player.orbital_count += 1
            self._rebuild_orbitals()

        self.upgrade_stacks[uid] = self.upgrade_stacks.get(uid, 0) + 1
        self.level_up_pending = False
        self.upgrade_choices = []
        # Nesmrtelnost po level-upu — hráč má čas se zorientovat
        self.player.invincibility_timer = LEVELUP_INVINCIBILITY_TIME

    def _rebuild_orbitals(self) -> None:
        """Znovuvytvoří orbitální projektily dle orbital_count."""
        self.orbital_projectiles.empty()
        count = self.player.orbital_count
        for i in range(count):
            angle = (2 * math.pi / count) * i
            orb = OrbitalProjectile(angle)
            self.orbital_projectiles.add(orb)

    def update(self, dt: float) -> None:
        """Update game state."""
        self.particle_system.update(dt)

        if self.game_over or self.level_up_pending:
            return

        self.frame_count += 1
        self.score = self.frame_count // FPS

        # Spawn enemy — timer místo frame_count %
        self.spawn_timer += dt
        spawn_interval_s = self._current_spawn_interval() / FPS
        if self.spawn_timer >= spawn_interval_s:
            self.spawn_timer -= spawn_interval_s
            self.spawner.spawn_enemy()

        # Shoot — timer místo frame_count %
        self.wand_timer += dt
        wand_cooldown_s = self.wand_cooldown_frames / FPS
        if self.wand_timer >= wand_cooldown_s:
            self.wand_timer -= wand_cooldown_s
            self.combat.shoot()

        # Update player
        self.player.update(dt)

        # Update enemies (s slow_factor z ledové aury)
        aura_radius = self.player.aura_radius
        for enemy in self.enemies:
            if aura_radius > 0 and enemy.position.distance_to(self.player.position) < aura_radius:
                slow = self.player.aura_slow
            else:
                slow = 1.0
            enemy.update(dt, self.player.position, self.elapsed_seconds, slow)

        # Enemy separation — spatial grid O(n×k) místo O(n²)
        grid = self._separation_grid
        grid.clear()
        for enemy in self.enemies:
            grid.insert(enemy)
        seen: set[tuple[int, int]] = set()
        for e1 in self.enemies:
            id1 = id(e1)
            for e2 in grid.get_neighbors(e1):
                pair = (id1, id(e2)) if id1 < id(e2) else (id(e2), id1)
                if pair in seen:
                    continue
                seen.add(pair)
                diff = e1.position - e2.position
                dist = diff.length()
                if 0 < dist < ENEMY_SEPARATION_DIST:
                    push = diff.normalize() * (ENEMY_SEPARATION_DIST - dist) * 0.5
                    e1.position += push
                    e2.position -= push
                    e1.rect.center = e1.position
                    e2.rect.center = e2.position

        # Enemy vs Tree collision
        for enemy in self.enemies:
            for tree in self.trees:
                if enemy.rect.colliderect(tree.hitbox):
                    diff = enemy.position - pygame.math.Vector2(
                        tree.hitbox.centerx, tree.hitbox.centery
                    )
                    if diff.length() > 0:
                        enemy.position += diff.normalize() * 2
                        enemy.rect.center = enemy.position

        # Enemy vs Water tiles — kontrola okolních dlaždic středu nepřítele
        tile_px = TILE_SIZE * TILESET_SCALE
        for enemy in self.enemies:
            ec = enemy.rect.centerx // tile_px
            er = enemy.rect.centery // tile_px
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    col, row = ec + dc, er + dr
                    if (col, row) not in self.water_tiles:
                        continue
                    wr = pygame.Rect(col * tile_px, row * tile_px, tile_px, tile_px)
                    if not enemy.rect.colliderect(wr):
                        continue
                    diff = enemy.position - pygame.math.Vector2(wr.centerx, wr.centery)
                    if diff.length() > 0:
                        enemy.position += diff.normalize() * 2
                        enemy.rect.center = enemy.position

        # Update projectiles
        self.projectiles.update(dt)

        # Update gems
        for gem in self.gems:
            gem.update(dt, self.player.position, self.player.magnet_radius, self.player.gem_speed_mult)

        # Update orbitálních projektilů
        for orb in self.orbital_projectiles:
            orb.update(dt, self.player.position)

        # Update camera
        self._update_camera()

        # Check collisions
        self.collision.check_collisions()

    def handle_events(self) -> None:
        """Process events."""
        self.input_handler.handle_events()

    def draw(self) -> None:
        """Draw game."""
        self.renderer.draw()

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
