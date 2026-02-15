import pygame
import random
import math
import sys
import time
import json
import os

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

COLORS = {
    'bg_dark': (15, 15, 25),
    'bg_mid': (30, 30, 45),
    'green': (34, 177, 76),
    'dark_green': (20, 120, 40),
    'brown': (139, 90, 43),
    'sky_blue': (95, 205, 228),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (237, 28, 36),
    'gold': (255, 217, 102),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
}

PLAYER_SIZE = 55
PLAYER_SPEED = 6
JUMP_STRENGTH = 16
GRAVITY = 0.8

TITLE = "title"
LOADING = "loading"
LEVEL_SELECT = "level_select"
PLAYING = "playing"
GAME_OVER = "game_over"

LOADING_QUOTES = [
    "Life exists in the spaces between permanence...",
    "Every step forward is a step toward dissolution.",
    "What you build will crumble. What remains?",
    "Time respects no creation.",
    "The only constant is the inevitable end.",
    "Progress and decay are one and the same.",
    "You cannot stop what has already begun.",
    "All things return to the void.",
    "Even memory fades into static.",
    "The universe tends toward chaos.",
    "What was solid becomes shadow.",
    "Your footprints disappear behind you.",
]

LEVEL_CONFIG = {
    1: {'time': 45, 'distance': 2000, '3star': 25, '2star': 35, 'no_death': False},
    2: {'time': 50, 'distance': 2400, '3star': 30, '2star': 40, 'no_death': False},
    3: {'time': 55, 'distance': 2800, '3star': 35, '2star': 45, 'no_death': False},
    4: {'time': 60, 'distance': 3200, '3star': 40, '2star': 50, 'no_death': True},
    5: {'time': 50, 'distance': 2600, '3star': 30, '2star': 40, 'no_death': False},
    6: {'time': 65, 'distance': 3400, '3star': 45, '2star': 55, 'no_death': False},
    7: {'time': 70, 'distance': 3800, '3star': 50, '2star': 60, 'no_death': True},
    8: {'time': 55, 'distance': 3000, '3star': 35, '2star': 45, 'no_death': False},
    9: {'time': 75, 'distance': 4200, '3star': 55, '2star': 65, 'no_death': False},
    10: {'time': 60, 'distance': 3600, '3star': 40, '2star': 50, 'no_death': True},
}

