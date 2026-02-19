"""BloodWar - Collision module."""

import pygame
from pygame.sprite import spritecollide

from constants import GEM_VALUE, XP_THRESHOLDS, EXPLOSION_RADIUS
from items import ExperienceGem


class Collision:
    """Handles collision detection and game logic."""

    def __init__(self, game) -> None:
        self.game = game

    def check_collisions(self) -> None:
        """Check all collision interactions."""
        if self.game.game_over:
            return

        # Projectile vs Enemy — pierce logika (False, False = nemazat automaticky)
        hits = pygame.sprite.groupcollide(
            self.game.enemies, self.game.projectiles, False, False
        )
        dead_enemies: set[int] = set()
        dead_projectiles: set[int] = set()

        for enemy, proj_list in hits.items():
            if id(enemy) in dead_enemies:
                continue
            if not enemy.alive():
                continue
            for proj in proj_list:
                if id(proj) in dead_projectiles:
                    continue
                # Nepřítel dostane hit
                killed = enemy.take_hit()
                # Pierce logika
                if proj.pierce_remaining > 0:
                    proj.pierce_remaining -= 1
                else:
                    dead_projectiles.add(id(proj))
                    proj.kill()
                # Smrt nepřítele
                if killed:
                    dead_enemies.add(id(enemy))
                    self._handle_enemy_death(enemy)
                    break

        # Orbital vs Enemy
        for orb in self.game.orbital_projectiles:
            for enemy in spritecollide(orb, self.game.enemies, False):
                if orb.can_hit(enemy):
                    orb.register_hit(enemy)
                    if enemy.take_hit():
                        self._handle_enemy_death(enemy)

        # Player vs Gems
        collected_gems = pygame.sprite.spritecollide(
            self.game.player, self.game.gems, True
        )
        for gem in collected_gems:
            self.game.xp += GEM_VALUE + self.game.player.xp_bonus
            self._check_level_up()
            self.game.particle_system.spawn_gem_pickup(gem.rect.centerx, gem.rect.centery)

        # Player vs Trees (hitbox) — směrový pushback
        player = self.game.player
        for tree in self.game.trees:
            if player.rect.colliderect(tree.hitbox):
                pr = player.rect
                hb = tree.hitbox
                overlap_x = min(pr.right, hb.right) - max(pr.left, hb.left)
                overlap_y = min(pr.bottom, hb.bottom) - max(pr.top, hb.top)
                if overlap_x < overlap_y:
                    if pr.centerx < hb.centerx:
                        player.position.x -= overlap_x
                    else:
                        player.position.x += overlap_x
                else:
                    if pr.centery < hb.centery:
                        player.position.y -= overlap_y
                    else:
                        player.position.y += overlap_y
                player.rect.center = player.position

        # Player vs Enemies — HP + neranitelnost
        if pygame.sprite.spritecollide(self.game.player, self.game.enemies, False):
            player = self.game.player
            if player.invincibility_timer <= 0:
                self.game.particle_system.spawn_player_hit(player.position.x, player.position.y)
            if player.take_hit():
                self.game.game_over = True

    def _handle_enemy_death(self, enemy, already_killed: set = None) -> None:
        """Zpracuje smrt nepřítele: dropy, vampirismus, exploze."""
        game = self.game
        player = game.player

        if already_killed is None:
            already_killed = set()
        already_killed.add(id(enemy))

        # Drop gemů
        for _ in range(enemy.gem_count):
            gem = ExperienceGem(enemy.position.x, enemy.position.y)
            game.gems.add(gem)
            game.all_sprites.add(gem)

        game.particle_system.spawn_death(enemy.position.x, enemy.position.y)
        enemy.kill()
        game.kills += 1

        # Vampirismus
        if player.heal_on_kill > 0:
            player.heal_accum += player.heal_on_kill
            if player.heal_accum >= 1.0:
                heal = int(player.heal_accum)
                player.heal_accum -= heal
                player.hp = min(player.max_hp, player.hp + heal)

        # Exploze — AoE kolem zabitého nepřítele
        if player.has_explosion:
            explosion_pos = enemy.position.copy()
            game.particle_system.spawn_explosion(explosion_pos.x, explosion_pos.y)
            for other in list(game.enemies):
                if id(other) in already_killed:
                    continue
                if other.position.distance_to(explosion_pos) <= EXPLOSION_RADIUS:
                    already_killed.add(id(other))
                    self._handle_enemy_death(other, already_killed)

    def _check_level_up(self) -> None:
        """Zkontroluje, zda hráč dosáhl dalšího levelu."""
        level = self.game.level
        if level >= len(XP_THRESHOLDS):
            return  # Max level
        if self.game.xp >= XP_THRESHOLDS[level]:
            self.game.level += 1
            self.game._trigger_level_up()
