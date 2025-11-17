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
                "tree1" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree1.png").convert_alpha(),
                "tree2" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree2.png").convert_alpha(),
                "tree3" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree3.png").convert_alpha(),
                "tree4" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}trees/Tree4.png").convert_alpha(),
                "rock1" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}rocks/Rock1.png").convert_alpha(),
                "rock2" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}rocks/Rock2.png").convert_alpha(),
                "rock3" : pygame.image.load(f"{settings.UI_PATH_BACKGROUND}rocks/Rock4.png").convert_alpha(),
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
            10 : self.tiles_spritesheet_water_detail.subsurface(pygame.Rect(0, 0, 32, 32)), #Variedad agua
            99: None
        }

        self.holes_template = [
            [0, 6, 6,0],
            [4,99,99,8],
            [4,99,99,8],
            [0, 2, 2,0]
        ]

        MAP_WIDTH_TILES = 150  
        MAP_HEIGHT_TILES = 150  

        # Guardamos los límites del mapa en píxeles
        self.map_width_pixels = MAP_WIDTH_TILES * self.tile_size
        self.map_height_pixels = MAP_HEIGHT_TILES * self.tile_size
        
        self.floor_layout = self.generate_map_layout(MAP_WIDTH_TILES, MAP_HEIGHT_TILES)

        # Ciudades generadas proceduralmente
        self.structure_layout = self.generate_structure_layout(num_cities = 1)
        
        # Props (árboles/rocas) generados proceduralmente
        self.prop_layout = self.generate_prop_layout(num_props=120)


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
                tile_image = self.tiles.get(tile_id)
                if tile_image:
                    tile_image = self.tiles[tile_id]
                    
                    world_x = x * self.tile_size
                    world_y = y * self.tile_size
                    
                    draw_x = world_x - camera_x
                    draw_y = world_y - camera_y
                    
                    surface.blit(tile_image, (draw_x, draw_y))

    def draw_background(self, surface, camera_x, camera_y):
        try:
            water_tile_image = self.tiles[9]
            water_detail_image = self.tiles[10]
        except KeyError:
            surface.fill(settings.WATER_COLOR)
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
                    row.append(0)
            layout.append(row)

        num_holes = 10

        for _ in range(num_holes):
            hole_w = len(self.holes_template[0])
            hole_h = len(self.holes_template)

            rand_x = random.randint(1, width - hole_w -1)
            rand_y = random.randint(1, height - hole_h -1)

            self._stamp_template(layout, self.holes_template, rand_x, rand_y)

        return layout
    
    def is_water_pit_at(self, world_x, world_y):
        grid_x = world_x // self.tile_size
        grid_y = world_y // self.tile_size
        
        if (grid_y < 0 or grid_y >= len(self.floor_layout) or 
            grid_x < 0 or grid_x >= len(self.floor_layout[0])):
            return True 
            
        tile_id = self.floor_layout[grid_y][grid_x]
        
        return tile_id == 99
    
    def is_near_water(self, world_x, world_y):

        offsets = [-self.tile_size, 0, self.tile_size]
        for ox in offsets:
            for oy in offsets:
                if self.is_water_pit_at(world_x + ox, world_y + oy):
                    return True
        return False

    def _stamp_template(self, main_layout, template, x_offset, y_offset):
        template_height = len(template)
        template_width = len(template[0])

        for x in range(template_width):
            for y in range(template_height):
                map_x = x_offset + x
                map_y = y_offset + y

                tile_id = template[y][x]

                main_layout[map_y][map_x] = tile_id

    def generate_structure_layout(self, num_cities=3):
        layout = []
        city_centers = []
        attempts = 0
        max_attempts = num_cities * 50
        margin = 300  

        # Elegimos centros de ciudad separados y fuera del agua
        while len(city_centers) < num_cities and attempts < max_attempts:
            attempts += 1
            center_x = random.randint(margin, self.map_width_pixels - margin)
            center_y = random.randint(margin, self.map_height_pixels - margin)

            # Usamos el helper "cerca de agua" para que no queden al lado de pozos
            if self.is_near_water(center_x, center_y):
                continue

            too_close = False
            for cx, cy in city_centers:
                dx = center_x - cx
                dy = center_y - cy
                if dx * dx + dy * dy < (600 * 600):
                    too_close = True
                    break
            if too_close:
                continue

            city_centers.append((center_x, center_y))

        # Para cada ciudad, ponemos los edificios alrededor del centro
        for center_x, center_y in city_centers:
            candidate_structure = [
                (settings.CASTLE,   center_x - 220, center_y +  40),
                (settings.HOUSE,    center_x +  40, center_y -  20),
                (settings.BARRACKS, center_x +  40, center_y + 120),
                (settings.TOWER,    center_x - 220, center_y - 120),
            ]

            for struct_type, wx, wy in candidate_structure:
                foot_x = wx + 64
                foot_y = wy + 128

                # No cerca de agua / pozo
                if self.is_near_water(foot_x, foot_y):
                    continue

                layout.append((struct_type, wx, wy))

        return layout
    
    def generate_prop_layout(self, num_props=120):
        layout = []
        attempts = 0
        max_attempts = num_props * 5

        structure_positions = [(x, y) for (_, x, y) in self.structure_layout]
        prop_keys = list(self.prop_images.keys())

        if not prop_keys:
            return []

        # margen en píxeles desde el borde del mapa
        margin = self.tile_size * 2  # 2 tiles hacia adentro

        while len(layout) < num_props and attempts < max_attempts:
            attempts += 1

            # Elegimos primero el tipo de prop para saber su tamaño
            prop_type = random.choice(prop_keys)
            img = self.prop_images[prop_type]

            max_x = max(margin, self.map_width_pixels - margin - img.get_width())
            max_y = max(margin, self.map_height_pixels - margin - img.get_height())

            world_x = random.randint(margin, max_x)
            world_y = random.randint(margin, max_y)

            # Pie del árbol/roca
            foot_x = world_x + img.get_width() // 2
            foot_y = world_y + img.get_height() - 10

            # No en pozos ni fuera del mapa
            if self.is_water_pit_at(foot_x, foot_y):
                continue

            # No demasiado cerca de estructuras
            too_close = False
            for sx, sy in structure_positions:
                dx = foot_x - sx
                dy = foot_y - sy
                if dx * dx + dy * dy < (200 * 200):
                    too_close = True
                    break
            if too_close:
                continue

            layout.append((prop_type, world_x, world_y))

        return layout

    def get_props_for_render(self, camera_x, camera_y):
        items = []
        screen_w, screen_h = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT

        # Ordenamos por world_y para tener profundidad lógica entre props
        sorted_props = sorted(self.prop_layout, key=lambda item: item[2])

        for key, world_x, world_y in sorted_props:
            img = self.prop_images.get(key)
            if not img:
                continue

            draw_x = world_x - camera_x
            draw_y = world_y - camera_y

            # Culling básico
            if draw_x + img.get_width() < 0 or draw_x > screen_w:
                continue
            if draw_y + img.get_height() < 0 or draw_y > screen_h:
                continue

            depth = draw_y + img.get_height()  # “pie” del sprite
            items.append((depth, img, draw_x, draw_y))

        return items

    def draw(self, surface, camera_x, camera_y, structures):
        self.draw_background(surface, camera_x, camera_y)
        self.draw_floor(surface, camera_x, camera_y)

        # Props ordenados
        for depth, img, dx, dy in self.get_props_for_render(camera_x, camera_y):
            surface.blit(img, (dx, dy))

        # Estructuras
        for struct in structures:
            struct.draw(surface, camera_x, camera_y)
