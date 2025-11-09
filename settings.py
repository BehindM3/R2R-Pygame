# settings.py
import pygame
import random

#Dimesiones de la pantalla
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

#Estados del juego
running = True
PLAYING = "playing"
LEVEL_UP = "level_up"
START_MENU = "start_menu"
GAME_OVER = "game_over"

#FONTS
FONT_TITLE = pygame.font.SysFont("Arial", 60)
FONT_MENU = pygame.font.SysFont("Arial", 30)


#Ajustes de FPS
FPS = 60

#Ajustes del jugador
DEATH = "death"
SHOOT = "shoot"
ATACK = "atack"
RUN = "run"
RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"
IDLE = "idle"
PLAYER_SPEED = 5
ANIMATION_SPEED_RUN = 150
ANIMATION_SPEED_IDLE = 200
ANIMATION_SPEED_SHOOT = 100
ANIMATION_SPEED_DEATH = 150
ANIMATION_SPEED_ATACK = 85
PLAYER_MAGNET_RADIUS = 150
UPGRADE_ICON_ANIM_SPEED = 200

#Ajustes del enemigo
NUM_ENEMIES = 10
ENEMY_DETECTION_RADIUS = 1500.
ENEMY_ATTACK_RADIUS = 50
ENEMY_SPEED = 3 
ENEMY_SPEED_RUN = 4
ENEMY_SPEED_MIN_MOD = 0.3
ENEMY_SPEED_MAX_MOD = 1.0

#Entidades 
ARROW_SPEED = 10
CASTLE = "Castle"
TOWER = "Tower"
HOUSE = "House1"
BARRACKS = "Barracks"
GEM_ANIMATION_SPEED = 150
GEM_STATS = {
    "gold": ([
            (177,18,14,14),
            (193,18,14,14),
            (209,18,14,14),
            (255,18,14,14),
            (241,18,14,14),
            (257,18,14,14),
            (273,18,14,14)
            ], 
            700, 
            5
        ),
    "silver": ([
            (177,34,14,14),
            (193,34,14,14),
            (209,34,14,14),
            (255,34,14,14),
            (241,34,14,14),
            (257,34,14,14),
            (273,34,14,14)
            ], 
            300, 
            25
        ),
    "bronze": ([
            (177,66,14,14),
            (193,66,14,14),
            (209,66,14,14),
            (255,66,14,14),
            (241,66,14,14),
            (257,66,14,14),
            (273,66,14,14)
            ], 
            100,
            70
        ),
}


#Rutas de archivos - PATHS
PATH_START_SCREEN_BG = "./assets/ui/start_screen_background.jpg"
PATH_ICON_GAME = "./assets/Icons/icon_game.png"
PATH_PLAYER = "./assets/units"
PATH_ARROW = "./assets/arrow/arrow.png"
UI_PATH_SPRITESHEET = "./assets/ui/ui_spritesheet.png"
UI_PATH_BACKGROUND = "./assets/ui/background/"
BUILDINGS_PATH = UI_PATH_BACKGROUND + "buildings/"

#ICONOS DE MEJORAS
UPGRADE_DATA = {
    "health_up": ("Vida maxima +", "20 Vida maxima", UI_PATH_SPRITESHEET, [(401,195,14,13),(417,195,14,13),(435,195,10,13),(454,195,5,13),(481,195,14,13)]),
    "damage_up": ("Daño de Flecha +", "+5 Daño", UI_PATH_SPRITESHEET, [(756,592,7,16), (773, 593,5,13)]),
    "speed_up": ("Velocidad +", "+10% Velocidad de Movimiento", f"{PATH_PLAYER}/black/Archer/Run.png", [(57,51,70,85),(249,47,73,89),(443,46,71,90),(635,47,69,89)]),
    "arrow_speed_up": ("Velocidad de Flecha +", "+10% Velocidad de Flecha", PATH_ARROW, [(10,26,43,12)] )
}

#Colores
ENEMIES_COLOR = "red"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

#Funciones auxiliares
def grayscale(surface):
    temp_surface = surface.copy().convert_alpha()
    px_array = pygame.PixelArray(temp_surface)

    for x in range(px_array.shape[0]):
        for y in range(px_array.shape[1]):
            mapped_int = px_array[x, y]

            try:
                 r, g, b, a = temp_surface.unmap_rgb(mapped_int)
            except ValueError:
                 r, g, b = temp_surface.unmap_rgb(mapped_int)
                 a = 255

            if a == 0:
                px_array[x, y] = (0, 0, 0, 0)
                continue

            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            px_array[x,y] = (gray, gray, gray, a)

    new_surface = px_array.make_surface()
    del px_array
    return new_surface

def apply_upgrade(player, upgrade_key):
    print(f"¡Mejora aplicada: {upgrade_key}!")
    
    if upgrade_key == "health_up":
        player.stats.max_health += 20
        player.stats.heal(20)
    
    elif upgrade_key == "damage_up":
        player.stats.damage += 5
        
    elif upgrade_key == "speed_up":
        player.stats.speed *= 1.10
        
    elif upgrade_key == "arrow_speed_up":
        player.stats.arrow_speed *= 1.10
