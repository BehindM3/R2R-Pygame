import pygame
import settings
import random
from character import Character
from stats import Stats
from math import hypot
from gem import Gem

class Enemy(Character):
    
    def __init__(self, x_start=100, y_start=100):

        unique_speed = settings.ENEMY_SPEED * random.uniform(settings.ENEMY_SPEED_MIN_MOD, settings.ENEMY_SPEED_MAX_MOD)

        enemy_stats = Stats(
            health=50,
            damage=10,
            speed= unique_speed
        )

        super().__init__(stats_obj=enemy_stats)

        #Cargar imagenes del arquero
        self.load_sprites(settings.ENEMIES_COLOR)

        #Definimos la imagen y rect inicial
        self.set_status(settings.RUN)
        self.image = self.animation[settings.RUN][0]
        self.rect = self.image.get_rect(topleft=(x_start, y_start ))
        self.facing_right = True
        self.is_moving = False
        self.attack_cooldown = 1500
        self.last_attack_time = 0

    def load_sprites(self, colour):
        ENEMY_CLASS = "Warrior"

        base_path = f"{settings.PATH_PLAYER}/{colour}/{ENEMY_CLASS}"
        path_idle = f"{base_path}/Idle.png"
        path_run = f"{base_path}/Run.png"
        path_atack = f"{base_path}/Attack1.png"
        path_dead = "./assets/particles/multiple/Effect.png"
        
        # Cargamos las imagenes y manejamos errores
        try:
            spritesheet_idle = pygame.image.load(path_idle).convert_alpha()
            spritesheet_run = pygame.image.load(path_run).convert_alpha()
            spritesheet_atack = pygame.image.load(path_atack).convert_alpha()
            spritesheet_dead = pygame.image.load(path_dead).convert_alpha()
        except pygame.error as e:
            print(f"Error al cargar el sprite del enemigo ({ENEMY_CLASS}): {e}")
            pygame.quit()
            exit()

        # Cargar animacion de idle
        frame_idle_list = []
        coords_idle = [(62,48,79,89),(254,48,79,89),(446,49,79,88),(636,51,81,86),(827,52,83,85),(1020,52,83,85),(1212,50,82,87),(1405,49,80,88)]

        for coord in coords_idle:
            frame = spritesheet_idle.subsurface(pygame.Rect(coord))
            frame_idle_list.append(pygame.transform.scale(frame, (64, 64)))

        self.animation[settings.IDLE] = frame_idle_list

        # Cargamos animacion de run
        frame_run_list = []
        coords_run = [(62,53,76,84),(257,46,68,91),(449,46,67,91),(638,52,76,85),(821,46,93,91),(1014,48,89,89)]

        for coord in coords_run:
            frame = spritesheet_run.subsurface(pygame.Rect(coord))
            frame_run_list.append(pygame.transform.scale(frame, (64, 64)))

        self.animation[settings.RUN] = frame_run_list

        # Cargar animacion de atack
        frame_atack_list = []
        coords_atack = [(57,47,65,90),(246,44,66,93),(427,50,120,104),(619,55,114,101)]

        for coord in coords_atack:
            frame = spritesheet_atack.subsurface(pygame.Rect(coord))
            frame_atack_list.append(pygame.transform.scale(frame, (64, 64)))

        self.animation[settings.ATACK] = frame_atack_list

        #Cargamos animacion de muerte
        frame_dead_list = []
        coords_dead = [(1393,24,97,122),(1585,31,96,114),(1787,29,86,110),(1979,28,85,97),(1959,42,85,97)]

        for coord in coords_dead:
            frame = spritesheet_dead.subsurface(pygame.Rect(coord))
            gray_frame = settings.grayscale(frame)
            frame_dead_list.append(pygame.transform.scale(gray_frame, (64, 64)))

        self.animation[settings.DEATH] = frame_dead_list

    def update(self, player_x, player_y):
        if not self.stats.alive:
            if self.actual_status != settings.DEATH:
                self.set_status(settings.DEATH)
                self.index_frame = len(self.animation.get(settings.DEATH, [None])) -1
            self.update_animation()
            return
        
        now = pygame.time.get_ticks()
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance = hypot(dx,dy)

        can_attack = distance < settings.ENEMY_ATTACK_RADIUS
        cooldown_ready = (now - self.last_attack_time > self.attack_cooldown)


        if self.actual_status == settings.ATACK:
            self.is_moving = False
        elif can_attack and cooldown_ready:
            self.set_status(settings.ATACK)
            self.last_attack_time = now
            self.is_moving = False

            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False
        else:
            self.set_status(settings.RUN)
            self.is_moving = True

            move_x, move_y = 0, 0
            if distance > 1:
                move_x = (dx/distance) * self.stats.speed
                move_y = (dy/distance) * self.stats.speed

            self.rect.x += move_x
            self.rect.y += move_y

            if move_x > 0:
                self.facing_right = True
            elif move_x < 0:
                self.facing_right = False

        self.update_animation()

    def draw(self, surface, camera_x, camera_y):
        pos_in_screen_x = self.rect.x - camera_x
        pos_in_screen_y = self.rect.y - camera_y

        image_to_draw = self.image
        if not self.facing_right:
            image_to_draw = pygame.transform.flip(self.image, True, False)
        
        surface.blit(image_to_draw, (pos_in_screen_x, pos_in_screen_y))

        debug_color = (0, 255, 0) # Verde por defecto (run/idle)
        if self.actual_status == "atack":
            debug_color = (255, 0, 0) # Rojo si está atacando
        elif self.actual_status == "death":
             debug_color = (100, 100, 100) # Gris si está muerto
        
        debug_circle_pos = (pos_in_screen_x + self.rect.width // 2, pos_in_screen_y - 10)
        
        pygame.draw.circle(surface, debug_color, debug_circle_pos, 5)

    def die(self):
        super().die()

        gem_types = []
        gem_weights = []

        for gem_type, (coords,xp,weight) in settings.GEM_STATS.items():
            if weight > 0:
                gem_types.append(gem_type)
                gem_weights.append(weight)
            
        if not gem_types:
            return None

        gem_type_to_drop = random.choices(gem_types, weights = gem_weights, k=1)[0]

        new_gem = Gem(self.rect.centerx, self.rect.centery, gem_type_to_drop)
        
        return new_gem