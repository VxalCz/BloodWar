"""BloodWar - Sprite caching module.

Centralized sprite caching for enemies to avoid repeated loading and scaling.
"""

import pygame
from typing import Optional


# Module-level sprite sheet (loaded once on first use) and frame cache
_sprite_sheet: Optional[pygame.Surface] = None
_sprite_cache: dict[tuple[int, tuple], list[pygame.Surface]] = {}


def _get_enemy_frames(anim_scale: int, color_tint: tuple | None) -> list[pygame.Surface]:
    """Return cached list of 2 frames for given scale and tint.
    
    Args:
        anim_scale: Scale factor for the sprite
        color_tint: RGB tuple for tinting, or None for original colors
        
    Returns:
        List of 2 pygame.Surface objects (the 2 animation frames)
    """
    global _sprite_sheet, _sprite_cache
    
    key = (anim_scale, color_tint)
    cached = _sprite_cache.get(key)
    if cached is not None:
        return cached

    if _sprite_sheet is None:
        _sprite_sheet = pygame.image.load("image/slime.png").convert()
        _sprite_sheet.set_colorkey((0, 0, 0))

    sheet = _sprite_sheet
    frame_width = sheet.get_width() // 2
    frame_height = sheet.get_height()
    scaled_w = frame_width * anim_scale
    scaled_h = frame_height * anim_scale

    frames = []
    for col in range(2):
        frame = sheet.subsurface(
            pygame.Rect(col * frame_width, 0, frame_width, frame_height)
        )
        scaled = pygame.transform.scale(frame, (scaled_w, scaled_h))
        if color_tint is not None:
            scaled = scaled.copy()
            scaled.fill(color_tint, special_flags=pygame.BLEND_RGB_MULT)
        frames.append(scaled)

    _sprite_cache[key] = frames
    return frames


def clear_cache() -> None:
    """Clear all cached sprites. Useful for testing or memory management."""
    global _sprite_sheet, _sprite_cache
    _sprite_sheet = None
    _sprite_cache.clear()
