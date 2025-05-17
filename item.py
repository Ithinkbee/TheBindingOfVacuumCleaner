import pygame
from config import *

class Item:
    def __init__(self, x, y, item_type, texture_path=None):
        self.type = item_type
        self.rect = pygame.Rect(x, y, 50, 50)
        self.collected = False

        try:
            self.image = pygame.image.load(texture_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except:
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 255, 0), (15, 15), 15)

    def update(self, player_rect):
        if not self.collected and self.rect.colliderect(player_rect):
            self.collected = True
            return self.apply_effect()
        return None
    
    def apply_effect(self):
        return {}
    
    def draw(self, screen):
        if not self.collected:
            screen.blit(self.image, self.rect)

class HealthUpItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y, "health_up", "assets/items/hp_up.png")
    
    def apply_effect(self):
        return {"hp_change": 3}  

class SpeedUpItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y, "speed_up", "assets/items/speed_up.png")
    
    def apply_effect(self):
        return {"speed_change": 1}  

class DamageUpItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y, "damage_up", "assets/items/dmg_up.png")
    
    def apply_effect(self):
        return {"damage_change": 1}  
        
class Upgrade(Item):
    def __init__(self, x, y):
        super().__init__(x, y, "upgrade", "assets/items/upgrade.png")

    def apply_effect(self):
        return {
            "hp_change": 3, 
            "speed_change": 1, 
            "damage_change": 1,
            "upgrade": True 
        }

class TrophyItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y, "trophy", "assets/items/trophy.png")
    
    def apply_effect(self):
        return {"win_game": True}
