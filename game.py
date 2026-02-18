"""BloodWar - main game class."""

import random
import sys

import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    ENEMY_SPAWN_INTERVAL
)
from tiles import get_tile, init_grass_variants
from player import Player
from items import Tree

from src.input_handler import InputHandler
from src.spawner import Spawner
from src.combat import Combat
from src.collision import Collision
from src.renderer import Renderer


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

        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.player)

        # Generate 20 random trees
        for _ in range(20):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            if self.player.position.distance_to(pygame.math.Vector2(x, y)) < 100:
                continue
            tree = Tree(x, y)
            self.trees.add(tree)

        # Game state
        self.running = True
        self.game_over = False
        self.frame_count = 0
        self.score = 0
        self.show_grid = False
        self.camera_x = 0
        self.camera_y = 0

        # Grass tile for background
        self.grass_tile = get_tile(2, 3)

        # Initialize modules
        self.input_handler = InputHandler(self)
        self.spawner = Spawner(self)
        self.combat = Combat(self)
        self.collision = Collision(self)
        self.renderer = Renderer(self)

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.game_over:
            return

        self.frame_count += 1
        self.score += 1

        # Spawn enemy every 60 frames
        if self.frame_count % ENEMY_SPAWN_INTERVAL == 0:
            self.spawner.spawn_enemy()

        # Shoot every 60 frames
        if self.frame_count % 60 == 0:
            self.combat.shoot()

        # Update player (handles its own input)
        self.player.update(dt)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player.position)

        # Update projectiles
        self.projectiles.update(dt)

        # Update gems
        for gem in self.gems:
            gem.update(dt, self.player.position)

        # Handle camera (for debug grid)
        self.input_handler.handle_camera()

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
