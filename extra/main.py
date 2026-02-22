import numpy as np
import sys
import pygame
import random

# --- setup ---
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chaos")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)

#get the stream output from the camera

#input = int(sys.stdin.read().strip())

# --- player ---
dino = pygame.Rect(80, 250, 40, 60)
velocity_y = -0
gravity = 1
jump_strength = -18
on_ground = True

# --- obstacles ---
obstacles = []
spawn_timer = 0
speed = 8

# --- score ---
score = 0

def draw_text(text, x, y):
    img = font.render(text, True, BLACK)
    screen.blit(img, (x, y))

# --- game loop ---
running = True
while running:
    
    #stream input
    #input = int(sys.stdin.read().strip())
    # if the input is 1 it jumps
    input = 4
    if input == 1 and on_ground:
        velocity_y = jump_strength
        on_ground = False
    #if the input is 2 it crouches
    if input == 2 and on_ground:
        dino.height= 30 
        dino.y = 270 + dino.height
    if input == 0:
        dino.height= 60 
        dino.y = 270 + dino.height


    clock.tick(60)
    screen.fill(WHITE)

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #jumping
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                velocity_y = jump_strength
                on_ground = False
        #crouching
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL and on_ground:
                dino.height= 30 
                dino.y = 300 + dino.height
        else:
            dino.height= 60 
        print(dino.y)
    # --- physics ---
    velocity_y += gravity
    dino.y += velocity_y

    if dino.y >= 240-dino.height    :
        dino.y = 240-dino.height
        velocity_y = -0
        on_ground = True

    # --- spawn obstacles ---
    spawn_timer += 1
    if spawn_timer > random.randint(60, 120):
        obstacles.append(pygame.Rect(WIDTH, 280, 30, 60))
        spawn_timer = 0

    # --- move obstacles ---
    for obs in obstacles[:]:
        obs.x -= speed
        if obs.right < 0:
            obstacles.remove(obs)
            score += 1

    # --- collision ---
    for obs in obstacles:
        if dino.colliderect(obs):
            print("Game Over! Score:", score)
            pygame.quit()
            sys.exit()

    # --- draw ---
    pygame.draw.rect(screen, GREEN, dino)
    for obs in obstacles:
        pygame.draw.rect(screen, BLACK, obs)

    pygame.draw.line(screen, BLACK, (0, 340), (WIDTH, 340), 2)

    draw_text(f"Score: {score}", 10, 10)

    pygame.display.update()

pygame.quit()
