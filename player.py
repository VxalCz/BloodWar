"""Třída Player - hlavní postava hry."""

import pygame

from constants import (
    WORLD_WIDTH, WORLD_HEIGHT, PLAYER_SPEED,
    ANIMATION_SCALE, ANIMATION_SPEED, BLUE,
    MAGNET_RADIUS, PLAYER_MAX_HP, PLAYER_INVINCIBILITY_TIME,
    PROJECTILE_SPEED, PROJECTILE_SIZE,
    EXPLOSION_DAMAGE, EXPLOSION_RADIUS,
)


class Player(pygame.sprite.Sprite):
    """Hráč - sprite s animací pohybu."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__()

        # Načtení sprite sheetu
        sprite_sheet = pygame.image.load("image/hero_sheet.png").convert()

        # Nastavení průhlednosti (černá barva)
        sprite_sheet.set_colorkey((0, 0, 0))

        # Rozměr jednoho snímku
        frame_width = sprite_sheet.get_width() // 4
        frame_height = sprite_sheet.get_height() // 4

        # Zvětšení snímku
        self.frame_width = frame_width * ANIMATION_SCALE
        self.frame_height = frame_height * ANIMATION_SCALE

        # Rozkrájení na 2D pole: self.animations[dir][frame]
        # Řádek 0 = DOLŮ, 1 = DOPRAVA, 2 = DOLEVA, 3 = NAHORU
        self.animations: list[list[pygame.Surface]] = []
        for row in range(4):
            direction_frames = []
            for col in range(4):
                # Vyříznutí snímku
                frame = sprite_sheet.subsurface(
                    pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                )
                # Zvětšení a přidání do seznamu
                scaled_frame = pygame.transform.scale(frame, (self.frame_width, self.frame_height))
                direction_frames.append(scaled_frame)
            self.animations.append(direction_frames)

        # Mapování: index 1 = DOLEVA, index 2 = DOPRAVA (opačně než původní řádky)
        self.direction_map = {
            0: 0,   # DOLŮ -> řádek 0
            1: 2,   # DOPRAVA -> řádek 2 (původně řádek 1)
            2: 1,   # DOLEVA -> řádek 1 (původně řádek 2)
            3: 3    # NAHORU -> řádek 3
        }

        # Nastavení počátečního snímku
        self.current_frame = 0
        self.animation_timer = 0.0
        self.last_direction = 0  # 0 = dolů

        # Nastavení image a rect
        self.image = self.animations[self.last_direction][0]
        self.rect = self.image.get_rect(center=(x, y))

        # Pozice a rychlost pomocí Vector2
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)

        # Hitbox pro kolize — menší než rect (sprite je 48×96, postava zabírá střed)
        hb_size = int(self.frame_width * 0.55)
        self.hitbox = pygame.Rect(0, 0, hb_size, hb_size)
        self.hitbox.center = (int(x), int(y))

        # Mutable gameplay stats (modifikovatelné upgrady)
        self.speed = PLAYER_SPEED
        self.magnet_radius = MAGNET_RADIUS
        self.projectile_count = 1

        # Projektil stats
        self.proj_size = PROJECTILE_SIZE
        self.proj_speed = PROJECTILE_SPEED
        self.proj_lifetime = 2.0
        self.pierce = 0
        self.bonus_damage = 0          # +1 za každý damage upgrade

        # XP a sběr
        self.xp_bonus = 0
        self.gem_speed_mult = 1.0

        # Vampirismus
        self.heal_on_kill = 0.0
        self.heal_accum = 0.0

        # Regenerace (z vylepšeného heal upgradu)
        self.regen_rate = 0.0       # HP za sekundu
        self.regen_accum = 0.0      # akumulátor pro zlomkové HP

        # Speciální schopnosti
        self.adrenalin = False
        self.adrenalin_damage_mult = 1.0  # DPS bonus při adrenalinu
        self.has_explosion = False
        self.explosion_damage = EXPLOSION_DAMAGE
        self.explosion_radius = EXPLOSION_RADIUS
        self.aura_radius = 0
        self.aura_slow = 1.0   # 1.0 = bez efektu; klesá s levely aury
        self.orbital_count = 0

        # HP systém
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.invincibility_timer = 0.0

    def get_input(self) -> None:
        """Zpracování vstupu z klávesnice."""
        keys = pygame.key.get_pressed()

        # Reset rychlosti
        self.velocity.x = 0
        self.velocity.y = 0

        # WASD ovládání
        if keys[pygame.K_w]:
            self.velocity.y = -1
        if keys[pygame.K_s]:
            self.velocity.y = 1
        if keys[pygame.K_a]:
            self.velocity.x = -1
        if keys[pygame.K_d]:
            self.velocity.x = 1

        # Normalizace diagonálního pohybu
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize()

    def update(self, dt: float) -> None:
        """Aktualizace pozice hráče a animace."""
        self.get_input()

        # Regenerace HP
        if self.regen_rate > 0 and self.hp < self.max_hp:
            self.regen_accum += self.regen_rate * dt
            if self.regen_accum >= 1.0:
                heal = int(self.regen_accum)
                self.regen_accum -= heal
                self.hp = min(self.max_hp, self.hp + heal)

        # Pohyb podle delta time (adrenalin: +150 px/s při HP ≤ 30 %)
        adrenalin_active = self.adrenalin and self.hp <= self.max_hp * 0.3
        effective_speed = self.speed + (150 if adrenalin_active else 0)
        self.position += self.velocity * effective_speed * dt

        # Omezení pohybu na hranice světa
        half_width = self.frame_width // 2
        half_height = self.frame_height // 2
        self.position.x = max(half_width, min(WORLD_WIDTH - half_width, self.position.x))
        self.position.y = max(half_height, min(WORLD_HEIGHT - half_height, self.position.y))

        # Aktualizace rect a hitboxu
        self.rect.center = self.position
        self.hitbox.center = self.rect.center

        # Animace podle směru pohybu
        direction = self.last_direction

        if self.velocity.y > 0:
            direction = 0      # DOLŮ
        elif self.velocity.y < 0:
            direction = 3      # NAHORU
        elif self.velocity.x > 0:
            direction = 1      # DOPRAVA
        elif self.velocity.x < 0:
            direction = 2      # DOLEVA

        self.last_direction = direction

        # Animace - pouze pokud se hráč hybe
        if self.velocity.length() > 0:
            self.animation_timer += dt
            if self.animation_timer >= ANIMATION_SPEED:
                self.animation_timer = 0.0
                self.current_frame = (self.current_frame + 1) % 4
        else:
            # Pokud se nehýbe, zůstat na prvním snímku
            self.current_frame = 0

        # Nastavení aktuálního snímku (přes mapování)
        actual_direction = self.direction_map[direction]
        self.image = self.animations[actual_direction][self.current_frame]

        # Neranitelnost po zásahu
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt

    @property
    def is_adrenalin_active(self) -> bool:
        """Vrací True pokud je adrenalin aktivní (HP ≤ 30 %)."""
        return self.adrenalin and self.hp <= self.max_hp * 0.3

    def take_hit(self, damage: int = 1) -> bool:
        """Zpracuje zásah hráče. Vrací True pokud hráč zemřel."""
        if self.invincibility_timer > 0:
            return False
        self.hp -= damage
        self.invincibility_timer = PLAYER_INVINCIBILITY_TIME
        return self.hp <= 0
