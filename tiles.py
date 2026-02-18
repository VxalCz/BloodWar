"""Tileset - práce s dlaždicemi a tilesetem."""

import pygame

from constants import (
    TILE_SIZE, TILESET_SCALE, GRASS_TILE_COL, GRASS_TILE_ROW,
    _tileset_cache
)


def get_tile(col: int, row: int, width: int = 1, height: int = 1) -> pygame.Surface:
    """Vyřízne dlaždici z tilesetu a zvětší ji."""
    key = (col, row, width, height)
    if key in _tileset_cache:
        return _tileset_cache[key]

    # Použij convert_alpha pro zachování průhlednosti
    tileset = pygame.image.load("image/tileset.png").convert_alpha()

    tile = tileset.subsurface(pygame.Rect(
        col * TILE_SIZE, row * TILE_SIZE,
        width * TILE_SIZE, height * TILE_SIZE
    ))
    scaled = pygame.transform.scale(
        tile,
        (width * TILE_SIZE * TILESET_SCALE, height * TILE_SIZE * TILESET_SCALE)
    )
    _tileset_cache[key] = scaled
    return scaled


def _load_grass_tile() -> pygame.Surface:
    """Načte jednu dlaždici trávy."""
    return get_tile(GRASS_TILE_COL, GRASS_TILE_ROW)


GRASS_TILE: pygame.Surface = None  # type: ignore


def init_grass_variants() -> None:
    """Inicializace trávy (zavolat po pygame.init())."""
    global GRASS_TILE
    GRASS_TILE = _load_grass_tile()
