"""BloodWar - Spawner module."""

import random

import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_SIZE
from enemy import Enemy


class Spawner:
    """Handles enemy spawning."""

    def __init__(self, game) -> None:
        self.game = game

    def spawn_enemy(self) -> None:
        """Create new enemy at screen edge (world-space)."""
        cx = self.game.camera_x
        cy = self.game.camera_y
        side = random.randint(0, 3)

        if side == 0:  # Top
            x = cx + random.randint(0, SCREEN_WIDTH)
            y = cy - ENEMY_SIZE
        elif side == 1:  # Bottom
            x = cx + random.randint(0, SCREEN_WIDTH)
            y = cy + SCREEN_HEIGHT + ENEMY_SIZE
        elif side == 2:  # Left
            x = cx - ENEMY_SIZE
            y = cy + random.randint(0, SCREEN_HEIGHT)
        else:  # Right
            x = cx + SCREEN_WIDTH + ENEMY_SIZE
            y = cy + random.randint(0, SCREEN_HEIGHT)

        enemy = Enemy(x, y)
        self.game.enemies.add(enemy)
        self.game.all_sprites.add(enemy)
