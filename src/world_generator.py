"""BloodWar - World generation module.

Handles world generation including water tiles and trees.
"""

import random
from typing import Set

import pygame

from constants import (
    WORLD_WIDTH, WORLD_HEIGHT,
    TILE_SIZE, TILESET_SCALE,
)


class WorldGenerator:
    """Handles world generation - water tiles and trees."""
    
    def __init__(self, seed: int = 42) -> None:
        """Initialize world generator with optional seed.
        
        Args:
            seed: Random seed for reproducible world generation
        """
        self._rng = random.Random(seed)
        self._water_tiles: Set[tuple[int, int]] = set()
    
    @property
    def water_tiles(self) -> Set[tuple[int, int]]:
        """Return set of water tile coordinates (col, row)."""
        return self._water_tiles
    
    def generate_water(self, spawn_col: int, spawn_row: int) -> None:
        """Generate water bodies (lakes) in the world.
        
        Creates rectangular lakes with at least 1-tile gap between them.
        Lakes are not generated near the spawn area.
        
        Args:
            spawn_col: World column of player spawn
            spawn_row: World row of player spawn
        """
        tile_px = TILE_SIZE * TILESET_SCALE
        world_tw = WORLD_WIDTH // tile_px
        world_th = WORLD_HEIGHT // tile_px
        
        size_pool = [
            (2, 2), (2, 3), (3, 2),                    # malé
            (3, 4), (4, 3), (4, 4), (5, 3), (3, 5),   # střední
            (6, 4), (4, 6), (7, 5), (5, 7),            # velká jezírka
        ]
        
        for _ in range(30):
            w, h = self._rng.choice(size_pool)
            cx = self._rng.randint(2, world_tw - w - 2)
            cy = self._rng.randint(2, world_th - h - 2)
            
            # Skip if near spawn
            if abs(cx + w // 2 - spawn_col) < 10 and abs(cy + h // 2 - spawn_row) < 10:
                continue
            
            # Check 1-tile border around new rectangle
            if any((tx, ty) in self._water_tiles
                   for ty in range(cy - 1, cy + h + 1)
                   for tx in range(cx - 1, cx + w + 1)):
                continue
            
            # Add water tiles
            for ty in range(cy, cy + h):
                for tx in range(cx, cx + w):
                    self._water_tiles.add((tx, ty))
    
    def generate_trees(
        self,
        player_position: pygame.math.Vector2,
        tree_count: int = 200,
    ) -> list[tuple[int, int]]:
        """Generate trees in the world, avoiding water and spawn area.
        
        Args:
            player_position: Player spawn position in world coordinates
            tree_count: Number of trees to generate
            
        Returns:
            List of (x, y) world coordinates for tree positions
        """
        tile_px = TILE_SIZE * TILESET_SCALE
        tree_positions: list[tuple[int, int]] = []
        
        # TREE_WIDTH and TREE_HEIGHT in tiles
        tree_width_tiles = 2
        tree_height_tiles = 3
        
        for _ in range(tree_count * 2):  # Try more times to find valid positions
            if len(tree_positions) >= tree_count:
                break
                
            x = self._rng.randint(100, WORLD_WIDTH - 100)
            y = self._rng.randint(100, WORLD_HEIGHT - 100)
            
            # Skip if near player spawn
            if player_position.distance_to(pygame.math.Vector2(x, y)) < 200:
                continue
            
            # Check if tree area (2×3 tiles) overlaps with water
            tc0 = x // tile_px
            tc1 = (x + tree_width_tiles * tile_px - 1) // tile_px
            tr0 = (y - tree_height_tiles * tile_px) // tile_px
            tr1 = (y - 1) // tile_px
            
            if any((tc, tr) in self._water_tiles
                   for tr in range(tr0, tr1 + 1)
                   for tc in range(tc0, tc1 + 1)):
                continue
            
            tree_positions.append((x, y))
        
        return tree_positions
