"""BloodWar - Combat module."""

import math

import pygame

from enemy import Enemy, Projectile


class Combat:
    """Handles combat mechanics - targeting and shooting."""

    def __init__(self, game) -> None:
        self.game = game

    def find_nearest_enemy(self) -> "Enemy | None":
        """Find nearest enemy to player."""
        if not self.game.enemies:
            return None

        nearest_enemy = None
        nearest_distance = float('inf')

        for enemy in self.game.enemies:
            distance = self.game.player.position.distance_to(enemy.position)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_enemy = enemy

        return nearest_enemy

    def shoot(self) -> None:
        """Shoot projectiles toward nearest enemy."""
        target = self.find_nearest_enemy()
        if target is None:
            return

        direction = target.position - self.game.player.position
        if direction.length() == 0:
            return

        count = self.game.player.projectile_count

        if count == 1:
            self._spawn_projectile(direction)
        else:
            # Spread: rozložit projektily symetricky kolem cíle
            spread_angle = 15.0  # stupňů mezi projektily
            base_angle = math.atan2(direction.y, direction.x)
            total_spread = spread_angle * (count - 1)
            start_angle = base_angle - math.radians(total_spread / 2)

            for i in range(count):
                angle = start_angle + math.radians(spread_angle * i)
                spread_dir = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                self._spawn_projectile(spread_dir)

    def _spawn_projectile(self, direction: pygame.math.Vector2) -> None:
        """Vytvoří projektil z pozice hráče."""
        projectile = Projectile(
            self.game.player.position.x,
            self.game.player.position.y,
            direction
        )
        self.game.projectiles.add(projectile)
        self.game.all_sprites.add(projectile)