class Building:
    def __init__(self, x, y, width, height, layer, building_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.layer = layer  # 0 = far back, 1 = mid, 2 = close
        self.type = building_type  # 'tall', 'wide', 'square'
        
    def draw(self, screen, camera, decay_factor, glitch_intensity):
        # Parallax effect - further layers move slower
        parallax_factor = [0.3, 0.6, 0.85][self.layer]
        draw_x = int(self.x - camera.x * parallax_factor)
        
        # Don't draw if off screen
        if draw_x + self.width < 0 or draw_x > WIDTH:
            return
        
        # Color based on layer and decay
        base_gray = [60, 80, 100][self.layer]
        gray_val = int(base_gray * (1 - decay_factor * 0.5))  # Less dramatic color change
        building_color = (gray_val, gray_val, gray_val + 10)
        
        # Subtle crumbling effect - only at high decay
        if decay_factor > 0.6:
            # Building develops cracks and missing sections (rubble effect)
            num_sections = int(3 + decay_factor * 4)  # Fewer sections
            section_height = self.height // num_sections
            
            for i in range(num_sections):
                section_y = self.y + i * section_height
                
                # Very subtle fall - only top sections
                fall_offset = 0
                if i < num_sections - 2:  # Only affect top sections
                    fall_offset = int((decay_factor - 0.6) * i * 8)  # Much less fall
                
                # Small horizontal cracks
                crack_offset = random.randint(-2, 2) if decay_factor > 0.8 else 0
                
                # Some sections missing (creating rubble gaps)
                section_missing = (decay_factor > 0.85 and random.random() < (decay_factor - 0.85) * 2)
                
                if not section_missing:
                    section_x = draw_x + crack_offset
                    section_w = self.width
                    
                    # Draw building section
                    pygame.draw.rect(screen, building_color, 
                                   (section_x, section_y + fall_offset, section_w, section_height))
                    
                    # Draw windows if not too decayed
                    if decay_factor < 0.75:
                        window_color = (int(gray_val * 1.3), int(gray_val * 1.3), int((gray_val + 10) * 1.3))
                        window_size = 8
                        for wx in range(0, section_w, 24):
                            # Some windows broken at higher decay
                            if random.random() > (decay_factor - 0.6) * 1.5:
                                pygame.draw.rect(screen, window_color,
                                               (section_x + wx + 8, section_y + fall_offset + 4, 
                                                window_size, window_size))
                else:
                    # Draw rubble where section is missing
                    if random.random() < 0.6:
                        rubble_color = (int(gray_val * 0.7), int(gray_val * 0.7), int((gray_val + 10) * 0.7))
                        rubble_pieces = random.randint(3, 6)
                        for _ in range(rubble_pieces):
                            rubble_x = draw_x + random.randint(0, self.width - 8)
                            rubble_y = section_y + fall_offset + random.randint(0, section_height - 8)
                            rubble_size = random.randint(4, 12)
                            pygame.draw.rect(screen, rubble_color,
                                           (rubble_x, rubble_y, rubble_size, rubble_size))
        else:
            # Intact or slightly worn building
            pygame.draw.rect(screen, building_color, (draw_x, self.y, self.width, self.height))
            
            # Draw windows
            window_color = (int(gray_val * 1.3), int(gray_val * 1.3), int((gray_val + 10) * 1.3))
            for wy in range(self.y + 20, self.y + self.height - 20, 32):
                for wx in range(0, self.width, 24):
                    # Slight decay - some windows dark
                    if random.random() > decay_factor * 0.5:
                        pygame.draw.rect(screen, window_color,
                                       (draw_x + wx + 8, wy, 8, 8))
                    elif decay_factor > 0.4:
                        # Broken window (darker)
                        dark_window = (int(gray_val * 0.5), int(gray_val * 0.5), int((gray_val + 10) * 0.5))
                        pygame.draw.rect(screen, dark_window,
                                       (draw_x + wx + 8, wy, 8, 8))

class Camera:
    def __init__(self):
        self.x = 0
        
    def update(self, player):
        target_x = player.x - WIDTH // 3
        self.x += (target_x - self.x) * 0.1
        self.x = max(0, self.x)

class Player:
    def __init__(self, x, y, sprites=None):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = 48
        self.height = 48
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.furthest_x = x
        self.deaths = 0
        self.sprites = sprites or {}
        self.facing = "right"
        self.is_moving = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150

        if self.sprites.get("stand_right"):
            self.width = self.sprites["stand_right"].get_width()
            self.height = self.sprites["stand_right"].get_height()
        else:
            self.width = PLAYER_SIZE
            self.height = PLAYER_SIZE
        
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.vel_y = 0
        
    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= PLAYER_SPEED
            self.is_moving = True
            self.facing = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += PLAYER_SPEED
            self.is_moving = True
            self.facing = "right"
            
        if self.x > self.furthest_x:
            self.furthest_x = self.x
        
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        self.on_ground = False
        for platform in platforms:
            if (self.x + self.width > platform['x'] and 
                self.x < platform['x'] + platform['width'] and
                self.y + self.height > platform['y'] and
                self.y + self.height < platform['y'] + 20 and
                self.vel_y > 0):
                self.y = platform['y'] - self.height
                self.vel_y = 0
                self.on_ground = True
                
        if self.y + self.height > HEIGHT - 50:
            self.y = HEIGHT - 50 - self.height
            self.vel_y = 0
            self.on_ground = True
            
    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            
    def draw(self, screen, camera, decay_factor):
        draw_x = int(self.x - camera.x)
        draw_y = int(self.y)

        sprite = None
        if self.sprites:
            self.animation_timer += 16
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 2
            
            if self.is_moving:
                sprite_key = f"walk_{self.facing}_{self.animation_frame}"
                sprite = self.sprites.get(sprite_key)
                if not sprite:
                    sprite = self.sprites.get(f"walk_{self.facing}_0")
            else:
                sprite_key = f"stand_{self.facing}"
                sprite = self.sprites.get(sprite_key)

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            color_intensity = int(255 * (1 - decay_factor))
            player_color = (color_intensity, 100 + int(155 * (1 - decay_factor)), color_intensity)
            pygame.draw.rect(screen, player_color, (draw_x, draw_y, self.width, self.height))
            eye_color = COLORS['black'] if decay_factor < 0.7 else COLORS['gray']
            pygame.draw.rect(screen, eye_color, (draw_x + 6, draw_y + 8, 4, 4))
            pygame.draw.rect(screen, eye_color, (draw_x + 14, draw_y + 8, 4, 4))

class Platform:
    def __init__(self, x, y, width, height, platform_type='grass'):
        self.data = {'x': x, 'y': y, 'width': width, 'height': height, 'type': platform_type}
        
    def draw(self, screen, camera, decay_factor, glitch_intensity):
        x, y, w, h = self.data['x'], self.data['y'], self.data['width'], self.data['height']
        draw_x = int(x - camera.x)
        
        if self.data['type'] == 'grass':
            green_val = int(177 * (1 - decay_factor))
            color = (34, green_val, 76)
        else:
            color = COLORS['brown']
        
        if glitch_intensity > 0.2:
            num_pieces = int(3 + glitch_intensity * 12)
            piece_width = max(8, w // num_pieces)
            max_offset = int(glitch_intensity * glitch_intensity * 20)
            
            for i in range(num_pieces):
                piece_x = draw_x + i * piece_width
                offset_y = random.randint(-max_offset, max_offset // 2)
                piece_y = y + offset_y
                
                if random.random() > glitch_intensity * 0.4:
                    aligned_x = (piece_x // 4) * 4
                    aligned_y = (piece_y // 4) * 4
                    pygame.draw.rect(screen, color, (aligned_x, aligned_y, piece_width, h))
        else:
            pygame.draw.rect(screen, color, (draw_x, y, w, h))

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def draw(self, screen, camera, decay_factor, glitch_intensity):
        draw_x = int(self.x - camera.x)
        color = COLORS['red']
        
        if glitch_intensity > 0.3:
            num_fragments = int(2 + glitch_intensity * 4)
            max_offset = int(glitch_intensity * glitch_intensity * 25)
            
            for i in range(num_fragments):
                offset_x = random.randint(-max_offset, max_offset)
                offset_y = random.randint(-max_offset, max_offset)
                frag_x = ((draw_x + offset_x) // 4) * 4
                frag_y = ((self.y + offset_y) // 4) * 4
                frag_size = max(8, self.width // num_fragments)
                pygame.draw.rect(screen, color, (frag_x, frag_y, frag_size, frag_size))
        else:
            pygame.draw.rect(screen, color, (draw_x, self.y, self.width, self.height))
        
    def check_collision(self, player):
        return (player.x + player.width > self.x and 
                player.x < self.x + self.width and
                player.y + player.height > self.y and
                player.y < self.y + self.height)

class Goal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        self.pulse = 0
        
    def draw(self, screen, camera, decay_factor):
        draw_x = int(self.x - camera.x)
        
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        pulse_size = int(4 * math.sin(self.pulse))
        
        color = COLORS['gold']
        pygame.draw.rect(screen, color, 
                        (draw_x - pulse_size, self.y - pulse_size, 
                         self.width + pulse_size * 2, self.height + pulse_size * 2))
        
        star_color = (255, 255, 150)
        pygame.draw.rect(screen, star_color, (draw_x + 12, self.y + 8, 8, 8))
        
    def check_collision(self, player):
        return (player.x + player.width > self.x and 
                player.x < self.x + self.width and
                player.y + player.height > self.y and
                player.y < self.y + self.height)

class DeathChunk:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self, screen):
        for x in range(0, self.width, 8):
            for y in range(0, self.height, 8):
                if random.random() < 0.7:
                    gray = random.choice([0, 64, 128, 192, 255])
                    pygame.draw.rect(screen, (gray, gray, gray), 
                                   (self.x + x, self.y + y, 8, 8))

class LevelButton:
    def __init__(self, x, y, level_num, stars=0, locked=False):
        self.x = x
        self.y = y
        self.size = 90
        self.level_num = level_num
        self.stars = stars
        self.locked = locked
        self.hovered = False
        
    def draw(self, screen, font, star_image=None):
        border_color = (255, 200, 50) if self.hovered else (180, 140, 30)
        bg_color = (20, 20, 35) if not self.locked else (40, 40, 50)
        
        pygame.draw.rect(screen, border_color, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, bg_color, (self.x + 6, self.y + 6, self.size - 12, self.size - 12))
        
        if self.locked:
            lock_color = (100, 100, 100)
            pygame.draw.rect(screen, lock_color, (self.x + 35, self.y + 40, 20, 24))
            pygame.draw.rect(screen, lock_color, (self.x + 39, self.y + 30, 12, 16))
            pygame.draw.rect(screen, bg_color, (self.x + 41, self.y + 32, 8, 12))
        else:
            text = font.render(str(self.level_num), True, COLORS['white'])
            text_rect = text.get_rect(center=(self.x + self.size // 2, self.y + 30))
            screen.blit(text, text_rect)
            
            if self.stars > 0:
                star_y = self.y + self.size - 22
                if star_image:
                    star_size = star_image.get_width()
                    star_spacing = star_size + 6
                    total_width = self.stars * star_spacing - 6
                    start_x = int(self.x + self.size // 2 - total_width / 2)
                    for i in range(self.stars):
                        star_x = start_x + i * star_spacing
                        star_y_offset = -6 if (i == 1 and self.stars == 3) else 0
                        screen.blit(star_image, (star_x, star_y + star_y_offset))
                else:
                    star_spacing = 18
                    start_x = self.x + self.size // 2 - (self.stars * star_spacing) // 2
                    for i in range(self.stars):
                        star_x = start_x + i * star_spacing
                        star_y_offset = -6 if (i == 1 and self.stars == 3) else 0
                        star_color = (255, 217, 102)
                        pygame.draw.rect(screen, star_color, (star_x + 4, star_y + star_y_offset, 4, 12))
                        pygame.draw.rect(screen, star_color, (star_x, star_y + 4 + star_y_offset, 12, 4))
                    
    def check_hover(self, mouse_pos):
        self.hovered = (self.x <= mouse_pos[0] <= self.x + self.size and
                       self.y <= mouse_pos[1] <= self.y + self.size)
        return self.hovered and not self.locked
        
    def check_click(self, mouse_pos):
        return self.check_hover(mouse_pos)

class ArrowButton:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.size = 80
        self.direction = direction
        self.hovered = False
        
    def draw(self, screen):
        color = (255, 200, 50) if self.hovered else (180, 140, 30)
        
        if self.direction == 'left':
            points = [
                (self.x + 60, self.y + 20),
                (self.x + 20, self.y + 40),
                (self.x + 60, self.y + 60)
            ]
        else:
            points = [
                (self.x + 20, self.y + 20),
                (self.x + 60, self.y + 40),
                (self.x + 20, self.y + 60)
            ]
            
        for i in range(len(points)):
            next_i = (i + 1) % len(points)
            pygame.draw.line(screen, color, points[i], points[next_i], 8)
            
    def check_hover(self, mouse_pos):
        self.hovered = (self.x <= mouse_pos[0] <= self.x + self.size and
                       self.y <= mouse_pos[1] <= self.y + self.size)
        return self.hovered
        
    def check_click(self, mouse_pos):
        return self.check_hover(mouse_pos)

def ensure_playable_platforms(platforms):
    max_gap = 180
    min_width = max(90, PLAYER_SIZE + 20)
    min_y = 240
    max_y = 520

    platforms.sort(key=lambda p: p.data['x'])
    safe_platforms = []
    last_end_x = None
    last_y = None

    for platform in platforms:
        x = platform.data['x']
        y = platform.data['y']
        width = max(min_width, platform.data['width'])
        height = platform.data['height']

        if height != 50:
            y = max(min_y, min(max_y, y))

        platform.data['width'] = width
        platform.data['y'] = y

        if last_end_x is not None:
            gap = x - last_end_x
            if gap > max_gap:
                bridge_x = last_end_x + max_gap
                bridge_y = y if last_y is None else int((y + last_y) / 2)
                bridge_y = max(min_y, min(max_y, bridge_y))
                safe_platforms.append(Platform(bridge_x, bridge_y, min_width, 20, 'grass'))

        safe_platforms.append(platform)
        last_end_x = platform.data['x'] + platform.data['width']
        last_y = platform.data['y']

    return safe_platforms

def draw_8bit_static(screen, intensity, block_size=8):
    if intensity <= 0:
        return
    
    for x in range(0, WIDTH, block_size):
        for y in range(0, HEIGHT, block_size):
            if random.random() < intensity * 0.6:
                gray = random.choice([0, 64, 128, 192, 255])
                pygame.draw.rect(screen, (gray, gray, gray), (x, y, block_size, block_size))

def create_level(level_num):
    """Create fixed, hand-designed levels that progressively get harder"""
    config = LEVEL_CONFIG[level_num]
    distance = config['distance']
    
    platforms = []
    obstacles = []
    buildings = []
    
    # Ground platform
    platforms.append(Platform(0, HEIGHT - 50, distance + 500, 50, 'grass'))
    
    # LEVEL DESIGNS - Each is carefully crafted
    if level_num == 1:
        # Tutorial level - easy jumps
        platforms.extend([
            Platform(300, 500, 120, 20, 'grass'),
            Platform(500, 450, 120, 20, 'grass'),
            Platform(750, 400, 150, 20, 'grass'),
            Platform(1000, 350, 120, 20, 'grass'),
            Platform(1250, 400, 150, 20, 'grass'),
            Platform(1550, 450, 120, 20, 'grass'),
            Platform(1800, 500, 120, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(650, HEIGHT - 82, 24, 32),
            Obstacle(1400, HEIGHT - 82, 24, 32),
        ])
        
    elif level_num == 2:
        # Introduce longer jumps
        platforms.extend([
            Platform(250, 480, 100, 20, 'grass'),
            Platform(450, 420, 100, 20, 'grass'),
            Platform(700, 380, 120, 20, 'grass'),
            Platform(950, 340, 100, 20, 'grass'),
            Platform(1200, 380, 120, 20, 'grass'),
            Platform(1450, 440, 100, 20, 'grass'),
            Platform(1700, 400, 120, 20, 'grass'),
            Platform(1950, 460, 120, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(600, HEIGHT - 82, 24, 32),
            Obstacle(850, 300, 24, 32),
            Obstacle(1600, 360, 24, 32),
        ])
        
    elif level_num == 3:
        # Tighter platforming
        platforms.extend([
            Platform(200, 500, 80, 20, 'grass'),
            Platform(350, 440, 80, 20, 'grass'),
            Platform(520, 380, 80, 20, 'grass'),
            Platform(690, 320, 100, 20, 'grass'),
            Platform(900, 280, 80, 20, 'grass'),
            Platform(1100, 340, 100, 20, 'grass'),
            Platform(1320, 400, 80, 20, 'grass'),
            Platform(1520, 360, 100, 20, 'grass'),
            Platform(1750, 420, 80, 20, 'grass'),
            Platform(1950, 480, 100, 20, 'grass'),
            Platform(2200, 440, 120, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(450, 400, 24, 32),
            Obstacle(800, 280, 24, 32),
            Obstacle(1420, 360, 24, 32),
            Obstacle(2100, HEIGHT - 82, 24, 32),
        ])
        
    elif level_num == 4:
        # HARD - No deaths allowed, precise jumps
        platforms.extend([
            Platform(180, 520, 90, 20, 'grass'),
            Platform(340, 460, 70, 20, 'grass'),
            Platform(490, 400, 80, 20, 'grass'),
            Platform(660, 340, 70, 20, 'grass'),
            Platform(820, 280, 90, 20, 'grass'),
            Platform(1000, 240, 80, 20, 'grass'),
            Platform(1190, 300, 70, 20, 'grass'),
            Platform(1350, 360, 90, 20, 'grass'),
            Platform(1540, 320, 80, 20, 'grass'),
            Platform(1730, 380, 70, 20, 'grass'),
            Platform(1900, 440, 90, 20, 'grass'),
            Platform(2100, 400, 80, 20, 'grass'),
            Platform(2300, 460, 100, 20, 'grass'),
            Platform(2550, 420, 120, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(580, 360, 24, 32),
            Obstacle(910, 240, 24, 32),
            Obstacle(1260, 320, 24, 32),
            Obstacle(1820, 340, 24, 32),
            Obstacle(2200, 360, 24, 32),
        ])
        
    elif level_num == 5:
        # Moving up and down rhythm
        platforms.extend([
            Platform(250, 520, 100, 20, 'grass'),
            Platform(450, 450, 90, 20, 'grass'),
            Platform(640, 380, 100, 20, 'grass'),
            Platform(840, 320, 90, 20, 'grass'),
            Platform(1030, 380, 100, 20, 'grass'),
            Platform(1230, 440, 90, 20, 'grass'),
            Platform(1420, 380, 100, 20, 'grass'),
            Platform(1620, 320, 90, 20, 'grass'),
            Platform(1820, 400, 100, 20, 'grass'),
            Platform(2050, 480, 120, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(550, 410, 24, 32),
            Obstacle(930, 280, 24, 32),
            Obstacle(1520, 340, 24, 32),
            Obstacle(1920, 360, 24, 32),
        ])
        
    elif level_num == 6:
        # Longer jumps, requires momentum
        platforms.extend([
            Platform(220, 500, 110, 20, 'grass'),
            Platform(480, 440, 90, 20, 'grass'),
            Platform(750, 380, 100, 20, 'grass'),
            Platform(1050, 320, 90, 20, 'grass'),
            Platform(1350, 280, 110, 20, 'grass'),
            Platform(1650, 340, 90, 20, 'grass'),
            Platform(1920, 400, 100, 20, 'grass'),
            Platform(2200, 360, 110, 20, 'grass'),
            Platform(2500, 420, 120, 20, 'grass'),
            Platform(2800, 480, 120, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(380, HEIGHT - 82, 24, 32),
            Obstacle(850, 340, 24, 32),
            Obstacle(1540, 300, 24, 32),
            Obstacle(2100, 360, 24, 32),
            Obstacle(2700, 440, 24, 32),
        ])
        
    elif level_num == 7:
        # HARD - Tight technical platforming
        platforms.extend([
            Platform(200, 520, 80, 20, 'grass'),
            Platform(350, 460, 70, 20, 'grass'),
            Platform(500, 400, 80, 20, 'grass'),
            Platform(660, 340, 70, 20, 'grass'),
            Platform(810, 280, 80, 20, 'grass'),
            Platform(980, 240, 70, 20, 'grass'),
            Platform(1140, 200, 80, 20, 'grass'),
            Platform(1310, 260, 70, 20, 'grass'),
            Platform(1470, 320, 80, 20, 'grass'),
            Platform(1640, 280, 70, 20, 'grass'),
            Platform(1800, 340, 80, 20, 'grass'),
            Platform(1970, 400, 70, 20, 'grass'),
            Platform(2140, 360, 80, 20, 'grass'),
            Platform(2320, 420, 70, 20, 'grass'),
            Platform(2500, 380, 80, 20, 'grass'),
            Platform(2680, 440, 90, 20, 'grass'),
            Platform(2900, 490, 120, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(430, 420, 24, 32),
            Obstacle(730, 300, 24, 32),
            Obstacle(1070, 200, 24, 32),
            Obstacle(1550, 280, 24, 32),
            Obstacle(2050, 360, 24, 32),
            Obstacle(2600, 400, 24, 32),
        ])
        
    elif level_num == 8:
        # Speed challenge - wider platforms but more obstacles
        platforms.extend([
            Platform(250, 500, 140, 20, 'grass'),
            Platform(500, 450, 130, 20, 'grass'),
            Platform(750, 400, 140, 20, 'grass'),
            Platform(1000, 350, 130, 20, 'grass'),
            Platform(1280, 400, 140, 20, 'grass'),
            Platform(1550, 450, 130, 20, 'grass'),
            Platform(1820, 400, 140, 20, 'grass'),
            Platform(2100, 450, 150, 20, 'grass'),
            Platform(2400, 500, 140, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(350, 460, 24, 32),
            Obstacle(600, 410, 24, 32),
            Obstacle(850, 360, 24, 32),
            Obstacle(1100, 310, 24, 32),
            Obstacle(1380, 360, 24, 32),
            Obstacle(1650, 410, 24, 32),
            Obstacle(1920, 360, 24, 32),
            Obstacle(2200, 410, 24, 32),
            Obstacle(2500, 460, 24, 32),
        ])
        
    elif level_num == 9:
        # Epic journey - long level with varied challenges
        platforms.extend([
            Platform(230, 510, 100, 20, 'grass'),
            Platform(420, 460, 90, 20, 'grass'),
            Platform(600, 410, 100, 20, 'grass'),
            Platform(800, 360, 90, 20, 'grass'),
            Platform(1000, 310, 100, 20, 'grass'),
            Platform(1210, 270, 90, 20, 'grass'),
            Platform(1420, 230, 100, 20, 'grass'),
            Platform(1640, 290, 90, 20, 'grass'),
            Platform(1840, 350, 100, 20, 'grass'),
            Platform(2050, 310, 90, 20, 'grass'),
            Platform(2260, 370, 100, 20, 'grass'),
            Platform(2470, 430, 90, 20, 'grass'),
            Platform(2680, 380, 100, 20, 'grass'),
            Platform(2900, 440, 90, 20, 'grass'),
            Platform(3120, 400, 100, 20, 'grass'),
            Platform(3350, 460, 120, 20, 'grass'),
            Platform(3600, 510, 140, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(510, 420, 24, 32),
            Obstacle(890, 320, 24, 32),
            Obstacle(1300, 230, 24, 32),
            Obstacle(1730, 310, 24, 32),
            Obstacle(2150, 270, 24, 32),
            Obstacle(2560, 390, 24, 32),
            Obstacle(2990, 400, 24, 32),
            Obstacle(3450, 420, 24, 32),
        ])
        
    elif level_num == 10:
        # FINAL HARD LEVEL - Master test
        platforms.extend([
            Platform(180, 530, 80, 20, 'grass'),
            Platform(320, 480, 70, 20, 'grass'),
            Platform(460, 430, 80, 20, 'grass'),
            Platform(610, 380, 70, 20, 'grass'),
            Platform(750, 330, 80, 20, 'grass'),
            Platform(900, 280, 70, 20, 'grass'),
            Platform(1050, 240, 80, 20, 'grass'),
            Platform(1210, 200, 70, 20, 'grass'),
            Platform(1360, 250, 80, 20, 'grass'),
            Platform(1520, 300, 70, 20, 'grass'),
            Platform(1670, 260, 80, 20, 'grass'),
            Platform(1830, 220, 70, 20, 'grass'),
            Platform(1990, 280, 80, 20, 'grass'),
            Platform(2150, 340, 70, 20, 'grass'),
            Platform(2310, 300, 80, 20, 'grass'),
            Platform(2480, 360, 70, 20, 'grass'),
            Platform(2650, 320, 80, 20, 'grass'),
            Platform(2820, 380, 70, 20, 'grass'),
            Platform(3000, 440, 80, 20, 'grass'),
            Platform(3190, 400, 90, 20, 'grass'),
            Platform(3390, 460, 100, 20, 'grass'),
        ])
        obstacles.extend([
            Obstacle(400, 440, 24, 32),
            Obstacle(690, 340, 24, 32),
            Obstacle(990, 240, 24, 32),
            Obstacle(1300, 210, 24, 32),
            Obstacle(1610, 270, 24, 32),
            Obstacle(1920, 230, 24, 32),
            Obstacle(2240, 310, 24, 32),
            Obstacle(2570, 330, 24, 32),
            Obstacle(2910, 390, 24, 32),
            Obstacle(3290, 410, 24, 32),
        ])
    
    # Generate parallax buildings
    for layer in range(3):
        num_buildings = 8 + layer * 4
        for i in range(num_buildings):
            x = random.randint(100, distance + 500)
            y = random.randint(150, 400)
            width = random.randint(80, 200)
            height = random.randint(HEIGHT - y - 50, HEIGHT - y + 100)
            building_type = random.choice(['tall', 'wide', 'square'])
            buildings.append(Building(x, y, width, height, layer, building_type))
    
    # Sort buildings by layer for proper rendering
    buildings.sort(key=lambda b: b.layer)
    
    goal = Goal(distance, HEIGHT - 98)
    
    platforms = ensure_playable_platforms(platforms)
    return platforms, obstacles, buildings, goal

def draw_loading_screen(screen, font, quote):
    screen.fill(COLORS['bg_dark'])
    
    dots = "." * ((pygame.time.get_ticks() // 500) % 4)
    loading_text = font.render(f"LOADING{dots}", True, COLORS['white'])
    screen.blit(loading_text, (WIDTH // 2 - loading_text.get_width() // 2, HEIGHT // 2 - 50))
    
    quote_font = pygame.font.Font(None, 28)
    quote_text = quote_font.render(quote, True, COLORS['gray'])
    screen.blit(quote_text, (WIDTH // 2 - quote_text.get_width() // 2, HEIGHT // 2 + 50))
    
    bar_width = 400
    bar_height = 20
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = HEIGHT // 2 + 100
    
    pygame.draw.rect(screen, COLORS['dark_gray'], (bar_x, bar_y, bar_width, bar_height))
    
    fill_width = int((pygame.time.get_ticks() % 2000) / 2000 * bar_width)
    pygame.draw.rect(screen, COLORS['green'], (bar_x, bar_y, fill_width, bar_height))

def draw_title_screen(screen, font, large_font, start_button, quit_button, mouse_pos, title_image=None, sub_image=None):
    for y in range(0, HEIGHT, 8):
        darkness = int(15 + (y / HEIGHT) * 20)
        pygame.draw.rect(screen, (darkness, darkness, darkness + 10), (0, y, WIDTH, 8))
    
    if title_image:
        title_rect = title_image.get_rect(center=(WIDTH // 2, 180))
        screen.blit(title_image, title_rect)
    else:
        title = large_font.render("ENTROPY", True, COLORS['white'])
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        
    if sub_image:
        sub_rect = sub_image.get_rect(center=(WIDTH // 2, 255))
        screen.blit(sub_image, sub_rect)
    else:
        subtitle = font.render("Nothing Lasts Forever", True, COLORS['gray'])
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 280))
    
    start_button.check_hover(mouse_pos)
    quit_button.check_hover(mouse_pos)
    
    for button in [start_button, quit_button]:
        draw_8bit_button(screen, button, font)
    
    for i in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(HEIGHT - 100, HEIGHT)
        size = 4
        gray = random.choice([0, 64, 128, 192, 255])
        pygame.draw.rect(screen, (gray, gray, gray), (x, y, size, size))

def draw_8bit_button(screen, button, font):
    border_color = (100, 200, 100) if button.hovered else (80, 80, 120)
    bg_color = (30, 30, 45)
    
    pygame.draw.rect(screen, border_color, button.rect)
    pygame.draw.rect(screen, bg_color, button.rect.inflate(-12, -12))
    
    text_color = (200, 255, 200) if button.hovered else (200, 200, 220)
    text_surf = font.render(button.text, True, text_color)
    text_rect = text_surf.get_rect(center=button.rect.center)
    screen.blit(text_surf, text_rect)

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
        
    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def calculate_stars(level_num, time_taken, deaths):
    config = LEVEL_CONFIG[level_num]
    
    if config['no_death'] and deaths > 0:
        return 0
    
    if time_taken <= config['3star'] and deaths == 0:
        return 3
    elif time_taken <= config['2star']:
        return 2
    elif time_taken <= config['time']:
        return 1
    else:
        return 0

def save_progress(level_scores):
    save_data = {
        'level_scores': level_scores,
        'unlocked_levels': []
    }
    
    for i in range(1, 11):
        if i == 1 or level_scores.get(i - 1, 0) > 0:
            save_data['unlocked_levels'].append(i)
    
    try:
        with open('entropy_save.txt', 'w') as f:
            json.dump(save_data, f)
    except Exception as e:
        print(f"Error saving: {e}")

def load_progress():
    if not os.path.exists('entropy_save.txt'):
        return {}
    
    try:
        with open('entropy_save.txt', 'r') as f:
            content = f.read().strip()
            if not content:  # Empty file
                return {}
            save_data = json.loads(content)
            return save_data.get('level_scores', {})
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Save file corrupted, starting fresh: {e}")
        return {}
    except Exception as e:
        print(f"Error loading: {e}")
        return {}

def is_level_unlocked(level_num, level_scores):
    if level_num == 1:
        return True
    return level_scores.get(level_num - 1, 0) > 0

def load_gif_frames(path, scale_size=(PLAYER_SIZE, PLAYER_SIZE)):
    frames = []
    try:
        from PIL import Image
        gif = Image.open(path)
        
        frame_index = 0
        while True:
            try:
                gif.seek(frame_index)
                frame = gif.convert('RGBA')
                
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                
                py_image = pygame.image.fromstring(data, size, mode)
                py_image = pygame.transform.scale(py_image, scale_size)
                frames.append(py_image)
                
                frame_index += 1
            except EOFError:
                break
                
    except Exception as e:
        print(f"Error loading GIF {path}: {e}")
    
    return frames

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Entropy - 8-bit Edition")
    clock = pygame.time.Clock()
    
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    large_font = pygame.font.Font(None, 96)
    
    # Load images
    title_image = None
    try:
        for path in ['/mnt/user-data/uploads/title.png', 'title.png', './title.png']:
            if os.path.exists(path):
                title_image = pygame.image.load(path).convert_alpha()
                if title_image.get_width() > 600:
                    scale_factor = 600 / title_image.get_width()
                    new_height = int(title_image.get_height() * scale_factor)
                    title_image = pygame.transform.scale(title_image, (600, new_height))
                break
    except Exception as e:
        print(f"Could not load title image: {e}")

    sub_image = None
    try:
        for path in ['/mnt/user-data/uploads/subtxt.png', 'subtxt.png', './subtxt.png']:
            if os.path.exists(path):
                sub_image = pygame.image.load(path).convert_alpha()
                if sub_image.get_width() > 500:
                    scale_factor = 500 / sub_image.get_width()
                    new_height = int(sub_image.get_height() * scale_factor)
                    sub_image = pygame.transform.scale(sub_image, (500, new_height))
                break
    except Exception as e:
        print(f"Could not load subtitle image: {e}")

    star_small = None
    star_large = None
    star_large_dim = None
    try:
        for path in ['/mnt/user-data/uploads/star.png', 'star.png', './star.png']:
            if os.path.exists(path):
                star_image = pygame.image.load(path).convert_alpha()
                star_small = pygame.transform.scale(star_image, (16, 16))
                star_large = pygame.transform.scale(star_image, (40, 40))
                star_large_dim = star_large.copy()
                star_large_dim.fill((120, 120, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
                break
    except Exception as e:
        print(f"Could not load star image: {e}")

    player_sprites = {}
    try:
        sprite_gifs = {
            "stand_left": "oldManStandLeft.gif",
            "stand_right": "oldManStandRight.gif",
            "walk_left": "oldManWalkLeft.gif",
            "walk_right": "oldManWalkRight.gif",
        }
        
        for key, filename in sprite_gifs.items():
            for path in [filename, f'./{filename}', f'/mnt/user-data/uploads/{filename}']:
                if os.path.exists(path):
                    frames = load_gif_frames(path, (PLAYER_SIZE, PLAYER_SIZE))
                    if frames:
                        for i, frame in enumerate(frames):
                            player_sprites[f"{key}_{i}"] = frame
                        if frames:
                            player_sprites[key] = frames[0]
                    break
    except Exception as e:
        print(f"Could not load player sprites: {e}")
        player_sprites = {}
    
    state = TITLE
    current_level = 1
    camera = Camera()
    player = None
    platforms = []
    obstacles = []
    buildings = []
    goal = None
    death_chunks = []
    
    start_time = 0
    final_time = 0
    game_over = False
    won = False
    loading_start = 0
    loading_quote = random.choice(LOADING_QUOTES)
    
    level_scores = load_progress()
    
    start_button = Button(WIDTH // 2 - 150, 380, 300, 70, "START GAME", "start")
    quit_button = Button(WIDTH // 2 - 150, 480, 300, 70, "QUIT", "quit")
    replay_button = Button(WIDTH // 2 - 170, HEIGHT // 2 + 140, 340, 60, "REPLAY LEVEL", "replay")
    levels_button = Button(WIDTH // 2 - 170, HEIGHT // 2 + 210, 340, 60, "BACK TO LEVELS", "levels")
    
    def create_level_buttons():
        buttons = []
        for i in range(1, 11):
            local_idx = i - 1
            row = local_idx // 5
            col = local_idx % 5
            x = 355 + col * 120
            y = 170 + row * 120
            stars = level_scores.get(i, 0)
            locked = not is_level_unlocked(i, level_scores)
            buttons.append(LevelButton(x, y, i, stars, locked))
        return buttons
    
    level_buttons = create_level_buttons()
    back_arrow = ArrowButton(50, HEIGHT // 2 - 40, 'left')
    mouse_pos = (0, 0)
    
    running = True
    while running:
        dt = clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if state == TITLE:
                        if start_button.check_click(mouse_pos):
                            state = LEVEL_SELECT
                        elif quit_button.check_click(mouse_pos):
                            running = False
                            
                    elif state == LEVEL_SELECT:
                        if back_arrow.check_click(mouse_pos):
                            state = TITLE
                        else:
                            for btn in level_buttons:
                                if btn.check_click(mouse_pos):
                                    current_level = btn.level_num
                                    state = LOADING
                                    loading_start = pygame.time.get_ticks()
                                    loading_quote = random.choice(LOADING_QUOTES)
                                    break
                    elif state == GAME_OVER:
                        if replay_button.check_click(mouse_pos):
                            player = Player(50, HEIGHT - 100, player_sprites)
                            platforms, obstacles, buildings, goal = create_level(current_level)
                            camera = Camera()
                            death_chunks = []
                            start_time = pygame.time.get_ticks()
                            final_time = 0
                            game_over = False
                            won = False
                            state = PLAYING
                        elif levels_button.check_click(mouse_pos):
                            level_buttons = create_level_buttons()
                            state = LEVEL_SELECT
                                    
            elif event.type == pygame.KEYDOWN:
                if state == PLAYING and not game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                        player.jump()
        
        if state == TITLE:
            draw_title_screen(screen, font, large_font, start_button, quit_button, mouse_pos, title_image, sub_image)
            
        elif state == LOADING:
            draw_loading_screen(screen, font, loading_quote)
            
            if pygame.time.get_ticks() - loading_start > 2000:
                player = Player(50, HEIGHT - 100, player_sprites)
                platforms, obstacles, buildings, goal = create_level(current_level)
                camera = Camera()
                death_chunks = []
                start_time = pygame.time.get_ticks()
                final_time = 0
                game_over = False
                won = False
                state = PLAYING
            
        elif state == LEVEL_SELECT:
            for y in range(0, HEIGHT, 8):
                darkness = int(20 + (y / HEIGHT) * 15)
                pygame.draw.rect(screen, (darkness, darkness, darkness + 10), (0, y, WIDTH, 8))
            
            title = large_font.render("LEVEL SELECT", True, COLORS['white'])
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
            
            for btn in level_buttons:
                btn.check_hover(mouse_pos)
                btn.draw(screen, font, star_small)
            
            back_arrow.check_hover(mouse_pos)
            back_arrow.draw(screen)
            
        elif state == PLAYING:
            if not game_over:
                player.update([p.data for p in platforms])
                camera.update(player)
                
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
                config = LEVEL_CONFIG[current_level]
                time_remaining = max(0, config['time'] - elapsed_time)
                
                distance_decay = min(1.0, player.furthest_x / config['distance'])
                decay_factor = distance_decay
                glitch_intensity = distance_decay
                
                if time_remaining <= 15:
                    static_intensity = (15 - time_remaining) / 15.0
                else:
                    static_intensity = 0
                
                for obstacle in obstacles:
                    if obstacle.check_collision(player):
                        player.lives -= 1
                        player.deaths += 1
                        
                        num_chunks = random.randint(2, 3)
                        for _ in range(num_chunks):
                            chunk_width = random.randint(100, 180)
                            chunk_height = random.randint(80, 140)
                            chunk_x = random.randint(0, WIDTH - chunk_width)
                            chunk_y = random.randint(0, HEIGHT - chunk_height)
                            death_chunks.append(DeathChunk(chunk_x, chunk_y, chunk_width, chunk_height))
                        
                        player.reset()
                        
                        if player.lives <= 0:
                            game_over = True
                            final_time = int(elapsed_time)
                            state = GAME_OVER
                
                if goal.check_collision(player):
                    won = True
                    game_over = True
                    final_time = int(elapsed_time)
                    stars = calculate_stars(current_level, final_time, player.deaths)
                    level_scores[current_level] = max(level_scores.get(current_level, 0), stars)
                    save_progress(level_scores)
                    state = GAME_OVER
                
                if time_remaining <= 0:
                    game_over = True
                    final_time = config['time']
                    state = GAME_OVER
            
            # Draw with parallax
            sky_intensity = int(228 * (1 - decay_factor * 0.8))
            sky_color = (int(95 * (1 - decay_factor * 0.5)), 
                        int(205 * (1 - decay_factor * 0.6)), 
                        sky_intensity)
            screen.fill(sky_color)
            
            # Draw buildings (parallax background)
            for building in buildings:
                building.draw(screen, camera, decay_factor, glitch_intensity)
            
            for platform in platforms:
                platform.draw(screen, camera, decay_factor, glitch_intensity)
            
            for obstacle in obstacles:
                obstacle.draw(screen, camera, decay_factor, glitch_intensity)
            
            goal.draw(screen, camera, decay_factor)
            player.draw(screen, camera, decay_factor)
            
            for chunk in death_chunks:
                chunk.draw(screen)
            
            if static_intensity > 0:
                draw_8bit_static(screen, static_intensity, 8)
            
            pygame.draw.rect(screen, COLORS['bg_dark'], (0, 0, WIDTH, 50))
            
            lives_text = font.render(f"LIVES: {player.lives}", True, COLORS['white'])
            screen.blit(lives_text, (20, 10))
            
            config = LEVEL_CONFIG[current_level]
            
            if game_over:
                display_time = final_time
            else:
                display_time = int(max(0, config['time'] - (pygame.time.get_ticks() - start_time) / 1000))
            
            time_text = font.render(f"TIME: {display_time}", True, COLORS['white'])
            screen.blit(time_text, (WIDTH - 180, 10))
            
            level_text = small_font.render(f"LEVEL {current_level}", True, COLORS['white'])
            screen.blit(level_text, (WIDTH // 2 - 60, 15))
            
        elif state == GAME_OVER:
            screen.fill(COLORS['bg_dark'])
            
            if won:
                title = large_font.render("COMPLETE!", True, COLORS['green'])
                
                stars = level_scores.get(current_level, 0)
                
                stars_y = HEIGHT // 2 - 60
                if star_large and star_large_dim:
                    star_size = star_large.get_width()
                    star_spacing = star_size + 20
                    total_width = 3 * star_spacing - 20
                    start_x = WIDTH // 2 - total_width // 2
                    for i in range(3):
                        star_x = start_x + i * star_spacing
                        star_y_offset = -8 if i == 1 else 0
                        star_image = star_large if i < stars else star_large_dim
                        screen.blit(star_image, (star_x, stars_y + star_y_offset))
                else:
                    star_spacing = 60
                    start_x = WIDTH // 2 - (3 * star_spacing) // 2
                    for i in range(3):
                        star_x = start_x + i * star_spacing
                        star_y_offset = -8 if i == 1 else 0
                        color = COLORS['gold'] if i < stars else COLORS['dark_gray']
                        pygame.draw.rect(screen, color, (star_x + 16, stars_y + star_y_offset, 8, 24))
                        pygame.draw.rect(screen, color, (star_x, stars_y + 8 + star_y_offset, 40, 8))
                
                time_text = font.render(f"Time: {final_time}s", True, COLORS['white'])
                screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 50))
                
                deaths_text = font.render(f"Deaths: {player.deaths}", True, COLORS['white'])
                screen.blit(deaths_text, (WIDTH // 2 - deaths_text.get_width() // 2, HEIGHT // 2 + 90))
                
            elif player.lives <= 0:
                title = large_font.render("DISSOLVED", True, COLORS['red'])
            else:
                title = large_font.render("TIME ENDED", True, COLORS['gray'])
            
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 150))
            
            replay_button.check_hover(mouse_pos)
            levels_button.check_hover(mouse_pos)
            draw_8bit_button(screen, replay_button, font)
            draw_8bit_button(screen, levels_button, font)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()