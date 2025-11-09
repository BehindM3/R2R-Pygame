import pygame
import math
import settings

class HUD:
    def __init__(self):
        
        self.loaded_spritesheets_cache = {}
        self.heart_image = None
        self.upgrade_icons = {}
        self.icon_anim_state = {}
        self.MAX_ICON_SIZE = (50,50)

        try: 
            self.font_hud = pygame.font.SysFont("Arial", 24)
            self.font_menu = pygame.font.SysFont('Arial', 30)
        except Exception as e:
            print(f"Error al cargar la fuente del HUD: {e}")
            self.font_hud = pygame.font.SysFont(None, 30)
            self.font_menu = pygame.font.SysFont('Arial', 30)
            
        try:
            heart_spritesheet = pygame.image.load(settings.UI_PATH_SPRITESHEET).convert_alpha()
            HEART_COORDS = (401, 195, 14, 13)
            original_heart_image = heart_spritesheet.subsurface(pygame.Rect(HEART_COORDS))
            self.heart_image = pygame.transform.scale(original_heart_image, (32,32))
        except Exception as e:
            print(f"Error al cargar el sprite de corazon: {e}")
            self.heart_image = pygame.Surface((32,32))
            self.heart_image.fill(settings.RED)

        try:
            for key, data in settings.UPGRADE_DATA.items():
                icon_path = data[2]
                icon_coords_list = data[3]

                if icon_path not in self.loaded_spritesheets_cache:
                    print(f"DEBUG HUD: Cargando nuevo spritesheet para '{key}': {icon_path}")
                    sheet_surface = pygame.image.load(icon_path).convert_alpha()
                    self.loaded_spritesheets_cache[icon_path] = sheet_surface

                spritesheet_surface = self.loaded_spritesheets_cache[icon_path]
                frame_list = []

                for coords in icon_coords_list:
                    icon_image_original = spritesheet_surface.subsurface(pygame.Rect(coords))

                    original_width, original_height = icon_image_original.get_size()

                    scale_factor_w = self.MAX_ICON_SIZE[0] / original_width
                    scale_factor_h = self.MAX_ICON_SIZE[1] / original_height

                    scale_factor = min(scale_factor_w, scale_factor_h)

                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)

                    scaled_image = pygame.transform.scale(icon_image_original, (new_width, new_height))
                    frame_list.append(scaled_image)

                self.upgrade_icons[key] = frame_list
                self.icon_anim_state[key] = {"index": 0, "last_update": pygame.time.get_ticks()}

        except Exception as e:
            print(f"Error al cargar los iconos de mejora para la clave '{key}': {e}")


        self.icon_frame_index = 0
        self.icon_last_update = pygame.time.get_ticks()
        self.heart_value = 10
        self.heart_spacing = 5


    def draw(self, surface, player_stats):
        hearts_to_draw = int(max(0, player_stats.health) / self.heart_value)
        bobbing_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3

        for i in range(hearts_to_draw):
            pos_x = 10 + i * (self.heart_image.get_width() + self.heart_spacing)
            pos_y = 10 + bobbing_offset
            surface.blit(self.heart_image, (pos_x, pos_y))

        xp_text_str = f"XP: {player_stats.xp} / {player_stats.xp_to_next_level}"
        xp_surface = self.font_hud.render(xp_text_str, True, settings.WHITE)
        surface.blit(xp_surface, (10,50))

        level_text_str = f"Nivel: {player_stats.lvl}"
        level_surface = self.font_hud.render(level_text_str, True, settings.WHITE)
        surface.blit(level_surface, (10,75))

    def draw_level_up_menu(self, surface, upgrade_options):
            
            title_text = self.font_menu.render("MENU DE MEJORAS", True, settings.WHITE)
            title_rect = title_text.get_rect()
            
            total_height = title_rect.height + 30
            total_height += len(upgrade_options) * 70 
            
            max_option_text_width = 0
            for i, option_key in enumerate(upgrade_options):
                if option_key in settings.UPGRADE_DATA:
                    title, desc = settings.UPGRADE_DATA[option_key][0], settings.UPGRADE_DATA[option_key][1]
                    option_text_surface = self.font_menu.render(f"{i+1}: {title}", True, settings.WHITE)
                    max_option_text_width = max(max_option_text_width, option_text_surface.get_width())
            
            total_width = 30 + self.MAX_ICON_SIZE[0] + 10 + max_option_text_width + 30 
            
            total_width = max(total_width, 400)
            total_height = max(total_height, 200)
            
            #Dibujamos el fondo dinamico
            s = pygame.Surface((total_width, total_height)) # Usa el tamaño calculado
            s.set_alpha(128) 
            s.fill((50, 50, 50)) 
            
            panel_x = surface.get_width() // 2 - total_width // 2
            panel_y = surface.get_height() // 2 - total_height // 2
            surface.blit(s, (panel_x, panel_y))

            title_rect.center = (panel_x + total_width // 2, panel_y + title_rect.height // 2 + 10)
            surface.blit(title_text, title_rect)

            #Dibujamos las opciones del bucle
            now = pygame.time.get_ticks()
            y_pos = panel_y + title_rect.height + 20

            for i, option_key in enumerate(upgrade_options):
                if option_key not in settings.UPGRADE_DATA or option_key not in self.upgrade_icons:
                    continue
                
                try: 
                    state = self.icon_anim_state[option_key]
                    frames = self.upgrade_icons[option_key]
                    num_frames = len(frames)

                    if now- state["last_update"] > settings.UPGRADE_ICON_ANIM_SPEED:
                        state["index"] = (state["index"] + 1) % num_frames
                        state["last_update"] = now 

                    current_icon_image = frames[state["index"]]

                except (KeyError, IndexError): 
                    current_icon_image = self.upgrade_icons[option_key][0]

                icon_draw_y = y_pos + (70 - current_icon_image.get_height()) // 2
                surface.blit(current_icon_image, (panel_x + 30, icon_draw_y))

                # Dibuja el texto
                title_option, desc = settings.UPGRADE_DATA[option_key][0], settings.UPGRADE_DATA[option_key][1]
                title_text_option = self.font_menu.render(f"{i+1}: {title_option}", True, settings.WHITE)
                
                # Centra el texto verticalmente
                text_draw_y = y_pos + (70 - title_text_option.get_height()) // 2

                surface.blit(title_text_option, (panel_x + 30 + self.MAX_ICON_SIZE[0] + 10, text_draw_y))
                
                y_pos += 70