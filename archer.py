import pygame
import settings
from character import Character
from stats import Stats
from arrow import Arrow
from gem import Gem

class Archer(Character):

    def __init__(self, colour):
        
        player_stats = Stats(
            health=100, 
            damage=20,
            speed=settings.PLAYER_SPEED,
            xp_to_next_level=100
        )
        super().__init__(stats_obj=player_stats)
        self.pending_level_ups = 0

        #Cargar imagenes del arquero
        self.load_sprites(colour)

        #Definimos la imagen y rect inicial
        self.image = self.animation["idle"][0]
        self.rect = self.image.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2))
        

    def load_sprites(self, colour):
        
        CH_CLASS = "Archer"

        base_path = f"{settings.PATH_PLAYER}/{colour}/{CH_CLASS}"
        path_idle = f"{base_path}/Idle.png"
        path_run = f"{base_path}/Run.png"
        path_shoot = f"{base_path}/Shoot.png"
        path_dead = "./assets/particles/multiple/Effect.png"

        # Cargamos las imagenes y manejamos errores
        try:
            spritesheet_idle = pygame.image.load(path_idle).convert_alpha()
            spritesheet_run = pygame.image.load(path_run).convert_alpha()
            spritesheet_shoot = pygame.image.load(path_shoot).convert_alpha()
            spritesheet_dead = pygame.image.load(path_dead).convert_alpha()
        except pygame.error as e:
            print(f"Error al cargar el sprite del {CH_CLASS}: {e}")
            pygame.quit()
            exit()


        # Cargar animacion de idle
        frame_idle_list = []
        coords_idle = [(58,48,70,88),(249,48,71,88),(440,48,72,88),(633,47,71,89),(826,48,70,88),(1018,50,70,86)]

        for coord in coords_idle:
            frame = spritesheet_idle.subsurface(pygame.Rect(coord))
            frame_idle_list.append(pygame.transform.scale(frame, (64, 64)))

        self.animation["idle"] = frame_idle_list

        # Cargar animacion de correr
        frame_run_list = []
        coords_run = [(57,51,70,85),(249,47,73,89),(443,46,71,90),(635,47,69,89)]

        for coord in coords_run:
            frame = spritesheet_run.subsurface(pygame.Rect(coord))
            frame_run_list.append(pygame.transform.scale(frame, (64, 64)))

        self.animation["run"] = frame_run_list
        
        # Cargar animacion de disparo
        frame_shoot_list = []
        coords_shoot = [(56,46,72,90),(245,49,73,87),(438,50,68,86),(630,57,77,79),(821,54,79,82),(1013,52,87,84),(1206,54,78,82),(1399,50,73,86)]

        for coord in coords_shoot:
            frame = spritesheet_shoot.subsurface(pygame.Rect(coord))
            frame_shoot_list.append(pygame.transform.scale(frame, (64, 64)))

        self.animation["shoot"] = frame_shoot_list

        #Cargar animacion de muerte
        frame_dead_list = []
        coords_dead = [(1393,24,97,122),(1585,31,96,114),(1787,29,86,110),(1979,28,85,97),(1959,42,85,97)]

        for coord in coords_dead:
            frame = spritesheet_dead.subsurface(pygame.Rect(coord))
            gray_frame = settings.grayscale(frame)
            frame_dead_list.append(pygame.transform.scale(gray_frame, (64, 64)))

        self.animation[settings.DEATH] = frame_dead_list

    def perform_attack_action(self, camera_x, camera_y):
        player_world_x = camera_x + self.rect.centerx
        player_world_y = camera_y + self.rect.centery

        new_arrow = Arrow(player_world_x, player_world_y, self.facing_direction, self.stats.arrow_speed)
        return new_arrow        

    def add_xp(self, amount):
        levels_gained = self.stats.add_xp(amount)

        if levels_gained > 0:
            self.pending_level_ups += levels_gained
            print(f"Ganados: {levels_gained} niveles, pendientes {self.pending_level_ups}")
            self.stats.heal(20)
        
        return levels_gained

    def draw(self, surface):
        if self.image and self.rect:
            image_to_draw = self.image
            if not self.facing_right:
                image_to_draw = pygame.transform.flip(self.image, True, False)
            surface.blit(image_to_draw, self.rect)