import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Run")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
GRAY = (120, 120, 120)
LIGHT_GRAY = (200, 200, 200)
VERY_LIGHT_GRAY = (230, 230, 230)
RED = (220, 50, 50)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 140, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
SKY_BLUE_LIGHT = (240, 248, 255)
MENU_BG = (245, 245, 245)

GROUND_Y = HEIGHT - 50
HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    current = load_high_score()
    if score > current:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(int(score)))

screen.fill(WHITE)

DINO_HEIGHT = 40
DINO_HEIGHT_DUCK = 20
DINO_X = 50

class Obstacle:
    def __init__(self, x, y, width, height, is_bird=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_bird = is_bird
        self.variant = random.randint(0, 2) if not is_bird else random.randint(0, 1)

class Cloud:
    def __init__(self, x=None):
        self.x = x if x is not None else random.randint(WIDTH, WIDTH + 400)
        self.y = random.randint(30, 120)
        self.size = random.randint(30, 60)
        self.speed = random.uniform(0.3, 0.8)

class Mountain:
    def __init__(self, x, height, layer=1):
        self.x = x
        self.height = height
        self.width = random.randint(80, 150)
        self.layer = layer

clouds = [Cloud() for _ in range(5)]
mountains = []
for i in range(8):
    mountains.append(Mountain(i * 150, random.randint(60, 120), layer=1))
for i in range(6):
    mountains.append(Mountain(i * 200 + 50, random.randint(80, 140), layer=2))

ground_pebbles = []
for _ in range(40):
    ground_pebbles.append({'x': random.randint(0, WIDTH), 'size': random.randint(2, 5)})

grass_tufts = []
for _ in range(15):
    grass_tufts.append({'x': random.randint(0, WIDTH), 'height': random.randint(3, 8)})

dino_rect = pygame.Rect(DINO_X, GROUND_Y - DINO_HEIGHT, 40, DINO_HEIGHT)
dino_y = GROUND_Y - DINO_HEIGHT
dino_velocity = 0
is_jumping = False
is_ducking = False
GRAVITY = 0.8
JUMP_STRENGTH = -15
FAST_FALL = 1.5

obstacles = []
obstacle_timer = 0
game_speed = 6
score = 0
anim_frame = 0

title_font = pygame.font.Font(None, 72)
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)

game_over = False
space_held = False
game_state = 'start'
high_score = load_high_score()

def can_jump():
    keys = pygame.key.get_pressed()
    return keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

def jump_pressed(event):
    return event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP)

