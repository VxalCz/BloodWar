"""BloodWar - Particle system."""

import math
import random

import pygame


class Particle:
    """Single particle: position, velocity, lifetime, color, radius."""

    __slots__ = ('x', 'y', 'vx', 'vy', 'lifetime', 'max_lifetime', 'color', 'radius')

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 lifetime: float, color: tuple, radius: int = 3) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.radius = radius

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0


class ParticleSystem:
    """Manages all active particles."""

    def __init__(self) -> None:
        self._particles: list[Particle] = []

    def clear(self) -> None:
        self._particles.clear()

    def update(self, dt: float) -> None:
        self._particles = [p for p in self._particles if p.update(dt)]

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int) -> None:
        for p in self._particles:
            ratio = p.lifetime / p.max_lifetime
            r = max(1, int(p.radius * ratio))
            color = (
                int(p.color[0] * ratio),
                int(p.color[1] * ratio),
                int(p.color[2] * ratio),
            )
            sx = int(p.x - camera_x)
            sy = int(p.y - camera_y)
            pygame.draw.circle(surface, color, (sx, sy), r)

    # --- Private helper ---

    def _burst(self, x: float, y: float, count: int,
               speed_min: float, speed_max: float,
               lifetime_min: float, lifetime_max: float,
               colors: list, radius_min: int, radius_max: int) -> None:
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(speed_min, speed_max)
            lifetime = random.uniform(lifetime_min, lifetime_max)
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                lifetime,
                random.choice(colors),
                random.randint(radius_min, radius_max),
            ))

    # --- Spawn helpers ---

    def spawn_death(self, x: float, y: float) -> None:
        """Red/orange blood burst on enemy death."""
        self._burst(x, y, 10, 50, 180, 0.25, 0.6,
                    [(220, 40, 40), (255, 70, 20), (180, 10, 10)], 2, 5)

    def spawn_explosion(self, x: float, y: float) -> None:
        """Large orange/yellow burst for explosion upgrade."""
        self._burst(x, y, 22, 100, 320, 0.35, 0.8,
                    [(255, 210, 50), (255, 130, 20), (255, 80, 0)], 3, 8)

    def spawn_gem_pickup(self, x: float, y: float) -> None:
        """Green sparkles on XP gem pickup."""
        self._burst(x, y, 5, 40, 120, 0.2, 0.45,
                    [(80, 230, 130), (120, 255, 160)], 2, 4)

    def spawn_player_hit(self, x: float, y: float) -> None:
        """White/red flash on player hit."""
        self._burst(x, y, 8, 60, 150, 0.2, 0.45,
                    [(255, 255, 255), (255, 100, 100)], 2, 5)

    def spawn_level_up(self, x: float, y: float) -> None:
        """Golden burst on level up."""
        self._burst(x, y, 30, 60, 250, 0.5, 1.2,
                    [(255, 220, 50), (255, 255, 150), (255, 180, 30)], 3, 7)
