import pygame
import settings
from stats import Stats

class Character:
    def __init__(self, stats_obj):
        #Propiedades genericas a heredar
        self.image = None
        self.rect = None
        self.animation = {}
        self.actual_status = "idle"
        self.index_frame = 0
        self.attack_spawn_frame = 3
        self.last_update = pygame.time.get_ticks()
        self.is_moving = False
        self.facing_right = True
        self.facing_direction = "right"
        self.stats = stats_obj
        self.last_hit_time = 0
        self.invincibility_cooldown = 1000
        self.animation_finished = False

    def set_status(self, new_status):

        if self.actual_status == settings.DEATH:
            return

        if new_status not in self.animation:
            print(f"El estado{new_status} no es valido para este personaje.")
            return

        if new_status != self.actual_status:
            self.actual_status = new_status
            self.index_frame = 0

    def update_animation(self):
        try:
            current_animation = self.animation[self.actual_status]
        except KeyError:
            print(f"Error: Estado '{self.actual_status}' no encontrado en las animaciones del personaje.")
            return

        speed = settings.ANIMATION_SPEED_RUN if self.actual_status == "run" else settings.ANIMATION_SPEED_IDLE        
        action_signal = None

        if self.actual_status == settings.RUN:
            speed = settings.ANIMATION_SPEED_RUN
        
        elif self.actual_status == settings.SHOOT:
            speed = settings.ANIMATION_SPEED_SHOOT
        
        elif self.actual_status == settings.ATACK:
            speed = settings.ANIMATION_SPEED_ATACK

        elif self.actual_status == settings.DEATH:
            speed = settings.ANIMATION_SPEED_DEATH

        self.animation_finished = False

        now = pygame.time.get_ticks()
        if now - self.last_update > speed:
                self.last_update = now
                self.index_frame += 1
                                                
                if self.index_frame >= len(current_animation):
                    if self.actual_status in [settings.SHOOT, settings.ATACK]:
                        self.index_frame = 0
                        self.set_status(settings.IDLE)
                        self.animation_finished = True
                    elif self.actual_status == settings.DEATH:
                        self.index_frame = len(current_animation) - 1
                        self.animation_finished = True
                        print(f"DEBUG: ¡Animación de muerte TERMINADA para {self.rect.topleft if self.rect else 'Personaje'}!")
                    else:
                        self.index_frame = 0

                if self.actual_status == settings.SHOOT and self.index_frame == self.attack_spawn_frame:
                    action_signal = settings.SHOOT

                if self.index_frame < len(current_animation):
                    self.image = current_animation[self.index_frame]
                
        return action_signal

    def draw(self, surface):
            if self.image and self.rect:
                image_to_draw = self.image
                if not self.facing_right:
                    image_to_draw = pygame.transform.flip(self.image, True, False)
                surface.blit(image_to_draw, self.rect)

    def handle_input(self, keys_pressed):
        
        if not self.stats.alive:
            self.set_status(settings.DEATH)
            return 0, 0
        
        if self.actual_status == settings.SHOOT:
            return 0, 0
        
        if keys_pressed[pygame.K_a]:
            self.set_status(settings.SHOOT)
            return 0, 0
        
        dx, dy = 0, 0
        self.is_moving = False

        if keys_pressed[pygame.K_LEFT]:
            dx -= self.stats.speed
            self.is_moving = True
            self.facing_right = False
            self.facing_direction = "left"
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.stats.speed
            self.is_moving = True
            self.facing_right = True
            self.facing_direction = "right"
        if keys_pressed[pygame.K_UP]:
            dy -= self.stats.speed
            self.is_moving = True
            self.facing_direction = "up"
        if keys_pressed[pygame.K_DOWN]:
            dy += self.stats.speed
            self.is_moving = True
            self.facing_direction = "down"

        # Actualizamos el estado del personaje segun su movimiento
        if self.is_moving:
            self.set_status("run")
        else:
            self.set_status("idle")

        return dx, dy
    
    def take_damage(self, amount):
        now = pygame.time.get_ticks()

        if now - self.last_hit_time < self.invincibility_cooldown:
            return False
        
        self.last_hit_time = now
        just_died = self.stats.take_damage(amount)
        
        if just_died:
            self.die()

        return just_died

    def heal(self, amount):
        return self.stats.heal(amount)
    
    def die(self):
        self.set_status(settings.DEATH)

    def perform_attack_action(self, camera_x, camera_y):
        return None
    