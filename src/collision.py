"""BloodWar - Collision module."""

import pygame
from pygame.sprite import spritecollide

from constants import GEM_VALUE, xp_threshold, EXPLOSION_RADIUS, TILE_SIZE, TILESET_SCALE, PROJECTILE_DAMAGE, EXPLOSION_DAMAGE
from math import floor
from items import ExperienceGem


def resolve_rect_pushback(mover_rect: pygame.Rect, obstacle_rect: pygame.Rect) -> tuple[float, float]:
    """Calculate pushback vector to resolve collision between two rectangles.
    
    Returns:
        Tuple of (push_x, push_y) - the amount to move the mover to resolve collision.
        Positive values push away from the obstacle center.
    """
    overlap_x = min(mover_rect.right, obstacle_rect.right) - max(mover_rect.left, obstacle_rect.left)
    overlap_y = min(mover_rect.bottom, obstacle_rect.bottom) - max(mover_rect.top, obstacle_rect.top)
    
    if overlap_x < overlap_y:
        # Push horizontally
        if mover_rect.centerx < obstacle_rect.centerx:
            return (-overlap_x, 0)
        else:
            return (overlap_x, 0)
    else:
        # Push vertically
        if mover_rect.centery < obstacle_rect.centery:
            return (0, -overlap_y)
        else:
            return (0, overlap_y)


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

        # Damage = base + bonus_damage, × adrenalin
        player = self.game.player
        base_dmg = PROJECTILE_DAMAGE + player.bonus_damage
        dmg_mult = player.adrenalin_damage_mult if player.is_adrenalin_active else 1.0
        proj_damage = floor(base_dmg * dmg_mult)

        for enemy, proj_list in hits.items():
            if id(enemy) in dead_enemies:
                continue
            if not enemy.alive():
                continue
            for proj in proj_list:
                if id(proj) in dead_projectiles:
                    continue
                # Každý projektil může zasáhnout daného nepřítele max jednou
                eid = id(enemy)
                if eid in proj._hit_enemies:
                    continue
                proj._hit_enemies.add(eid)
                # Nepřítel dostane hit
                killed = enemy.take_hit(proj_damage)
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
        orbital_damage = floor(base_dmg * dmg_mult)
        for orb in self.game.orbital_projectiles:
            for enemy in spritecollide(orb, self.game.enemies, False):
                if orb.can_hit(enemy):
                    orb.register_hit(enemy)
                    if enemy.take_hit(orbital_damage):
                        self._handle_enemy_death(enemy)

        # Player vs Gems
        collected_gems = pygame.sprite.spritecollide(
            self.game.player, self.game.gems, True
        )
        for gem in collected_gems:
            self.game.xp += GEM_VALUE + self.game.player.xp_bonus
            self._check_level_up()
            self.game.particle_system.spawn_gem_pickup(gem.rect.centerx, gem.rect.centery)

        # Player vs Trees — směrový pushback
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

        # Player vs Water tiles — pushback z vodních dlaždic
        tile_px = TILE_SIZE * TILESET_SCALE
        water_tiles = self.game.water_tiles
        pc = player.rect.centerx // tile_px
        pr_row = player.rect.centery // tile_px
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                col, row = pc + dc, pr_row + dr
                if (col, row) not in water_tiles:
                    continue
                wr = pygame.Rect(col * tile_px, row * tile_px, tile_px, tile_px)
                if not player.rect.colliderect(wr):
                    continue
                pr = player.rect
                overlap_x = min(pr.right, wr.right) - max(pr.left, wr.left)
                overlap_y = min(pr.bottom, wr.bottom) - max(pr.top, wr.top)
                if overlap_x < overlap_y:
                    if pr.centerx < wr.centerx:
                        player.position.x -= overlap_x
                    else:
                        player.position.x += overlap_x
                else:
                    if pr.centery < wr.centery:
                        player.position.y -= overlap_y
                    else:
                        player.position.y += overlap_y
                player.rect.center = player.position

        # Player vs Enemies — HP + neranitelnost (damage = max contact_damage z kolizních nepřátel)
        # Používáme hitbox (menší než rect) pro přesnou detekci dotyku
        colliding = pygame.sprite.spritecollide(
            self.game.player, self.game.enemies, False,
            lambda p, e: p.hitbox.colliderect(e.hitbox),
        )
        if colliding:
            player = self.game.player
            if player.invincibility_timer <= 0:
                self.game.particle_system.spawn_player_hit(player.position.x, player.position.y)
            damage = max(e.contact_damage for e in colliding)
            if player.take_hit(damage):
                self.game.game_over = True

    def _handle_enemy_death(self, enemy, already_killed: set = None, from_explosion: bool = False) -> None:
        """Zpracuje smrt nepřítele: dropy, vampirismus, exploze.

        from_explosion=True: vampirismus se nepočítá (řetězové exploze by daly příliš mnoho léčení).
        """
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

        # Vampirismus — pouze přímá zabití (projektil, orbitál), ne výbuchové řetězy
        if player.heal_on_kill > 0 and not from_explosion:
            player.heal_accum += player.heal_on_kill
            if player.heal_accum >= 1.0:
                heal = int(player.heal_accum)
                player.heal_accum -= heal
                player.hp = min(player.max_hp, player.hp + heal)

        # Exploze — AoE kolem zabitého nepřítele; udělá EXPLOSION_DAMAGE, nezabíjí ihned
        if player.has_explosion:
            explosion_pos = enemy.position.copy()
            game.particle_system.spawn_explosion(explosion_pos.x, explosion_pos.y)
            for other in list(game.enemies):
                if id(other) in already_killed:
                    continue
                if other.position.distance_to(explosion_pos) <= player.explosion_radius:
                    if other.take_hit(player.explosion_damage):
                        already_killed.add(id(other))
                        self._handle_enemy_death(other, already_killed, from_explosion=True)

    def _check_level_up(self) -> None:
        """Zkontroluje, zda hráč dosáhl dalšího levelu."""
        if self.game.xp >= xp_threshold(self.game.level):
            self.game.level += 1
            self.game._trigger_level_up()
