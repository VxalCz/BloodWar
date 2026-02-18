"""BloodWar - main game class."""

import random
import sys

import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WORLD_WIDTH, WORLD_HEIGHT,
)
from tiles import get_tile, init_grass_variants
from player import Player
from items import Tree

from src.input_handler import InputHandler
from src.spawner import Spawner
from src.combat import Combat
from src.collision import Collision
from src.renderer import Renderer

# Definice dostupných upgradů
UPGRADES = [
    {"id": "speed",     "name": "Rychlost pohybu",   "desc": "+50 px/s"},
    {"id": "firerate",  "name": "Kadence střelby",    "desc": "-10 framů cooldown"},
    {"id": "magnet",    "name": "Magnetický dosah",   "desc": "+60 px dosah gemů"},
    {"id": "multishot", "name": "Dvojitá střela",     "desc": "+1 projektil"},
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
        self.level_up_pending = False
        self.upgrade_choices = []

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.game_over or self.level_up_pending:
            return

        self.frame_count += 1
        self.score = self.frame_count // FPS

        # Spawn enemy (dynamický interval)
        if self.frame_count % self._current_spawn_interval() == 0:
            self.spawner.spawn_enemy()

        # Shoot (dynamický cooldown)
        if self.frame_count % self.wand_cooldown_frames == 0:
            self.combat.shoot()

        # Update player
        self.player.update(dt)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player.position, self.elapsed_seconds)

        # Update projectiles
        self.projectiles.update(dt)

        # Update gems
        for gem in self.gems:
            gem.update(dt, self.player.position, self.player.magnet_radius)

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
