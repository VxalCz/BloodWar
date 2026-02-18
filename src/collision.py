"""BloodWar - Collision module."""

import pygame

from constants import GEM_VALUE, XP_THRESHOLDS
from items import ExperienceGem


class Collision:
    """Handles collision detection and game logic."""

    def __init__(self, game) -> None:
        self.game = game

    def check_collisions(self) -> None:
        """Check all collision interactions."""
        if self.game.game_over:
            return

        # Projectile vs Enemy
        hits = pygame.sprite.groupcollide(
            self.game.enemies, self.game.projectiles, True, True
        )
        for enemy in hits:
            gem = ExperienceGem(enemy.position.x, enemy.position.y)
            self.game.gems.add(gem)
            self.game.all_sprites.add(gem)
            self.game.kills += 1

        # Player vs Gems
        collected_gems = pygame.sprite.spritecollide(
            self.game.player, self.game.gems, True
        )
        for _ in collected_gems:
            self.game.xp += GEM_VALUE
            self._check_level_up()

        # Player vs Trees (hitbox) — world-space collision, push back
        for tree in self.game.trees:
            if self.game.player.rect.colliderect(tree.hitbox):
                self.game.player.position.y -= 1
                self.game.player.rect.center = self.game.player.position

        # Player vs Enemies
        if pygame.sprite.spritecollide(self.game.player, self.game.enemies, False):
            self.game.game_over = True

    def _check_level_up(self) -> None:
        """Zkontroluje, zda hráč dosáhl dalšího levelu."""
        level = self.game.level
        if level >= len(XP_THRESHOLDS):
            return  # Max level
        if self.game.xp >= XP_THRESHOLDS[level]:
            self.game.level += 1
            self.game._trigger_level_up()
