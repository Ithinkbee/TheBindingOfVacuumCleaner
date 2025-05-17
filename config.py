import pygame

pygame.init()

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

EXPLOSION_DURATION = 2000

#rooms
WIDTH, HEIGHT = 800, 600
DOOR_INSET = 1 
WALL_THICKNESS = 50
DOOR_SIZE = 60

#player stats
PLAYER_HP = 8
PLAYER_SPEED = 1
PLAYER_DMG = 1
PLAYER_SHOOTING_COOLDOWN = 5
PLAYER_SHOOT_DELAY = 90
PLAYER_INVISIBILITY_DURATION = 500
PLAYER_FLASH_INTERVAL = 10

#fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)

#sounds
MUSIC_MENU = "assets/music/menu.mp3"
MUSIC_LEVEL = "assets/music/cellar.mp3"
SOUND_VICTORY = "assets/sounds/win.mp3"
SOUND_FAILURE = "assets/sounds/death.mp3"
SOUND_PLAYER_HURT = "assets/sounds/hurt.mp3"
SOUND_PLAYER_SHOOT = "assets/sounds/piu.mp3"
SOUND_PROJECTILE_HIT = "assets/sounds/water_drop.mp3"
SOUND_DOOR_CLOSE = "assets/sounds/door_close.mp3"
SOUND_DOOR_OPEN = "assets/sounds/door_open.mp3"