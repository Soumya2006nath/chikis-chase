import pygame
import random
import sqlite3
from collections import deque
import math

# =========================
# Setup / Constants
# =========================
pygame.init()
WIDTH, HEIGHT = 800, 600
TILE = 20
ROWS, COLS = HEIGHT // TILE, WIDTH // TILE
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
GAME_SURFACE = pygame.Surface((WIDTH, HEIGHT))

pygame.display.set_caption("Snake Chase - Chick Adventure (Upgraded)")
# Colors
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)
SNAKE_HEAD = (150, 50, 200)  # Vibrant purple
SNAKE_BODY = (200, 100, 250)  # Magenta
SNAKE_SPOT = (100, 50, 150)  # Darker purple for spots
CHICK_YELLOW = (255, 255, 0)
CHICK_ORANGE = (255, 180, 0)
CHICK_DARK = (220, 160, 0)
CHICK_BEAK = (255, 150, 0)
CHICK_EYE = (30, 30, 30)
CHICK_WING = (255, 200, 0)
BERRY_COLOR = (220, 20, 60)
MUSHROOM_COLOR = (255, 200, 200)
MUSHROOM_SPOT_COLOR = (200, 50, 50)
GOLDEN_EGG = (255, 215, 0)
ROCK_COLOR = (120, 120, 120)
GRASS_LIGHT = (100, 200, 100)
GRASS_DARK = (80, 160, 80)
GRASS_DETAIL = (70, 140, 70)
YELLOW = (250, 250, 50)
RED = (255, 50, 50)
PINK = (255, 150, 150)
PORTAL_COLOR = (150, 100, 255)
WATER_COLOR = (64, 164, 223)
LAVA_COLOR = (255, 100, 50)
SPEED_BOOST_COLOR = (50, 200, 255)  # Blue for speed boost
INVINCIBILITY_COLOR = (255, 215, 0)  # Gold for invincibility
CONFUSION_COLOR = (200, 50, 200)  # Purple for confusion
FREEZE_COLOR = (100, 200, 255)  # Light blue for freeze
# Fonts
FONT_BIG = pygame.font.SysFont("Arial", 48, bold=True)
FONT_MED = pygame.font.SysFont("Arial", 32, bold=True)
FONT_SM = pygame.font.SysFont("Arial", 24, bold=True)
FONT_XS = pygame.font.SysFont("Arial", 16, bold=True)
# Session best (not persisted to disk)
SESSION_BEST_LEVEL = 1
# Buff/Debuff notification
buff_notification = None
buff_notification_timer = 0

