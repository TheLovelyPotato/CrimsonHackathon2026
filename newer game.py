import os
import sys
import cv2
import time
import random
import mediapipe as mp
import pygame

# MediaPipe Tasks imports
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ----------------------------
# Camera
# ----------------------------
capture = cv2.VideoCapture(0)  # change index based on cam num and position

# ----------------------------
# Game settings
# ----------------------------
WIDTH, HEIGHT = 900, 250
FPS = 60

GROUND_Y = 200
DINO_X = 80

GRAVITY = 0.9
JUMP_VEL = -14
START_SPEED = 7.0

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GROUND_COLOR = (80, 80, 80)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

STATE_RUN = "RUN"
STATE_JUMP = "JUMP"
STATE_DUCK = "DUCK"

OBS_PAPER = "PAPER"
OBS_BIRD_HIGH = "BIRD_HIGH"   # jump over
OBS_BIRD_LOW = "BIRD_LOW"     # duck under

# ----------------------------
# pygame init + audio (KEEP from file #1)
# ----------------------------
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("Menu song.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)

game_death = pygame.mixer.Sound("Shoebill Stork Sound.wav")
jump_sound = pygame.mixer.Sound("Quack.wav")

# ----------------------------
# Menu (KEEP from file #1)
# ----------------------------
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

button_font = pygame.font.SysFont('Comic Sans MS', 30)
title_font = pygame.font.SysFont('Comic Sans MS', 30)
credits_font = pygame.font.SysFont('Comic Sans MS', 20)
intern = pygame.font.SysFont('Comic Sans MS', 10)

start_button = button_font.render('Start Game', True, BLACK)
exit_button = button_font.render('Exit', True, BLACK)

credits_line_title = title_font.render('SUPER DUCKY RUN', True, BLACK)
credits_line0 = credits_font.render('----CREDITS-----', True, BLACK)
credits_line1 = credits_font.render('Nicholas Horner', True, BLACK)
credits_line2 = credits_font.render('Zac Calvert', True, BLACK)
credits_line3 = credits_font.render('Sam Palatnikov', True, BLACK)
credits_line4 = credits_font.render('Kaitlyn Dunphy', True, BLACK)
credits_line5 = intern.render('+ Intern', True, BLACK)

screen.blit(credits_line_title, (550, 25))
screen.blit(credits_line0, (600, 100))
screen.blit(credits_line1, (600, 125))
screen.blit(credits_line2, (600, 150))
screen.blit(credits_line3, (600, 175))
screen.blit(credits_line4, (600, 200))
screen.blit(credits_line5, (600, 225))

while exit_menu == 0:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.draw.rect(
        screen, RED,
        (exit_button_xLeft, exit_button_yBottom,
         exit_button_xRight - exit_button_xLeft,
         exit_button_yTop - exit_button_yBottom)
    )
    pygame.draw.rect(
        screen, GREEN,
        (start_button_xLeft, start_button_yBottom,
         start_button_xRight - start_button_xLeft,
         start_button_yTop - start_button_yBottom)
    )

    if (start_button_xLeft < mouse_x < start_button_xRight) and (start_button_yBottom < mouse_y < start_button_yTop):
        pygame.draw.rect(
            screen, (0, 150, 0),
            (start_button_xLeft, start_button_yBottom,
             start_button_xRight - start_button_xLeft,
             start_button_yTop - start_button_yBottom)
        )
        if pygame.mouse.get_pressed(3)[0]:
            exit_menu = 1

    if (exit_button_xLeft < mouse_x < exit_button_xRight) and (exit_button_yBottom < mouse_y < exit_button_yTop):
        pygame.draw.rect(
            screen, (150, 0, 0),
            (exit_button_xLeft, exit_button_yBottom,
             exit_button_xRight - exit_button_xLeft,
             exit_button_yTop - exit_button_yBottom)
        )
        if pygame.mouse.get_pressed(3)[0]:
            pygame.quit()
            sys.exit()

    screen.blit(start_button, (start_button_xLeft + 20, start_button_yBottom + 65))
    screen.blit(exit_button, (exit_button_xLeft + 70, exit_button_yBottom + 65))
    pygame.display.update()

# ----------------------------
# Switch to game
# ----------------------------
pygame.display.set_caption("Dino Clone")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 34)

