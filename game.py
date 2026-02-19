"""BloodWar - main game class."""

import random
import sys

import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WORLD_WIDTH, WORLD_HEIGHT,
    ENEMY_SEPARATION_DIST,
    AURA_SLOW, AURA_RADIUS,
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

# Definice dostupných upgradů
UPGRADES = [
    {"id": "speed",      "name": "Rychlost pohybu",   "desc": "+50 px/s pohybu"},
    {"id": "firerate",   "name": "Kadence střelby",   "desc": "-10 framů cooldown"},
    {"id": "magnet",     "name": "Magnetický dosah",  "desc": "+60 px dosah gemů"},
    {"id": "multishot",  "name": "Dvojitá střela",    "desc": "+1 projektil"},
    {"id": "health",     "name": "Léčení",            "desc": "+1 HP"},
    {"id": "armor",      "name": "Pancíř",            "desc": "+1 max HP"},
    {"id": "proj_size",  "name": "Větší střela",      "desc": "+6 velikost střely"},
    {"id": "proj_speed", "name": "Rychlejší střela",  "desc": "+80 px/s střela"},
    {"id": "proj_range", "name": "Delší dosah",       "desc": "+0.5s životnost"},
    {"id": "xp_boost",   "name": "XP Bonus",          "desc": "+5 XP za gem"},
    {"id": "vampire",    "name": "Vampirismus",       "desc": "Léčení za zabití"},
    {"id": "pierce",     "name": "Průbojná střela",   "desc": "+1 průchod střely"},
    {"id": "adrenalin",  "name": "Adrenalin",         "desc": "+150 px/s při 1 HP"},
    {"id": "gem_speed",  "name": "Rychlé sbírání",    "desc": "Gemy 50 % rychlejší"},
    {"id": "explosion",  "name": "Exploze",           "desc": "Zabití → AoE výbuch"},
    {"id": "aura",       "name": "Ledová aura",       "desc": "Zpomalení nepřátel"},
    {"id": "orbital",    "name": "Orbitující střela", "desc": "+1 orbitální projektil"},
]


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

        # Create player in world center
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.all_sprites.add(self.player)

        # Generate 150 random trees spread across the world
        for _ in range(200):
            x = random.randint(100, WORLD_WIDTH - 100)
            y = random.randint(100, WORLD_HEIGHT - 100)
            if self.player.position.distance_to(pygame.math.Vector2(x, y)) < 200:
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
        self.level = 0      # index do XP_THRESHOLDS
        self.level_up_pending = False
        self.upgrade_choices: list[dict] = []

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

    @property
    def elapsed_seconds(self) -> float:
        return self.frame_count / FPS

    def _current_spawn_interval(self) -> int:
        """Spawn interval klesá každých 10s o 5 framů, minimum 10."""
        reduction = int(self.elapsed_seconds // 10) * 5
        return max(10, 60 - reduction)

    def _update_camera(self) -> None:
        """Kamera sleduje hráče, clampováno na hranice světa."""
        self.camera_x = self.player.position.x - SCREEN_WIDTH / 2
        self.camera_y = self.player.position.y - SCREEN_HEIGHT / 2
        self.camera_x = max(0, min(WORLD_WIDTH - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(WORLD_HEIGHT - SCREEN_HEIGHT, self.camera_y))

    def _trigger_level_up(self) -> None:
        """Spustí level-up obrazovku s náhodnými volbami."""
        self.level_up_pending = True
        self.upgrade_choices = random.sample(UPGRADES, min(3, len(UPGRADES)))
        self.particle_system.spawn_level_up(self.player.position.x, self.player.position.y)

    def apply_upgrade(self, upgrade: dict) -> None:
        """Aplikuje vybraný upgrade."""
        uid = upgrade["id"]
        if uid == "speed":
            self.player.speed += 50
        elif uid == "firerate":
            self.wand_cooldown_frames = max(10, self.wand_cooldown_frames - 10)
        elif uid == "magnet":
            self.player.magnet_radius += 60
        elif uid == "multishot":
            self.player.projectile_count += 1
        elif uid == "health":
            self.player.hp = min(self.player.max_hp, self.player.hp + 1)
        elif uid == "armor":
            self.player.max_hp += 1
            self.player.hp += 1
        elif uid == "proj_size":
            self.player.proj_size += 6
        elif uid == "proj_speed":
            self.player.proj_speed += 80
        elif uid == "proj_range":
            self.player.proj_lifetime += 0.5
        elif uid == "xp_boost":
            self.player.xp_bonus += 5
        elif uid == "vampire":
            self.player.heal_on_kill += 0.25
        elif uid == "pierce":
            self.player.pierce += 1
        elif uid == "adrenalin":
            self.player.adrenalin = True
        elif uid == "gem_speed":
            self.player.gem_speed_mult += 0.5
        elif uid == "explosion":
            self.player.has_explosion = True
        elif uid == "aura":
            self.player.aura_radius = AURA_RADIUS
        elif uid == "orbital":
            self.player.orbital_count += 1
            self._rebuild_orbitals()
        self.level_up_pending = False
        self.upgrade_choices = []

    def _rebuild_orbitals(self) -> None:
        """Znovuvytvoří orbitální projektily dle orbital_count."""
        import math
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
                slow = AURA_SLOW
            else:
                slow = 1.0
            enemy.update(dt, self.player.position, self.elapsed_seconds, slow)

        # Enemy separation — zamezí prolínání nepřátel
        enemies_list = list(self.enemies)
        for i in range(len(enemies_list)):
            for j in range(i + 1, len(enemies_list)):
                e1 = enemies_list[i]
                e2 = enemies_list[j]
                diff = e1.position - e2.position
                dist = diff.length()
                if 0 < dist < ENEMY_SEPARATION_DIST:
                    push = diff.normalize() * (ENEMY_SEPARATION_DIST - dist) * 0.5
                    e1.position += push
                    e2.position -= push
                    e1.rect.center = e1.position
                    e2.rect.center = e2.position

        # Enemy vs Tree collision — nepřátelé nemohou procházet stromy
        for enemy in self.enemies:
            for tree in self.trees:
                if enemy.rect.colliderect(tree.hitbox):
                    diff = enemy.position - pygame.math.Vector2(
                        tree.hitbox.centerx, tree.hitbox.centery
                    )
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