# =========================
# Background (pre-render)
# =========================
background = pygame.Surface((WIDTH, HEIGHT))
random.seed(7)  # consistent background decoration
for y in range(0, HEIGHT, TILE):
    for x in range(0, WIDTH, TILE):
        color = GRASS_DARK if (x // TILE + y // TILE) % 2 == 0 else GRASS_LIGHT
        pygame.draw.rect(background, color, (x, y, TILE, TILE))
        if random.random() < 0.2:
            pygame.draw.line(background, GRASS_DETAIL,
                             (x + TILE // 2, y + 2),
                             (x + TILE // 2, y + 5), 2)
        if random.random() < 0.05:
            flower_color = random.choice([(255, 100, 100), (255, 200, 100), (200, 100, 255)])
            pygame.draw.circle(background, flower_color, (x + TILE // 2, y + TILE // 2), 2)
            pygame.draw.circle(background, (240, 240, 240), (x + TILE // 2, y + TILE // 2), 1)

# =========================
# Utilities / Draw helpers
# =========================
def draw_text_center(surface, text, font, x, y, color=WHITE):
    ts = font.render(text, True, color)
    rect = ts.get_rect(center=(x, y))
    surface.blit(ts, rect)

def draw_text(surface, text, font, x, y, color=WHITE):
    ts = font.render(text, True, color)
    surface.blit(ts, (x, y))

def draw_pixel_heart(surface, x, y, size, filled=True):
    heart_pattern = [
        [0, 1, 1, 0, 1, 1, 0],
        [1, 2, 2, 1, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [0, 1, 2, 2, 2, 1, 0],
        [0, 0, 1, 2, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0]
    ]
    colors = [None, RED, (255, 100, 100) if filled else (60, 60, 60)]
    px = size // 7
    for r in range(7):
        for c in range(7):
            val = heart_pattern[r][c]
            if val > 0:
                pygame.draw.rect(surface, colors[val], (x + c * px, y + r * px, px, px))

def draw_hearts(surface, x, y, lives, max_lives=3):
    heart_size = 21
    spacing = 10
    for i in range(max_lives):
        filled = i < lives
        draw_pixel_heart(surface, x + i * (heart_size + spacing), y, heart_size, filled=filled)

def draw_rock(surface, x, y):
    pygame.draw.circle(surface, ROCK_COLOR, (x + TILE // 2, y + TILE // 2), TILE // 2)
    pygame.draw.circle(surface, (100, 100, 100), (x + TILE // 3, y + TILE // 3), TILE // 6)
    pygame.draw.circle(surface, (140, 140, 140), (x + 2 * TILE // 3, y + 2 * TILE // 3), TILE // 6)

def draw_water(surface, x, y):
    pygame.draw.circle(surface, WATER_COLOR, (x + TILE // 2, y + TILE // 2), TILE // 2)
    for i in range(3):
        wave_y = y + TILE // 4 + i * TILE // 6
        pygame.draw.arc(surface, (100, 180, 255),
                        (x + TILE // 4, wave_y, TILE // 2, TILE // 4),
                        0, math.pi, 2)

def draw_lava(surface, x, y):
    pygame.draw.circle(surface, LAVA_COLOR, (x + TILE // 2, y + TILE // 2), TILE // 2)
    for i in range(2):
        bubble_x = x + TILE // 4 + i * TILE // 2
        bubble_y = y + TILE // 3
        pygame.draw.circle(surface, (255, 200, 100), (bubble_x, bubble_y), TILE // 8)

def draw_berry(surface, x, y):
    pygame.draw.circle(surface, BERRY_COLOR, (x + TILE // 2, y + TILE // 2), int(TILE // 2.5))  # Increased size
    pygame.draw.circle(surface, (150, 20, 20), (x + TILE // 2, y + TILE // 2), int(TILE // 5))
    pygame.draw.rect(surface, (0, 100, 0), (x + TILE // 2 - 1, y + TILE // 4, 2, int(TILE // 3)))

def draw_mushroom(surface, x, y):
    pygame.draw.rect(surface, (240, 220, 180), (x + TILE // 3, y + TILE // 2, TILE // 3, int(TILE // 1.5)))  # Increased size
    pygame.draw.circle(surface, MUSHROOM_COLOR, (x + TILE // 2, y + TILE // 2), int(TILE // 1.5))
    pygame.draw.circle(surface, MUSHROOM_SPOT_COLOR, (x + TILE // 3, y + TILE // 3), int(TILE // 6))
    pygame.draw.circle(surface, MUSHROOM_SPOT_COLOR, (x + 2 * TILE // 3, y + TILE // 3), int(TILE // 6))
    pygame.draw.circle(surface, MUSHROOM_SPOT_COLOR, (x + TILE // 2, y + TILE // 2), int(TILE // 6))

def draw_golden_egg(surface, x, y):
    pygame.draw.ellipse(surface, GOLDEN_EGG, (x + TILE * 0.2, y + TILE * 0.1, int(TILE * 0.6), int(TILE * 0.8)))  # Increased size
    pygame.draw.ellipse(surface, (255, 240, 170), (x + TILE * 0.3, y + TILE * 0.2, int(TILE * 0.4), int(TILE * 0.6)))

def draw_portal(surface, x, y, t):
    # t can be a time-based float for pulsing
    cx, cy = x + TILE // 2, y + TILE // 2
    base = TILE // 2
    pulse = int((math.sin(t * 0.005) + 1) * 3)
    for i in range(3):
        pygame.draw.circle(surface, (100 + i * 30, 50 + i * 30, 200 + i * 10),
                           (cx, cy), base - i * 4 + pulse, 2)

def draw_speed_boost(surface, x, y):
    pygame.draw.circle(surface, SPEED_BOOST_COLOR, (x + TILE // 2, y + TILE // 2), int(TILE // 2.5))  # Increased size
    # Improved: double arrow for speed
    pygame.draw.polygon(surface, WHITE, [
        (x + TILE // 2 - int(TILE // 4), y + int(TILE // 3)),
        (x + TILE // 2 - int(TILE // 4), y + int(3 * TILE // 4)),
        (x + TILE // 2 + int(TILE // 4), y + int(TILE // 2))
    ])
    pygame.draw.polygon(surface, WHITE, [
        (x + TILE // 2 + int(TILE // 4), y + int(TILE // 3)),
        (x + TILE // 2 + int(TILE // 4), y + int(3 * TILE // 4)),
        (x + 3 * TILE // 4, y + int(TILE // 2))
    ])
    # Speed lines
    pygame.draw.line(surface, WHITE, (x + int(TILE // 3), y + int(TILE // 2.5)), (x + int(TILE // 2.5), y + int(TILE // 2.5)), 2)
    pygame.draw.line(surface, WHITE, (x + int(TILE // 3), y + int(TILE // 2)), (x + int(TILE // 2.5), y + int(TILE // 2)), 2)
    pygame.draw.line(surface, WHITE, (x + int(TILE // 3), y + int(2 * TILE // 3)), (x + int(TILE // 2.5), y + int(2 * TILE // 3)), 2)

def draw_invincibility(surface, x, y):
    # Improved: shield shape
    pygame.draw.polygon(surface, INVINCIBILITY_COLOR, [
        (x + TILE // 2, y + int(TILE // 3)),
        (x + int(TILE // 3), y + int(TILE // 1.8)),
        (x + int(TILE // 3), y + int(3 * TILE // 4)),
        (x + int(3 * TILE // 4), y + int(3 * TILE // 4)),
        (x + int(3 * TILE // 4), y + int(TILE // 1.8))
    ])
    # Inner glow
    pygame.draw.polygon(surface, WHITE, [
        (x + TILE // 2, y + int(TILE // 2.5)),
        (x + int(TILE // 2.5), y + int(TILE // 1.7)),
        (x + int(TILE // 2.5), y + int(2 * TILE // 3)),
        (x + int(2 * TILE // 3), y + int(2 * TILE // 3)),
        (x + int(2 * TILE // 3), y + int(TILE // 1.7))
    ], 2)

def draw_confusion(surface, x, y):
    pygame.draw.circle(surface, CONFUSION_COLOR, (x + TILE // 2, y + TILE // 2), int(TILE // 2.5))  # Increased size
    # Improved: swirl pattern
    pygame.draw.arc(surface, WHITE, (x + int(TILE // 3), y + int(TILE // 3), int(TILE // 1.5), int(TILE // 1.5)), 0, math.pi * 1.5, 3)
    pygame.draw.arc(surface, WHITE, (x + int(TILE // 2.5), y + int(TILE // 2.5), int(TILE // 2.5), int(TILE // 2.5)), math.pi, math.pi * 2.5, 3)
    # Question mark approximation
    pygame.draw.line(surface, WHITE, (x + int(TILE // 2), y + int(TILE // 2.5)), (x + int(TILE // 2), y + int(TILE // 1.8)), 2)
    pygame.draw.line(surface, WHITE, (x + int(TILE // 2), y + int(TILE // 1.8)), (x + int(2 * TILE // 3), y + int(TILE // 1.8)), 2)
    pygame.draw.line(surface, WHITE, (x + int(2 * TILE // 3), y + int(TILE // 1.8)), (x + int(TILE // 2), y + int(2 * TILE // 3)), 2)
    pygame.draw.circle(surface, WHITE, (x + int(TILE // 2), y + int(3 * TILE // 4)), 2)

def draw_freeze(surface, x, y):
    pygame.draw.circle(surface, FREEZE_COLOR, (x + TILE // 2, y + TILE // 2), int(TILE // 2.5))  # Increased size
    # Improved: snowflake with more points
    points = []
    for i in range(6):
        angle = i * math.pi / 3
        px = x + TILE // 2 + math.cos(angle) * (int(TILE // 2.5))
        py = y + TILE // 2 + math.sin(angle) * (int(TILE // 2.5))
        points.append((px, py))
        mx = x + TILE // 2 + math.cos(angle) * (int(TILE // 5))
        my = y + TILE // 2 + math.sin(angle) * (int(TILE // 5))
        pygame.draw.line(surface, WHITE, (mx, my), (px, py), 2)
    pygame.draw.polygon(surface, WHITE, points, 1)

# =========================
# Entities
# =========================
class Chick:
    def __init__(self):
        self.x, self.y = TILE, TILE
        self.slow_timer = 0
        self.direction = "DOWN"
        self.speed = 3
        self.walk_timer = 0
        self.invincible = 0
        self.lives = 3
        self.target_x, self.target_y = self.x, self.y
        self.moving = False
        self.size_multiplier = 1.5
        self.hit_animation = 0
        self.speed_boost = 0
        self.confused = 0

    def move(self, keys, walls, hazards):
        if self.slow_timer > 0:
            self.slow_timer -= 1
        if self.speed_boost > 0:
            self.speed_boost -= 1
        if self.confused > 0:
            self.confused -= 1
        target_set = False
        if not self.moving:
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                self.target_x = max(0, self.x - TILE)
                self.target_y = self.y
                self.direction = "LEFT" if self.confused == 0 else "RIGHT"
                target_set = True
            elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.target_x = min(WIDTH - TILE, self.x + TILE)
                self.target_y = self.y
                self.direction = "RIGHT" if self.confused == 0 else "LEFT"
                target_set = True
            elif (keys[pygame.K_UP] or keys[pygame.K_w]):
                self.target_x = self.x
                self.target_y = max(0, self.y - TILE)
                self.direction = "UP" if self.confused == 0 else "DOWN"
                target_set = True
            elif (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                self.target_x = self.x
                self.target_y = min(HEIGHT - TILE, self.y + TILE)
                self.direction = "DOWN" if self.confused == 0 else "UP"
                target_set = True
        if target_set:
            target_rect = pygame.Rect(self.target_x, self.target_y, TILE, TILE)
            for wx, wy in walls:
                if target_rect.colliderect(pygame.Rect(wx * TILE, wy * TILE, TILE, TILE)):
                    self.moving = False
                    self.slow_timer = max(self.slow_timer, 6)
                    return
            for hx, hy, _ in hazards:
                if target_rect.colliderect(pygame.Rect(hx * TILE, hy * TILE, TILE, TILE)):
                    self.moving = False
                    self.slow_timer = max(self.slow_timer, 6)
                    return
            self.moving = True
        speed = self.speed * 1.5 if self.speed_boost > 0 else self.speed
        if self.moving and self.slow_timer == 0:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            if dx != 0:
                self.x += speed if dx > 0 else -speed
                if (dx > 0 and self.x >= self.target_x) or (dx < 0 and self.x <= self.target_x):
                    self.x = self.target_x
            if dy != 0:
                self.y += speed if dy > 0 else -speed
                if (dy > 0 and self.y >= self.target_y) or (dy < 0 and self.y <= self.target_y):
                    self.y = self.target_y
            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False
        self.walk_timer += 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.hit_animation > 0:
            self.hit_animation -= 1

    def draw(self):
        if self.hit_animation > 0 and self.hit_animation % 10 < 5:
            return
        pattern = [
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 2, 2, 2, 2, 1, 0, 0],
            [0, 1, 2, 2, 2, 2, 2, 2, 1, 0],
            [0, 1, 2, 2, 2, 2, 2, 2, 1, 0],
            [1, 4, 2, 2, 2, 2, 2, 4, 1, 0],  # wings
            [0, 1, 2, 2, 2, 2, 2, 1, 0, 0],
            [0, 0, 1, 2, 2, 2, 1, 3, 0, 0],
            [0, 0, 1, 2, 2, 2, 1, 3, 0, 0],
            [0, 0, 0, 1, 2, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        ]
        colors = [None, CHICK_DARK, CHICK_YELLOW, CHICK_ORANGE, CHICK_WING]
        pixel_size = int((TILE // 10) * self.size_multiplier) or 1
        for row in range(10):
            for col in range(10):
                px = pattern[row][col]
                if px > 0:
                    pygame.draw.rect(
                        WIN, colors[px],
                        (int(self.x + col * pixel_size),
                         int(self.y + row * pixel_size),
                         pixel_size, pixel_size)
                    )
        # Beak
        if self.direction == "RIGHT":
            pygame.draw.rect(WIN, CHICK_BEAK,
                             (int(self.x + 7 * pixel_size), int(self.y + 4 * pixel_size),
                              int(TILE // 5 * self.size_multiplier), pixel_size))
        elif self.direction == "LEFT":
            pygame.draw.rect(WIN, CHICK_BEAK,
                             (int(self.x + 1 * pixel_size), int(self.y + 4 * pixel_size),
                              int(TILE // 5 * self.size_multiplier), pixel_size))
        else:
            pygame.draw.rect(WIN, CHICK_BEAK,
                             (int(self.x + 4 * pixel_size), int(self.y + 7 * pixel_size),
                              int(TILE // 5 * self.size_multiplier), pixel_size))
        # Eyes
        eye_size = max(1, int(TILE // 15 * self.size_multiplier))
        if self.direction == "RIGHT":
            pygame.draw.circle(WIN, CHICK_EYE,
                               (int(self.x + 7 * pixel_size + pixel_size / 2),
                                int(self.y + 3 * pixel_size + pixel_size / 2)), eye_size)
        elif self.direction == "LEFT":
            pygame.draw.circle(WIN, CHICK_EYE,
                               (int(self.x + 3 * pixel_size + pixel_size / 2),
                                int(self.y + 3 * pixel_size + pixel_size / 2)), eye_size)
        else:
            pygame.draw.circle(WIN, CHICK_EYE,
                               (int(self.x + 3 * pixel_size + pixel_size / 2),
                                int(self.y + 3 * pixel_size + pixel_size / 2)), eye_size)
            pygame.draw.circle(WIN, CHICK_EYE,
                               (int(self.x + 6 * pixel_size + pixel_size / 2),
                                int(self.y + 3 * pixel_size + pixel_size / 2)), eye_size)
        # Draw effect indicators
        if self.speed_boost > 0:
            pygame.draw.circle(WIN, SPEED_BOOST_COLOR, (int(self.x + TILE - 5), int(self.y + 5)), 4)
        if self.confused > 0:
            pygame.draw.circle(WIN, CONFUSION_COLOR, (int(self.x + TILE - 5), int(self.y + TILE - 5)), 4)

class Snake:
    def __init__(self, level=1):
        self.body = [(WIDTH - 4 * TILE, HEIGHT - 4 * TILE)]
        self.length = 25 + level * 5  # Increased base length
        self.base_speed = 2 + level * 0.25
        self.speed = self.base_speed
        self.counter = 0
        self.path = []
        self.path_update_counter = 0
        self.target_x, self.target_y = self.body[0]
        self.moving = False
        self.direction = "LEFT"
        self.wave_offset = 0
        self.slow_timer = 0
        self.frozen = 0

    def grid(self, pos):
        return (pos[0] // TILE, pos[1] // TILE)

    def lead_goal_cell(self, player):
        px, py = player.x // TILE, player.y // TILE
        lead = 2 + min(2, max(0, abs(self.body[0][0] - player.x) // TILE + abs(self.body[0][1] - player.y) // TILE) // 6)
        dx = dy = 0
        if player.direction == "RIGHT":
            dx = 1
        if player.direction == "LEFT":
            dx = -1
        if player.direction == "DOWN":
            dy = 1
        if player.direction == "UP":
            dy = -1
        gx, gy = px + dx * lead, py + dy * lead
        return max(0, min(COLS - 1, gx)), max(0, min(ROWS - 1, gy))

    def bfs(self, start_cell, goal_cell, walls, hazards):
        if abs(start_cell[0] - goal_cell[0]) + abs(start_cell[1] - goal_cell[1]) > 16:
            dx = 1 if goal_cell[0] > start_cell[0] else -1 if goal_cell[0] < start_cell[0] else 0
            dy = 1 if goal_cell[1] > start_cell[1] else -1 if goal_cell[1] < start_cell[1] else 0
            return [(start_cell[0] + dx, start_cell[1] + dy)]
        queue = deque([start_cell])
        visited = {start_cell: None}
        blocked = set(walls) | set([(hx, hy) for hx, hy, _ in hazards])
        while queue:
            cur = queue.popleft()
            if cur == goal_cell:
                break
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nxt = (cur[0] + dx, cur[1] + dy)
                if 0 <= nxt[0] < COLS and 0 <= nxt[1] < ROWS:
                    if nxt not in visited and nxt not in blocked:
                        visited[nxt] = cur
                        queue.append(nxt)
        path = []
        cur = goal_cell
        while cur in visited and visited[cur] is not None:
            path.append(cur)
            cur = visited[cur]
        return path[::-1]

    def update(self, player, walls, hazards, level, score):
        if self.frozen > 0:
            self.frozen -= 1
            return
        self.counter += 1
        self.path_update_counter += 1
        self.wave_offset += 0.1
        self.base_speed = 2 + level * 0.25 + score * 0.05
        if self.slow_timer > 0:
            self.slow_timer -= 1
            self.speed = max(1.2, self.base_speed * 0.6)
        else:
            self.speed = self.base_speed
        head_cell = self.grid(self.body[0])
        if self.path_update_counter >= 10:
            if random.random() < 0.35:
                goal = self.lead_goal_cell(player)
            else:
                goal = (player.x // TILE, player.y // TILE)
            self.path = self.bfs(head_cell, goal, walls, hazards)
            self.path_update_counter = 0
        if self.path and not self.moving:
            nx, ny = self.path[0]
            self.target_x, self.target_y = nx * TILE, ny * TILE
            self.moving = True
            head_x, head_y = self.body[0]
            if self.target_x > head_x:
                self.direction = "RIGHT"
            elif self.target_x < head_x:
                self.direction = "LEFT"
            elif self.target_y > head_y:
                self.direction = "DOWN"
            elif self.target_y < head_y:
                self.direction = "UP"
        if self.moving:
            head_x, head_y = self.body[0]
            dx = self.target_x - head_x
            dy = self.target_y - head_y
            move_x = min(self.speed, abs(dx)) * (1 if dx > 0 else -1) if dx != 0 else 0
            move_y = min(self.speed, abs(dy)) * (1 if dy > 0 else -1) if dy != 0 else 0
            new_head = (head_x + move_x, head_y + move_y)
            self.body.insert(0, new_head)
            if abs(new_head[0] - self.target_x) < self.speed and abs(new_head[1] - self.target_y) < self.speed:
                self.body[0] = (self.target_x, self.target_y)
                self.moving = False
                if self.path:
                    self.path.pop(0)
            while len(self.body) > self.length:
                self.body.pop()

    def draw(self):
        for i, (seg_x, seg_y) in enumerate(self.body):
            is_head = (i == 0)
            if is_head:
                color = SNAKE_HEAD
                size = TILE // 2 - 1
            else:
                factor = 1.0 - (i / len(self.body)) * 0.5
                color = (
                    int(SNAKE_BODY[0] * factor),
                    int(SNAKE_BODY[1] * factor),
                    int(SNAKE_BODY[2] * factor)
                )
                size = TILE // 2 - 2
            wave = math.sin(self.wave_offset + i * 0.3) * 2 if i > 0 else 0
            offset_x = wave if self.direction in ["UP", "DOWN"] else 0
            offset_y = wave if self.direction in ["LEFT", "RIGHT"] else 0
            pygame.draw.circle(WIN, color,
                               (int(seg_x) + TILE // 2 + int(offset_x),
                                int(seg_y) + TILE // 2 + int(offset_y)),
                               size)
            if is_head:
                eye = 3
                if self.direction == "RIGHT":
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + TILE - 6, int(seg_y) + 6), eye)
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + TILE - 6, int(seg_y) + TILE - 6), eye)
                elif self.direction == "LEFT":
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + 6, int(seg_y) + 6), eye)
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + 6, int(seg_y) + TILE - 6), eye)
                elif self.direction == "DOWN":
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + 6, int(seg_y) + TILE - 6), eye)
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + TILE - 6, int(seg_y) + TILE - 6), eye)
                else:
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + 6, int(seg_y) + 6), eye)
                    pygame.draw.circle(WIN, BLACK, (int(seg_x) + TILE - 6, int(seg_y) + 6), eye)
            if not is_head and i % 2 == 0:
                pattern_size = size // 2
                pygame.draw.circle(WIN, SNAKE_SPOT,
                                   (int(seg_x) + TILE // 2 + int(offset_x),
                                    int(seg_y) + TILE // 2 + int(offset_y)),
                                   pattern_size)
        # Draw freeze effect if snake is frozen
        if self.frozen > 0:
            for i, (seg_x, seg_y) in enumerate(self.body):
                if i % 3 == 0:  # Draw ice crystals on some segments
                    pygame.draw.circle(WIN, FREEZE_COLOR,
                                       (int(seg_x) + TILE // 2, int(seg_y) + TILE // 2), 3)
        if self.slow_timer > 0:
            pygame.draw.circle(WIN, CONFUSION_COLOR, (int(self.body[0][0] + TILE - 5), int(self.body[0][1] + TILE - 5)), 4)

# =========================
# Game helpers
# =========================
def random_pos(walls, hazards):
    blocked = set(walls) | set([(hx, hy) for hx, hy, _ in hazards])
    while True:
        gx, gy = random.randrange(COLS), random.randrange(ROWS)
        if (gx, gy) not in blocked and (gx, gy) != (1, 1) and not (gx >= COLS - 3 and gy <= 3):
            return gx * TILE, gy * TILE

def draw_progress_bar(surface, x, y, w, h, value, max_value):
    pct = 0 if max_value <= 0 else max(0, min(1, value / max_value))
    # BG
    pygame.draw.rect(surface, (0, 0, 0, 150), (x, y, w, h))
    # Fill
    inner = pygame.Surface((int(w * pct), h), pygame.SRCALPHA)
    inner.fill((255, 255, 255, 200))
    surface.blit(inner, (x, y))
    # Border
    pygame.draw.rect(surface, WHITE, (x, y, w, h), 2)

def title_screen():
    blink = 0
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        WIN.blit(background, (0, 0))
        draw_text_center(WIN, "Snake Chase - Chick Adventure", FONT_BIG, WIDTH // 2, HEIGHT // 3, YELLOW)
        draw_text_center(WIN, "Use Arrow Keys / WASD to move", FONT_SM, WIDTH // 2, HEIGHT // 2 - 10, WHITE)
        if (blink // 30) % 2 == 0:
            draw_text_center(WIN, "Press SPACE to Start", FONT_MED, WIDTH // 2, HEIGHT // 2 + 40, PINK)
        draw_text(WIN, "Power-ups: Berry(+1), Mushroom(slow snake), Golden Egg(+1 life)", FONT_SM, 20, HEIGHT - 60, WHITE)
        draw_text(WIN, "Speed Boost (Blue): Faster movement | Invincibility (Gold): No damage", FONT_SM, 20, HEIGHT - 30, WHITE)
        pygame.display.flip()
        blink += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

# =========================
# Main game
# =========================
def main():
    global SESSION_BEST_LEVEL, buff_notification, buff_notification_timer
    clock = pygame.time.Clock()
    run = True
    game_over = False
    level, score = 1, 0
    target_score = 3
    score_flash_timer = 0
    paused = False
    chick = Chick()
    snake = Snake(level)
    walls = set()
    hazards = []
    # Particles
    particles = []
    hit_particles = []
    portal_particles = []
    # Level flags
    escape = None
    level_complete = False
    level_complete_timer = 0
    t0 = pygame.time.get_ticks()
    # Timed items (appear for limited time)
    timed_items = []
    timed_item_types = []
    timed_item_timers = []
    next_timed_item = 120  # frames until next timed item appears
    player_name = ""
    input_active = False  # Tracks if player is typing their name
    input_prompt = False  # Tracks if we need to prompt for name
    score_row_id = None   # <--- ID of the saved score row


    def generate_level():
        nonlocal walls, hazards
        walls = set()
        hazards = []
        num_walls = min(40, 15 + level * 3)
        while len(walls) < num_walls:
            w = (random.randrange(COLS), random.randrange(ROWS))
            if w != (1, 1) and not (w[0] >= COLS - 3 and w[1] <= 3):
                walls.add(w)
        num_hazards = min(8, 2 + level // 2)
        for _ in range(num_hazards):
            hx, hy = random.randrange(COLS), random.randrange(ROWS)
            if (hx, hy) != (1, 1) and (hx, hy) not in walls and not (hx >= COLS - 3 and hy <= 3):
                htype = random.choice(["water", "lava"])
                hazards.append((hx, hy, htype))

    def spawn_items():
        items, item_types = [], []
        num_items = 5 + level
        for _ in range(num_items):
            pos = random_pos(walls, hazards)
            items.append(pos)
            r = random.random()
            if r < 0.65:
                item_types.append("berry")
            elif r < 0.9:
                item_types.append("mushroom")
            else:
                item_types.append("golden_egg")
        return items, item_types

    def apply_item_effect(item_type):
        nonlocal score, score_flash_timer
        if item_type == "berry":
            score += 1
            score_flash_timer = 20
            buff_notification = "Berry: +1 Score"
            buff_notification_timer = 120
        elif item_type == "mushroom":
            score += 1
            snake.slow_timer = max(snake.slow_timer, 120)
            score_flash_timer = 20
            buff_notification = "Mushroom: Snake Slowed"
            buff_notification_timer = 120
        elif item_type == "golden_egg":
            chick.lives = min(3, chick.lives + 1)
            score_flash_timer = 20
            buff_notification = "Golden Egg: +1 Life"
            buff_notification_timer = 120
        elif item_type == "speed_boost":
            chick.speed_boost = 180
            buff_notification = "Speed Boost: Faster Movement"
            buff_notification_timer = 120
        elif item_type == "invincibility":
            chick.invincible = 300
            buff_notification = "Invincibility: No Damage"
            buff_notification_timer = 120
        elif item_type == "confusion":
            snake.slow_timer = max(snake.slow_timer, 120)
            chick.confused = 120
            buff_notification = "Confusion: Reversed Controls"
            buff_notification_timer = 120
        elif item_type == "freeze":
            snake.frozen = 180
            buff_notification = "Freeze: Snake Stopped"
            buff_notification_timer = 120

    # Init first level
    generate_level()
    items, item_types = spawn_items()
    # Title screen
    title_screen()
    while run:
        clock.tick(60)
        now = pygame.time.get_ticks()
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if game_over and event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN and player_name.strip():
                        # Save score when Enter is pressed
                        if score_row_id is not None:
                            update_player_name(score_row_id, player_name)
                        else:
                            score_row_id = save_score(player_name, score)
                        input_active = False
                        input_prompt = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.unicode.isprintable() and len(player_name) < 20:
                        player_name += event.unicode
                elif event.key == pygame.K_r:
                    # Restart
                    game_over = False
                    level, score = 1, 0
                    target_score = 3
                    chick = Chick()
                    snake = Snake(level)
                    generate_level()
                    items, item_types = spawn_items()
                    escape = None
                    particles.clear()
                    hit_particles.clear()
                    portal_particles.clear()
                    level_complete = False
                    t0 = pygame.time.get_ticks()
                    buff_notification = None
                    buff_notification_timer = 0
                    player_name = ""
                    input_active = False
                    input_prompt = False
                    score_row_id = None
                elif event.key == pygame.K_q:
                    run = False
                elif event.key == pygame.K_s and not input_prompt:
                    # Trigger name input on 'S' key
                    input_active = True
                    input_prompt = True
                elif event.key == pygame.K_l:
                    # Show leaderboard
                    leaderboard = show_leaderboard()
                    # Display leaderboard (temporary, will render until another key is pressed)
                    while True:
                        WIN.blit(background, (0, 0))
                        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        s.fill((0, 0, 0, 180))
                        WIN.blit(s, (0, 0))
                        draw_text_center(WIN, "Leaderboard", FONT_BIG, WIDTH // 2, HEIGHT // 2 - 100, YELLOW)
                        for i, (name, score) in enumerate(leaderboard):
                            draw_text(WIN, f"{i+1}. {name}: {score}", FONT_SM, WIDTH // 2 - 100, HEIGHT // 2 - 40 + i * 30, WHITE)
                        draw_text_center(WIN, "Press any key to return", FONT_SM, WIDTH // 2, HEIGHT // 2 + 150, PINK)
                        pygame.display.flip()
                        for lb_event in pygame.event.get():
                            if lb_event.type == pygame.QUIT:
                                pygame.quit()
                                raise SystemExit
                            if lb_event.type == pygame.KEYDOWN:
                                break
                        else:
                            continue
                        break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if paused and event.key == pygame.K_c:
                    paused = False
        # Update
        if not game_over and not level_complete and not paused:
            keys = pygame.key.get_pressed()
            chick.move(keys, walls, hazards)
            snake.update(chick, walls, hazards, level, score)
            next_timed_item -= 1
            if next_timed_item <= 0 and len(timed_items) < 2:
                pos = random_pos(walls, hazards)
                timed_items.append(pos)
                item_choice = random.choice(["speed_boost", "invincibility", "confusion", "freeze"])
                timed_item_types.append(item_choice)
                timed_item_timers.append(300)
                next_timed_item = random.randint(180, 360)
            for i in range(len(timed_item_timers) - 1, -1, -1):
                timed_item_timers[i] -= 1
                if timed_item_timers[i] <= 0:
                    timed_items.pop(i)
                    timed_item_types.pop(i)
                    timed_item_timers.pop(i)
            chick_rect = pygame.Rect(chick.x, chick.y, TILE, TILE)
            for hx, hy, htype in hazards:
                hazard_rect = pygame.Rect(hx * TILE, hy * TILE, TILE, TILE)
                if chick_rect.colliderect(hazard_rect) and chick.invincible == 0:
                    if htype == "lava":
                        chick.lives -= 1
                        chick.invincible = 120
                        chick.hit_animation = 30
                        for _ in range(18):
                            hit_particles.append({
                                'x': chick.x + TILE // 2,
                                'y': chick.y + TILE // 2,
                                'dx': random.uniform(-3, 3),
                                'dy': random.uniform(-3, 3),
                                'color': (255, 120, 80),
                                'size': random.randint(2, 5),
                                'life': 28
                            })
                        if chick.lives <= 0:
                            game_over = True
                            # Auto-save with default name if not already prompted
                            if not input_prompt and score_row_id is None:
                                score_row_id = save_score("Player", score)
                    else:
                        chick.slow_timer = max(chick.slow_timer, 30)
                        buff_notification = "Water: Slowed Movement"
                        buff_notification_timer = 120
            if chick.moving and random.random() < 0.22:
                particles.append({
                    'x': chick.x + TILE // 2,
                    'y': chick.y + TILE // 2,
                    'dx': random.uniform(-1.2, 1.2),
                    'dy': random.uniform(-1.2, 1.2),
                    'color': (220, 220, 220),
                    'size': random.randint(1, 3),
                    'life': 20
                })
            for i, item in list(enumerate(items)):
                ix, iy = item
                if chick.x < ix + TILE and chick.x + TILE > ix and chick.y < iy + TILE and chick.y + TILE > iy:
                    itype = item_types[i]
                    apply_item_effect(itype)
                    for _ in range(12):
                        particles.append({
                            'x': ix + TILE // 2,
                            'y': iy + TILE // 2,
                            'dx': random.uniform(-2, 2),
                            'dy': random.uniform(-2, 2),
                            'color': GOLDEN_EGG if itype == "golden_egg" else (BERRY_COLOR if itype == "berry" else MUSHROOM_COLOR),
                            'size': random.randint(2, 4),
                            'life': 30
                        })
                    items.pop(i)
                    item_types.pop(i)
            for i, item in list(enumerate(timed_items)):
                ix, iy = item
                if chick.x < ix + TILE and chick.x + TILE > ix and chick.y < iy + TILE and chick.y + TILE > iy:
                    itype = timed_item_types[i]
                    apply_item_effect(itype)
                    for _ in range(15):
                        particles.append({
                            'x': ix + TILE // 2,
                            'y': iy + TILE // 2,
                            'dx': random.uniform(-2, 2),
                            'dy': random.uniform(-2, 2),
                            'color': SPEED_BOOST_COLOR if itype == "speed_boost" else
                                     INVINCIBILITY_COLOR if itype == "invincibility" else
                                     CONFUSION_COLOR if itype == "confusion" else FREEZE_COLOR,
                            'size': random.randint(2, 5),
                            'life': 35
                        })
                    timed_items.pop(i)
                    timed_item_types.pop(i)
                    timed_item_timers.pop(i)
            if score >= target_score and escape is None:
                escape = random_pos(walls, hazards)
            if escape:
                ex, ey = escape
                if chick.x < ex + TILE and chick.x + TILE > ex and chick.y < ey + TILE and chick.y + TILE > ey:
                    level_complete = True
                    level_complete_timer = 60
                    SESSION_BEST_LEVEL = max(SESSION_BEST_LEVEL, level)
                if random.random() < 0.25:
                    portal_particles.append({
                        'x': ex + TILE // 2,
                        'y': ey + TILE // 2,
                        'dx': random.uniform(-0.8, 0.8),
                        'dy': random.uniform(-0.8, 0.8),
                        'color': (200, 170, 255),
                        'size': random.randint(1, 3),
                        'life': 30
                    })
            snake.length = 25 + level * 5 + score * 2
            head_x, head_y = snake.body[0]
            if chick.x < head_x + TILE and chick.x + TILE > head_x and chick.y < head_y + TILE and chick.y + TILE > head_y:
                if chick.invincible == 0:
                    chick.lives -= 1
                    chick.invincible = 120
                    chick.hit_animation = 30
                    for _ in range(15):
                        hit_particles.append({
                            'x': chick.x + TILE // 2,
                            'y': chick.y + TILE // 2,
                            'dx': random.uniform(-3, 3),
                            'dy': random.uniform(-3, 3),
                            'color': (255, 100, 100),
                            'size': random.randint(2, 5),
                            'life': 30
                        })
                    buff_notification = "Snake Hit: -1 Life"
                    buff_notification_timer = 120
                    if chick.lives <= 0:
                        game_over = True
                        # Auto-save with default name if not already prompted
                        if not input_prompt and score_row_id is None:
                            score_row_id = save_score("Player", score)
        # Update particles
        for arr in (particles, hit_particles, portal_particles):
            for p in arr[:]:
                p['life'] -= 1
                if p['life'] <= 0:
                    arr.remove(p)
                else:
                    p['x'] += p.get('dx', 0)
                    p['y'] += p.get('dy', 0)
                    if arr is hit_particles:
                        p['dy'] = p.get('dy', 0) + 0.08
        if score_flash_timer > 0:
            score_flash_timer -= 1
        if buff_notification_timer > 0:
            buff_notification_timer -= 1
        # Draw
        WIN.blit(background, (0, 0))
        for hx, hy, htype in hazards:
            if htype == "water":
                draw_water(WIN, hx * TILE, hy * TILE)
            else:
                draw_lava(WIN, hx * TILE, hy * TILE)
        for wx, wy in walls:
            draw_rock(WIN, wx * TILE, wy * TILE)
        for i, (ix, iy) in enumerate(items):
            it = item_types[i]
            if it == "berry":
                draw_berry(WIN, ix, iy)
            elif it == "mushroom":
                draw_mushroom(WIN, ix, iy)
            else:
                draw_golden_egg(WIN, ix, iy)
        for i, (ix, iy) in enumerate(timed_items):
            it = timed_item_types[i]
            if it == "speed_boost":
                draw_speed_boost(WIN, ix, iy)
            elif it == "invincibility":
                draw_invincibility(WIN, ix, iy)
            elif it == "confusion":
                draw_confusion(WIN, ix, iy)
            elif it == "freeze":
                draw_freeze(WIN, ix, iy)
        if escape:
            draw_portal(WIN, escape[0], escape[1], now)
            for p in portal_particles:
                pygame.draw.circle(WIN, p['color'], (int(p['x']), int(p['y'])), p['size'])
        snake.draw()
        chick.draw()
        for p in particles:
            pygame.draw.circle(WIN, p['color'], (int(p['x']), int(p['y'])), p['size'])
        for p in hit_particles:
            pygame.draw.circle(WIN, p['color'], (int(p['x']), int(p['y'])), p['size'])
        ui_bg = pygame.Surface((WIDTH, 90), pygame.SRCALPHA)
        ui_bg.fill((0, 0, 0, 140))
        WIN.blit(ui_bg, (0, HEIGHT - 90))
        draw_text(WIN, f"Level {level}", FONT_SM, 15, HEIGHT - 80, WHITE)
        draw_progress_bar(WIN, 150, HEIGHT - 70, 300, 16, score, target_score)
        draw_text(WIN, f"{score}/{target_score}", FONT_SM, 460, HEIGHT - 80,
                  WHITE if score_flash_timer == 0 else (255, 255, 120))
        draw_text(WIN, f"Snake Len: {snake.length}", FONT_SM, WIDTH - 210, HEIGHT - 80, WHITE)
        draw_text(WIN, f"Best: {SESSION_BEST_LEVEL}", FONT_SM, WIDTH - 210, HEIGHT - 50, (200, 255, 200))
        draw_hearts(WIN, 15, HEIGHT - 50, chick.lives)
        draw_text_center(WIN, "Snake Chase - Chick Adventure", FONT_SM, WIDTH // 2, 12, WHITE)
        buff_y = 40
        buff_spacing = 30
        if chick.speed_boost > 0:
            draw_speed_boost(WIN, WIDTH - 30, buff_y)
            draw_text(WIN, f"Speed: {chick.speed_boost // 60 + 1}s", FONT_XS, WIDTH - 80, buff_y + 5, SPEED_BOOST_COLOR)
            buff_y += buff_spacing
        if chick.invincible > 0:
            draw_invincibility(WIN, WIDTH - 30, buff_y)
            draw_text(WIN, f"Invinc: {chick.invincible // 60 + 1}s", FONT_XS, WIDTH - 80, buff_y + 5, INVINCIBILITY_COLOR)
            buff_y += buff_spacing
        if chick.confused > 0:
            draw_confusion(WIN, WIDTH - 30, buff_y)
            draw_text(WIN, f"Conf: {chick.confused // 60 + 1}s", FONT_XS, WIDTH - 80, buff_y + 5, CONFUSION_COLOR)
            buff_y += buff_spacing
        if snake.frozen > 0:
            draw_freeze(WIN, WIDTH - 30, buff_y)
            draw_text(WIN, f"Freeze: {snake.frozen // 60 + 1}s", FONT_XS, WIDTH - 80, buff_y + 5, FREEZE_COLOR)
            buff_y += buff_spacing
        if snake.slow_timer > 0:
            draw_confusion(WIN, WIDTH - 30, buff_y)
            draw_text(WIN, f"Slow: {snake.slow_timer // 60 + 1}s", FONT_XS, WIDTH - 80, buff_y + 5, CONFUSION_COLOR)
            buff_y += buff_spacing
        if buff_notification and buff_notification_timer > 0:
            s = pygame.Surface((300, 40), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            WIN.blit(s, (WIDTH // 2 - 150, HEIGHT // 2 - 20))
            draw_text_center(WIN, buff_notification, FONT_SM, WIDTH // 2, HEIGHT // 2, WHITE)
        if paused:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 120))
            WIN.blit(s, (0, 0))
            draw_text_center(WIN, "PAUSED", FONT_BIG, WIDTH // 2, HEIGHT // 2 - 40, YELLOW)
            draw_text_center(WIN, "Press C to Continue", FONT_MED, WIDTH // 2, HEIGHT // 2 + 20, WHITE)
            draw_text_center(WIN, "Press P to Pause/Unpause", FONT_SM, WIDTH // 2, HEIGHT // 2 + 60, PINK)
        if game_over:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            WIN.blit(s, (0, 0))
            draw_text_center(WIN, "GAME OVER", FONT_BIG, WIDTH // 2, HEIGHT // 2 - 100, (255, 120, 120))
            draw_text_center(WIN, f"Final Level: {level}", FONT_MED, WIDTH // 2, HEIGHT // 2 - 40, WHITE)
            draw_text_center(WIN, f"Final Score: {score}", FONT_MED, WIDTH // 2, HEIGHT // 2, WHITE)
            draw_text_center(WIN, f"Best Level (Session): {SESSION_BEST_LEVEL}", FONT_SM, WIDTH // 2, HEIGHT // 2 + 40, (200, 255, 200))
            if input_prompt:
                draw_text_center(WIN, "Enter Name and Press ENTER to Save Score", FONT_SM, WIDTH // 2, HEIGHT // 2 + 80, PINK)
                input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 110, 200, 30)
                pygame.draw.rect(WIN, WHITE, input_box, 2)
                draw_text_center(WIN, player_name + ("|" if input_active and (pygame.time.get_ticks() // 500 % 2) else ""),
                                 FONT_SM, WIDTH // 2, HEIGHT // 2 + 125, WHITE)
            else:
                draw_text_center(WIN, "Press S to Save Score | R to Restart | Q to Quit | L for Leaderboard", FONT_SM, WIDTH // 2, HEIGHT // 2 + 80, PINK)
        elif level_complete:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 120))
            WIN.blit(s, (0, 0))
            draw_text_center(WIN, f"LEVEL {level} COMPLETE!", FONT_BIG, WIDTH // 2, HEIGHT // 2 - 40, YELLOW)
            draw_text_center(WIN, f"Starting Level {level + 1}", FONT_MED, WIDTH // 2, HEIGHT // 2 + 10, WHITE)
        pygame.display.flip()
        if level_complete:
            level_complete_timer -= 1
            if level_complete_timer <= 0:
                level += 1
                target_score = 3 + level
                
                chick = Chick()
                snake = Snake(level)
                generate_level()
                items, item_types = spawn_items()
                escape = None
                particles.clear()
                hit_particles.clear()
                portal_particles.clear()
                timed_items.clear()
                timed_item_types.clear()
                timed_item_timers.clear()
                level_complete = False
                t0 = pygame.time.get_ticks()
                buff_notification = None
                buff_notification_timer = 0

# Database functions
conn = sqlite3.connect("game_scores.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL
    )
""")
conn.commit()
conn.close()

def save_score(player_name, score):
    conn = sqlite3.connect("game_scores.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leaderboard (player_name, score) VALUES (?, ?)", (player_name, score))
    row_id = cursor.lastrowid  # <--- get ID of this row
    conn.commit()
    conn.close()
    return row_id  # <--- return it


def show_leaderboard():
    conn = sqlite3.connect("game_scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, score FROM leaderboard ORDER BY score DESC LIMIT 5")
    results = cursor.fetchall()
    conn.close()
    return results


def update_player_name(row_id, player_name):
    conn = sqlite3.connect("game_scores.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE leaderboard SET player_name = ? WHERE id = ?", (player_name, row_id))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()