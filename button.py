import pygame
from config import *

class Button:
    def __init__(self, text, color=GRAY, hover_color=LIGHT_GRAY):
        self.width, self.height = 300, 60
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.rect = pygame.Rect(0, 0, self.width, self.height)

    def update_position(self, x, y):
        self.rect.topleft = (x, y)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = font_medium.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

