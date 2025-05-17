import pygame
import sys
from button import Button
from realisation import show_info, show_records, start_game
from config import *

def main_menu(screen):
    clock = pygame.time.Clock()
    
    buttons = [
        Button("New Game"),
        Button("Run Records"),
        Button("Info"),
        Button("Exit", RED, (255, 150, 150))
    ]

    def update_buttons():
        screen_width, screen_height = screen.get_size()
        start_y = screen_height // 2 - (len(buttons) * 70) // 2  

        for i, button in enumerate(buttons):
            x = screen_width // 2 - button.width // 2
            y = start_y + i * 80  
            button.update_position(x, y)

    update_buttons()

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                update_buttons()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, button in enumerate(buttons):
                        if button.is_hovered:
                            if i == 0:
                                if start_game(screen):
                                    try:
                                        pygame.mixer.music.load(MUSIC_MENU)
                                        pygame.mixer.music.play(-1)
                                    except:
                                        print("Could not load menu music")
                            elif i == 1:
                                show_records(screen)
                            elif i == 2:
                                show_info(screen)
                            elif i == 3:
                                pygame.quit()
                                sys.exit()
        
        screen.fill(BLACK)
        
        title = font_medium.render("The Binding of Vacuum Cleaner: Recleaning", True, RED)
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)
        
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

