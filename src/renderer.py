"""BloodWar - Renderer module."""

import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, TILE_SIZE, TILESET_SCALE
)
from tiles import get_tile


class Renderer:
    """Handles all rendering and drawing."""

    def __init__(self, game) -> None:
        self.game = game

    def draw(self) -> None:
        """Draw game to screen."""
        self._draw_background()
        self._draw_objects()
        self._draw_ui()

        if self.game.show_grid:
            self._draw_debug_grid()

        pygame.display.flip()

    def _draw_background(self) -> None:
        """Draw tiled grass background."""
        grass_tile = self.game.grass_tile
        grass_width = grass_tile.get_width()
        grass_height = grass_tile.get_height()

        cols_needed = (SCREEN_WIDTH // grass_width) + 2
        rows_needed = (SCREEN_HEIGHT // grass_height) + 2

        for row in range(rows_needed):
            for col in range(cols_needed):
                x = col * grass_width
                y = row * grass_height
                if x < SCREEN_WIDTH + grass_width and y < SCREEN_HEIGHT + grass_height:
                    self.game.screen.blit(grass_tile, (x, y))

    def _draw_objects(self) -> None:
        """Draw all game objects with Y-sorting."""
        renderables = []

        # Player
        renderables.append((self.game.player.position.y, self.game.player))

        # Enemies
        for enemy in self.game.enemies:
            renderables.append((enemy.position.y, enemy))

        # Trees (by hitbox bottom)
        for tree in self.game.trees:
            renderables.append((tree.rect.bottom, tree))

        # Sort by Y
        renderables.sort(key=lambda x: x[0])

        # Draw sorted objects
        for y, obj in renderables:
            self.game.screen.blit(obj.image, obj.rect)

        # Draw gems and projectiles
        self.game.all_sprites.draw(self.game.screen)

    def _draw_ui(self) -> None:
        """Draw UI elements (score, game over)."""
        screen = self.game.screen

        if not self.game.game_over:
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Skóre: {self.game.score // 60}", True, WHITE)
            screen.blit(score_text, (10, 10))
        else:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GAME OVER", True, (255, 50, 50))
            text_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            screen.blit(game_over_text, text_rect)

            font_small = pygame.font.Font(None, 36)
            restart_text = font_small.render("Stiskni R pro restart", True, WHITE)
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            screen.blit(restart_text, restart_rect)

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

                font = pygame.font.Font(None, 12)
                text = font.render(f"({col},{row})", True, (255, 255, 255))
                screen.blit(text, (screen_x + 2, screen_y + 2))
