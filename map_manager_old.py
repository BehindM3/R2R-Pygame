import pygame 
import settings
import random

class MapManager:

    def __init__(self):
        try:
            self.tiles_spritesheet = pygame.image.load(f"{settings.UI_PATH_BACKGROUND}terrains/Tilemap_color1.png").convert_alpha()
            self.tiles_spritesheet_water = pygame.image.load(f"{settings.UI_PATH_BACKGROUND}terrains/Water_background.png").convert_alpha()
            self.tiles_spritesheet_water_detail = pygame.image.load(f"{settings.UI_PATH_BACKGROUND}terrains/Water_Foam.png").convert_alpha()
    
            self.prop_images = {
                "tree1" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree1.png"),
                "tree2" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree2.png"),
                "tree3" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree3.png"),
                "tree4" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree4.png"),
                "rock1" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}rocks/Rock1.png"),
                "rock2" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}rocks/Rock2.png"),
                "rock3" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}rocks/Rock3.png"),
                "rock3" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}rocks/Rock4.png"),
                "castle" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}buildings/Castle.png"),
                "monastery" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}buildings/Monastery.png"),
                "Tower" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}buildings/Tower.png")
            }
        except Exception as e:
            print(f"Error al cargar assets del mapa: {e}")
            self.prop_images = {}
            return

        self.tile_size = 32
        self.tiles = {
            0 : self._get_tile(18,18,32,32),#Panle medio
            1 : self._get_tile(0,0,32,32),#Esquina S/I
            2 : self._get_tile(32,0,32,32), #Lateral S
            3 : self._get_tile(157,0,32,32), #Esquina S/D
            4 : self._get_tile(159,50,32,32), #Lateral D
            5 : self._get_tile(159,158,32,32), #Esquina I/D
            6 : self._get_tile(41,160,32,32), #Lateral Inf
            7 : self._get_tile(0,161,32,32), #Esquina I/I
            8 : self._get_tile(0,53,32,32), #Esquina I/I
            9 : self.tiles_spritesheet_water.subsurface(pygame.Rect(0, 0, 32, 32)), #Variedad agua
            10 : self.tiles_spritesheet_water_detail.subsurface(pygame.Rect(0, 0, 32, 32)) #Variedad agua
            
        }

        MAP_WIDTH_TILES = 100  # Ancho del mapa
        MAP_HEIGHT_TILES = 100 # Alto del mapa 
        self.floor_layout = self.generate_map_layout(MAP_WIDTH_TILES, MAP_HEIGHT_TILES)
        
        # Guardamos los límites del mapa en píxeles
        self.map_width_pixels = MAP_WIDTH_TILES * self.tile_size
        self.map_height_pixels = MAP_HEIGHT_TILES * self.tile_size

        self.prop_layout = [
            ("tree1", 200, 150),
            ("rock1", 500, 450),
            ("castle", 800, 500),
        ]

    def _get_tile(self, x,y,w,h):
        return self.tiles_spritesheet.subsurface(pygame.Rect(x, y, w, h))
    
    def draw_floor(self, surface, camera_x, camera_y):
        
        start_col = int(camera_x // self.tile_size - 1)
        end_col = int((camera_x + settings.SCREEN_WIDTH) // self.tile_size + 1)

        start_row = int(camera_y // self.tile_size - 1)
        end_row = int((camera_y + settings.SCREEN_HEIGHT) // self.tile_size + 1) 

        start_row = max(0, start_row)
        end_row = min(len(self.floor_layout), end_row)
        
        start_col = max(0, start_col)
        end_col = min(len(self.floor_layout[0]), end_col)


        # Itera sobre el plano - floor_layout
        for y in range(start_row, end_row):
            row = self.floor_layout[y]
            for x in range(start_col, end_col):
                
                tile_id = row[x]
                if tile_id in self.tiles:
                    tile_image = self.tiles[tile_id]
                    
                    world_x = x * self.tile_size
                    world_y = y * self.tile_size
                    
                    draw_x = world_x - camera_x
                    draw_y = world_y - camera_y
                    
                    surface.blit(tile_image, (draw_x, draw_y))

    def draw_props(self, surface, camera_x, camera_y):
        for key, world_x, world_y in self.prop_layout:
            if key in self.prop_images:
                img = self.prop_images[key]
                draw_x = world_x - camera_x
                draw_y = world_y - camera_y
                surface.blit(img, (draw_x, draw_y))

    def draw_background(self, surface, camera_x, camera_y):
        try:
            water_tile_image = self.tiles[9]
            water_detail_image = self.tiles[10]
        except KeyError:
            surface.fill(settings.WATER_COLOR) # Fallback a un color si no se cargó
            return
    
        tile_width, tile_height = water_tile_image.get_size()

        # Calcula el desfase (offset) para el scrolling
        offset_x = camera_x % tile_width
        offset_y = camera_y % tile_height

        num_tiles_x = settings.SCREEN_WIDTH // tile_width + 2
        num_tiles_y = settings.SCREEN_HEIGHT // tile_height + 2

        for y in range(num_tiles_y):
            for x in range(num_tiles_x):
                draw_x = (x * tile_width) - offset_x
                draw_y = (y * tile_height) - offset_y

                surface.blit(water_tile_image, (draw_x, draw_y))

                world_x = (x * tile_width) - offset_x + camera_x
                world_y = (y * tile_height) - offset_y + camera_y

                if hash(f"{world_x},{world_y}") % 10 == 0:
                    surface.blit(water_detail_image, (draw_x, draw_y))

    def generate_map_layout(self, width, height):
        layout = []
        for y in range(height):
            row = []
            for x in range(width):
                # Coloca las esquinas
                if x == 0 and y == 0:
                    row.append(1)
                elif x == width - 1 and y == 0:
                    row.append(3)
                elif x == 0 and y == height - 1:
                    row.append(7)
                elif x == width - 1 and y == height - 1:
                    row.append(5)
                # Coloca los bordes
                elif y == 0:
                    row.append(2) # Lateral Superior
                elif y == height - 1:
                    row.append(6) # Lateral Inferior
                elif x == 0:
                    row.append(8) # Lateral Izquierdo
                elif x == width - 1:
                    row.append(4) # Lateral Derecho
                # Rellena el centro
                else:
                    rand_num = random.random()
                    
                    if rand_num < 0.03:
                         row.append(99)
                    else:
                         row.append(0)
            layout.append(row)
        return layout
    
    def is_water_pit_at(self, world_x, world_y):
        grid_x = world_x // self.tile_size
        grid_y = world_y // self.tile_size
        
        if (grid_y < 0 or grid_y >= len(self.floor_layout) or 
            grid_x < 0 or grid_x >= len(self.floor_layout[0])):
            return True 
            
        tile_id = self.floor_layout[grid_y][grid_x]
        
        return tile_id == 99