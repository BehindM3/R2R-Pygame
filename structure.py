import pygame
from settings import *
from character import Character
from stats import Stats

class Structure(Character):

    def __init__(self, x, y, structure_type):

        struct_general_stats = {
            CASTLE : [10, 12000],
            TOWER : [75, 7000],
            HOUSE : [35, 10000],
            BARRACKS : [25, 11000]
    
            #CASTLE : [1000, 12000],
            #TOWER : [750, 7000],
            #HOUSE : [350, 10000],
            #BARRACKS : [250, 11000]
            
        }

        try:
            image_path = BUILDINGS_PATH + structure_type + ".png"
            print(f"IMAGE PATH ES: {image_path}")
            self.structure_image = pygame.image.load(image_path).convert_alpha()
        except Exception as e:
            print(f"Error al cargar la estructura {structure_type}: {e}")
            self.structure_image = pygame.Surface((96, 96))
            self.structure_image.fill((200, 0, 0))

        structure_stats = Stats(
            health=struct_general_stats[structure_type][0],
            damage=0,
            speed=0
        )

        super().__init__(stats_obj=structure_stats)

        self.spawn_type = "Warrior"
        self.spawn_cooldown = struct_general_stats[structure_type][1]

        self.image = self.structure_image
        self.rect = self.image.get_rect(topleft=(x, y))

        self.last_spawn_time = pygame.time.get_ticks()
        self._load_death_animation()


    def _load_death_animation(self):
        try:
            spritesheet_dead = pygame.image.load(DEATH_PARTICLES_PATH).convert_alpha()

            frame_dead_list = []
            coords_dead = [
                (1393, 24, 97, 122),
                (1585, 31, 96, 114),
                (1787, 29, 86, 110),
                (1979, 28, 85, 97),
                (1959, 42, 85, 97),
            ]

            target_w = max(self.image.get_width(), 96)
            target_h = max(self.image.get_height(), 96)

            for coord in coords_dead:
                frame = spritesheet_dead.subsurface(pygame.Rect(coord))
                gray_frame = grayscale(frame)  # función de settings.py
                scaled = pygame.transform.scale(gray_frame, (target_w, target_h))
                frame_dead_list.append(scaled)

            self.animation[DEATH] = frame_dead_list
            print("DEBUG STRUCTURE: animación de muerte cargada correctamente.")

        except Exception as e:
            print(f"Error al cargar animación de muerte de estructura: {e}")
            self.animation[DEATH] = [self.structure_image]


    def update(self):
        # Si está muerta, reproducimos la animación DEATH
        if not self.stats.alive:
            if self.actual_status != DEATH:
                self.set_status(DEATH)
                self.index_frame = 0
            self.update_animation()
            return None

        # Si está viva, solo manejamos el spawn
        now = pygame.time.get_ticks()

        if now - self.last_spawn_time > self.spawn_cooldown:
            self.last_spawn_time = now
            print(f"Estructura {self.rect.topleft} spawneando un {self.spawn_type}")
            return self.spawn_type

        return None

    def die(self):
        super().die()  # pone estado DEATH en Character
        print(f"Estructura {self.rect.topleft} destruida, soltando horda final.")

        spawn_list = []
        for _ in range(6):
            spawn_list.append(self.spawn_type)

        return spawn_list
    
    def draw(self, surface, camera_x, camera_y):
        # Dibuja imagen o frame actual de animación
        super().draw(surface, camera_x, camera_y)

        # Si ya está muerta, no dibujamos barra de vida
        if not self.stats.alive:
            return

        pos_in_screen_x = self.rect.x - camera_x
        pos_in_screen_y = self.rect.y - camera_y

        bar_width = self.image.get_width() * 0.8
        bar_height = 10
        bar_x = pos_in_screen_x + (self.image.get_width() * 0.1)
        bar_y = pos_in_screen_y + self.image.get_height() + 5

        health_ratio = self.stats.health / self.stats.max_health
        current_health_width = int(bar_width * health_ratio)

        pygame.draw.rect(surface, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), 1)
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, current_health_width, bar_height))
