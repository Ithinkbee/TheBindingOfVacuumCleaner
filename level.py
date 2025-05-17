import pygame
from config import *
from enemy import *
from item import *

class Level:
    def __init__(self, generator):
        self.rooms = generator.grid
        self.current_room_pos = generator.start_pos
        
        self.load_textures()
        self.load_sounds()
    
        print(f"Trying to access room at: {self.current_room_pos}")
        print(f"Grid size: {len(generator.grid[0])}x{len(generator.grid)}")
    
        self.current_room = self.rooms[self.current_room_pos[1]][self.current_room_pos[0]]
    
        if self.current_room is None:
            for y in range(len(self.rooms)):
                for x in range(len(self.rooms[0])):
                    print(f"({x},{y}): {'Room' if self.rooms[y][x] else 'None'}")
            raise ValueError("Start room not found!")
    
        self.offset_x = 0
        self.offset_y = 0
        self.calculate_offsets()
    
    def load_textures(self, tile_size=128):
        try:
            original_floor = pygame.image.load('assets/floor.jpg').convert()
            self.floor_texture = pygame.transform.smoothscale(original_floor, (tile_size, tile_size))
            
            original_wall = pygame.image.load('assets/wall.png').convert()
            self.wall_texture = pygame.transform.smoothscale(original_wall, (tile_size, tile_size))
            
            original_door = pygame.image.load('assets/door_open.jpg').convert()
            self.door_texture = pygame.transform.smoothscale(original_door, (tile_size, tile_size))

            original_door_closed = pygame.image.load('assets/door_closed.jpg').convert()
            self.door_closed_texture = pygame.transform.smoothscale(original_door_closed, (tile_size, tile_size))

            self.heart_icon = pygame.image.load('assets/heart_icon.png').convert_alpha()
            self.sword_icon = pygame.image.load('assets/sword_icon.png').convert_alpha()
            self.boot_icon = pygame.image.load('assets/boot_icon.png').convert_alpha()
         
            self.heart_icon = pygame.transform.scale(self.heart_icon, (30, 30))
            self.sword_icon = pygame.transform.scale(self.sword_icon, (30, 30))
            self.boot_icon = pygame.transform.scale(self.boot_icon, (20, 20))
            
        except Exception as e:
            print(f"Failed to load textures: {e}")
            self.floor_texture = None
            self.wall_texture = None
            self.door_texture = None
            self.door_closed_texture = None
            self.heart_icon = None
            self.sword_icon = None
            self.boot_icon = None
    
    def load_sounds(self):
        try:
            self.door_close_sound = pygame.mixer.Sound(SOUND_DOOR_CLOSE)
            self.door_open_sound = pygame.mixer.Sound(SOUND_DOOR_OPEN)
            self.door_close_sound.set_volume(0.5)
            self.door_open_sound.set_volume(0.5)
        except Exception as e:
            print(f"Could not load door sounds: {e}")
            self.door_close_sound = None
            self.door_open_sound = None

    def calculate_offsets(self):
        if self.current_room is None:
            print("Error: current_room equals None!")
            return
    
        if not hasattr(self.current_room, 'physical_room'):
            print("Error: current_room have no physical_room attribute!")
            return
    
        self.offset_x = (WIDTH - self.current_room.physical_room.width) // 2
        self.offset_y = (HEIGHT - self.current_room.physical_room.height) // 2
    
    def check_collision(self, rect: pygame.Rect) -> bool:
        return self.current_room.physical_room.check_collision(rect)
    
    def change_room(self, direction: str, player):
        if any(enemy.alive for enemy in self.current_room.physical_room.enemies):
            return False

        if self.current_room.connections[direction]:
            new_room = self.current_room.connections[direction]
            self.current_room = new_room
            self.current_room_pos = new_room.position
            self.calculate_offsets()

            if any(enemy.alive for enemy in self.current_room.physical_room.enemies):
                if self.door_close_sound:
                    self.door_close_sound.play()

            room = self.current_room.physical_room
            wall_thickness = room.wall_thickness 
            if direction == "up":
                player.rect.bottom = room.rect.bottom - wall_thickness - 2*DOOR_INSET
                player.rect.centerx = room.rect.centerx
            elif direction == "down":
                player.rect.top = room.rect.top + wall_thickness + 2*DOOR_INSET
                player.rect.centerx = room.rect.centerx
            elif direction == "left":
                player.rect.right = room.rect.right - wall_thickness - 2*DOOR_INSET
                player.rect.centery = room.rect.centery
            elif direction == "right":
                player.rect.left = room.rect.left + wall_thickness + 2*DOOR_INSET
                player.rect.centery = room.rect.centery

            player.float_x = player.rect.centerx
            player.float_y = player.rect.centery

            player.can_move = False
            return True
        return False
    
    def draw(self, screen, elapsed_time=None):
        room = self.current_room.physical_room

        has_living_enemies = any(enemy.alive for enemy in room.enemies)

        previous_enemies_state = hasattr(self, '_previous_enemies_alive') and self._previous_enemies_alive
        current_enemies_state = any(enemy.alive for enemy in room.enemies)

        if previous_enemies_state and not current_enemies_state and hasattr(self, 'door_open_sound'):
            self.door_open_sound.play()

        self._previous_enemies_alive = current_enemies_state

        if room.type == "boss" and not any(enemy.alive for enemy in room.enemies):
            if not any(isinstance(item, TrophyItem) for item in room.items):
                room.items.append(TrophyItem(room.width//2, room.height//2))

        if self.floor_texture:
            floor_surface = pygame.Surface((room.width, room.height))
            tw, th = self.floor_texture.get_size()
        
            for x in range(0, room.width, tw):
                for y in range(0, room.height, th):
                    floor_surface.blit(self.floor_texture, (x, y))
        
            screen.blit(floor_surface, (self.offset_x, self.offset_y))
        else:
            pygame.draw.rect(screen, (50, 50, 50), 
                           (self.offset_x, self.offset_y, room.width, room.height))

        for wall in room.walls:
            if self.wall_texture:
                wall_surface = pygame.Surface((wall.width, wall.height))
                tw, th = self.wall_texture.get_size()
            
                for x in range(0, wall.width, tw):
                    for y in range(0, wall.height, th):
                        wall_surface.blit(self.wall_texture, (x, y))
            
                screen.blit(wall_surface, (wall.x + self.offset_x, wall.y + self.offset_y))
            else:
                pygame.draw.rect(screen, (100, 100, 100), 
                               (wall.x + self.offset_x, wall.y + self.offset_y, 
                                wall.width, wall.height))

        for direction, door in room.doors:
            if has_living_enemies and self.door_closed_texture:
                door_texture = self.door_closed_texture
            else:
                door_texture = self.door_texture

            if door_texture: 
                rotated = door_texture  

                if direction == "down":
                    rotated = pygame.transform.rotate(rotated, 180)
                elif direction == "right":
                    rotated = pygame.transform.rotate(rotated, -90)
                elif direction == "left":
                    rotated = pygame.transform.rotate(rotated, 90)

                scaled_door = pygame.transform.scale(rotated, (door.width, door.height))
                screen.blit(scaled_door, (door.x + self.offset_x, door.y + self.offset_y))
            else:
                pygame.draw.rect(screen, (139, 69, 19), 
                               (door.x + self.offset_x, door.y + self.offset_y,
                                door.width, door.height))
    
        font = pygame.font.Font(None, 24)
        room_info = font.render(f"Room: {self.current_room.type}", True, (255, 255, 255))
        screen.blit(room_info, (20, 20))

        self.draw_timer(screen, elapsed_time)
        self.draw_player_stats(screen)

        room.enemies = [e for e in room.enemies if e.alive]
        for enemy in room.enemies:
            enemy.draw(screen)
        for item in self.current_room.physical_room.items:
            item.draw(screen)

    def draw_timer(self, screen, elapsed_time):
        if elapsed_time is None:
            return
    
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
    
        timer_font = pygame.font.Font(None, 36)
    
        timer_surface = timer_font.render(time_text, True, (255, 255, 255))
    
        timer_bg = pygame.Surface((100, 40), pygame.SRCALPHA)
        timer_bg.fill((0, 0, 0, 0)) 
    
        bg_rect = timer_bg.get_rect(top=10, centerx=WIDTH//1.5)
        text_rect = timer_surface.get_rect(center=bg_rect.center)
    
        screen.blit(timer_bg, bg_rect)
        screen.blit(timer_surface, text_rect)

    def draw_player_stats(self, screen):
        stats_font = pygame.font.Font(None, 28)
        stats_bg = pygame.Surface((80, 100), pygame.SRCALPHA)
        stats_bg.fill((0, 0, 0, 128))
    
        bg_rect = stats_bg.get_rect(top=10, right=WIDTH - 10)
        screen.blit(stats_bg, bg_rect)
    
        icon_x = bg_rect.left + 10
        text_x = icon_x + 30
        y_offset = 10
    
        if hasattr(self, 'heart_icon') and self.heart_icon:
            screen.blit(self.heart_icon, (icon_x, bg_rect.top + y_offset))
        hp_text = stats_font.render(f"{self.player.hp}", True, (255, 255, 255))
        screen.blit(hp_text, (text_x, bg_rect.top + y_offset))
    
        if hasattr(self, 'sword_icon') and self.sword_icon:
            screen.blit(self.sword_icon, (icon_x, bg_rect.top + y_offset + 30))
        damage_text = stats_font.render(f"{self.player.damage}", True, (255, 255, 255))
        screen.blit(damage_text, (text_x, bg_rect.top + y_offset + 30))
    
        if hasattr(self, 'boot_icon') and self.boot_icon:
            screen.blit(self.boot_icon, (icon_x, bg_rect.top + y_offset + 60))
        speed_text = stats_font.render(f"{self.player.speed:.1f}", True, (255, 255, 255))
        screen.blit(speed_text, (text_x, bg_rect.top + y_offset + 60))

    def check_door_collision(self, player_rect):
        room = self.current_room.physical_room
        if any(enemy.alive for enemy in room.enemies):
            return None  
    
        check_rect = player_rect.inflate(2, 2) 
    
        for direction, door in room.doors:
            if check_rect.colliderect(door):
                return direction
        return None

    def check_projectile_collisions(self, projectiles, player):
        for projectile in projectiles[:]: 
            for enemy in self.current_room.physical_room.enemies[:]:
                if enemy.alive and projectile.rect.colliderect(enemy.rect):
                    new_enemies = enemy.take_damage(player.damage) 
                    if new_enemies:  
                        self.current_room.physical_room.enemies.extend(new_enemies)
                    projectiles.remove(projectile)
                    break

    def check_item_collisions(self, player):
        if not hasattr(self.current_room.physical_room, 'items'):
            return
            
        for item in self.current_room.physical_room.items[:]:
            effect = item.update(player.rect)
            if effect:
                if "win_game" in effect:
                    return effect 
                player.apply_item_effect(effect)
                self.current_room.physical_room.items.remove(item)
        return None