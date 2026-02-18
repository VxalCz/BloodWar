"""Třídy Enemy a Projectile - nepřátelé a střelba."""

import pygame

from constants import (
    ENEMY_SIZE, BASE_ENEMY_SPEED, RED,
    PROJECTILE_SPEED, PROJECTILE_SIZE, YELLOW,
    ENEMY_ANIM_SCALE, ENEMY_ANIM_SPEED
)


class Enemy(pygame.sprite.Sprite):
    """Nepřítel - slime s animací, pohybuje se k hráči."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__()

        # Načtení sprite sheetu (2 framy vedle sebe)
        sprite_sheet = pygame.image.load("image/slime.png").convert()

        # Nastavení průhlednosti (černá barva)
        sprite_sheet.set_colorkey((0, 0, 0))

        # Rozměr jednoho snímku
        frame_width = sprite_sheet.get_width() // 2
        frame_height = sprite_sheet.get_height()

        # Zvětšení snímku
        self.frame_width = frame_width * ENEMY_ANIM_SCALE
        self.frame_height = frame_height * ENEMY_ANIM_SCALE

        # Rozkrájení na 2 framy
        self.frames: list[pygame.Surface] = []
        for col in range(2):
            frame = sprite_sheet.subsurface(
                pygame.Rect(col * frame_width, 0, frame_width, frame_height)
            )
            scaled_frame = pygame.transform.scale(frame, (self.frame_width, self.frame_height))
            self.frames.append(scaled_frame)

        # Nastavení počátečního snímku
        self.current_frame = 0
        self.animation_timer = 0.0

        # Nastavení image a rect
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

        # Pozice a rychlost pomocí Vector2
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)

    def update(self, dt: float, player_position: pygame.math.Vector2, elapsed_seconds: float = 0.0) -> None:
        """Aktualizace pozice nepřítele - pohyb k hráči."""
        # Vektor od nepřítele k hráči
        direction = player_position - self.position

        # Normalizace a nastavení rychlosti
        if direction.length() > 0:
            self.velocity = direction.normalize()
        else:
            self.velocity = pygame.math.Vector2(0, 0)

        # Rychlost roste s časem: každé 2 minuty +100%
        speed = BASE_ENEMY_SPEED * (1.0 + elapsed_seconds / 120.0)

        # Pohyb podle delta time
        self.position += self.velocity * speed * dt

        # Aktualizace rect
        self.rect.center = self.position

        # Animace - střídání 2 framu
        self.animation_timer += dt
        if self.animation_timer >= ENEMY_ANIM_SPEED:
            self.animation_timer = 0.0
            self.current_frame = (self.current_frame + 1) % 2

        self.image = self.frames[self.current_frame]


class Projectile(pygame.sprite.Sprite):
    """Projektil - žlutý čtvereček vystřelený směrem k nepříteli."""

    def __init__(self, x: float, y: float, direction: pygame.math.Vector2) -> None:
        super().__init__()
        # Vytvoření surface pro sprite
        self.image = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

        # Pozice a rychlost pomocí Vector2
        self.position = pygame.math.Vector2(x, y)
        self.velocity = direction.normalize() * PROJECTILE_SPEED
        self._lifetime = 0.0

    def update(self, dt: float) -> None:
        """Aktualizace pozice projektilu."""
        self.position += self.velocity * dt
        self.rect.center = self.position

        # Odstranění po uplynutí životnosti (2 sekundy letu)
        self._lifetime += dt
        if self._lifetime > 2.0:
            self.kill()
