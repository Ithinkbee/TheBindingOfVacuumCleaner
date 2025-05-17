import pygame
import random
import math
from projectile import *

class Enemy:
    def __init__(self, x, y, image_paths=None, hp=3, speed=1.2):
        if image_paths and isinstance(image_paths, list):
            self.animation_frames = self.load_animation_frames(image_paths)
            self.current_frame = 0
            self.animation_speed = 0.1 
            self.animation_timer = 0
            self.image = self.animation_frames[0]
        else:
            self.image = self.load_texture(image_paths if image_paths else "assets/enemy.gif")
        
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = hp
        self.speed = speed
        self.alive = True

    def load_animation_frames(self, paths):
        frames = []
        for path in paths:
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (50, 50))
                frames.append(image)
            except:
                print(f"Failed to load frame: {path}")
                surf = pygame.Surface((50, 50), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 0, 0), (25, 25), 25)
                frames.append(surf)
        return frames

    def load_texture(self, path):
        try:
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, (50, 50))
        except:
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 0, 0), (25, 25), 25)
            return surf

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def update_animation(self, dt):
        if not hasattr(self, 'animation_frames') or len(self.animation_frames) <= 1:
            return
            
        self.animation_timer += dt  
        frame_duration = 1000 / self.animation_speed 
        
        while self.animation_timer >= frame_duration:
            self.animation_timer -= frame_duration
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]

    def update(self, player_pos, level=None, dt=16):
        if not self.alive:
            return

        if hasattr(self, 'animation_frames'):
            self.update_animation(dt)

        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        
        move_x = self.speed * dx / dist * (dt / 16)  
        move_y = self.speed * dy / dist * (dt / 16)
        
        if not hasattr(self, '_remainder_x'):
            self._remainder_x = 0.0
            self._remainder_y = 0.0
            
        move_x += self._remainder_x
        move_y += self._remainder_y
        
        self.rect.x += int(move_x)
        self.rect.y += int(move_y)
        
        self._remainder_x = move_x - int(move_x)
        self._remainder_y = move_y - int(move_y)

    def check_hit_player(self, player_rect):
        return self.alive and self.rect.colliderect(player_rect)

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)


class WalkingEnemy(Enemy):
    def __init__(self, x, y, hp=6, speed=1.1):
        image_paths = [f"assets/frames/enemy_{i}.png" for i in range(12)]
        
        super().__init__(x, y, image_paths, hp, speed)
        self.animation_speed = 10  


class ShooterEnemy(Enemy):
    def __init__(self, x, y, shoot_interval=1200):
        image_paths = [
            "assets/frames/enemy_shooter_0.png",
            "assets/frames/enemy_shooter_1.png",
            "assets/frames/enemy_shooter_2.png",
            "assets/frames/enemy_shooter_3.png"
        ]
        super().__init__(x, y, image_paths, hp=4, speed=0)
        self.shoot_interval = shoot_interval
        self.last_shot = pygame.time.get_ticks()
        self.projectiles = []
        self.target_pos = (x, y)
        self.charging = False
        self.animation_speed = 8 
        self.shoot_sound = None
        self.load_sounds()

    def load_sounds(self):
        try:
            self.shoot_sound = pygame.mixer.Sound(SOUND_PLAYER_SHOOT)
            self.shoot_sound.set_volume(0.4) 
        except Exception as e:
            print(f"Could not load shooter enemy sound: {e}")
            self.shoot_sound = None

    def update(self, player_pos, level=None, dt=16):
        if not self.alive:
            return

        super().update(player_pos, level, dt)

        self.target_pos = player_pos

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_interval:
            self.last_shot = now
            self.shoot_at_target()

        self.projectiles = [p for p in self.projectiles if not p.update(level)]

    def shoot_at_target(self):
        player_pos = self.target_pos
        player_rect = pygame.Rect(player_pos[0] - 15, player_pos[1] - 15, 30, 30)
    
        if hasattr(self, 'player_speed_x') and hasattr(self, 'player_speed_y'):
            predict_x = player_pos[0] + self.player_speed_x * 10 
            predict_y = player_pos[1] + self.player_speed_y * 10
            player_pos = (predict_x, predict_y)
    
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
    
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        direction_x = dx / dist
        direction_y = dy / dist
    
        projectile = HomingProjectile(
            self.rect.centerx, 
            self.rect.centery,
            direction_x,
            direction_y
        )
        self.projectiles.append(projectile)
        if self.shoot_sound:
            self.shoot_sound.play()

    def check_hit_player(self, player_rect):
        for p in self.projectiles:
            if player_rect.colliderect(p.rect):
                self.projectiles.remove(p)
                return True
        return False

    def draw(self, screen):
        super().draw(screen)
        for p in self.projectiles:
            p.draw(screen)

