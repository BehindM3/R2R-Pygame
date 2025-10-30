import pygame
import settings
import random
from math import hypot

class Gem():

    def __init__(self, x, y, gem_type):
        
        if gem_type not in settings.GEM_STATS:
            print(f"Advertencia: Tipo de gema '{gem_type}' no encontrado en settings.GEM_STATS")
            gem_type = "silver"

        image_path, self.xp_value = settings.GEM_STATS[gem_type]
        self.type = gem_type

        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (16,16))
        except Exception as e:
            print(f"Error al cargar la imagen de la gema {gem_type}: {e}")
            self.image = pygame.Surface((16, 16))
            self.image.fill((200, 200, 200))

        self.rect = self.image.get_rect(center=(x,y))

        self.is_active = True

        self.target_player = None
        self.magnet_speed = 3

    def update(self, player_rect):
        distance = hypot(player_rect.centerx - self.rect.centerx, ...)
        if distance < settings.PLAYER_MAGNET_RADIUS:
            pass

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