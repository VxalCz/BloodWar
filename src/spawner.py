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
        """Create new enemy at screen edge."""
        side = random.randint(0, 3)

        if side == 0:  # Top
            x = random.randint(0, SCREEN_WIDTH)
            y = -ENEMY_SIZE
        elif side == 1:  # Bottom
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + ENEMY_SIZE
        elif side == 2:  # Left
            x = -ENEMY_SIZE
            y = random.randint(0, SCREEN_HEIGHT)
        else:  # Right
            x = SCREEN_WIDTH + ENEMY_SIZE
            y = random.randint(0, SCREEN_HEIGHT)

        enemy = Enemy(x, y)
        self.game.enemies.add(enemy)
        self.game.all_sprites.add(enemy)
