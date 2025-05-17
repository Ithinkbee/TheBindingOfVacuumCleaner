import pygame
import sys
import os
import xml.etree.ElementTree as ET
import random
from config import *
from levelgenerator import LevelGenerator
from level import Level
from player import Player
from item import *

def save_score_to_xml(time_seconds):
    filename = "scores.xml"
    
    if not os.path.exists(filename):
        root = ET.Element("scores")
        tree = ET.ElementTree(root)
    else:
        tree = ET.parse(filename)
        root = tree.getroot()
    
    score = ET.SubElement(root, "score")
    score.text = str(time_seconds)
    
    tree.write(filename)

def show_info(screen):
    info_running = True
    clock = pygame.time.Clock()

    while info_running:
        screen.fill(BLACK)

        box_width, box_height = 600, 400
        box_x = (screen.get_width() - box_width) // 2
        box_y = (screen.get_height() - box_height) // 2
        pygame.draw.rect(screen, LIGHT_GRAY, (box_x, box_y, box_width, box_height), border_radius=10)
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 2, border_radius=10)

        title = font_large.render("Info", True, BLACK)
        title_rect = title.get_rect(center=(screen.get_width() // 2, box_y + 40))
        screen.blit(title, title_rect)

        info_text = [
            "Move with WASD keys.",
            "Shoot with arrow keys.",
            "Defeat the boss to win.",
            "Try not to die.",
            "",
            "",
            "Press ESC to close this window."
        ]
        
        for i, line in enumerate(info_text):
            text_surf = font_medium.render(line, True, BLACK)
            text_rect = text_surf.get_rect(center=(screen.get_width() // 2, box_y + 100 + i * 40))
            screen.blit(text_surf, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                info_running = False 

        pygame.display.flip()
        clock.tick(60)

def show_records(screen):
    try:
        tree = ET.parse("scores.xml")
        root = tree.getroot()
        scores = [int(score.text) for score in root.findall("score")]
        scores.sort() 
        scores = scores[:5]  
    except:
        scores = []

    record_running = True
    clock = pygame.time.Clock()

    while record_running:
        screen.fill(BLACK)

        box_width, box_height = 600, 400
        box_x = (screen.get_width() - box_width) // 2
        box_y = (screen.get_height() - box_height) // 2
        pygame.draw.rect(screen, LIGHT_GRAY, (box_x, box_y, box_width, box_height), border_radius=10)
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 2, border_radius=10)

        title = font_large.render("Best Runs", True, BLACK)
        title_rect = title.get_rect(center=(screen.get_width() // 2, box_y + 40))
        screen.blit(title, title_rect)

        if not scores:
            no_records = font_medium.render("No records yet!", True, BLACK)
            no_rect = no_records.get_rect(center=(screen.get_width() // 2, box_y + box_height // 2))
            screen.blit(no_records, no_rect)
        else:
            for i, score in enumerate(scores):
                minutes = score // 60
                seconds = score % 60
                time_text = f"{i+1}. {minutes:02d}:{seconds:02d}"
                text_surf = font_medium.render(time_text, True, BLACK)
                text_rect = text_surf.get_rect(center=(screen.get_width() // 2, box_y + 100 + i * 50))
                screen.blit(text_surf, text_rect)

        close_text = font_medium.render("Press ESC to close", True, BLACK)
        close_rect = close_text.get_rect(center=(screen.get_width() // 2, box_y + box_height - 50))
        screen.blit(close_text, close_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                record_running = False

        pygame.display.flip()
        clock.tick(60)

def draw_level(screen, level):
    current_room_pos = (level.width // 2, level.height // 2) 
    current_room = level.grid[current_room_pos[1]][current_room_pos[0]]
    
    room = current_room.physical_room
    
    pygame.draw.rect(screen, (50, 50, 50), room.floor)
    
    for wall in room.walls:
        pygame.draw.rect(screen, (100, 100, 100), wall)
    
    for direction, door in room.doors:
        pygame.draw.rect(screen, (139, 69, 19), door) 
    
    font = pygame.font.Font(None, 24)
    room_type_text = font.render(f"Room: {current_room.type}", True, (255, 255, 255))
    screen.blit(room_type_text, (20, 20))

def start_game(screen):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    try:
        pygame.mixer.music.load(MUSIC_LEVEL)
        pygame.mixer.music.set_volume(0.3) 
    except Exception as e:
        print(f"Can't load music': {e}")

    generator = LevelGenerator()
    level_grid = generator.generate()
    
    print("\n==== Map ====")
    for y in range(len(level_grid)):
        row = []
        for x in range(len(level_grid[0])):
            if level_grid[y][x]:
                if level_grid[y][x].type == "start":
                    row.append("S")
                elif level_grid[y][x].type == "boss":
                    row.append("B")
                elif level_grid[y][x].type == "treasure":
                    row.append("T")
                else:
                    row.append(".")
            else:
                row.append(".")
        print(" ".join(row))
    print("=============\n")

    level = Level(generator)
    player = Player(WIDTH//2, HEIGHT//2)
    level.player = player

    pygame.mixer.music.play(-1)

    start_time = pygame.time.get_ticks()
    paused_time = 0
    elapsed_time = 0
    running = True
    game_active = True
    player_won = False

    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        dt = current_time - last_time 
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  
                if not game_active and event.key == pygame.K_SPACE:
                    pygame.mixer.music.stop() 
                    return True 

        if game_active:
            elapsed_time = (current_time - start_time - paused_time) // 1000
    
            keys = pygame.key.get_pressed()
            player.handle_movement(keys, level)

            door_direction = level.check_door_collision(player.rect)
            if door_direction:
                level.change_room(door_direction, player)
                player.last_update = pygame.time.get_ticks()  
    
            player.handle_shooting(keys)
            player.update_projectiles(level)
            level.check_projectile_collisions(player.projectiles, player)
            item_effect = level.check_item_collisions(player)

            if item_effect and "win_game" in item_effect:
                game_active = False
                player_won = True  
                pygame.mixer.music.stop()
                try:
                    win_sound = pygame.mixer.Sound(SOUND_VICTORY)
                    win_sound.play()
                except:
                    print("Could not play win sound")
                save_score_to_xml(elapsed_time)

            player.unlock_movement()  
            player.update_invincibility()

            if player.dead:
                game_active = False
                player_won = False 
                pygame.mixer.music.stop()
                try:
                    death_sound = pygame.mixer.Sound(SOUND_FAILURE)
                    death_sound.play()
                except:
                    print("Could not play death sound")

            screen.fill((0, 0, 0))
            level.draw(screen, elapsed_time)
            player.draw(screen)
            player.draw_projectiles(screen)

            for enemy in level.current_room.physical_room.enemies:
                enemy.update(player.rect.center, level, dt)

            player.check_projectile_hits(level.current_room.physical_room.enemies)
            player.check_enemy_collisions(level.current_room.physical_room.enemies)
        else:
            screen.fill((0, 0, 0))
            level.draw(screen)
            player.draw(screen)
    
            if hasattr(player, 'dead') and player.dead:
                draw_death_screen(screen, player)
            elif player_won: 
                draw_win_screen(screen, elapsed_time)

        pygame.display.flip()
        clock.tick(240) 
    
    return False  

def draw_death_screen(screen, player):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    wasted_font = pygame.font.Font(None, 120)
    wasted_text = wasted_font.render("WASTED", True, RED)
    wasted_rect = wasted_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    shake_offset = random.randint(-5, 5)
    wasted_rect.x += shake_offset
    
    screen.blit(wasted_text, wasted_rect)
    
    continue_font = pygame.font.Font(None, 36)
    continue_text = continue_font.render("Press SPACE to restart", True, WHITE)
    continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
    screen.blit(continue_text, continue_rect)

def draw_win_screen(screen, time_seconds):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    win_font = pygame.font.Font(None, 120)
    win_text = win_font.render("VICTORY!", True, (0, 255, 0))
    win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    screen.blit(win_text, win_rect)
    
    time_font = pygame.font.Font(None, 48)
    minutes = time_seconds // 60
    seconds = time_seconds % 60
    time_text = time_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
    time_rect = time_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(time_text, time_rect)
    
    continue_font = pygame.font.Font(None, 36)
    continue_text = continue_font.render("Press SPACE to exit", True, WHITE)
    continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))
    screen.blit(continue_text, continue_rect)