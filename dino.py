# import pygame
# import random
# import sys

# # ----------------------------
# # Chrome Dino-ish clone (pygame)
# # ----------------------------

# WIDTH, HEIGHT = 900, 250
# FPS = 60

# GROUND_Y = 200              # y position of ground line
# DINO_X = 80                 # dino x position
# DINO_W, DINO_H = 40, 50     # dino size
# GRAVITY = 0.9
# JUMP_VEL = -15.5

# OBSTACLE_MIN_GAP = 260
# OBSTACLE_MAX_GAP = 520

# # Colors (Dino game vibe)
# WHITE = (255, 255, 255)
# BLACK = (20, 20, 20)
# GRAY = (120, 120, 120)

# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Dino Clone")
# clock = pygame.time.Clock()

# font = pygame.font.SysFont("consolas", 20)
# big_font = pygame.font.SysFont("consolas", 34)

# def reset_game():
#     dino = pygame.Rect(DINO_X, GROUND_Y - DINO_H, DINO_W, DINO_H)
#     dino_vel_y = 0
#     on_ground = True

#     obstacles = []
#     spawn_x = WIDTH + 200
#     speed = 7.0
#     score = 0
#     game_over = False
#     return dino, dino_vel_y, on_ground, obstacles, spawn_x, speed, score, game_over

# def spawn_obstacle(x):
#     # Classic cactus-ish rectangles: random width/height, grounded.
#     w = random.choice([18, 22, 26, 34])
#     h = random.choice([35, 45, 55, 65])
#     return pygame.Rect(x, GROUND_Y - h, w, h)

# def draw_ground():
#     # Ground line + a few little "pebbles" dashes
#     pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

# def draw_dino(dino, ducking=False):
#     # Simple "pixel" body: rectangle + little head bump
#     pygame.draw.rect(screen, BLACK, dino)
#     head = pygame.Rect(dino.x + 25, dino.y + 8, 14, 14)
#     pygame.draw.rect(screen, BLACK, head)
#     eye = pygame.Rect(dino.x + 34, dino.y + 12, 3, 3)
#     pygame.draw.rect(screen, WHITE, eye)

# def draw_obstacle(obs):
#     pygame.draw.rect(screen, BLACK, obs)

# def show_text_center(lines):
#     y = HEIGHT // 2 - 30
#     for i, line in enumerate(lines):
#         surf = big_font.render(line, True, BLACK)
#         rect = surf.get_rect(center=(WIDTH // 2, y + i * 40))
#         screen.blit(surf, rect)

# dino, dino_vel_y, on_ground, obstacles, spawn_x, speed, score, game_over = reset_game()

# while True:
#     dt = clock.tick(FPS) / 1000.0

#     # Events
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()

#         if event.type == pygame.KEYDOWN:
#             if not game_over:
#                 if event.key in (pygame.K_SPACE, pygame.K_UP):
#                     if on_ground:
#                         dino_vel_y = JUMP_VEL
#                         on_ground = False
#             else:
#                 # restart
#                 if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP):
#                     dino, dino_vel_y, on_ground, obstacles, spawn_x, speed, score, game_over = reset_game()

#     # Update
#     if not game_over:
#         # Gravity / jump physics
#         dino_vel_y += GRAVITY
#         dino.y += int(dino_vel_y)

#         if dino.bottom >= GROUND_Y:
#             dino.bottom = GROUND_Y
#             dino_vel_y = 0
#             on_ground = True

#         # Spawn obstacles
#         if len(obstacles) == 0 or obstacles[-1].x < WIDTH - random.randint(OBSTACLE_MIN_GAP, OBSTACLE_MAX_GAP):
#             obstacles.append(spawn_obstacle(WIDTH + random.randint(0, 120)))

#         # Move obstacles
#         for obs in obstacles:
#             obs.x -= int(speed)

#         # Remove offscreen
#         obstacles = [o for o in obstacles if o.right > -20]

#         # Collision
#         for obs in obstacles:
#             if dino.colliderect(obs):
#                 game_over = True
#                 break

