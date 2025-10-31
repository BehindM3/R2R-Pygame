import pygame, sys
import random
from pygame.locals import *
from settings import *
from archer import Archer
from enemy import Enemy
from gem import Gem

# Initializamos Pygame
pygame.init()

# Configuramos la pantalla
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Road to revenge")
icon = pygame.image.load("./assets/Icons/icon_game.png")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 30)

#Declaracion y llamados a funciones
pygame.display.set_icon(icon)
character = Archer(colour="black")
list_of_arrows = []
list_gems = [] 
camera_x, camera_y = 0, 0
game_state = PLAYING
upgrade_options = []

#Enemigo de prueba
enemies_list = []
NUM_ENEMIES = 5

for _ in range(NUM_ENEMIES):
    x_start = random.randint(-SCREEN_WIDTH // 2, SCREEN_WIDTH + SCREEN_WIDTH // 2)
    y_start = random.randint(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT + SCREEN_HEIGHT // 2)
    if abs(x_start - (SCREEN_WIDTH // 2)) < 100 and abs(y_start - (SCREEN_HEIGHT // 2)) < 100:
        x_start += random.choice([-200, 200])
    new_enemy = Enemy(x_start, y_start)
    enemies_list.append(new_enemy)

#Bucle del juego
while running:
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if game_state == LEVEL_UP:
            if event.type == KEYDOWN:
                if event.key == K_1: 
                    apply_upgrade(character, upgrade_options[0])
                    game_state = "playing" 
                elif event.key == K_2: 
                    apply_upgrade(character, upgrade_options[1])
                    game_state = "playing"
                elif event.key == K_3: 
                    apply_upgrade(character, upgrade_options[2])
                    game_state = "playing"

        if event.type == KEYDOWN:
            if event.key == K_t:
                print("Auch! Recibiendo 15 de daño.")
                character.take_damage(15)
                print(f"Vida actual del personaje: {character.stats.health}")

    # Capturamos las teclas presionadas
    if game_state == PLAYING:
        keys_pressed = pygame.key.get_pressed()

        mov_camera_x, mov_camera_y = character.handle_input(keys_pressed)
        camera_x += mov_camera_x
        camera_y += mov_camera_y

        attack_action_signal = character.update_animation()
        if attack_action_signal == SHOOT:
            new_arrow = character.perform_attack_action(camera_x, camera_y)

            if new_arrow:
                list_of_arrows.append(new_arrow)


        character_world_x = camera_x + SCREEN_WIDTH // 2
        character_world_y = camera_y + SCREEN_HEIGHT // 2

        player_world_hitbox = character.rect.copy()
        player_world_hitbox.center = (character_world_x, character_world_y)

        for enemy in enemies_list:
            enemy.update(character_world_x, character_world_y)

        for arrow in list_of_arrows:
            arrow.update()

        for gem in list_gems: 
            gem.update(player_world_hitbox)



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
        
        if character.stats.alive:
            for enemy in enemies_list:
                if enemy.stats.alive and player_world_hitbox.colliderect(enemy.rect) and enemy.actual_status == ATACK:
                    character.take_damage(enemy.stats.damage)
                    print(f"Vida actual del personaje: {character.stats.health}")

        if character.stats.alive:
            for gem in list_gems:
                if gem.is_active and player_world_hitbox.colliderect(gem.rect):
                    did_level_up = character.add_xp(gem.xp_value)
                    print(f"¡Gema {gem.type} recogida! Valor: {gem.xp_value}")
                    gem.is_active = False

                    if did_level_up:
                        game_state = LEVEL_UP
                        print("Juego pausado para mejoras!")
                        all_upgrades = list(UPGRADE_DATA.keys())
                        upgrade_options = random.sample(all_upgrades, k=3)

    SCREEN.fill(GREEN)

    character.draw(SCREEN)
    pygame.draw.rect(SCREEN, RED, character.rect, 2)

    for enemy in enemies_list:
        enemy.draw(SCREEN, camera_x, camera_y)
        
    for arrow in list_of_arrows:
        arrow.draw(SCREEN, camera_x, camera_y)

    for gem in list_gems:
        gem.draw(SCREEN, camera_x, camera_y)

    list_of_arrows = [arrow for arrow in list_of_arrows if arrow.is_active]
    list_gems = [gem for gem in list_gems if gem.is_active]

    active_enemies = []
    for en in enemies_list:
        if en.stats.alive or (not en.stats.alive and not en.animation_finished):
            active_enemies.append(en)
        else:
            print(f"DEBUG: Eliminando enemigo {enemy.rect.topleft} (Muerto y animación terminada)")
        enemies_list = active_enemies

    if game_state == "level_up":
        text1 = FONT.render(f"1: {UPGRADE_DATA[upgrade_options[0]][0]}", True, WHITE)
        text2 = FONT.render(f"2: {UPGRADE_DATA[upgrade_options[1]][0]}", True, WHITE)
        text3 = FONT.render(f"3: {UPGRADE_DATA[upgrade_options[2]][0]}", True, WHITE)
        SCREEN.blit(text1, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        SCREEN.blit(text2, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        SCREEN.blit(text3, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
        pass

    clock.tick(FPS)
    pygame.display.flip()

    

    




