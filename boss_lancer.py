import pygame
import settings
from enemy import Enemy


class BossLancer(Enemy):

    def __init__(self, x_start=100, y_start=100):
        super().__init__(x_start, y_start)

        # Stats del jefe
        self.stats.max_health = 650
        self.stats.health = self.stats.max_health
        self.stats.damage = 30
        self.stats.speed = settings.ENEMY_SPEED * 0.75

        # lanza = más alcance
        self.attack_radius = settings.ENEMY_ATTACK_RADIUS * 2.5
        self.attack_cooldown = 900  # ms

        self.is_boss = True
        self.drop_gem = False

        # volver a centrar rect con el nuevo tamaño de imagen
        self.set_status(settings.IDLE)
        self.image = self.animation[settings.IDLE][0]
        self.rect = self.image.get_rect(center=(x_start, y_start))

        # Ajuste de hitbox
        self.rect.width  = int(self.rect.width * 0.55)
        self.rect.height = int(self.rect.height * 0.65)

        self.rect.centerx = x_start
        self.rect.centery = y_start

    def _slice_sheet(self, sheet, num_frames, scale):
        sheet_w, sheet_h = sheet.get_size()
        frame_w = sheet_w // num_frames
        frames = []
        for i in range(num_frames):
            rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
            frame = sheet.subsurface(rect)
            frame = pygame.transform.scale(
                frame,
                (int(frame_w * scale), int(sheet_h * scale))
            )
            frames.append(frame)
        return frames

    def load_sprites(self, _unused_colour):
        base_path = getattr(settings, "BOSS_ASSETS_PATH", "./assets/boss")

        idle_path   = f"{base_path}/Lancer_Idle.png"
        run_path    = f"{base_path}/Lancer_Run.png"
        attack_path = f"{base_path}/Lancer_Right_Attack.png"
        death_path  = "./assets/particles/multiple/Effect.png"

        idle_sheet   = pygame.image.load(idle_path).convert_alpha()
        run_sheet    = pygame.image.load(run_path).convert_alpha()
        attack_sheet = pygame.image.load(attack_path).convert_alpha()
        death_sheet  = pygame.image.load(death_path).convert_alpha()

        # factor de escala del boss
        scale = 0.9

        self.animation[settings.IDLE]  = self._slice_sheet(idle_sheet,   12, scale)
        self.animation[settings.RUN]   = self._slice_sheet(run_sheet,     6, scale)
        self.animation[settings.ATACK] = self._slice_sheet(attack_sheet,  3, scale)

        # animación de muerte: mismo efecto, más grande
        death_frames = []
        coords_dead = [
            (1393, 24, 97, 122),
            (1585, 31, 96, 114),
            (1787, 29, 86, 110),
            (1979, 28, 85, 97),
            (1959, 42, 85, 97),
        ]
        for x, y, w, h in coords_dead:
            frame = death_sheet.subsurface((x, y, w, h))
            gray = settings.grayscale(frame)
            death_frames.append(
                pygame.transform.scale(
                    gray,
                    (int(w * scale * 1.3), int(h * scale * 1.3))
                )
            )
        self.animation[settings.DEATH] = death_frames

    def update(self, player_x, player_y):
        if not self.stats.alive:
            if self.actual_status != settings.DEATH:
                self.set_status(settings.DEATH)
                self.index_frame = 0
            self.update_animation()
            return

        now = pygame.time.get_ticks()

        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        dist = (dx * dx + dy * dy) ** 0.5

        in_range = dist < self.attack_radius
        cd_ready = (now - self.last_attack_time > self.attack_cooldown)

        if in_range and cd_ready:
            self.set_status(settings.ATACK)
            self.last_attack_time = now
            self.is_moving = False
        else:
            self.set_status(settings.RUN)
            self.is_moving = True
            if dist > 1:
                self.rect.x += (dx / dist) * self.stats.speed
                self.rect.y += (dy / dist) * self.stats.speed

        self.facing_right = dx >= 0
        self.update_animation()

    def can_attack(self, target):
        if not self.stats.alive:
            return False

        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = (dx*dx + dy*dy)**0.5

        now = pygame.time.get_ticks()
        in_range = dist < self.attack_radius
        cd_ready = (now - self.last_attack_time > self.attack_cooldown)

        return in_range and cd_ready

    def attack(self, target):
        if not self.stats.alive:
            return
        target.take_damage(self.stats.damage)
        self.last_attack_time = pygame.time.get_ticks()