#         # Score + speed ramp
#         score += 1
#         if score % 400 == 0:
#             speed += 0.6

#     # Draw
#     screen.fill(WHITE)
#     draw_ground()

#     # Score display like Dino
#     score_text = font.render(f"{score:06d}", True, BLACK)
#     screen.blit(score_text, (WIDTH - 120, 15))

#     # Draw dino + obstacles
#     draw_dino(dino)
#     for obs in obstacles:
#         draw_obstacle(obs)

#     if game_over:
#         show_text_center(["GAME OVER", "Press SPACE to restart"])

#     pygame.display.flip()



import pygame
import random
import sys

# ----------------------------
# Chrome Dino-ish clone (pygame) — merged version
# RUN / JUMP / DUCK + cactus + bird
# ----------------------------

WIDTH, HEIGHT = 900, 250
FPS = 60

GROUND_Y = 200          # y position of ground line
DINO_X = 80             # dino x position

# Physics
GRAVITY = 0.9
JUMP_VEL = -14

# Game tuning
START_SPEED = 7.0

# Colors (Dino game vibe)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (120, 120, 120)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Clone")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 34)

# -----------------------------
# Dino "sprite" (drawn by code)
# -----------------------------
DINO_RUN_W, DINO_RUN_H = 44, 48
DINO_DUCK_W, DINO_DUCK_H = 60, 28

STATE_RUN = "RUN"
STATE_JUMP = "JUMP"
STATE_DUCK = "DUCK"

# -----------------------------
# Obstacles
# -----------------------------
OBS_CACTUS = "CACTUS"
OBS_BIRD = "BIRD"


def draw_ground():
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)


def draw_dino(rect, state):
    """
    Draw a simple pixel-ish dinosaur inside rect.
    rect is the collision box (what matters for gameplay).
    """
    x, y, w, h = rect

    # Body block
    pygame.draw.rect(screen, BLACK, (x + 8, y + 10, w - 16, h - 18), border_radius=2)

    # Head (front)
    pygame.draw.rect(screen, BLACK, (x + w - 18, y + 6, 18, 18), border_radius=2)

    # Snout
    pygame.draw.rect(screen, BLACK, (x + w - 6, y + 12, 10, 8), border_radius=2)

    # Eye (tiny white pixel)
    pygame.draw.rect(screen, WHITE, (x + w - 14, y + 10, 3, 3))

    # Tail
    pygame.draw.rect(screen, BLACK, (x, y + 18, 10, 10), border_radius=2)

    # Legs (change a bit for duck)
    if state == STATE_DUCK:
        pygame.draw.rect(screen, BLACK, (x + 16, y + h - 8, 10, 8))
        pygame.draw.rect(screen, BLACK, (x + 34, y + h - 8, 10, 8))
    else:
        pygame.draw.rect(screen, BLACK, (x + 14, y + h - 12, 10, 12))
        pygame.draw.rect(screen, BLACK, (x + 30, y + h - 12, 10, 12))


def spawn_obstacle():
    kind = random.choices([OBS_CACTUS, OBS_BIRD], weights=[0.65, 0.35])[0]

    if kind == OBS_CACTUS:
        w = random.choice([18, 22, 28])
        h = random.choice([32, 38, 44])
        rect = pygame.Rect(WIDTH + 10, GROUND_Y - h, w, h)
        return {"kind": OBS_CACTUS, "rect": rect}
    else:
        w, h = 34, 22
        bird_y = random.choice([GROUND_Y - 80, GROUND_Y - 60])  # heights to duck under
        rect = pygame.Rect(WIDTH + 10, bird_y, w, h)
        return {"kind": OBS_BIRD, "rect": rect}


