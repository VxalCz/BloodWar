"""Tileset - práce s dlaždicemi a tilesetem."""

import pygame

from constants import (
    TILE_SIZE, TILESET_SCALE, GRASS_TILE_COL, GRASS_TILE_ROW,
    POND_TILE_X, POND_TILE_Y,
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

_tileset_cols: int = 0
_tileset_rows: int = 0


def get_tileset_dims() -> tuple[int, int]:
    """Vrátí (počet sloupců, počet řádků) tilesetu."""
    return _tileset_cols, _tileset_rows


def get_water_tile(top: bool, bottom: bool, left: bool, right: bool) -> pygame.Surface:
    """Autotile: vybere správnou dlaždici vody podle 4 kardinálních sousedů.

    top/bottom/left/right = True pokud soused je také voda.
    Mapuje na 3×3 sadu jezírka (POND_TILE_X/Y je levý horní roh sady).
    """
    tg, bg, lg, rg = not top, not bottom, not left, not right
    # Rohy mají přednost před hranami
    if tg and lg:   col, row = POND_TILE_X,     POND_TILE_Y        # ┌ TL roh
    elif tg and rg: col, row = POND_TILE_X + 2, POND_TILE_Y        # ┐ TR roh
    elif bg and lg: col, row = POND_TILE_X,     POND_TILE_Y + 2    # └ BL roh
    elif bg and rg: col, row = POND_TILE_X + 2, POND_TILE_Y + 2    # ┘ BR roh
    elif tg:        col, row = POND_TILE_X + 1, POND_TILE_Y        # ─ horní hrana
    elif bg:        col, row = POND_TILE_X + 1, POND_TILE_Y + 2    # ─ dolní hrana
    elif lg:        col, row = POND_TILE_X,     POND_TILE_Y + 1    # │ levá hrana
    elif rg:        col, row = POND_TILE_X + 2, POND_TILE_Y + 1    # │ pravá hrana
    else:           col, row = POND_TILE_X + 1, POND_TILE_Y + 1    # □ střed (hluboká voda)
    return get_tile(col, row)


def init_grass_variants() -> None:
    """Inicializace trávy a uložení rozměrů tilesetu (zavolat po pygame.init())."""
    global GRASS_TILE, _tileset_cols, _tileset_rows
    GRASS_TILE = _load_grass_tile()
    ts = pygame.image.load("image/tileset.png")
    _tileset_cols = ts.get_width() // TILE_SIZE
    _tileset_rows = ts.get_height() // TILE_SIZE
