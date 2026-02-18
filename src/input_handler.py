"""BloodWar - Input handler module."""

import pygame


class InputHandler:
    """Handler for keyboard input."""

    def __init__(self, game) -> None:
        self.game = game

    def handle_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            # Toggle debug grid
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    self.game.show_grid = not self.game.show_grid

            # Restart after game over
            if event.type == pygame.KEYDOWN and self.game.game_over:
                if event.key == pygame.K_r:
                    self.game.__init__()

    def handle_camera(self) -> None:
        """Handle camera movement when debug grid is shown."""
        if not self.game.show_grid:
            return

        keys = pygame.key.get_pressed()
        camera_speed = 300 * (self.game.clock.get_time() / 1000.0)

        if keys[pygame.K_w]:
            self.game.camera_y -= camera_speed
        if keys[pygame.K_s]:
            self.game.camera_y += camera_speed
        if keys[pygame.K_a]:
            self.game.camera_x -= camera_speed
        if keys[pygame.K_d]:
            self.game.camera_x += camera_speed