# stop menu music, start in-game music (KEEP from file #1)
pygame.mixer.stop()
pygame.mixer.music.load("Proper Duckie Song.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)

# ----------------------------
# Assets + sprite/hitbox system (FROM file #2)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def find_asset(name_or_stem: str) -> str:
    """
    Find an image in ./assets case-insensitively.
    Accepts: "Big bird" or "Big bird.png"
    Supports: .png .jpg .jpeg .webp
    """
    if not os.path.isdir(ASSETS_DIR):
        raise FileNotFoundError(f"assets folder not found at: {ASSETS_DIR}")

    want_stem, want_ext = os.path.splitext(name_or_stem)
    want_stem = want_stem.lower()
    want_ext = want_ext.lower()

    exts_ok = (".png", ".jpg", ".jpeg", ".webp")

    for f in os.listdir(ASSETS_DIR):
        stem, ext = os.path.splitext(f)
        if stem.lower() != want_stem:
            continue
        if want_ext:
            if ext.lower() == want_ext:
                return os.path.join(ASSETS_DIR, f)
        else:
            if ext.lower() in exts_ok:
                return os.path.join(ASSETS_DIR, f)

    raise FileNotFoundError(
        f"Could not find '{name_or_stem}' in {ASSETS_DIR}. Files: {os.listdir(ASSETS_DIR)}"
    )

def scale_img(img, scale):
    w = max(1, int(img.get_width() * scale))
    h = max(1, int(img.get_height() * scale))
    return pygame.transform.smoothscale(img, (w, h))

def sprite_bottom_ink_y(img: pygame.Surface) -> int:
    """Returns y of lowest non-transparent pixel in sprite."""
    w, h = img.get_width(), img.get_height()
    img.lock()
    try:
        for y in range(h - 1, -1, -1):
            for x in range(w):
                if img.get_at((x, y)).a > 0:
                    return y
    finally:
        img.unlock()
    return h - 1

def compute_feet_offset(img: pygame.Surface) -> int:
    """Pixels that exist BELOW the feet ink."""
    h = img.get_height()
    ink_y = sprite_bottom_ink_y(img)
    return (h - 1) - ink_y

# Player sprites (required)
RUN_PATH  = find_asset("Big bird")
DUCK_PATH = find_asset("shoved down bird")

# Low-flying obstacle sprite (optional)
LOW_OBS_PATH = None
try:
    LOW_OBS_PATH = find_asset("flyingwhitebird")
except FileNotFoundError:
    LOW_OBS_PATH = None

DINO_SCALE = 0.85
run_raw  = pygame.image.load(RUN_PATH).convert_alpha()
duck_raw = pygame.image.load(DUCK_PATH).convert_alpha()
run_img  = scale_img(run_raw,  DINO_SCALE)
duck_img = scale_img(duck_raw, DINO_SCALE)

RUN_W, RUN_H = run_img.get_width(), run_img.get_height()
DUCK_W, DUCK_H = duck_img.get_width(), duck_img.get_height()

RUN_FEET_OFFSET  = compute_feet_offset(run_img)
DUCK_FEET_OFFSET = compute_feet_offset(duck_img)

# Player hitbox padding
RUN_PAD_X = 10
RUN_PAD_TOP = 6
RUN_PAD_BOTTOM = 6

DUCK_PAD_X = 12
DUCK_PAD_TOP = 6
DUCK_PAD_BOTTOM = 4

def get_player_sprite_and_hitbox(x, y_top, state, on_ground):
    using_duck = (state == STATE_DUCK and on_ground)

    if using_duck:
        img = duck_img
        w, h = DUCK_W, DUCK_H
        pad_x, pad_top, pad_bottom = DUCK_PAD_X, DUCK_PAD_TOP, DUCK_PAD_BOTTOM
    else:
        img = run_img
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

# Obstacle birds
OB_SCALE = 0.85
HIGH_BIRD_W = max(1, int(34 * OB_SCALE))
HIGH_BIRD_H = max(1, int(22 * OB_SCALE))

def draw_high_bird(surface, rect):
    r = rect
    pygame.draw.rect(surface, BLACK, (r.x, r.y + 6, r.w, r.h - 6), border_radius=2)
    pygame.draw.rect(surface, BLACK, (r.x + 5, r.y, 8, 8), border_radius=2)
    pygame.draw.rect(surface, BLACK, (r.x + 14, r.y, 8, 8), border_radius=2)

low_bird_img = None
LOW_BIRD_W, LOW_BIRD_H = max(1, int(60 * OB_SCALE)), max(1, int(20 * OB_SCALE))
if LOW_OBS_PATH:
    low_raw = pygame.image.load(LOW_OBS_PATH).convert_alpha()
    low_bird_img = scale_img(low_raw, OB_SCALE)
    LOW_BIRD_W, LOW_BIRD_H = low_bird_img.get_width(), low_bird_img.get_height()

def draw_low_bird(surface, rect):
    if low_bird_img:
        surface.blit(low_bird_img, rect)
    else:
        pygame.draw.rect(surface, BLACK, rect, border_radius=2)

def shrink_hitbox(rect, pad_x, pad_y):
    return pygame.Rect(
        rect.x + pad_x,
        rect.y + pad_y,
        max(1, rect.w - 2 * pad_x),
        max(1, rect.h - 2 * pad_y),
    )

def spawn_obstacle(speed):
    # Gap logic (distance-based spawns)
    base_min = 280
    base_max = 570
    shrink = int((speed - START_SPEED) * 8)

    gap_min = max(240, base_min - shrink)
    gap_max = max(gap_min + 140, base_max - shrink)
    next_gap_px = random.randint(gap_min, gap_max)

    kind = random.choices(
        [OBS_PAPER, OBS_BIRD_HIGH, OBS_BIRD_LOW],
        weights=[0.45, 0.15, 0.40]
    )[0]

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

    if kind == OBS_BIRD_HIGH:
        y_top = GROUND_Y - HIGH_BIRD_H - 58
        rect = pygame.Rect(WIDTH + 10, y_top, HIGH_BIRD_W, HIGH_BIRD_H)
        hit = shrink_hitbox(rect, 6, 4)
        return {"kind": OBS_BIRD_HIGH, "rect": rect, "hit": hit}, next_gap_px

    # Low bird (duck under)
    LOW_BOTTOM_OFFSET = 58  # smaller => higher/harder, larger => lower/easier
    low_bottom = GROUND_Y - LOW_BOTTOM_OFFSET

    rect = pygame.Rect(WIDTH + 10, low_bottom - LOW_BIRD_H, LOW_BIRD_W, LOW_BIRD_H)
    hit = shrink_hitbox(rect, 10, 6)
    return {"kind": OBS_BIRD_LOW, "rect": rect, "hit": hit}, next_gap_px

def reset_game():
    dino_state = STATE_RUN
    dino_vel_y = 0.0
    on_ground = True

    # Feet pinned to ground (RUN sprite)
    dino_y = float(GROUND_Y - (RUN_H - RUN_FEET_OFFSET))

    obstacles = []
    speed = START_SPEED
    score = 0
    game_over = False
    dist_until_spawn = random.randint(260, 520)
    death_played = False

    return dino_y, dino_state, dino_vel_y, on_ground, obstacles, speed, score, game_over, dist_until_spawn, death_played

# ----------------------------
# MediaPipe Face Landmarker (KEEP from file #1)
# ----------------------------
base_options = python.BaseOptions(model_asset_path="face_landmarker.task")
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)
landmarker = vision.FaceLandmarker.create_from_options(options)

