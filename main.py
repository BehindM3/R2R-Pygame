import pygame, sys
import random
from pygame.locals import *

pygame.init()
pygame.font.init()

from settings import *
from archer import Archer
from enemy import Enemy
from gem import Gem
from hud import HUD
from map_manager import MapManager
from structure import Structure
from boss_lancer import BossLancer


# RESET GAME
def reset_game():
    character = Archer(colour="black")
    camera_x, camera_y = 0, 0

    map_manager = MapManager()

    structure_list = []
    for struct_type, x, y in map_manager.structure_layout:
        structure_list.append(Structure(x, y, struct_type))

    enemies_list = []
    arrows = []
    gems = []

    return (
        character, enemies_list, arrows, gems,
        camera_x, camera_y, structure_list, map_manager,
        PLAYING
    )



# SETUP
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Road to Revenge")
icon = pygame.image.load(PATH_ICON_GAME)
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

character = Archer(colour="black")
hud = HUD()
map_manager = MapManager()

enemies_list = []
list_of_arrows = []
list_gems = []

structure_list = []
for struct_type, x, y in map_manager.structure_layout:
    structure_list.append(Structure(x, y, struct_type))

camera_x = 0
camera_y = 0

game_state = START_MENU
boss_spawned = False
boss_ref = None
upgrade_options = []

running = True



# START SCREEN
try:
    start_screen_bg = pygame.image.load(PATH_START_SCREEN_BG).convert()
    orig_w, orig_h = start_screen_bg.get_size()
    ratio_s = SCREEN_WIDTH / SCREEN_HEIGHT
    ratio_i = orig_w / orig_h

    if ratio_s > ratio_i:
        new_h = SCREEN_HEIGHT
        new_w = int(orig_w * (new_h / orig_h))
    else:
        new_w = SCREEN_WIDTH
        new_h = int(orig_h * (new_w / orig_w))

    start_screen_bg = pygame.transform.scale(start_screen_bg, (new_w, new_h))
    start_screen_pos = (
        (SCREEN_WIDTH - new_w)//2,
        (SCREEN_HEIGHT - new_h)//2
    )
except:
    start_screen_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    start_screen_bg.fill((20,20,50))