def draw_obstacle(obs):
    r = obs["rect"]
    if obs["kind"] == OBS_CACTUS:
        pygame.draw.rect(screen, BLACK, r, border_radius=2)
    else:
        # Bird: little blocky "wings"
        pygame.draw.rect(screen, BLACK, (r.x, r.y + 8, r.w, r.h - 8), border_radius=2)
        pygame.draw.rect(screen, BLACK, (r.x + 6, r.y, 10, 10), border_radius=2)
        pygame.draw.rect(screen, BLACK, (r.x + 18, r.y, 10, 10), border_radius=2)


def show_text_center(lines):
    y = HEIGHT // 2 - 30
    for i, line in enumerate(lines):
        surf = big_font.render(line, True, BLACK)
        rect = surf.get_rect(center=(WIDTH // 2, y + i * 40))
        screen.blit(surf, rect)


def reset_game():
    dino_state = STATE_RUN
    dino_vel_y = 0
    on_ground = True

    dino = pygame.Rect(DINO_X, GROUND_Y - DINO_RUN_H, DINO_RUN_W, DINO_RUN_H)

    obstacles = []
    spawn_timer = 0
    spawn_delay = 70  # base delay; effectively shrinks with speed

    speed = START_SPEED
    score = 0
    game_over = False

    return dino, dino_state, dino_vel_y, on_ground, obstacles, spawn_timer, spawn_delay, speed, score, game_over


dino, dino_state, dino_vel_y, on_ground, obstacles, spawn_timer, spawn_delay, speed, score, game_over = reset_game()

while True:
    clock.tick(FPS)

    want_jump = False
    want_duck = False

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP):
                dino, dino_state, dino_vel_y, on_ground, obstacles, spawn_timer, spawn_delay, speed, score, game_over = reset_game()

            if not game_over and event.key in (pygame.K_SPACE, pygame.K_UP):
                want_jump = True

    # Hold-to-duck
    keys = pygame.key.get_pressed()
    if not game_over and keys[pygame.K_DOWN]:
        want_duck = True

    # Update
    if not game_over:
        # State transitions
        if on_ground:
            if want_jump:
                dino_state = STATE_JUMP
                dino_vel_y = JUMP_VEL
                on_ground = False
            elif want_duck:
                dino_state = STATE_DUCK
            else:
                dino_state = STATE_RUN
        else:
            dino_state = STATE_JUMP

        # Hitbox changes (duck vs run/jump)
        if dino_state == STATE_DUCK and on_ground:
            dino.bottom = GROUND_Y
            dino.width = DINO_DUCK_W
            dino.height = DINO_DUCK_H
        else:
            dino.bottom = min(dino.bottom, GROUND_Y)
            dino.width = DINO_RUN_W
            dino.height = DINO_RUN_H

        # Gravity + jump physics
        if not on_ground:
            dino_vel_y += GRAVITY
            dino.y += int(dino_vel_y)

            if dino.bottom >= GROUND_Y:
                dino.bottom = GROUND_Y
                dino_vel_y = 0
                on_ground = True
                dino_state = STATE_DUCK if want_duck else STATE_RUN

        # Spawn obstacles (delay ramps with speed)
        spawn_timer += 1
        dynamic_delay = max(35, int(spawn_delay - (speed - START_SPEED) * 2))
        if spawn_timer >= dynamic_delay:
            spawn_timer = 0
            obstacles.append(spawn_obstacle())

        # Move obstacles
        for obs in obstacles:
            obs["rect"].x -= int(speed)

        # Remove offscreen
        obstacles = [o for o in obstacles if o["rect"].right > -40]

        # Collision
        for obs in obstacles:
            if dino.colliderect(obs["rect"]):
                game_over = True
                break

        # Score + speed ramp
        score += 1
        if score % 400 == 0:
            speed += 0.6

    # Draw
    screen.fill(WHITE)
    draw_ground()

    # Score display (old style)
    score_text = font.render(f"{score:06d}", True, BLACK)
    screen.blit(score_text, (WIDTH - 120, 15))

    # Obstacles
    for obs in obstacles:
        draw_obstacle(obs)

    # Dino
    draw_dino(dino, dino_state)

    if game_over:
        show_text_center(["GAME OVER", "Press SPACE to restart"])

    pygame.display.flip()