def draw_dino(surface, x, y, height, ducking, frame):
    if ducking:
        body_y = y + height - 15
        pygame.draw.ellipse(surface, DARK_GRAY, (x + 5, body_y, 30, 15))
        pygame.draw.ellipse(surface, BLACK, (x + 5, body_y, 30, 15), 2)
        pygame.draw.circle(surface, BLACK, (x + 30, body_y + 5), 4)
        pygame.draw.circle(surface, WHITE, (x + 31, body_y + 4), 1)
    else:
        head_y = y + 2
        pygame.draw.ellipse(surface, DARK_GRAY, (x + 25, head_y, 22, 18))
        pygame.draw.ellipse(surface, BLACK, (x + 25, head_y, 22, 18), 2)
        
        pygame.draw.ellipse(surface, DARK_GRAY, (x + 8, y + 10, 28, 22))
        pygame.draw.ellipse(surface, BLACK, (x + 8, y + 10, 28, 22), 2)
        
        pygame.draw.circle(surface, BLACK, (x + 38, head_y + 8), 4)
        pygame.draw.circle(surface, WHITE, (x + 39, head_y + 7), 1)
        
        pygame.draw.line(surface, BLACK, (x + 12, y + 32), (x + 10, y + 38), 3)
        pygame.draw.line(surface, BLACK, (x + 22, y + 32), (x + 24, y + 38), 3)
        
        leg_offset = 3 if (frame // 8) % 2 == 0 else -3
        pygame.draw.line(surface, BLACK, (x + 15, y + 32), (x + 15 + leg_offset, y + 40), 4)
        pygame.draw.line(surface, BLACK, (x + 25, y + 32), (x + 25 - leg_offset, y + 40), 4)

def draw_cactus(surface, rect, variant):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    
    pygame.draw.rect(surface, GREEN, (x + 5, y, w - 10, h))
    pygame.draw.rect(surface, BLACK, (x + 5, y, w - 10, h), 2)
    
    pygame.draw.rect(surface, DARK_GREEN, (x + 5, y + 5, w - 10, h - 10))
    
    if variant == 0:
        pygame.draw.rect(surface, GREEN, (x, y + 10, 8, 5))
        pygame.draw.rect(surface, BLACK, (x, y + 10, 8, 5), 2)
        pygame.draw.rect(surface, GREEN, (x + w - 8, y + h - 15, 8, 5))
        pygame.draw.rect(surface, BLACK, (x + w - 8, y + h - 15, 8, 5), 2)
    elif variant == 1:
        pygame.draw.rect(surface, GREEN, (x - 3, y + 5, 6, 4))
        pygame.draw.rect(surface, BLACK, (x - 3, y + 5, 6, 4), 2)

def draw_bird(surface, rect, frame, variant):
    x, y = rect.x, rect.y
    
    wing_offset = 0 if (frame // 6) % 2 == 0 else 8
    
    pygame.draw.ellipse(surface, ORANGE, (x + 5, y + 5, 20, 12))
    pygame.draw.ellipse(surface, BLACK, (x + 5, y + 5, 20, 12), 2)
    
    pygame.draw.polygon(surface, BROWN, [
        (x, y + 10),
        (x + 10, y + 10 - wing_offset),
        (x + 5, y + 12)
    ])
    pygame.draw.polygon(surface, BLACK, [
        (x, y + 10),
        (x + 10, y + 10 - wing_offset),
        (x + 5, y + 12)
    ], 1)
    
    pygame.draw.circle(surface, BLACK, (x + 25, y + 10), 3)
    pygame.draw.circle(surface, WHITE, (x + 26, y + 9), 1)
    
    pygame.draw.line(surface, BLACK, (x + 10, y + 17), (x + 5 + wing_offset//2, y + 22), 2)
    pygame.draw.line(surface, BLACK, (x + 15, y + 17), (x + 20 - wing_offset//2, y + 22), 2)

def draw_background(surface):
    gradient = SKY_BLUE_LIGHT
    surface.fill(gradient)
    
    for cloud in clouds:
        cloud.x -= cloud.speed
        if cloud.x < -100:
            cloud.x = WIDTH + 100
            cloud.y = random.randint(30, 120)
        
        pygame.draw.ellipse(surface, WHITE, (cloud.x, cloud.y, cloud.size, cloud.size // 2))
        pygame.draw.ellipse(surface, WHITE, (cloud.x + 15, cloud.y - 10, cloud.size // 2, cloud.size // 2))
        pygame.draw.ellipse(surface, WHITE, (cloud.x + cloud.size - 25, cloud.y - 5, cloud.size // 2, cloud.size // 2))
    
    for mt in mountains:
        if mt.layer == 2:
            mt.x -= 0.5
            if mt.x < -mt.width:
                mt.x = WIDTH + 50
            
            points = [
                (mt.x, GROUND_Y),
                (mt.x + mt.width // 2, GROUND_Y - mt.height),
                (mt.x + mt.width, GROUND_Y)
            ]
            pygame.draw.polygon(surface, VERY_LIGHT_GRAY, points)
        else:
            mt.x -= 1
            if mt.x < -mt.width:
                mt.x = WIDTH + 100
            
            points = [
                (mt.x, GROUND_Y),
                (mt.x + mt.width // 2, GROUND_Y - mt.height),
                (mt.x + mt.width, GROUND_Y)
            ]
            pygame.draw.polygon(surface, LIGHT_GRAY, points)

def draw_ground(surface):
    pygame.draw.rect(surface, GRAY, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.line(surface, DARK_GRAY, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
    pygame.draw.line(surface, LIGHT_GRAY, (0, GROUND_Y + 3), (WIDTH, GROUND_Y + 3), 1)
    
    for pebble in ground_pebbles:
        pebble['x'] -= game_speed
        if pebble['x'] < -10:
            pebble['x'] = WIDTH + 10
        
        if 0 <= pebble['x'] <= WIDTH:
            size = pebble['size']
            pygame.draw.ellipse(surface, LIGHT_GRAY, (pebble['x'], GROUND_Y + 12, size, size // 2))
    
    for tuft in grass_tufts:
        tuft['x'] -= game_speed
        if tuft['x'] < -10:
            tuft['x'] = WIDTH + 10
        
        if 0 <= tuft['x'] <= WIDTH:
            h = tuft['height']
            x = tuft['x']
            pygame.draw.line(surface, GREEN, (x, GROUND_Y + 5), (x - 2, GROUND_Y + 5 - h), 2)
            pygame.draw.line(surface, GREEN, (x + 3, GROUND_Y + 5), (x + 3, GROUND_Y + 5 - h + 2), 2)
            pygame.draw.line(surface, GREEN, (x + 6, GROUND_Y + 5), (x + 8, GROUND_Y + 5 - h + 1), 2)

def reset_game():
    global dino_y, dino_velocity, is_jumping, is_ducking, obstacles, obstacle_timer, score, game_over, game_speed, anim_frame
    dino_y = GROUND_Y - DINO_HEIGHT
    dino_velocity = 0
    is_jumping = False
    is_ducking = False
    obstacles = []
    obstacle_timer = 0
    score = 0
    game_over = False
    game_speed = 6
    anim_frame = 0

def get_dino_height():
    return DINO_HEIGHT_DUCK if is_ducking else DINO_HEIGHT

running = True
start_pulse = 0

while running:
    screen.fill(MENU_BG)
    
    if game_state == 'start':
        draw_background(screen)
        draw_ground(screen)
        
        title_shadow = title_font.render("DINO RUN", True, LIGHT_GRAY)
        title = title_font.render("DINO RUN", True, GREEN)
        
        screen.blit(title_shadow, (WIDTH // 2 - 148, HEIGHT // 2 - 80))
        screen.blit(title, (WIDTH // 2 - 150, HEIGHT // 2 - 82))
        
        start_pulse += 0.1
        alpha = int(127 + 127 * math.sin(start_pulse))
        
        start_text = small_font.render("Press SPACE, W, or UP to start", True, DARK_GRAY)
        screen.blit(start_text, (WIDTH // 2 - 130, HEIGHT // 2 + 20))
        
        controls_text = small_font.render("SPACE/W/UP: Jump    DOWN/S: Duck", True, GRAY)
        screen.blit(controls_text, (WIDTH // 2 - 160, HEIGHT // 2 + 60))
        
        if high_score > 0:
            hs_text = font.render(f"High Score: {high_score}", True, GRAY)
            screen.blit(hs_text, (WIDTH // 2 - 100, HEIGHT // 2 + 100))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if jump_pressed(event):
                    game_state = 'playing'
                    reset_game()
    
    elif game_state == 'playing':
        draw_background(screen)
        draw_ground(screen)
        anim_frame += 1
        
        score_text = font.render(f"Score: {int(score)}", True, DARK_GRAY)
        screen.blit(score_text, (WIDTH - 180, 15))
        
        controls_text = small_font.render("SPACE/W/UP: Jump    DOWN/S: Duck", True, GRAY)
        screen.blit(controls_text, (15, 12))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if jump_pressed(event) and not is_jumping and not game_over:
                    dino_velocity = JUMP_STRENGTH
                    is_jumping = True
                    space_held = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if not is_ducking and not is_jumping:
                        is_ducking = True
                        dino_y = GROUND_Y - DINO_HEIGHT_DUCK
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    space_held = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if is_ducking:
                        is_ducking = False
                        dino_y = GROUND_Y - DINO_HEIGHT
        
        if not game_over:
            current_height = get_dino_height()
            
            if is_jumping and space_held and can_jump() and dino_velocity < 0:
                dino_velocity += GRAVITY * 0.3
            elif is_jumping and (pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]):
                dino_velocity += FAST_FALL
            
            dino_velocity += GRAVITY
            dino_y += dino_velocity
            
            if dino_y >= GROUND_Y - current_height:
                dino_y = GROUND_Y - current_height
                is_jumping = False
                dino_velocity = 0
            
            dino_rect.y = int(dino_y)
            dino_rect.height = current_height
            draw_dino(screen, DINO_X, int(dino_y), current_height, is_ducking, anim_frame)
            
            obstacle_timer += 1
            spawn_threshold = max(60, 120 - int(score / 10))
            
            if obstacle_timer > random.randint(60, spawn_threshold):
                obstacle_timer = 0
                
                if random.random() < 0.3 and score > 50:
                    bird_y = GROUND_Y - random.randint(55, 80)
                    obstacles.append(Obstacle(WIDTH, bird_y, 30, 20, is_bird=True))
                else:
                    height = random.randint(30, 60)
                    obstacles.append(Obstacle(WIDTH, GROUND_Y - height, 20, height, is_bird=False))
            
            for obstacle in obstacles[:]:
                obstacle.rect.x -= game_speed
                if obstacle.rect.x < -30:
                    obstacles.remove(obstacle)
                    score += 1
                else:
                    if obstacle.is_bird:
                        draw_bird(screen, obstacle.rect, anim_frame, obstacle.variant)
                    else:
                        draw_cactus(screen, obstacle.rect, obstacle.variant)
                
                if dino_rect.colliderect(obstacle.rect):
                    game_over = True
                    save_high_score(score)
                    high_score = load_high_score()
            
            score += 0.1
            game_speed = 6 + score / 100
        else:
            draw_dino(screen, DINO_X, int(dino_y), get_dino_height(), is_ducking, 0)
            
            for obstacle in obstacles:
                if obstacle.is_bird:
                    draw_bird(screen, obstacle.rect, 0, obstacle.variant)
                else:
                    draw_cactus(screen, obstacle.rect, obstacle.variant)
            
            game_over_shadow = title_font.render("GAME OVER", True, LIGHT_GRAY)
            game_over_text = title_font.render("GAME OVER", True, RED)
            final_score_text = font.render(f"Final Score: {int(score)}", True, DARK_GRAY)
            restart_text = font.render("Press R to restart", True, DARK_GRAY)
            
            screen.blit(game_over_shadow, (WIDTH // 2 - 143, HEIGHT // 2 - 78))
            screen.blit(game_over_text, (WIDTH // 2 - 145, HEIGHT // 2 - 80))
            screen.blit(final_score_text, (WIDTH // 2 - 90, HEIGHT // 2 + 10))
            if score >= high_score and score > 0:
                new_hs_text = font.render("NEW HIGH SCORE!", True, GREEN)
                screen.blit(new_hs_text, (WIDTH // 2 - 90, HEIGHT // 2 + 50))
            else:
                hs_text = font.render(f"High Score: {high_score}", True, GRAY)
                screen.blit(hs_text, (WIDTH // 2 - 80, HEIGHT // 2 + 50))
            screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2 + 90))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        reset_game()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()