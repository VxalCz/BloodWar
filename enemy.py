"""Třídy Enemy, Projectile a OrbitalProjectile - nepřátelé a střelba."""

import math

import pygame

from constants import (
    ENEMY_SIZE, BASE_ENEMY_SPEED, RED,
    PROJECTILE_SPEED, PROJECTILE_SIZE, YELLOW,
    ENEMY_ANIM_SCALE, ENEMY_ANIM_SPEED,
    FAST_ENEMY_SPEED_MULT, FAST_ENEMY_SCALE,
    TANK_ENEMY_HP, TANK_ENEMY_SCALE, TANK_ENEMY_SPEED_MULT, TANK_ENEMY_GEM_COUNT,
    ORBIT_RADIUS, ORBIT_SPEED,
)


class Enemy(pygame.sprite.Sprite):
    """Nepřítel - slime s animací, pohybuje se k hráči."""

    def __init__(
        self, x: float, y: float,
        hp: int = 1,
        speed_mult: float = 1.0,
        anim_scale: int = ENEMY_ANIM_SCALE,
        gem_count: int = 1,
    ) -> None:
        super().__init__()

        # HP a stats
        self.max_hp = hp
        self.hp = hp
        self.speed_mult = speed_mult
        self.gem_count = gem_count

        # Načtení sprite sheetu (2 framy vedle sebe)
        sprite_sheet = pygame.image.load("image/slime.png").convert()

        # Nastavení průhlednosti (černá barva)
        sprite_sheet.set_colorkey((0, 0, 0))

        # Rozměr jednoho snímku
        frame_width = sprite_sheet.get_width() // 2
        frame_height = sprite_sheet.get_height()

        # Zvětšení snímku dle anim_scale
        self.frame_width = frame_width * anim_scale
        self.frame_height = frame_height * anim_scale

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

    def take_hit(self) -> bool:
        """Zpracuje zásah. Vrací True pokud nepřítel zemřel."""
        self.hp -= 1
        return self.hp <= 0

    def update(self, dt: float, player_position: pygame.math.Vector2, elapsed_seconds: float = 0.0, slow_factor: float = 1.0) -> None:
        """Aktualizace pozice nepřítele - pohyb k hráči."""
        # Vektor od nepřítele k hráči
        direction = player_position - self.position

        # Normalizace a nastavení rychlosti
        if direction.length() > 0:
            self.velocity = direction.normalize()
        else:
            self.velocity = pygame.math.Vector2(0, 0)

        # Rychlost roste s časem: každé 2 minuty +100%; násobeno speed_mult a slow_factor
        speed = BASE_ENEMY_SPEED * self.speed_mult * (1.0 + elapsed_seconds / 120.0) * slow_factor

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


class FastEnemy(Enemy):
    """Rychlý, malý nepřítel - 2× rychlost, menší sprite."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x, y,
            hp=1,
            speed_mult=FAST_ENEMY_SPEED_MULT,
            anim_scale=FAST_ENEMY_SCALE,
            gem_count=1,
        )


class TankEnemy(Enemy):
    """Pomalý, velký nepřítel - 3 životy, větší sprite, 3 gemy."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x, y,
            hp=TANK_ENEMY_HP,
            speed_mult=TANK_ENEMY_SPEED_MULT,
            anim_scale=TANK_ENEMY_SCALE,
            gem_count=TANK_ENEMY_GEM_COUNT,
        )


class Projectile(pygame.sprite.Sprite):
    """Projektil - žlutý čtvereček vystřelený směrem k nepříteli."""

    def __init__(
        self, x: float, y: float, direction: pygame.math.Vector2,
        speed: float = None, size: int = None, lifetime: float = 2.0, pierce: int = 0,
    ) -> None:
        super().__init__()
        if speed is None:
            speed = PROJECTILE_SPEED
        if size is None:
            size = PROJECTILE_SIZE

        # Vytvoření surface pro sprite
        self.image = pygame.Surface((size, size))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

        # Pozice a rychlost pomocí Vector2
        self.position = pygame.math.Vector2(x, y)
        self.velocity = direction.normalize() * speed
        self._lifetime = 0.0
        self._max_lifetime = lifetime
        self.pierce_remaining = pierce

    def update(self, dt: float) -> None:
        """Aktualizace pozice projektilu."""
        self.position += self.velocity * dt
        self.rect.center = self.position

        # Odstranění po uplynutí životnosti
        self._lifetime += dt
        if self._lifetime > self._max_lifetime:
            self.kill()


class OrbitalProjectile(pygame.sprite.Sprite):
    """Orbitální projektil - rotuje kolem hráče a poškozuje nepřátele."""

    HIT_COOLDOWN = 0.5  # sekundy mezi zásahy téhož nepřítele

    def __init__(self, angle_offset: float) -> None:
        super().__init__()
        self.angle = angle_offset
        self._hit_cooldowns: dict[int, float] = {}

        # Fialový kruh
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 80, 255), (9, 9), 9)
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(0, 0)

    def update(self, dt: float, player_position: pygame.math.Vector2) -> None:
        """Rotuje kolem hráče a aktualizuje cooldowny zásahů."""
        self.angle = (self.angle + ORBIT_SPEED * dt) % (2 * math.pi)
        self.position = player_position + pygame.math.Vector2(
            math.cos(self.angle) * ORBIT_RADIUS,
            math.sin(self.angle) * ORBIT_RADIUS,
        )
        self.rect.center = self.position

        # Odpočítání cooldownů
        for k in list(self._hit_cooldowns):
            self._hit_cooldowns[k] -= dt
            if self._hit_cooldowns[k] <= 0:
                del self._hit_cooldowns[k]

    def can_hit(self, enemy) -> bool:
        """Vrací True, pokud lze nepřítele znovu zasáhnout."""
        return id(enemy) not in self._hit_cooldowns

    def register_hit(self, enemy) -> None:
        """Zaregistruje zásah — spustí cooldown pro daného nepřítele."""
        self._hit_cooldowns[id(enemy)] = self.HIT_COOLDOWN
