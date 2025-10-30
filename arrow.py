import pygame
import settings

class Arrow:
    def __init__(self, x, y, direction):

        try:    
            original_image = pygame.image.load(settings.PATH_ARROW).convert_alpha()
            original_image = pygame.transform.scale(original_image, (44, 16))
        except Exception as e:
            print(f"Error al cargar la imagen de la flecha: {e}")
            original_image = pygame.Surface((32, 10))
            original_image.fill((255, 0, 0))

        self.speed = settings.ARROW_SPEED
        self.direction = direction

        if self.direction == settings.RIGHT:
            self.speed_x = self.speed
            self.speed_y = 0
            self.image = original_image
        elif self.direction == settings.LEFT:
            self.speed_x = -self.speed
            self.speed_y = 0
            self.image = pygame.transform.flip(original_image, True, False)
        elif self.direction == settings.UP:
            self.speed_x = 0
            self.speed_y = -self.speed
            self.image = pygame.transform.rotate(original_image, -90)
        elif self.direction == settings.DOWN:
            self.speed_x = 0
            self.speed_y = self.speed
            self.image = pygame.transform.rotate(original_image, 90)

        self.rect = self.image.get_rect(center=(x, y))
        self.is_active = True
        
         
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.x > 5000 or self.rect.x < -2000 or self.rect.y > 5000 or self.rect.y < -2000:
            self.is_active = False
    
    def draw(self, surface, camera_x, camera_y):
        pos_x = self.rect.x - camera_x
        pos_y = self.rect.y - camera_y
        surface.blit(self.image, (pos_x, pos_y))