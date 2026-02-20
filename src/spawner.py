"""BloodWar - Spawner module."""

import random

import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_SIZE
from enemy import Enemy, FastEnemy, TankEnemy


class Spawner:
    """Handles enemy spawning."""

    def __init__(self, game) -> None:
        self.game = game

    def _pick_enemy_class(self) -> type:
        """Vybere typ nepřítele podle uplynulého času."""
        elapsed = self.game.elapsed_seconds
        if elapsed < 60:
            # Prvních 60s — jen základní slimové
            return Enemy
        elif elapsed < 120:
            # 60–120s — mix slimů a rychlých
            return random.choice([Enemy, Enemy, FastEnemy])
        else:
            # 120s+ — všechny typy včetně tanků
            return random.choice([Enemy, FastEnemy, TankEnemy])

    def _spawn_count(self) -> int:
        """Počet nepřátel na jeden spawn — roste lineárně každou minutu."""
        return 1 + int(self.game.elapsed_seconds // 60)

    def _spawn_one(self) -> None:
        """Spawnuje jednoho nepřítele na náhodném okraji obrazovky."""
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

        EnemyClass = self._pick_enemy_class()
        enemy = EnemyClass(x, y, elapsed_seconds=self.game.elapsed_seconds)
        self.game.enemies.add(enemy)
        self.game.all_sprites.add(enemy)

    def spawn_enemy(self) -> None:
        """Spawnuje skupinu nepřátel — počet roste lineárně s časem."""
        for _ in range(self._spawn_count()):
            self._spawn_one()
