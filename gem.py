import pygame
import settings
import random
from math import hypot

try:
    GEMS_ANIM_SPRITESHEET_SURFACE = pygame.image.load(settings.GEM_PATH_SPRITESHEET)
except Exception as e:
    print(f"Error al cargar el spritesheet de gemas: {e}")
    GEMS_ANIM_SPRITESHEET_SURFACE = None


class Gem():

    def __init__(self, x, y, gem_type):
        
        if gem_type not in settings.GEM_STATS or GEMS_ANIM_SPRITESHEET_SURFACE == None:
            print(f"Advertencia: Tipo de gema '{gem_type}' no encontrada, o spritesheet no encontrado.")
            gem_type = "bronze"

        frame_coords_list, self.xp_value, _ = settings.GEM_STATS[gem_type]
        self.animation_frames = []
        self.type = gem_type

        try:
            for coord in frame_coords_list:
                frame = GEMS_ANIM_SPRITESHEET_SURFACE.subsurface(pygame.Rect(coord))
                frame = pygame.transform.scale(frame, (20, 20))
                self.animation_frames.append(frame)

        except Exception as e:
            print(f"Error al cargar la imagen de la gema {gem_type}: {e}")
            fallbac_image = pygame.Surface((24,24))
            fallbac_image.fill((200,200,200))
            self.animation_frames = [fallbac_image]

        self.current_frame_index = 0
        self.image = self.animation_frames[self.current_frame_index]
        self.last_frame_update = pygame.time.get_ticks()

        self.rect = self.image.get_rect(center=(x,y))

        self.is_active = True

        self.target_player = None
        self.magnet_speed = 5

    def update(self, player_rect):

        if not self.is_active:
            return
        
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > settings.GEM_ANIMATION_SPEED:
            self.last_frame_update = now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame_index]

        if player_rect:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery

            distance = hypot(dx, dy)
            if distance < settings.PLAYER_MAGNET_RADIUS:
                if distance > 1:
                    move_x = (dx/distance) * self.magnet_speed
                    move_y = (dy/distance) * self.magnet_speed
                    self.rect.x += move_x
                    self.rect.y += move_y

    def draw(self, surface, camera_x, camera_y):
        if self.is_active:
            pos_x = self.rect.x - camera_x
            pos_y = self.rect.y - camera_y
            surface.blit(self.image, (pos_x, pos_y))

    def die(self):
        super().die()

        available_gem_types = list(settings.GEM_STATS.keys())
        gem_weights = [70, 25, 5]
        gem_type_to_drop = random.choices(available_gem_types, weights=gem_weights, k=1)[0]
        new_gem = Gem(self.rect.centerx, self.rect.centery, gem_type_to_drop)

        return new_gem