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
capture = cv2.VideoCapture(1)

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





















# Window / timing
WIDTH, HEIGHT = 900, 250
FPS = 60

# World
GROUND_Y = 200
DINO_X = 80

# Physics
GRAVITY = 0.9
JUMP_VEL = -14

# Game tuning
START_SPEED = 7.0

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GROUND_COLOR = (80, 80, 80)

# States
STATE_RUN = "RUN"
STATE_JUMP = "JUMP"
STATE_DUCK = "DUCK"

# Obstacles
OBS_PAPER = "PAPER"
OBS_BIRD = "BIRD"

# ----------------------------
# Init pygame + display FIRST (required for convert_alpha)
# ----------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Clone")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 34)

# ----------------------------
# Assets
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def find_asset(stem_name: str) -> str:
    """Find stem_name(.png/.jpg/.jpeg) in assets/ case-insensitively."""
    if not os.path.isdir(ASSETS_DIR):
        raise FileNotFoundError(f"assets folder not found at: {ASSETS_DIR}")

    wanted_stem = os.path.splitext(stem_name)[0].lower()
    for f in os.listdir(ASSETS_DIR):
        stem, ext = os.path.splitext(f)
        if stem.lower() == wanted_stem and ext.lower() in (".png", ".jpg", ".jpeg"):
            return os.path.join(ASSETS_DIR, f)

    raise FileNotFoundError(
        f"Could not find '{stem_name}' in {ASSETS_DIR}. "
        f"Files: {os.listdir(ASSETS_DIR)}"
    )

BIG_BIRD_PATH = find_asset("Big bird")
DUCK_BIRD_PATH = find_asset("shoved down bird")

# Load after display init
big_bird_img_raw = pygame.image.load(BIG_BIRD_PATH).convert_alpha()
duck_bird_img_raw = pygame.image.load(DUCK_BIRD_PATH).convert_alpha()

def scale_img(img, scale):
    w = max(1, int(img.get_width() * scale))
    h = max(1, int(img.get_height() * scale))
    return pygame.transform.smoothscale(img, (w, h))

# Player "cold shrink"
DINO_SCALE = 0.85
dino_run_img = scale_img(big_bird_img_raw, DINO_SCALE)
dino_duck_img = scale_img(duck_bird_img_raw, DINO_SCALE)

RUN_W, RUN_H = dino_run_img.get_width(), dino_run_img.get_height()
DUCK_W, DUCK_H = dino_duck_img.get_width(), dino_duck_img.get_height()

# Player hitbox (smaller than sprite)
RUN_PAD_X = 10
RUN_PAD_TOP = 6
RUN_PAD_BOTTOM = 6

DUCK_PAD_X = 12
DUCK_PAD_TOP = 6
DUCK_PAD_BOTTOM = 4

def get_player_sprite_and_hitbox(x, y_top, state, on_ground):
    """Return (img, sprite_rect, hitbox_rect)."""
    using_duck = (state == STATE_DUCK and on_ground)

    if using_duck:
        img = dino_duck_img
        w, h = DUCK_W, DUCK_H
        pad_x, pad_top, pad_bottom = DUCK_PAD_X, DUCK_PAD_TOP, DUCK_PAD_BOTTOM
    else:
        img = dino_run_img
        w, h = RUN_W, RUN_H
        pad_x, pad_top, pad_bottom = RUN_PAD_X, RUN_PAD_TOP, RUN_PAD_BOTTOM

    sprite_rect = pygame.Rect(x, int(y_top), w, h)

    hit_w = max(1, w - 2 * pad_x)
    hit_h = max(1, h - pad_top - pad_bottom)
    hitbox = pygame.Rect(
        sprite_rect.x + pad_x,
        sprite_rect.y + pad_top,
        hit_w,
        hit_h
    )
    return img, sprite_rect, hitbox