if not capture.isOpened():
    print("Could not open camera.")
    pygame.quit()
    sys.exit()

# ----------------------------
# Normalize human (KEEP from file #1)
# ----------------------------
last_time = time.time()
current_time = last_time
print("Normalizing human in 10 seconds!")

while (current_time - last_time) < 10:
    current_time = time.time()

    ret, frame = capture.read()
    if not ret:
        print("Failed to capture frame.")
        pygame.quit()
        sys.exit()

    frame = cv2.resize(frame, (800, 600))
    seconds_left = int(10 - (current_time - last_time))
    cv2.putText(frame, "Seconds Left: " + str(seconds_left), (10, 30),
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 5)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = landmarker.detect(mp_image)

    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (255, 255, 0), -1)

    cv2.imshow("Mediapipe Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# baseline capture
ret, frame = capture.read()
if not ret:
    print("Failed to capture")
    capture.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

frame = cv2.resize(frame, (800, 600))
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
result = landmarker.detect(mp_image)

total_yBase = 0
face_landmarks_count = 0

if result.face_landmarks:
    for face_landmarks in result.face_landmarks:
        face_landmarks_count = len(face_landmarks)
        for landmark in face_landmarks:
            total_yBase += int(landmark.y * 600)

if total_yBase == 0 or face_landmarks_count == 0:
    print("No face detected. Please try again.")
    capture.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

baseline_y = int(total_yBase / face_landmarks_count)

# ----------------------------
# Game loop with face control (MERGED)
# ----------------------------
dino_y, dino_state, dino_vel_y, on_ground, obstacles, speed, score, game_over, dist_until_spawn, death_played = reset_game()

start_time = time.time()
want_duck = False  # persistent duck signal like your original

while True:
    update_time = time.time()

    ret, frame = capture.read()
    if not ret:
        break

    frame = cv2.resize(frame, (800, 600))

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = landmarker.detect(mp_image)

    total_yNew = 0
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                total_yNew += int(landmark.y * 600)

    ratio = total_yNew / total_yBase if total_yBase != 0 else 1.0

    clock.tick(FPS)

    want_jump = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            capture.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP):
                dino_y, dino_state, dino_vel_y, on_ground, obstacles, speed, score, game_over, dist_until_spawn, death_played = reset_game()
                start_time = time.time()
                want_duck = False

    # Face control timing threshold (KEEP your 0.5s debounce)
    if ratio < 0.85 and (update_time - start_time) > 0.5:
        want_jump = True
        jump_sound.play()
        start_time = time.time()
    elif ratio > 1.15 and (update_time - start_time) > 0.5:
        want_duck = True
        start_time = time.time()
    elif (update_time - start_time) > 0.5:
        want_duck = False

    # -----------------------------
    # Update
    # -----------------------------
    if not game_over:
        pygame.mixer.music.unpause()

        # State transitions
        if on_ground:
            if want_jump:
                dino_state = STATE_JUMP
                dino_vel_y = float(JUMP_VEL)
                on_ground = False
            elif want_duck:
                dino_state = STATE_DUCK
            elif not want_duck:
                dino_state = STATE_RUN
        else:
            dino_state = STATE_JUMP

        # Feet pinning while grounded
        if on_ground:
            if dino_state == STATE_DUCK:
                dino_y = float(GROUND_Y - (DUCK_H - DUCK_FEET_OFFSET))
            else:
               dino_y = float(GROUND_Y - (RUN_H - RUN_FEET_OFFSET))

        # Jump physics
        if not on_ground:
            dino_vel_y += GRAVITY
            dino_y += dino_vel_y

            # land when feet reach ground (use RUN feet offset in air)
            if dino_y + (RUN_H - RUN_FEET_OFFSET) >= GROUND_Y:
                dino_y = float(GROUND_Y - (RUN_H - RUN_FEET_OFFSET))
                dino_vel_y = 0.0
                on_ground = True
                dino_state = STATE_DUCK if want_duck else STATE_RUN

        # Player hitbox
        img, sprite_rect, dino_hitbox = get_player_sprite_and_hitbox(DINO_X, dino_y, dino_state, on_ground)

        # Move obstacles
        for obs in obstacles:
            obs["rect"].x -= int(speed)
            if "hit" in obs:
                obs["hit"].x -= int(speed)

        # Remove offscreen
        obstacles = [o for o in obstacles if o["rect"].right > -60]

        # Spawn (distance-based)
        dist_until_spawn -= int(speed)
        if dist_until_spawn <= 0:
            new_obs, next_gap = spawn_obstacle(speed)
            obstacles.append(new_obs)
            dist_until_spawn = next_gap

        # Collision
        for obs in obstacles:
            if obs["kind"] in (OBS_BIRD_HIGH, OBS_BIRD_LOW):
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
        elif obs["kind"] == OBS_BIRD_HIGH:
            draw_high_bird(screen, obs["rect"])
        else:
            draw_low_bird(screen, obs["rect"])

    # Dino sprite
    img, sprite_rect, dino_hitbox = get_player_sprite_and_hitbox(DINO_X, dino_y, dino_state, on_ground)
    screen.blit(img, sprite_rect)

    if game_over:
        pygame.mixer.music.pause()
        if not death_played:
            game_death.play()
            death_played = True
        show_text_center(["GAME OVER", "Press SPACE to restart"])

    pygame.display.flip()

    # -----------------------------
    # Debug camera overlay (KEEP from file #1)
    # -----------------------------
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (255, 0, 255), -1)

    cv2.line(frame, (200, baseline_y), (600, baseline_y), (0, 255, 0), 2)
    cv2.imshow("Mediapipe Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ----------------------------
# Cleanup
# ----------------------------
capture.release()
cv2.destroyAllWindows()
pygame.quit()