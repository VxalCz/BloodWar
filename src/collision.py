"""BloodWar - Collision module."""

import pygame

from constants import GEM_VALUE
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

        # Player vs Gems
        collected_gems = pygame.sprite.spritecollide(
            self.game.player, self.game.gems, True
        )
        for gem in collected_gems:
            self.game.score += GEM_VALUE

        # Player vs Trees (hitbox)
        for tree in self.game.trees:
            if self.game.player.rect.colliderect(tree.hitbox):
                self.game.player.position.y -= 1
                self.game.player.rect.center = self.game.player.position

        # Player vs Enemies
        if pygame.sprite.spritecollide(self.game.player, self.game.enemies, False):
            self.game.game_over = True
            print(f"Game Over! Skóre: {self.game.score // 60} vteřin")
