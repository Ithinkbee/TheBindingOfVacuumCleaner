import random
from typing import List, Tuple, Optional
import pygame
from config import *
from enemy import *
from item import *

class PhysicalRoom:
    def __init__(self, room_type: str = "normal", width: int = WIDTH, height: int = HEIGHT):
        self.type = room_type
        self.width = width
        self.height = height
        self.wall_thickness = WALL_THICKNESS
        self.door_size = DOOR_SIZE
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.walls = []
        self.doors = []
        self._generate_layout()
        self.enemies = []
        self.enemies_spawned = False
        self.spawn_enemies()
        self.items = []
        self.items_spawned = False

    def _generate_layout(self):
        self.walls = [
            pygame.Rect(0, 0, self.width, self.wall_thickness), 
            pygame.Rect(0, self.height - self.wall_thickness, self.width, self.wall_thickness), 
            pygame.Rect(0, 0, self.wall_thickness, self.height),  
            pygame.Rect(self.width - self.wall_thickness, 0, self.wall_thickness, self.height)  
        ]

    def add_door(self, direction: str): 
        door_pos = {
            "up": (
                self.width // 2 - self.door_size // 2,
                DOOR_INSET,  
                self.door_size,
                self.wall_thickness
            ),
            "down": (
                self.width // 2 - self.door_size // 2,
                self.height - self.wall_thickness - DOOR_INSET, 
                self.door_size,
                self.wall_thickness
            ),
            "left": (
                DOOR_INSET,  
                self.height // 2 - self.door_size // 2,
                self.wall_thickness,
                self.door_size
            ),
            "right": (
                self.width - self.wall_thickness - DOOR_INSET, 
                self.height // 2 - self.door_size // 2,
                self.wall_thickness,
                self.door_size
            )
        }

        door_rect = pygame.Rect(*door_pos[direction])
        self.doors.append((direction, door_rect))

    def check_collision(self, rect: pygame.Rect) -> bool:
        return any(rect.colliderect(wall) for wall in self.walls)

    def spawn_enemies(self):
        if self.enemies_spawned or self.type in ["start", "treasure"]:
            return
        
        self.enemies_spawned = True

        if self.type == "boss":
            boss = Dupok(self.width // 2, self.height // 2)
            self.enemies.append(boss)
        else:
            enemy_count = random.randint(1, 4)
            for _ in range(enemy_count):
                x = random.randint(100, self.width - 100)
                y = random.randint(100, self.height - 100)
                if random.random() < 0.5:
                    self.enemies.append(WalkingEnemy(x, y))
                else:
                    self.enemies.append(ShooterEnemy(x, y))

    def spawn_items(self):
        if self.items_spawned:
            return
        
        self.items_spawned = True
    
        if self.type == "treasure":
            item_types = [HealthUpItem, SpeedUpItem, DamageUpItem, Upgrade]
            for _ in range(random.randint(1, 1)):
                x = random.randint(100, self.width - 100)
                y = random.randint(100, self.height - 100)
                item_class = random.choice(item_types)
                self.items.append(item_class(x, y))


class Room:
    def __init__(self, room_type: str = "normal", position: Tuple[int, int] = (0, 0)):
        self.type = room_type
        self.position = position
        self.connections = {"up": None, "down": None, "left": None, "right": None}
        self.physical_room = PhysicalRoom(room_type) 

    def add_connection(self, direction: str, other_room):
        self.connections[direction] = other_room
        self.physical_room.add_door(direction)


class LevelGenerator:
    def __init__(self, width: int = 7, height: int = 7):
        self.width = max(5, width)
        self.height = max(5, height)
        self.grid: List[List[Optional[Room]]] = [[None for _ in range(width)] for _ in range(height)]
        self.start_pos = (width // 2, height // 2)

    def generate(self) -> List[List[Optional[Room]]]:
        start_x, start_y = self.start_pos
        self._create_room(start_x, start_y, "start")

        main_path = self._generate_main_path(start_x, start_y)

        boss_x, boss_y = main_path[-1]
    
        self.grid[boss_y][boss_x] = None
    
        boss_room = self._create_room(boss_x, boss_y, "boss")
    
        for direction, (dx, dy) in [("up", (0, -1)), ("down", (0, 1)), 
                                   ("left", (-1, 0)), ("right", (1, 0))]:
            nx, ny = boss_x + dx, boss_y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx]:
                opposite = {"up": "down", "down": "up", 
                           "left": "right", "right": "left"}[direction]
                boss_room.add_connection(direction, self.grid[ny][nx])
                self.grid[ny][nx].add_connection(opposite, boss_room)

        self._add_treasure_room(main_path)
        self._fill_with_connected_rooms(main_path)

        return self.grid

    def _create_room(self, x: int, y: int, room_type: str):
        room = Room(room_type, (x, y))
        self.grid[y][x] = room
        if room_type in ["start", "treasure", "boss"]:
            room.physical_room.enemies = []
            room.physical_room.enemies_spawned = False
            room.physical_room.spawn_enemies()
        return room

    def _generate_main_path(self, start_x: int, start_y: int) -> List[Tuple[int, int]]:
        path = [(start_x, start_y)]
        current_x, current_y = start_x, start_y
        min_path_length = min(4, self.width + self.height - 2)

        while len(path) < min_path_length:
            directions = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = current_x + dx, current_y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in path):
                    directions.append((dx, dy))

            if not directions:
                if len(path) > 1:
                    path.pop()
                    current_x, current_y = path[-1]
                    continue
                else:
                    return self._generate_main_path(start_x, start_y)

            dx, dy = random.choice(directions)
            next_x, next_y = current_x + dx, current_y + dy

            if self.grid[next_y][next_x] is None:
                self._create_room(next_x, next_y, "normal")

            direction = {(0, 1): "down", (1, 0): "right", (0, -1): "up", (-1, 0): "left"}[(dx, dy)]
            opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}[direction]

            self.grid[current_y][current_x].add_connection(direction, self.grid[next_y][next_x])
            self.grid[next_y][next_x].add_connection(opposite, self.grid[current_y][current_x])

            path.append((next_x, next_y))
            current_x, current_y = next_x, next_y

        return path

    def _add_treasure_room(self, main_path: List[Tuple[int, int]]):
        if len(main_path) > 2:
            x, y = random.choice(main_path[1:-1])
            room = self.grid[y][x]
            room.type = "treasure"
            room.physical_room.type = "treasure"
            room.physical_room.enemies = []
            room.physical_room.spawn_items()

    def _fill_with_connected_rooms(self, main_path: List[Tuple[int, int]]):
        for x, y in main_path:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (self._is_valid_position(nx, ny) and self.grid[ny][nx] is None and random.random() < 0.7):
                    self._create_and_connect_room(nx, ny, x, y)

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] is None and random.random() < 0.4:
                    self._create_and_connect_to_nearest(x, y)
    
    def _create_and_connect_room(self, x: int, y: int, connected_x: int, connected_y: int):
        self._create_room(x, y, "normal")
    
        dx, dy = x - connected_x, y - connected_y
    
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "down" if dy > 0 else "up"
    
        opposite = {"up": "down", "down": "up", 
                   "left": "right", "right": "left"}[direction]
    
        self.grid[connected_y][connected_x].add_connection(direction, self.grid[y][x])
        self.grid[y][x].add_connection(opposite, self.grid[connected_y][connected_x])
    
    def _create_and_connect_to_nearest(self, x: int, y: int):
        for distance in range(1, max(self.width, self.height)):
            for dx, dy in [(0, distance), (distance, 0), (0, -distance), (-distance, 0)]:
                nx, ny = x + dx, y + dy
                if self._is_valid_position(nx, ny) and self.grid[ny][nx]:
                    self._create_and_connect_room(x, y, nx, ny)
                    return
                
    def _get_next_room(self, x: int, y: int, direction: str) -> Tuple[int, int]:
        if direction == "up": return x, y - 1
        elif direction == "down": return x, y + 1
        elif direction == "left": return x - 1, y
        elif direction == "right": return x + 1, y

    def _get_direction(self, x1: int, y1: int, x2: int, y2: int) -> str:
        if x1 > x2: return "left"
        if y1 < y2: return "down"
        return "up"
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height