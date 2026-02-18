"""BloodWar - Renderer module."""

import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, TILE_SIZE, TILESET_SCALE,
    XP_THRESHOLDS
)
from tiles import get_tile


class Renderer:
    """Handles all rendering and drawing."""

    def __init__(self, game) -> None:
        self.game = game
        # Font caching — vytváříme jednou, ne každý frame
        self.font_huge  = pygame.font.Font(None, 72)
        self.font_big   = pygame.font.Font(None, 56)
        self.font       = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny  = pygame.font.Font(None, 20)
        self.font_debug = pygame.font.Font(None, 12)

    def draw(self) -> None:
        """Draw game to screen."""
        cx = int(self.game.camera_x)
        cy = int(self.game.camera_y)

        self._draw_background(cx, cy)
        self._draw_objects(cx, cy)
        self._draw_ui()

        if self.game.show_grid:
            self._draw_debug_grid()

        if self.game.level_up_pending:
            self._draw_level_up_overlay()

        pygame.display.flip()

    def _draw_background(self, cx: int, cy: int) -> None:
        """Draw tiled grass background offset by camera."""
        grass_tile = self.game.grass_tile
        tw = grass_tile.get_width()
        th = grass_tile.get_height()

        start_col = cx // tw
        start_row = cy // th
        cols_needed = (SCREEN_WIDTH // tw) + 2
        rows_needed = (SCREEN_HEIGHT // th) + 2

        for row in range(start_row, start_row + rows_needed):
            for col in range(start_col, start_col + cols_needed):
                sx = col * tw - cx
                sy = row * th - cy
                self.game.screen.blit(grass_tile, (sx, sy))

    def _draw_objects(self, cx: int, cy: int) -> None:
        """Draw all game objects with Y-sorting, offset by camera."""
        renderables = []

        # Player — přeskočit každý druhý snímek při neranitelnosti (blikání)
        player = self.game.player
        show_player = (
            player.invincibility_timer <= 0
            or int(player.invincibility_timer * 8) % 2 == 0
        )
        if show_player:
            renderables.append((player.position.y, player))

        # Enemies
        for enemy in self.game.enemies:
            renderables.append((enemy.position.y, enemy))

        # Trees (by hitbox bottom)
        for tree in self.game.trees:
            renderables.append((tree.rect.bottom, tree))

        # Sort by Y
        renderables.sort(key=lambda x: x[0])

        # Draw sorted objects with camera offset
        for _, obj in renderables:
            draw_x = obj.rect.left - cx
            draw_y = obj.rect.top - cy
            self.game.screen.blit(obj.image, (draw_x, draw_y))

        # Ledová aura hráče
        player = self.game.player
        if player.aura_radius > 0:
            r = int(player.aura_radius)
            aura_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (100, 180, 255, 35), (r, r), r)
            pygame.draw.circle(aura_surf, (150, 220, 255, 90), (r, r), r, 2)
            self.game.screen.blit(
                aura_surf,
                (int(player.position.x) - cx - r, int(player.position.y) - cy - r),
            )

        # Draw gems and projectiles with camera offset
        for sprite in self.game.gems:
            sx = sprite.rect.left - cx
            sy = sprite.rect.top - cy
            self.game.screen.blit(sprite.image, (sx, sy))

        for sprite in self.game.projectiles:
            sx = sprite.rect.left - cx
            sy = sprite.rect.top - cy
            self.game.screen.blit(sprite.image, (sx, sy))

        # Orbitální projektily (fialové orby)
        for orb in self.game.orbital_projectiles:
            sx = orb.rect.left - cx
            sy = orb.rect.top - cy
            self.game.screen.blit(orb.image, (sx, sy))

        # HP bary nepřátel s více než 1 HP
        for enemy in self.game.enemies:
            if enemy.max_hp > 1:
                bar_w = enemy.rect.width
                bar_h = 4
                bx = enemy.rect.left - cx
                by = enemy.rect.top - cy - 6
                pygame.draw.rect(self.game.screen, (60, 0, 0), (bx, by, bar_w, bar_h))
                fill = int(bar_w * enemy.hp / enemy.max_hp)
                if fill > 0:
                    pygame.draw.rect(self.game.screen, (220, 50, 50), (bx, by, fill, bar_h))

    def _draw_ui(self) -> None:
        """Draw HUD: score, level, XP bar, HP bar, game over."""
        screen = self.game.screen

        if self.game.game_over:
            game_over_text = self.font_huge.render("GAME OVER", True, (255, 50, 50))
            screen.blit(game_over_text, game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            ))
            restart_text = self.font.render("Stiskni R pro restart", True, WHITE)
            screen.blit(restart_text, restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55)
            ))
            score_text = self.font_small.render(
                f"Čas: {self.game.score}s  |  Kills: {self.game.kills}", True, (200, 200, 200)
            )
            screen.blit(score_text, score_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 95)
            ))
            return

        # Score (čas)
        score_text = self.font.render(f"Čas: {self.game.score}s", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Kills
        kills_text = self.font.render(f"Kills: {self.game.kills}", True, WHITE)
        screen.blit(kills_text, (10, 40))

        # Level
        level_text = self.font.render(f"Level: {self.game.level + 1}", True, (255, 220, 50))
        screen.blit(level_text, (10, 70))

        # Spawn interval (debug info)
        interval_text = self.font.render(
            f"Spawn: {self.game._current_spawn_interval()}f", True, (180, 180, 180)
        )
        screen.blit(interval_text, (SCREEN_WIDTH - 150, 10))

        # HP bar hráče
        self._draw_player_hp()

        # XP bar
        self._draw_xp_bar()

    def _draw_player_hp(self) -> None:
        """Draw player HP as a red bar in top-right corner."""
        screen = self.game.screen
        player = self.game.player
        bar_w = 150
        bar_h = 14
        bar_x = SCREEN_WIDTH - bar_w - 10
        bar_y = 10
        ratio = player.hp / player.max_hp if player.max_hp > 0 else 0

        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, (220, 50, 50), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (200, 100, 100), (bar_x, bar_y, bar_w, bar_h), 1)

        hp_text = self.font_tiny.render(f"HP  {player.hp} / {player.max_hp}", True, WHITE)
        screen.blit(hp_text, (bar_x + bar_w // 2 - hp_text.get_width() // 2, bar_y + 16))

    def _draw_xp_bar(self) -> None:
        """Draw XP progress bar at bottom of screen."""
        screen = self.game.screen
        bar_x = 10
        bar_y = SCREEN_HEIGHT - 20
        bar_w = SCREEN_WIDTH - 20
        bar_h = 12

        level = self.game.level
        xp = self.game.xp

        # XP do dalšího levelu
        if level < len(XP_THRESHOLDS):
            xp_needed = XP_THRESHOLDS[level]
            # Předchozí threshold (pro relativní progress)
            xp_prev = XP_THRESHOLDS[level - 1] if level > 0 else 0
            xp_relative = xp - xp_prev
            xp_range = xp_needed - xp_prev
            progress = min(1.0, xp_relative / xp_range) if xp_range > 0 else 1.0
        else:
            progress = 1.0  # Max level

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
        # Fill
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            pygame.draw.rect(screen, (80, 200, 120), (bar_x, bar_y, fill_w, bar_h))
        # Border
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_w, bar_h), 1)

        # XP text
        if level < len(XP_THRESHOLDS):
            xp_prev = XP_THRESHOLDS[level - 1] if level > 0 else 0
            xp_text = self.font_tiny.render(
                f"XP {xp - xp_prev}/{XP_THRESHOLDS[level] - xp_prev}", True, WHITE
            )
        else:
            xp_text = self.font_tiny.render("MAX LEVEL", True, (255, 220, 50))
        screen.blit(xp_text, (bar_x + bar_w // 2 - xp_text.get_width() // 2, bar_y - 2))

    def _draw_level_up_overlay(self) -> None:
        """Draw semi-transparent level-up choice overlay."""
        screen = self.game.screen

        # Tmavý overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Nadpis
        title = self.font_big.render("LEVEL UP!", True, (255, 220, 50))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))

        subtitle = self.font.render("Vyber upgrade (1 / 2 / 3):", True, WHITE)
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 155)))

        choices = self.game.upgrade_choices
        card_w = 200
        card_h = 110
        gap = 30
        total_w = len(choices) * card_w + (len(choices) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = 200

        for i, upgrade in enumerate(choices):
            cx = start_x + i * (card_w + gap)

            # Karta (tmavě modrá)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
            pygame.draw.rect(screen, (30, 50, 100), card_rect, border_radius=8)
            pygame.draw.rect(screen, (80, 130, 220), card_rect, 2, border_radius=8)

            # Číslo volby
            num = self.font_big.render(str(i + 1), True, (255, 220, 50))
            screen.blit(num, num.get_rect(center=(cx + card_w // 2, card_y + 25)))

            # Název upgradu
            name = self.font_small.render(upgrade["name"], True, WHITE)
            screen.blit(name, name.get_rect(center=(cx + card_w // 2, card_y + 65)))

            # Popis
            desc = self.font_small.render(upgrade["desc"], True, (160, 200, 255))
            screen.blit(desc, desc.get_rect(center=(cx + card_w // 2, card_y + 90)))

    def _draw_debug_grid(self) -> None:
        """Draw debug grid with tileset tiles."""
        cell_size = TILE_SIZE * TILESET_SCALE
        screen = self.game.screen

        start_col = int(self.game.camera_x // cell_size)
        end_col = start_col + (SCREEN_WIDTH // cell_size) + 2
        start_row = int(self.game.camera_y // cell_size)
        end_row = start_row + (SCREEN_HEIGHT // cell_size) + 2

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                screen_x = col * cell_size - self.game.camera_x
                screen_y = row * cell_size - self.game.camera_y

                tile = get_tile(col, row)
                screen.blit(tile, (screen_x, screen_y))

                pygame.draw.rect(
                    screen, (255, 255, 255),
                    (screen_x, screen_y, cell_size, cell_size), 1
                )

                text = self.font_debug.render(f"({col},{row})", True, (255, 255, 255))
                screen.blit(text, (screen_x + 2, screen_y + 2))
