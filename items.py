"""Třídy Tree a ExperienceGem - herní objekty a předměty."""

import pygame

from constants import (
    TILE_TREE_X, TILE_TREE_Y, TREE_WIDTH, TREE_HEIGHT,
    TILE_SIZE, TILESET_SCALE, GEM_SIZE, GREEN,
    GEM_SPEED
)
from tiles import get_tile


class Tree(pygame.sprite.Sprite):
    """Strom - malý křovnatý strom jako překážka."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        # Načtení obrázku stromu z tilesetu
        self.image = get_tile(TILE_TREE_X, TILE_TREE_Y, TREE_WIDTH, TREE_HEIGHT)
        self.rect = self.image.get_rect()

        # Pozice - spodní část stromu na zadané souřadnice
        self.rect.bottom = y
        self.rect.left = x

        # Hitbox - jen spodní 1/3 stromu (kmen/kořeny) - posunuto o 1 tile výš
        tree_height = self.rect.height
        self.hitbox = pygame.Rect(
            self.rect.left + self.rect.width // 4,
            self.rect.top + tree_height * 2 // 3 - TILE_SIZE * TILESET_SCALE,
            self.rect.width // 2,
            tree_height // 3
        )


class ExperienceGem(pygame.sprite.Sprite):
    """Experience Gem - zelený kroužek po smrti nepřítele."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        # Vytvoření surface - krouzek (průhledný střed)
        self.image = pygame.Surface((GEM_SIZE * 2, GEM_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (GEM_SIZE, GEM_SIZE), GEM_SIZE)
        pygame.draw.circle(self.image, (0, 0, 0), (GEM_SIZE, GEM_SIZE), GEM_SIZE // 2)
        self.rect = self.image.get_rect(center=(x, y))

        self.position = pygame.math.Vector2(x, y)

    def update(self, dt: float, player_position: pygame.math.Vector2, magnet_radius: float = 100.0) -> None:
        """Aktualizace pozice gemu - magnet efekt."""
        distance = self.position.distance_to(player_position)

        # Magnet efekt - pokud je hráč blízko, gem se pohybuje k hráči
        if distance < magnet_radius:
            direction = player_position - self.position
            if direction.length() > 0:
                self.position += direction.normalize() * GEM_SPEED * dt

        self.rect.center = self.position
