import cv2
import time
import mediapipe as mp
import pygame
import random
import sys

# MediaPipe Tasks imports
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Open camera, change index based on cam num and position
capture = cv2.VideoCapture(0)

#game init 
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
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init() # Need to init

pygame.mixer.init() # Initialize the mixer, and all of the sound variables
pygame.mixer.music.load("Menu song.mp3") # Load music file
pygame.mixer.music.set_volume(1) # Volume 100%
pygame.mixer.music.play(-1) # Loop Forever

# Sound Variables

game_death = pygame.mixer.Sound("Shoebill Stork Sound.wav")
jump_sound = pygame.mixer.Sound("Quack.wav")

# Block cycle for the menu

start_button_xLeft = 50
start_button_xRight = 250
start_button_yBottom = 25
start_button_yTop = 200

exit_button_xLeft = 300
exit_button_xRight = 500
exit_button_yBottom = 25
exit_button_yTop = 200

exit_menu = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(WHITE)

button_font = pygame.font.SysFont('Comic Sans MS', 30) # Font type and size
title_font= pygame.font.SysFont('Comic Sans MS', 30)
credits_font = pygame.font.SysFont('Comic Sans MS', 20)
intern = pygame.font.SysFont('Comic Sans MS', 10)

start_button = button_font.render('Start Game', True, BLACK) # True is for anti-aliasing lmao
exit_button = button_font.render('Exit', True, BLACK)

credits_line_title = title_font.render('SUPER DUCKY RUN', True, BLACK)
credits_line0 = credits_font.render('----CREDITS-----', True, BLACK)
credits_line1 = credits_font.render('Nicholas Horner', True, BLACK)
credits_line2 = credits_font.render('Zac Calvert', True, BLACK)
credits_line3 = credits_font.render('Sam Palatnikov', True, BLACK)
credits_line4 = credits_font.render('Kaitlyn Dunphy', True, BLACK)
credits_line5 = intern.render('+ Intern', True, BLACK)


screen.blit(credits_line_title, (550, 25)) # Hardcoded positions (x,y) for the title and credits text
screen.blit(credits_line0, (600, 100))
screen.blit(credits_line1, (600, 125))
screen.blit(credits_line2, (600, 150))
screen.blit(credits_line3, (600, 175))
screen.blit(credits_line4, (600, 200))
screen.blit(credits_line5, (600, 225))


while exit_menu == 0:
    mouse_x, mouse_y = pygame.mouse.get_pos() # Get the mouse position for press

    for event in pygame.event.get(): # Literally a function to stop this damn window
        if event.type == pygame.QUIT:
            exit()

    pygame.draw.rect(screen, RED, (exit_button_xLeft, exit_button_yBottom, exit_button_xRight - exit_button_xLeft, exit_button_yTop - exit_button_yBottom)) # Draw exit and start buttons
    pygame.draw.rect(screen, GREEN, (start_button_xLeft, start_button_yBottom, start_button_xRight - start_button_xLeft, start_button_yTop - start_button_yBottom))

    if (start_button_xLeft < mouse_x < start_button_xRight) and (start_button_yBottom < mouse_y < start_button_yTop): # Highlight hovering check for mouse position
        pygame.draw.rect(screen, (0, 150, 0), (start_button_xLeft, start_button_yBottom, start_button_xRight - start_button_xLeft, start_button_yTop - start_button_yBottom)) # Higlight the start button
        if pygame.mouse.get_pressed(3)[0] == True: # get_pressed needs either 3 or 5 buttons, [0] targets the left click 
            print("Start Game")
            exit_menu = 1

    if (exit_button_xLeft < mouse_x < exit_button_xRight) and (exit_button_yBottom < mouse_y < exit_button_yTop):
        pygame.draw.rect(screen, (150, 0, 0), (exit_button_xLeft, exit_button_yBottom, exit_button_xRight - exit_button_xLeft, exit_button_yTop - exit_button_yBottom))
        if pygame.mouse.get_pressed(3)[0] == True:
            print("Exit")
            exit()

    screen.blit(start_button, (start_button_xLeft + 20, start_button_yBottom + 65)) # Button text output
    screen.blit(exit_button, (exit_button_xLeft + 70, exit_button_yBottom + 65))

    pygame.display.update() # Update display


# Continue if not exited

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Clone")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 34)

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
    DINO_SCALE = 0.85

run_raw  = pygame.image.load(RUN_PATH).convert_alpha()
duck_raw = pygame.image.load(DUCK_PATH).convert_alpha()

run_img  = scale_img(run_raw,  DINO_SCALE)
duck_img = scale_img(duck_raw, DINO_SCALE)

RUN_W, RUN_H = run_img.get_width(), run_img.get_height()
DUCK_W, DUCK_H = duck_img.get_width(), duck_img.get_height()

# Feet offsets (fixes floating)
RUN_FEET_OFFSET  = compute_feet_offset(run_img)
DUCK_FEET_OFFSET = compute_feet_offset(duck_img)

# Player hitbox padding
RUN_PAD_X = 10
RUN_PAD_TOP = 6
RUN_PAD_BOTTOM = 6