class Dupok(Enemy):
    def __init__(self, x, y, size=3):
        self.size = size
        self.scale_factor = 1.0 + size * 0.5  
        
        base_size = 150 
        
        if size == 3:
            image_path = "assets/frames/boss_large.png"
            self.max_hp = 20 
            hp = self.max_hp
            speed = 2.5
            self.damage = 2
            current_size = base_size
            self.split_thresholds = [0.5, 0.25]  
        elif size == 2:
            image_path = "assets/frames/boss_medium.png"
            self.max_hp = 10
            hp = self.max_hp
            speed = 3.5
            self.damage = 1
            current_size = int(base_size * 0.75)
            self.split_thresholds = [0.5] 
        else:
            image_path = "assets/frames/boss_small.png"
            self.max_hp = 5
            hp = self.max_hp
            speed = 4.5
            self.damage = 1
            current_size = int(base_size * 0.5)
            self.split_thresholds = []  
            
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (current_size, current_size))
        except:
            self.original_image = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 0, 0), (current_size//2, current_size//2), current_size//2)
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = hp
        self.speed = speed
        self.alive = True
        self.has_split = []  
        
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.bounce_cooldown = 0
        self.bounce_force = 1.2
        self.rotation = 0
        self.rotation_speed = random.uniform(0.5, 2) * random.choice([-1, 1])
        self.velocity = [0, 0]
        self.acceleration = 0.1
        
        self.hitbox_rect = pygame.Rect(0, 0, current_size*0.8, current_size*0.8)
        self.hitbox_rect.center = self.rect.center
        
    def update(self, player_pos, level=None, dt=16):
        if not self.alive:
            return
            
        self.rotation += self.rotation_speed
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        self.velocity[0] += self.direction[0] * self.acceleration
        self.velocity[1] += self.direction[1] * self.acceleration
        
        max_speed = self.speed * (dt / 16)
        speed = (self.velocity[0]**2 + self.velocity[1]**2)**0.5
        if speed > max_speed:
            self.velocity[0] = self.velocity[0] / speed * max_speed
            self.velocity[1] = self.velocity[1] / speed * max_speed
            
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.hitbox_rect.center = self.rect.center
        
        if level and level.check_collision(self.hitbox_rect):
            if self.bounce_cooldown <= 0:
                self._handle_wall_collision(level)
                self.bounce_cooldown = 10
            else:
                self.bounce_cooldown -= 1
                
        self._keep_in_bounds(level)
        
    def _handle_wall_collision(self, level):
        test_rect = self.rect.copy()
        
        test_rect.x += self.direction[0] * 5
        if level.check_collision(test_rect):
            self.direction[0] *= -1
            self.velocity[0] *= -self.bounce_force
            
        test_rect = self.rect.copy()
        test_rect.y += self.direction[1] * 5
        if level.check_collision(test_rect):
            self.direction[1] *= -1
            self.velocity[1] *= -self.bounce_force
            
        if random.random() < 0.3:
            self.direction[0] += random.uniform(-0.5, 0.5)
            self.direction[1] += random.uniform(-0.5, 0.5)
            
        length = (self.direction[0]**2 + self.direction[1]**2)**0.5
        if length > 0:
            self.direction[0] /= length
            self.direction[1] /= length
            
    def _keep_in_bounds(self, level):
        if not level:
            return
            
        room = level.current_room.physical_room
        margin = 20 
        
        if self.rect.left < room.rect.left + margin:
            self.rect.left = room.rect.left + margin
            self.direction[0] = abs(self.direction[0])
            self.velocity[0] = abs(self.velocity[0])
            
        if self.rect.right > room.rect.right - margin:
            self.rect.right = room.rect.right - margin
            self.direction[0] = -abs(self.direction[0])
            self.velocity[0] = -abs(self.velocity[0])
            
        if self.rect.top < room.rect.top + margin:
            self.rect.top = room.rect.top + margin
            self.direction[1] = abs(self.direction[1])
            self.velocity[1] = abs(self.velocity[1])
            
        if self.rect.bottom > room.rect.bottom - margin:
            self.rect.bottom = room.rect.bottom - margin
            self.direction[1] = -abs(self.direction[1])
            self.velocity[1] = -abs(self.velocity[1])
    
    def check_hit_player(self, player_rect):
        if not self.alive:
            return False
            
        return self.hitbox_rect.colliderect(player_rect)
    
    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)
            
            if self.size == 3:
                s = pygame.Surface((self.rect.width+40, self.rect.height+40), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 0, 0, 50), 
                                 (self.rect.width//2+20, self.rect.height//2+20), 
                                 self.rect.width//2)
                screen.blit(s, (self.rect.x-20, self.rect.y-20))

    def take_damage(self, amount):
        old_hp_percent = self.hp / self.max_hp
        self.hp -= amount
        
        new_hp_percent = self.hp / self.max_hp
        children = []
        
        for threshold in self.split_thresholds:
            if old_hp_percent > threshold >= new_hp_percent and threshold not in self.has_split:
                children.extend(self._perform_split())
                self.has_split.append(threshold)
        
        if self.hp <= 0 and self.alive:
            self.alive = False
            if not self.split_thresholds:  
                return []
            return self._perform_final_split()
        
        return children
        
    def _perform_split(self):
        children = []
        count = 2 if self.size == 3 else 3
        
        for _ in range(count):
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            child = Dupok(
                self.rect.centerx + offset_x,
                self.rect.centery + offset_y,
                self.size - 1 
            )
            
            angle = random.uniform(0, 2 * math.pi)
            child.direction = [math.cos(angle), math.sin(angle)]
            child.velocity = [child.direction[0] * child.speed, 
                             child.direction[1] * child.speed]
            
            children.append(child)
        
        return children
    
    def _perform_final_split(self):
        if self.size > 1:
            children = []
            count = 2 if self.size == 3 else 3
            
            for _ in range(count):
                child = Dupok(
                    self.rect.centerx,
                    self.rect.centery,
                    self.size - 1 
                )
                
                angle = random.uniform(0, 2 * math.pi)
                child.direction = [math.cos(angle), math.sin(angle)]
                child.velocity = [child.direction[0] * child.speed,
                                 child.direction[1] * child.speed]
                
                children.append(child)
            
            return children
        return []
