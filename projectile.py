import pygame
from config import *

class Projectile:
    _texture = None
    _hit_sound = None

    @classmethod
    def load_texture(cls, path="assets/projectile.png", width=20, height=20):
        if cls._texture is None:
            try:
                image = pygame.image.load(path).convert_alpha()
                cls._texture = pygame.transform.scale(image, (width, height))
            except:
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 255, 0), (width//2, height//2), width//2)
                cls._texture = surf
        return cls._texture

    @classmethod
    def load_sounds(cls):
        if cls._hit_sound is None:
            try:
                cls._hit_sound = pygame.mixer.Sound(SOUND_PROJECTILE_HIT)
                cls._hit_sound.set_volume(0.3)
            except:
                print("Could not load projectile hit sound")
                cls._hit_sound = None

    def __init__(self, x, y, direction):
        self.image = Projectile.load_texture()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.direction = direction
        self.lifetime = 200
        self.load_sounds()
        
        if direction in ["left", "right"]:
            self.image = pygame.transform.rotate(self.image, 90)
        if direction == "up":
            self.image = pygame.transform.rotate(self.image, 180)

    def update(self, level=None):
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
        
        if level and level.check_collision(self.rect):
            if Projectile._hit_sound:
                Projectile._hit_sound.play()
            self.lifetime = 0 
        
        self.lifetime -= 1
        return self.lifetime <= 0 

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class HomingProjectile(Projectile):
    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(x, y, "right")  
        self.dir_x = dir_x
        self.dir_y = dir_y
        angle = -pygame.math.Vector2(dir_x, dir_y).angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, level=None):
        self.rect.x += self.dir_x * self.speed
        self.rect.y += self.dir_y * self.speed
        
        if level and level.check_collision(self.rect):
            if Projectile._hit_sound:
                Projectile._hit_sound.play()
            self.lifetime = 0 
        
        self.lifetime -= 1
        return self.lifetime <= 0
