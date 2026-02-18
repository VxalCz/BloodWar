"""BloodWar - Combat module."""

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
        """Shoot projectile toward nearest enemy."""
        target = self.find_nearest_enemy()
        if target is None:
            return

        direction = target.position - self.game.player.position

        if direction.length() > 0:
            projectile = Projectile(
                self.game.player.position.x,
                self.game.player.position.y,
                direction
            )
            self.game.projectiles.add(projectile)
            self.game.all_sprites.add(projectile)