DUCK_PAD_X = 12
DUCK_PAD_TOP = 6
DUCK_PAD_BOTTOM = 4


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

# Load face landmark model
base_options = python.BaseOptions(
    model_asset_path="face_landmarker.task"  # face_landmarker.task is in the same directory, literally an image used to build
) # Model from: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker#models

# Update the options for the face landmarker, use base options, don't bother with blend and transformations
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1 # Only 1 face 
)

landmarker = vision.FaceLandmarker.create_from_options(options) # Marker variable for face mapping

if not capture.isOpened(): # Safety check
    print("Could not open camera.")
    exit()

last_time = time.time() # Get the time of the computer, for running a while loop while counting
current_time = last_time

print("Normalizing human in 10 seconds!")

pygame.mixer.stop() #Stop the menu music
pygame.mixer.music.load("Proper Duckie Song.mp3") # Load music file for bird song
pygame.mixer.music.set_volume(1) # Volume 100%
pygame.mixer.music.play(-1) # Loop Forever

while (current_time - last_time) < 10: # Time is needed for person to adjust 

    current_time = time.time() # Update time

    ret, frame = capture.read() # Get a picture from camera
    if not ret:
        print("Failed to capture frame.")
        exit()

    frame = cv2.resize(frame, (800, 600)) # Sizing
    
    seconds_left = int(10 - (current_time - last_time)) # Update the time

    cv2.putText(frame, "Seconds Left: " + str(seconds_left), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 5) # Put time on display

    # Create an rgb frame from the bgr picture
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Update the media pipe image with the data
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Facemapping is detected and put into result
    result = landmarker.detect(mp_image)

    # Draw the landmarks over the person's face
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1]) # Get the normalized x and y values for each landmark
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (255, 255, 0), -1) # Draw a circle at each landmark

    cv2.imshow("Mediapipe Feed", frame) #Outut camera feed

    if cv2.waitKey(1) & 0xFF == ord('q'): # Break early if 'q' is pressed, mask out last 8 bits for ASCII input
        break                             # waitKey for 1 millisecond


ret, frame = capture.read() # Then actually read the camera for the capture image
if not ret:
    print("Failed to capture")
    capture.release()
    cv2.destroyAllWindows()
    exit()

frame = cv2.resize(frame, (800, 600))

rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

result = landmarker.detect(mp_image)

total_yBase = 0

if result.face_landmarks: # Grab all of the face_landmarks, get their non-normalized y value, and update the base
    for face_landmarks in result.face_landmarks:
        for landmark in face_landmarks:
            total_yBase += int(landmark.y * 600)

baseline_y = int(total_yBase / len(face_landmarks)) # Get the average y value for base line, based off number of face_landmarks

if total_yBase == 0: # Safety check if human not in frame
    print("No face detected. Please try again.")
    capture.release()
    cv2.destroyAllWindows()
    exit()

# Game loop chunk

start_time = time.time()
want_duck = False

while True:

    update_time = time.time() 

    ret, frame = capture.read()
    if not ret:
        break

    frame = cv2.resize(frame, (800, 600)) # same process as image capture

    # Create an rgb frame from the bgr picture
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Update the media pipe image with the data
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Facemapping is detected and put into result
    result = landmarker.detect(mp_image)

    total_yNew = 0

    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                total_yNew += int(landmark.y * 600)
    
    ratio = total_yNew / total_yBase # Compare new overall y-position with the base
    
    # Signal timing threshold of 0.5 seconds, creates a 0.5 second delay for game input
    # ^ People's avg jump time is apparently 0.5 - 0.9 seconds

    #Gamelooping 

    clock.tick(FPS)

    want_jump = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP):
                dino, dino_state, dino_vel_y, on_ground, obstacles, spawn_timer, spawn_delay, speed, score, game_over = reset_game()


    if ratio < 0.85 and (update_time - start_time) > 0.5: # Offset of 0.15 
        # Jump signal
        want_jump = True
        print("Jump")
        jump_sound.play()
        start_time = time.time()
    elif ratio > 1.15 and (update_time - start_time) > 0.5:
        #Crouch signal
        want_duck = True
        print("Crouch")
        start_time = time.time()
    elif (update_time - start_time) > 0.5:
        want_duck = False

    # Update
    if not game_over:
        pygame.mixer.music.unpause()
        # State transitions
        if on_ground:
            if want_jump:
                dino_state = STATE_JUMP
                dino_vel_y = JUMP_VEL
                on_ground = False
            elif want_duck:
                dino_state = STATE_DUCK
            elif not want_duck:
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
        pygame.mixer.music.pause()
        game_death.play()
        show_text_center(["GAME OVER", "Press SPACE to restart"])

    pygame.display.flip()

    # print(ratio)

    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (255, 0, 255), -1)
    
    cv2.line(frame, (200, baseline_y), (600, baseline_y), (0, 255, 0), 2) # Draw a horizontal line at the y base value

    cv2.imshow("Mediapipe Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): # Input signal needed for if the player dies to break the loop
        break

capture.release()
cv2.destroyAllWindows()