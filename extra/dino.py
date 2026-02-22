import os
import sys
import random
import pygame

# ----------------------------
# Dino runner (pygame)
# Random gaps + paper obstacles + birds with two heights
# Player sprite uses PNGs in assets/:
#   RUN/JUMP: "Big bird.png"
#   DUCK:     "shoved down bird.png"
# ----------------------------

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
