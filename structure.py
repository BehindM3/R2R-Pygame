import pygame
from settings import *
from character import Character
from stats import Stats
from enemy import Enemy

class Structure(Character):

    def __init__(self, x, y, structure_type):

        struct_general_stats = {
            CASTLE : [1000, 12000],
            TOWER : [750, 7000],
            HOUSE : [350, 10000],
            BARRACKS : [250, 11000]
        }

        try:
            image_path = BUILDINGS_PATH + structure_type + ".png"
            print(f"IMAGE PATH ES: {image_path}")
            self.structure_image = pygame.image.load(image_path)
        except Exception as e:
            print(f"Error al cargar la estructura {structure_type}")

        structure_stats = Stats(health=struct_general_stats[structure_type][0], damage=0, speed=0)
        self.spawn_type = "Warrior"
        self.spawn_cooldown = struct_general_stats[structure_type][1]
        super().__init__(stats_obj=structure_stats)

        self.image = self.structure_image
        self.rect = self.image.get_rect(topleft=(x,y))

        self.last_spawn_time = pygame.time.get_ticks()

    def update(self):
        if not self.stats.alive:
            return None
        
        now = pygame.time.get_ticks()

        if now - self.last_spawn_time > self.spawn_cooldown:
            self.last_spawn_time = now
            print(f"Estructura {self.rect.topleft} spawneando un {self.spawn_type}")
            return self.spawn_type
        
        return None

    def die(self):
        super().die()
        print(f"Estructura {self.rect.topleft} destruida, soltando horda final.")

        spawn_list = []
        for _ in range(6):
            spawn_list.append(self.spawn_type)

        return spawn_list

    def draw(self, surface, camera_x, camera_y):
        super().draw(surface, camera_x, camera_y)

        pos_in_screen_x = self.rect.x - camera_x
        pos_in_screen_y = self.rect.y - camera_y
        
        bar_width = self.image.get_width() * 0.8
        bar_height = 10
        bar_x = pos_in_screen_x + (self.image.get_width() * 0.1)
        bar_y = pos_in_screen_y + self.image.get_height() + 5

        health_ratio = self.stats.health / self.stats.max_health
        current_health_width = int(bar_width * health_ratio)

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, current_health_width, bar_height))