# GAME LOOP
while running:

    # EVENTS
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if game_state == START_MENU:
            if event.type == KEYDOWN and event.key == K_RETURN:
                game_state = PLAYING

        elif game_state == LEVEL_UP:
            if event.type == KEYDOWN:
                if event.key in [K_1, K_2, K_3]:
                    idx = {K_1:0, K_2:1, K_3:2}[event.key]
                    apply_upgrade(character, upgrade_options[idx])
                    character.pending_level_ups -= 1
                    if character.pending_level_ups > 0:
                        all_up = list(UPGRADE_DATA.keys())
                        upgrade_options = random.sample(all_up, k=3)
                    else:
                        game_state = PLAYING

        elif game_state == GAME_OVER:
            if event.type == KEYDOWN and event.key == K_RETURN:
                (
                    character, enemies_list, list_of_arrows, list_gems,
                    camera_x, camera_y, structure_list, map_manager, game_state
                ) = reset_game()
                boss_spawned = False
                boss_ref = None

        elif game_state == WIN:
            if event.type == KEYDOWN and event.key == K_RETURN:
                (
                    character, enemies_list, list_of_arrows, list_gems,
                    camera_x, camera_y, structure_list, map_manager, game_state
                ) = reset_game()
                boss_spawned = False
                boss_ref = None

    # UPDATE
    if game_state == PLAYING:

        keys = pygame.key.get_pressed()
        mov_x, mov_y = character.handle_input(keys)
        camera_x += mov_x
        camera_y += mov_y

        attack_signal = character.update_animation()
        if attack_signal == SHOOT:
            arrow = character.perform_attack_action(camera_x, camera_y)
            if arrow:
                list_of_arrows.append(arrow)

        # Player world pos
        character_world_x = camera_x + SCREEN_WIDTH//2
        character_world_y = camera_y + SCREEN_HEIGHT//2

        hitbox_player = character.rect.copy()
        hitbox_player.center = (character_world_x, character_world_y)

        # STRUCTURES
        for st in structure_list:
            spawn = st.update()
            if st.stats.alive and spawn:
                enemies_list.append(Enemy(st.rect.centerx, st.rect.centery))

        # ENEMIES
        for en in enemies_list:
            en.update(character_world_x, character_world_y)

        # ARROWS
        for ar in list_of_arrows:
            ar.update()

        # GEMS
        for gm in list_gems:
            gm.update(hitbox_player)

        # ARROW COLLISIONS
        for ar in list_of_arrows:
            if not ar.is_active:
                continue

            # Arrow → enemy
            for en in enemies_list:
                if en.stats.alive and ar.rect.colliderect(en.rect):
                    alive = en.stats.alive
                    en.take_damage(character.stats.damage)
                    ar.is_active = False
                    if alive and not en.stats.alive:
                        gem = en.die()
                        if gem:
                            list_gems.append(gem)
                    break

            if not ar.is_active:
                continue

            # Arrow → structure
            for st in structure_list:
                if st.stats.alive and ar.rect.colliderect(st.rect):
                    alive = st.stats.alive
                    st.take_damage(character.stats.damage)
                    ar.is_active = False

                    if alive and not st.stats.alive:
                        final = st.die()
                        for _ in final:
                            enemies_list.append(Enemy(st.rect.centerx, st.rect.centery))

                        # SPAWN BOSS
                        if not boss_spawned:
                            all_dead = all(not s.stats.alive for s in structure_list)
                            if all_dead:
                                boss_ref = BossLancer(st.rect.centerx, st.rect.centery)
                                enemies_list.append(boss_ref)
                                boss_spawned = True
                    break

        # Enemy → player
        if character.stats.alive:
            for en in enemies_list:
                if en.stats.alive and en.rect.colliderect(hitbox_player) and en.actual_status == ATACK:
                    character.take_damage(en.stats.damage)

        # Player → gems
        if character.stats.alive:
            for gm in list_gems:
                if gm.is_active and hitbox_player.colliderect(gm.rect):
                    level = character.add_xp(gm.xp_value)
                    gm.is_active = False
                    if level:
                        game_state = LEVEL_UP
                        all_up = list(UPGRADE_DATA.keys())
                        upgrade_options = random.sample(all_up, 3)

        # Water pit
        if character.stats.alive:
            if map_manager.is_water_pit_at(hitbox_player.centerx, hitbox_player.centery):
                character.take_damage(99999)

    #  STATE SWITCH 
    if not character.stats.alive and character.animation_finished:
        game_state = GAME_OVER

    # DRAW
    SCREEN.fill(BLACK)

    if game_state == START_MENU:
        SCREEN.blit(start_screen_bg, start_screen_pos)

    elif game_state == GAME_OVER:
        t = FONT_TITLE.render("HAS MUERTO", True, RED)
        r = FONT_MENU.render("ENTER para reiniciar", True, WHITE)
        SCREEN.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, SCREEN_HEIGHT//2 - 100))
        SCREEN.blit(r, (SCREEN_WIDTH//2 - r.get_width()//2, SCREEN_HEIGHT//2 + 50))

    elif game_state == WIN:
        SCREEN.fill((0,0,0))
        title = FONT_TITLE.render("VICTORIA", True, (255,215,0))
        msg = FONT_MENU.render("Has derrotado al jefe final", True, WHITE)
        rst = FONT_MENU.render("ENTER para reiniciar", True, WHITE)
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 100))
        SCREEN.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2))
        SCREEN.blit(rst, (SCREEN_WIDTH//2 - rst.get_width()//2, SCREEN_HEIGHT//2 + 100))

    elif game_state in (PLAYING, LEVEL_UP):

        # background
        map_manager.draw_background(SCREEN, camera_x, camera_y)
        map_manager.draw_floor(SCREEN, camera_x, camera_y)

        render = []

        # props
        for d, img, dx, dy in map_manager.get_props_for_render(camera_x, camera_y):
            render.append((d, "prop", (img, dx, dy)))

        # structures
        for st in structure_list:
            d = st.rect.bottom - camera_y
            render.append((d, "structure", st))

        # enemies
        for en in enemies_list:
            d = en.rect.bottom - camera_y
            render.append((d, "enemy", en))

        # gems
        for gm in list_gems:
            d = gm.rect.bottom - camera_y
            render.append((d, "gem", gm))

        # player
        d = character.rect.bottom
        render.append((d, "player", character))

        render.sort(key=lambda x: x[0])

        for d, kind, obj in render:
            if kind == "prop":
                img, dx, dy = obj
                SCREEN.blit(img, (dx, dy))
            elif kind == "structure":
                obj.draw(SCREEN, camera_x, camera_y)
            elif kind == "enemy":
                obj.draw(SCREEN, camera_x, camera_y)
            elif kind == "gem":
                obj.draw(SCREEN, camera_x, camera_y)
            elif kind == "player":
                obj.draw(SCREEN)

        # arrows
        for ar in list_of_arrows:
            ar.draw(SCREEN, camera_x, camera_y)

        # HUD
        hud.draw(SCREEN, character.stats)

        if game_state == LEVEL_UP:
            hud.draw_level_up_menu(SCREEN, upgrade_options)

    # cleanup
    list_of_arrows = [a for a in list_of_arrows if a.is_active]
    list_gems = [g for g in list_gems if g.is_active]

    enemies_list = [
        e for e in enemies_list
        if e.stats.alive or (not e.stats.alive and not e.animation_finished)
    ]

    structure_list = [
        s for s in structure_list
        if s.stats.alive or (not s.stats.alive and not s.animation_finished)
    ]

    pygame.display.flip()
    clock.tick(FPS)
