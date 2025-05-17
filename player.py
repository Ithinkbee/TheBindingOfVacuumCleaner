import pygame
from projectile import Projectile
from config import *
from enemy import *
from item import *

class Player:
    def __init__(self, x, y):
        self.original_image = self._load_sprite("assets/vacuum.png")
        self.upgraded_image = self._load_sprite("assets/black_vacuum.png")
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        
        self.upgraded = False

        self.hp = PLAYER_HP
        self.speed = PLAYER_SPEED
        self.damage = PLAYER_DMG

        self.float_x = x
        self.float_y = y

        self.next_rect = self.rect.copy()
        
        self.projectiles = []
        self.shoot_cooldown = PLAYER_SHOOTING_COOLDOWN
        self.shoot_delay = PLAYER_SHOOT_DELAY
        
        self.last_update = pygame.time.get_ticks()

        self.can_move = True
        self.facing_direction = "up"  
        self.shooting_direction = None  

        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = PLAYER_INVISIBILITY_DURATION
        self.flash_timer = 0
        self.flash_interval = PLAYER_FLASH_INTERVAL

        self.dead = False
        self.death_time = 0
        self.death_image = self._load_death_image()

        self.shoot_sound = None
        self.hurt_sound = None
        self.load_sounds()
        
    def load_sounds(self):
        try:
            self.shoot_sound = pygame.mixer.Sound(SOUND_PLAYER_SHOOT)
            self.hurt_sound = pygame.mixer.Sound(SOUND_PLAYER_HURT)
            self.shoot_sound.set_volume(0.3)
            self.hurt_sound.set_volume(0.5)
        except Exception as e:
            print(f"Could not load player sounds: {e}")
            self.shoot_sound = None
            self.hurt_sound = None

    def _load_sprite(self, path):
        try:
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, (50, 50))  
        except:
            print(f"Error loading sprite: {path}")
            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 255, 0), (0, 0, 40, 40))
            return surf
    
    def _load_death_image(self):
        try:
            image = pygame.image.load("assets/explosion.png").convert_alpha()
            return pygame.transform.scale(image, (80, 80))
        except:
            print("Error loading death image, using fallback")
            surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 100, 0), (40, 40), 40)
            return surf

    def rotate_to_direction(self):
        if not self.shooting_direction:
            return
    
        angle = 0
        if self.shooting_direction == "up":
            angle = 0
        elif self.shooting_direction == "down":
            angle = 180
        elif self.shooting_direction == "left":
            angle = 90
        elif self.shooting_direction == "right":
            angle = -90
    
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def update_sprite(self):
        if self.shooting_direction:
            self.rotate_to_direction()
        else:
            self.image = self.original_image.copy()
            if self.facing_direction == "down":
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(center=self.rect.center)
    
    def handle_movement(self, keys, level):
        if not self.can_move:
            return  

        direction_changed = False
        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= self.speed
            direction_changed = True
        if keys[pygame.K_s]:
            dy += self.speed
            direction_changed = True
        if keys[pygame.K_a]:
            dx -= self.speed
            direction_changed = True
            self.facing_direction = "left"
        if keys[pygame.K_d]:
            dx += self.speed
            direction_changed = True
            self.facing_direction = "right"

        if direction_changed:
            self.update_sprite()

        if dx != 0:
            next_float_x = self.float_x + dx
            next_rect = self.rect.copy()
            next_rect.centerx = int(next_float_x)
    
            if not level.check_collision(next_rect):
                self.float_x = next_float_x
                self.rect.centerx = int(self.float_x)
            else:
                walls = [wall for wall in level.current_room.physical_room.walls 
                        if (dx > 0 and wall.left > self.rect.right) or 
                           (dx < 0 and wall.right < self.rect.left)]
            
                if walls: 
                    if dx > 0: 
                        self.rect.right = min(wall.left for wall in walls)
                    else:  
                        self.rect.left = max(wall.right for wall in walls)
                self.float_x = self.rect.centerx

        if dy != 0:
            next_float_y = self.float_y + dy
            next_rect = self.rect.copy()
            next_rect.centery = int(next_float_y)
    
            if not level.check_collision(next_rect):
                self.float_y = next_float_y
                self.rect.centery = int(self.float_y)
            else:
                walls = [wall for wall in level.current_room.physical_room.walls 
                        if (dy > 0 and wall.top > self.rect.bottom) or 
                           (dy < 0 and wall.bottom < self.rect.top)]
            
                if walls: 
                    if dy > 0:  
                        self.rect.bottom = min(wall.top for wall in walls)
                    else:  
                        self.rect.top = max(wall.bottom for wall in walls)
                self.float_y = self.rect.centery

        room = level.current_room.physical_room
        self.rect.clamp_ip(pygame.Rect(
            level.offset_x, level.offset_y, 
            room.width, room.height
        ))
        self.float_x = self.rect.centerx
        self.float_y = self.rect.centery

    def unlock_movement(self):
        if not self.can_move and pygame.time.get_ticks() - self.last_update > 250:
            self.can_move = True
    
    def take_damage(self, amount):
        if not self.invincible and not self.dead:
            if self.hurt_sound:
                self.hurt_sound.play()
            self.hp -= amount
            print(f"Player took {amount} damage! HP left: {self.hp}")
            if self.hp <= 0:
                self.die()
            else:
                self.invincible = True
                self.invincible_timer = pygame.time.get_ticks()
    
    def die(self):
        self.dead = True
        self.death_time = pygame.time.get_ticks()

    def update_invincibility(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_timer >= self.invincible_duration:
                self.invincible = False
                self.flash_timer = 0

    def check_enemy_collisions(self, enemies):
        if self.invincible:
            return
        
        for enemy in enemies:
            if isinstance(enemy, ShooterEnemy):
                if enemy.check_hit_player(self.rect):
                    self.take_damage(1)
            elif enemy.check_hit_player(self.rect):
                self.take_damage(1)

    def handle_shooting(self, keys):
        if self.shoot_cooldown <= 0:
            self.shooting_direction = None
            direction = None
            
            if keys[pygame.K_UP]:
                direction = "up"
            elif keys[pygame.K_DOWN]:
                direction = "down"
            elif keys[pygame.K_LEFT]:
                direction = "left"
            elif keys[pygame.K_RIGHT]:
                direction = "right"
                
            if direction:
                self.shooting_direction = direction
                projectile = Projectile(
                    self.rect.centerx,
                    self.rect.centery,
                    direction
                )
                self.projectiles.append(projectile)
                if self.shoot_sound:
                    self.shoot_sound.play()
                self.shoot_cooldown = self.shoot_delay
                self.update_sprite()  

    def update_projectiles(self, level):
        self.projectiles = [p for p in self.projectiles if not p.update(level)]
        
        if not any([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
            self.shooting_direction = None
            self.update_sprite()
    
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw_projectiles(self, screen):
        for projectile in self.projectiles:
            projectile.draw(screen)

    def draw(self, screen):
        if self.dead:
            death_rect = self.death_image.get_rect(center=self.rect.center)
            screen.blit(self.death_image, death_rect)
        else:
            if self.invincible:
                current_time = pygame.time.get_ticks()
                if (current_time - self.flash_timer) >= self.flash_interval:
                    self.flash_timer = current_time
                    if (current_time - self.invincible_timer) // self.flash_interval % 2 == 0:
                        screen.blit(self.image, self.rect)
            else:
                screen.blit(self.image, self.rect)

    def check_projectile_hits(self, enemies):
        for projectile in self.projectiles[:]:  
            for enemy in enemies[:]: 
                if enemy.alive and projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(self.damage)
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    break  

    def apply_item_effect(self, effect):
        if "hp_change" in effect:
            self.hp += effect["hp_change"]
        
        if "speed_change" in effect:
            self.speed += effect["speed_change"]
            
        if "damage_change" in effect:
            self.damage += effect["damage_change"]
            
        if "upgrade" in effect and effect["upgrade"]:
            self.upgrade_player()

    def upgrade_player(self):
        self.upgraded = True
        self.original_image = self.upgraded_image
        self.image = self.upgraded_image.copy()
        self.update_sprite()