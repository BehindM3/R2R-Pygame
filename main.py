import pygame, sys
import random
import math
from pygame.locals import *

# Initializamos Pygame
pygame.init()
pygame.font.init()

from settings import *
from archer import Archer
from enemy import Enemy
from gem import Gem
from hud import HUD
from map_manager import MapManager
from structure import Structure

#Funcion RESET
def reset_game():
    print("¡Reiniciando el juego!")
    new_character = Archer(colour="black")
    new_camera_x,new_camera_y = 0, 0
    new_enemies_list = []
    
    return new_character, new_enemies_list, [], [], new_camera_x, new_camera_y, PLAYING

# Configuramos la pantalla
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Road to revenge")
icon = pygame.image.load("./assets/Icons/icon_game.png")
clock = pygame.time.Clock()


#Declaracion y llamados a funciones
pygame.display.set_icon(icon)
character = Archer(colour="black")
hud = HUD()
map_manager = MapManager()
enemies_list = []
list_of_arrows = []
list_gems = [] 
structure_list = []
upgrade_options = []
camera_x, camera_y = 0, 0
game_state = START_MENU

#Pantalla de inicio
start_screen_bg = None 
start_screen_pos = (0, 0)
try:
    start_screen_bg = pygame.image.load(PATH_START_SCREEN_BG).convert()

    original_width, original_height = start_screen_bg.get_size()

    screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    image_ratio = original_width / original_height

    if screen_ratio > image_ratio:
        new_height = SCREEN_HEIGHT
        new_width = int(original_width * (SCREEN_HEIGHT / original_height))
    else:
        new_width = SCREEN_WIDTH
        new_height = int(original_height * (SCREEN_WIDTH / original_width))

    start_screen_bg = pygame.transform.scale(start_screen_bg, (new_width, new_height))
    
    pos_x = (SCREEN_WIDTH - new_width) // 2
    pos_y = (SCREEN_HEIGHT - new_height) // 2
    start_screen_pos = (pos_x, pos_y)
except Exception as e:
    print(f"Error al cargar la imagen de la pantalla de inicio: {e}")
    start_screen_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    start_screen_bg.fill((20, 20, 50))

#Fondo de juego
try:
    bg_tile_image = pygame.image.load("./assets/ui/background/Tilemap_color1.png").convert()
    TILE_WIDTH, TILE_HEIGHT = bg_tile_image.get_size()
except Exception as e:
    print(f"Error al cargar el tile de fondo: {e}")
    bg_tile_image = None

#Enemigos
for type, x, y in map_manager.structure_layout:
    new_structure = Structure(x, y, type)
    structure_list.append(new_structure)


