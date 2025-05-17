import pygame
from menu import main_menu
from config import HEIGHT, WIDTH

def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("The Binding of Vacuum Cleaner: Recleaning")

    try:
        pygame.mixer.music.load("assets/music/menu.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  
    except Exception as e:
        print(f"Could not load menu music: {e}")

    main_menu(screen)

if __name__ == "__main__":
    main()
