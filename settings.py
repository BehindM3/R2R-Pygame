# settings.py
import pygame

#Dimesiones de la pantalla
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

#Variable del bucle infinito
running = True

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
PLAYER_SPEED = 5
ANIMATION_SPEED_RUN = 150
ANIMATION_SPEED_IDLE = 200
ANIMATION_SPEED_SHOOT = 100
ANIMATION_SPEED_DEATH = 150
ANIMATION_SPEED_ATACK = 85
PLAYER_MAGNET_RADIUS = 20

#Ajustes del enemigo
ENEMY_DETECTION_RADIUS = 1500.
ENEMY_ATTACK_RADIUS = 50
ENEMY_SPEED = 3 
ENEMY_SPEED_RUN = 4
ENEMY_SPEED_MIN_MOD = 0.3
ENEMY_SPEED_MAX_MOD = 1.0

#Entidades 
ARROW_SPEED = 10
GEM_PATH_SPRITESHEET = "./assets/gems/gems.png"
GEM_STATS = {
    "silver": ((), 100),
    "gold": ((), 300),
    "diamond": ((), 500),
}


#Rutas de archivos - PATHS
PATH_ICON_GAME = "./assets/Icons/icon_game.png"
PATH_PLAYER = "./assets/units"
PATH_ARROW = "./assets/arrow/arrow.png"

#Colores
ENEMIES_COLOR = "red"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

#Funciones auxiliares
def grayscale(surface):
    px_array = pygame.PixelArray(surface)

    for x in range(px_array.shape[0]):
        for y in range(px_array.shape[1]):
            mapped_int = px_array[x, y]
            r,g,b,a = surface.unmap_rgb(mapped_int)
            if a == 0:
                continue
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            px_array[x,y] = (gray, gray, gray)

    del px_array
    return surface