#Bucle del juego
while running:
    
    # --- 1. MANEJO DE EVENTOS ---
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # --- Eventos del Menú de Inicio ---
        elif game_state == START_MENU:
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    game_state = PLAYING

        # --- Eventos del Menú de Subida de Nivel ---
        elif game_state == LEVEL_UP:
            if event.type == KEYDOWN:
                option_chosen = None
                if event.key == K_1:
                    option_chosen = 0 
                elif event.key == K_2:
                    option_chosen = 1 
                elif event.key == K_3:
                    option_chosen = 2 

                if option_chosen is not None:
                    apply_upgrade(character, upgrade_options[option_chosen])
                    character.pending_level_ups -= 1 

                    if character.pending_level_ups > 0:
                        print(f"Niveles restantes: {character.pending_level_ups}")
                        all_upgrades = list(UPGRADE_DATA.keys())
                        upgrade_options = random.sample(all_upgrades, k=3)
                    else:
                        print("¡Todas las mejoras aplicadas! Reanudando...")
                        game_state = PLAYING

        # --- Eventos de la Pantalla de Muerte ---
        elif game_state == GAME_OVER:
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    (character, enemies_list, list_of_arrows, list_gems, 
                     camera_x, camera_y, game_state) = reset_game()

        # --- Eventos de Debug ---
        elif game_state == PLAYING:
            if event.type == KEYDOWN:
                if event.key == K_t:
                    print("Auch! Recibiendo 15 de daño.")
                    character.take_damage(15)
                    print(f"Vida actual del personaje: {character.stats.health}")

    # --- 2. LÓGICA DE ACTUALIZACIÓN ---
    if game_state == PLAYING:
        # 2a. Input del Jugador
        keys_pressed = pygame.key.get_pressed()
        mov_camera_x, mov_camera_y = character.handle_input(keys_pressed)
        camera_x += mov_camera_x
        camera_y += mov_camera_y

        # 2b. Animación del Jugador y Creación de Proyectiles
        attack_action_signal = character.update_animation()
        if attack_action_signal == SHOOT:
            new_arrow = character.perform_attack_action(camera_x, camera_y)
            if new_arrow:
                list_of_arrows.append(new_arrow)

        # 2c. Posición del Jugador en el Mundo
        character_world_x = camera_x + SCREEN_WIDTH // 2
        character_world_y = camera_y + SCREEN_HEIGHT // 2
        player_world_hitbox = character.rect.copy()
        player_world_hitbox.center = (character_world_x, character_world_y)

        # 2d. Actualizar Entidades (Enemigos, Flechas, Gemas)
        for structure in structure_list:
            if not structure.stats.alive:
                continue
            spawn_signal = structure.update()
            if spawn_signal:
                new_enemy = Enemy(structure.rect.centerx, structure.rect.centery)
                enemies_list.append(new_enemy)
        for enemy in enemies_list:
            enemy.update(character_world_x, character_world_y)
        for arrow in list_of_arrows:
            arrow.update()
        for gem in list_gems: 
            gem.update(player_world_hitbox)

        # 2e. Lógica de Colisiones
        for arrow in list_of_arrows:
            if arrow.is_active:
                for enemy in enemies_list:
                    if enemy.stats.alive and arrow.rect.colliderect(enemy.rect):
                        was_alive = enemy.stats.alive
                        enemy.take_damage(character.stats.damage)
                        arrow.is_active = False
                        if was_alive and not enemy.stats.alive:
                            new_gem = enemy.die()
                            if new_gem:
                                list_gems.append(new_gem)
                                print(f"¡Enemigo muerto! Gema {new_gem.type} generada.")
                        else:
                            print(f"Enemigo dañado, vida restante: {enemy.stats.health}")
                        break
                for structure in structure_list:
                    if structure.stats.alive and arrow.rect.colliderect(structure.rect):
                        was_alive = structure.stats.alive
                        structure.take_damage(character.stats.damage)
                        arrow.is_active = False

                        if was_alive and not structure.stats.alive:
                            final_spawn_list = structure.die()
                            for enemy_type in final_spawn_list:
                                new_enemy = Enemy(structure.rect.centerx, structure.rect.centery)
                                enemies_list.append(new_enemy)
                        else:
                            print(f"Estructura dañada, vida: {structure.stats.health}")
                        break

        if character.stats.alive:
            for enemy in enemies_list:
                if (enemy.stats.alive and 
                    player_world_hitbox.colliderect(enemy.rect) and 
                    enemy.actual_status == ATACK):
                    character.take_damage(enemy.stats.damage)

        # Jugador -> Gemas
        if character.stats.alive:
            for gem in list_gems:
                if gem.is_active and player_world_hitbox.colliderect(gem.rect):
                    did_level_up = character.add_xp(gem.xp_value)
                    print(f"¡Gema {gem.type} recogida! Valor: {gem.xp_value}")
                    gem.is_active = False
                    print(did_level_up)
                    
                    if did_level_up:
                        game_state = LEVEL_UP
                        print("¡Juego pausado para mejora!")
                        all_upgrades = list(UPGRADE_DATA.keys())
                        upgrade_options = random.sample(all_upgrades, k=3)

        if character.stats.alive:
            if map_manager.is_water_pit_at(player_world_hitbox.centerx, player_world_hitbox.centery):
                print("¡SPLASH! El jugador ha caído al agua.")
                character.take_damage(99999)

    # --- 3. CAMBIO DE ESTADO ---
    if not character.stats.alive and character.animation_finished:
        game_state = GAME_OVER # <-- TYPO CORREGIDO ('ame_state' -> 'game_state')

    # --- 4. LÓGICA DE DIBUJADO ---
    # 4a. Dibuja el fondo apropiado
    SCREEN.fill(BLACK)
    if game_state == START_MENU:
        if start_screen_bg:
            SCREEN.blit(start_screen_bg, start_screen_pos)
            
    elif game_state == GAME_OVER:
        title_text = FONT_TITLE.render("HAS MUERTO", True, RED)
        restart_text = FONT_MENU.render("Presiona ENTER para reiniciar", True, WHITE)
        SCREEN.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        SCREEN.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
    elif game_state == PLAYING or game_state == LEVEL_UP:

        map_manager.draw_background(SCREEN, camera_x, camera_y)

        map_manager.draw_floor(SCREEN, camera_x, camera_y)
        map_manager.draw_props(SCREEN, camera_x, camera_y)
        
        for structure in structure_list:
            structure.draw(SCREEN, camera_x, camera_y)

        character.draw(SCREEN)
        for enemy in enemies_list:
            enemy.draw(SCREEN, camera_x, camera_y)
        for arrow in list_of_arrows:
            arrow.draw(SCREEN, camera_x, camera_y)
        for gem in list_gems:
            gem.draw(SCREEN, camera_x, camera_y)
            
        hud.draw(SCREEN, character.stats)

        # 4b. Dibuja el menú de mejoras
        if game_state == LEVEL_UP:
            hud.draw_level_up_menu(SCREEN, upgrade_options)
        
    print(f"{enemies_list}")

    # --- 5. LIMPIEZA DE LISTAS INACTIVAS ---
    list_of_arrows = [arrow for arrow in list_of_arrows if arrow.is_active]
    list_gems = [gem for gem in list_gems if gem.is_active]

    active_en = [en for en in enemies_list if en.stats.alive or (not en.stats.alive and not en.animation_finished)]
    enemies_list = active_en

    active_structures = [s for s in structure_list if s.stats.alive or (not s.stats.alive and not s.animation_finished)]
    structure_list = active_structures

    # 6. DIBUJADO DE LISTAS DE MEJORAS
    if game_state == LEVEL_UP:
        hud.draw_level_up_menu(SCREEN, upgrade_options)


    # --- 7. FIN DEL FOTOGRAMA ---
    clock.tick(FPS)
    pygame.display.flip()