# ----------------------------
# Draw helpers
# ----------------------------
def draw_ground():
    pygame.draw.line(screen, GROUND_COLOR, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

def show_text_center(lines):
    y = HEIGHT // 2 - 30
    for i, line in enumerate(lines):
        surf = big_font.render(line, True, BLACK)
        rect = surf.get_rect(center=(WIDTH // 2, y + i * 40))
        screen.blit(surf, rect)

def draw_paper(surface, rect):
    x, y, w, h = rect

    pygame.draw.rect(surface, BLACK, rect, border_radius=2)
    inset = 3
    inner = pygame.Rect(x + inset, y + inset, w - 2 * inset, h - 2 * inset)
    if inner.w > 2 and inner.h > 2:
        pygame.draw.rect(surface, WHITE, inner, border_radius=1)

    line_y = y + 8
    while line_y < y + h - 6:
        pygame.draw.line(surface, BLACK, (x + 6, line_y), (x + w - 6, line_y), 1)
        line_y += 7

    fold = min(10, w // 3, h // 3)
    if fold >= 4:
        pygame.draw.line(surface, BLACK, (x + w - fold, y + 3), (x + w - 3, y + fold), 1)
        pygame.draw.line(surface, BLACK, (x + w - fold, y + 3), (x + w - fold, y + fold), 1)
        pygame.draw.line(surface, BLACK, (x + w - fold, y + fold), (x + w - 3, y + fold), 1)

# ----------------------------
# Obstacle bird tuning
# ----------------------------
# Smaller obstacle birds + smaller hitbox + slightly lower
OB_BIRD_SCALE = 0.85
OB_BIRD_PAD_X = 6
OB_BIRD_PAD_Y = 4

# Important: keep this modest or it breaks the DUCK/PASS math
OB_BIRD_LOWER = 3

def make_ob_bird_draw_rect(x_left, y_top):
    base_w, base_h = 34, 22
    w = max(1, int(base_w * OB_BIRD_SCALE))
    h = max(1, int(base_h * OB_BIRD_SCALE))
    return pygame.Rect(x_left, y_top, w, h)

def ob_bird_hitbox(draw_rect):
    return pygame.Rect(
        draw_rect.x + OB_BIRD_PAD_X,
        draw_rect.y + OB_BIRD_PAD_Y,
        max(1, draw_rect.w - 2 * OB_BIRD_PAD_X),
        max(1, draw_rect.h - 2 * OB_BIRD_PAD_Y),
    )

def draw_obstacle_bird(surface, draw_rect):
    r = draw_rect
    pygame.draw.rect(surface, BLACK, (r.x, r.y + 6, r.w, r.h - 6), border_radius=2)
    pygame.draw.rect(surface, BLACK, (r.x + 5, r.y, 8, 8), border_radius=2)
    pygame.draw.rect(surface, BLACK, (r.x + 14, r.y, 8, 8), border_radius=2)

# ----------------------------
# Spawning (KEEP your old "good" obstacle variety + distances)
# ----------------------------
def spawn_obstacle(speed, run_hit_top, duck_hit_top):
    """
    Returns (obstacle_dict, next_gap_px).
    Keeps your old paper shapes + your distance system.
    Bird obstacles: PASS (standing clears) or DUCK (must duck).
    """

    # --- your old gap feel ---
    base_min = 280
    base_max = 570
    shrink = int((speed - START_SPEED) * 8)

    gap_min = max(240, base_min - shrink)
    gap_max = max(gap_min + 140, base_max - shrink)
    next_gap_px = random.randint(gap_min, gap_max)

    kind = random.choices([OBS_PAPER, OBS_BIRD], weights=[0.65, 0.35])[0]

    if kind == OBS_PAPER:
        shape = random.choice(["tall", "square", "wide"])
        if shape == "tall":
            w = random.choice([22, 26, 30])
            h = random.choice([44, 54, 64])
        elif shape == "square":
            w = random.choice([34, 40, 46])
            h = random.choice([34, 40, 46])
        else:
            w = random.choice([50, 60, 72])
            h = random.choice([28, 34, 40])

        rect = pygame.Rect(WIDTH + 10, GROUND_Y - h, w, h)
        return {"kind": OBS_PAPER, "rect": rect}, next_gap_px

    # --- obstacle bird: PASS or DUCK ---
    bird_mode = random.choices(["PASS", "DUCK"], weights=[0.45, 0.55])[0]

    # The clearance math needs to reference PLAYER HITBOX tops.
    PASS_CLEAR = 6      # bird bottom above run-hit-top by this => standing clears
    DUCK_CLEAR = 6      # bird bottom above duck-hit-top by this => duck clears
    RUN_MUST_HIT = 6    # bird bottom below run-hit-top by this => standing hits

    if bird_mode == "PASS":
        bird_bottom = run_hit_top - PASS_CLEAR
    else:
        # duck clears => bird_bottom <= duck_hit_top - DUCK_CLEAR
        # run hits   => bird_bottom >= run_hit_top + RUN_MUST_HIT
        max_bottom_for_duck_clear = duck_hit_top - DUCK_CLEAR
        min_bottom_for_run_hit = run_hit_top + RUN_MUST_HIT

        if min_bottom_for_run_hit > max_bottom_for_duck_clear:
            # fallback: still make it "duckable"
            bird_bottom = duck_hit_top - DUCK_CLEAR
        else:
            bird_bottom = random.randint(min_bottom_for_run_hit, max_bottom_for_duck_clear)

    # Apply a SMALL lowering tweak AFTER choosing mode
    bird_bottom += OB_BIRD_LOWER

    # Build draw rect using scaled obstacle-bird height
    base_h = 22
    draw_h = max(1, int(base_h * OB_BIRD_SCALE))
    draw_rect = make_ob_bird_draw_rect(WIDTH + 10, bird_bottom - draw_h)

    return {
        "kind": OBS_BIRD,
        "rect": draw_rect,           # draw rect
        "hit": ob_bird_hitbox(draw_rect),
        "mode": bird_mode
    }, next_gap_px

# ----------------------------
# Reset
# ----------------------------
def reset_game():
    dino_state = STATE_RUN
    dino_vel_y = 0.0
    on_ground = True
    dino_y = float(GROUND_Y - RUN_H)

    obstacles = []
    speed = START_SPEED
    score = 0
    game_over = False

    dist_until_spawn = random.randint(260, 520)
    return dino_y, dino_state, dino_vel_y, on_ground, obstacles, speed, score, game_over, dist_until_spawn

dino_y, dino_state, dino_vel_y, on_ground, obstacles, speed, score, game_over, dist_until_spawn = reset_game()

# Precompute stable reference tops for bird spawning (based on hitboxes)
_, _, run_hit_ref = get_player_sprite_and_hitbox(DINO_X, GROUND_Y - RUN_H, STATE_RUN, True)
_, _, duck_hit_ref = get_player_sprite_and_hitbox(DINO_X, GROUND_Y - DUCK_H, STATE_DUCK, True)
RUN_HIT_TOP = run_hit_ref.top
DUCK_HIT_TOP = duck_hit_ref.top

# ----------------------------
# Main loop
# ----------------------------
while True:
    clock.tick(FPS)

    want_jump = False
    want_duck = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP):
                dino_y, dino_state, dino_vel_y, on_ground, obstacles, speed, score, game_over, dist_until_spawn = reset_game()

            if (not game_over) and event.key in (pygame.K_SPACE, pygame.K_UP):
                want_jump = True

    keys = pygame.key.get_pressed()
    if (not game_over) and keys[pygame.K_DOWN]:
        want_duck = True

    # -----------------------------
    # Update
    # -----------------------------
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

        # Keep feet planted
        if on_ground:
            dino_y = float(GROUND_Y - (DUCK_H if dino_state == STATE_DUCK else RUN_H))

        # Jump physics (RUN sprite in air)
        if not on_ground:
            dino_vel_y += GRAVITY
            dino_y += dino_vel_y
            if dino_y + RUN_H >= GROUND_Y:
                dino_y = float(GROUND_Y - RUN_H)
                dino_vel_y = 0.0
                on_ground = True
                dino_state = STATE_DUCK if want_duck else STATE_RUN

        # Player hitbox for collision
        img, sprite_rect, dino_hitbox = get_player_sprite_and_hitbox(DINO_X, dino_y, dino_state, on_ground)

        # Move obstacles
        for obs in obstacles:
            obs["rect"].x -= int(speed)
            if obs["kind"] == OBS_BIRD:
                obs["hit"].x -= int(speed)

        # Remove offscreen
        obstacles = [o for o in obstacles if o["rect"].right > -60]

        # Spawn (distance-based)
        dist_until_spawn -= int(speed)
        if dist_until_spawn <= 0:
            new_obs, next_gap = spawn_obstacle(speed, RUN_HIT_TOP, DUCK_HIT_TOP)
            obstacles.append(new_obs)
            dist_until_spawn = next_gap

        # Collision
        for obs in obstacles:
            if obs["kind"] == OBS_BIRD:
                if dino_hitbox.colliderect(obs["hit"]):
                    game_over = True
                    break
            else:
                if dino_hitbox.colliderect(obs["rect"]):
                    game_over = True
                    break

        # Score + speed ramp
        score += 1
        if score % 400 == 0:
            speed += 0.6

    # -----------------------------
    # Draw
    # -----------------------------
    screen.fill(WHITE)
    draw_ground()

    score_text = font.render(f"{score:06d}", True, BLACK)
    screen.blit(score_text, (WIDTH - 120, 15))

    for obs in obstacles:
        if obs["kind"] == OBS_PAPER:
            draw_paper(screen, obs["rect"])
        else:
            draw_obstacle_bird(screen, obs["rect"])
            # Debug obstacle bird hitbox:
            # pygame.draw.rect(screen, (255, 0, 0), obs["hit"], 1)

    img, sprite_rect, dino_hitbox = get_player_sprite_and_hitbox(DINO_X, dino_y, dino_state, on_ground)
    screen.blit(img, sprite_rect)

    # Debug player hitbox:
    # pygame.draw.rect(screen, (255, 0, 0), dino_hitbox, 1)

    if game_over:
        show_text_center(["GAME OVER", "Press SPACE to restart"])

    pygame.display.flip()