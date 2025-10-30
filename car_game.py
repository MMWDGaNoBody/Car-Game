import pygame
import random

# --- Initialization ---
pygame.init()

# Window
SCREEN_W, SCREEN_H = 500, 700  
window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Lane Racer Plus")

# Clock
FPS = 120
clock = pygame.time.Clock()

# Colors
GRASS = (76, 208, 56)
ROAD = (100, 100, 100)
LINE = (255, 255, 255)
EDGE = (255, 232, 0)
DANGER = (200, 0, 0)

# Road
ROAD_W = 300
MARKER_W, MARKER_H = 10, 50

# Lane positions
LANE_POSITIONS = [150, 250, 350]

# Player
PLAYER_Y = 600
LANE_SPEED = 10  # pixels per frame for smooth lane change

# --- Classes ---
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, img, lane_index, y_pos):
        super().__init__()
        lane_width = ROAD_W / 3
        max_width = lane_width * 1.2
        scale = min(max_width / img.get_width(), 1)
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.lane_index = lane_index
        self.rect.centerx = LANE_POSITIONS[lane_index]
        self.rect.y = y_pos

class PlayerCar(Vehicle):
    def __init__(self, lane_index, y_pos):
        img = pygame.image.load("images/car.png")
        super().__init__(img, lane_index, y_pos)

# --- Sprite Groups ---
player_group = pygame.sprite.Group()
traffic_group = pygame.sprite.Group()

# --- Create Player ---
player_lane = 1
player_car = PlayerCar(player_lane, PLAYER_Y)
player_group.add(player_car)
player_target_x = LANE_POSITIONS[player_lane]

# Load traffic vehicles
vehicle_images = [pygame.image.load(f"images/{name}") for name in ["ambulance.png", "Audi.png", "taxi.png", "mini_van.png", "Black_viper.png", "Mini_truck.png", "Police.png", "truck.png"]]

# Crash image
crash_img = pygame.image.load("images/explosion0.png")
crash_rect = crash_img.get_rect()

# --- Game variables ---
running = True
game_over = False
road_offset = 0
speed = 2
score = 0
last_speedup = 0

# --- Helper Functions ---
def spawn_vehicle():
    lane_index = random.randint(0, 2)
    img = random.choice(vehicle_images)
    traffic = Vehicle(img, lane_index, -img.get_height())
    traffic_group.add(traffic)

def draw_road():
    window.fill(GRASS)
    pygame.draw.rect(window, ROAD, (100, 0, ROAD_W, SCREEN_H))
    pygame.draw.rect(window, EDGE, (95, 0, MARKER_W, SCREEN_H))
    pygame.draw.rect(window, EDGE, (395, 0, MARKER_W, SCREEN_H))

    # Lane markers
    global road_offset
    road_offset += speed * 2
    if road_offset >= MARKER_H * 2:
        road_offset = 0

    for lane_x in LANE_POSITIONS[:-1]:
        for y in range(-MARKER_H*2, SCREEN_H, MARKER_H*2):
            marker_x = lane_x + 45
            pygame.draw.rect(window, LINE, (marker_x, y + road_offset, MARKER_W, MARKER_H))

def reset_game():
    global score, speed, last_speedup, game_over, player_lane, player_target_x
    score = 0
    speed = 2
    last_speedup = 0
    game_over = False
    traffic_group.empty()
    player_lane = 1
    player_car.rect.centerx = LANE_POSITIONS[player_lane]
    player_target_x = LANE_POSITIONS[player_lane]

# --- Main Loop ---
while running:
    clock.tick(FPS)

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_LEFT and player_lane > 0:
                player_lane -= 1
                player_target_x = LANE_POSITIONS[player_lane]
            elif event.key == pygame.K_RIGHT and player_lane < 2:
                player_lane += 1
                player_target_x = LANE_POSITIONS[player_lane]

    # --- Smooth Lane Movement ---
    if player_car.rect.centerx < player_target_x:
        player_car.rect.centerx += min(LANE_SPEED, player_target_x - player_car.rect.centerx)
    elif player_car.rect.centerx > player_target_x:
        player_car.rect.centerx -= min(LANE_SPEED, player_car.rect.centerx - player_target_x)

    # --- Spawn Traffic ---
    if len(traffic_group) < 2:
        if all(v.rect.top > v.rect.height * 1.5 for v in traffic_group):
            spawn_vehicle()

    # --- Move Traffic ---
    for vehicle in traffic_group:
        vehicle.rect.y += speed
        if vehicle.rect.top > SCREEN_H:
            vehicle.kill()
            score += 1
            if score - last_speedup >= 5:
                speed += 1
                last_speedup = score

    # --- Collision (only same lane) ---
    for vehicle in traffic_group:
        if vehicle.lane_index == player_lane and player_car.rect.colliderect(vehicle.rect):
            game_over = True
            crash_rect.center = player_car.rect.center
            break

    # --- Draw ---
    draw_road()
    player_group.draw(window)
    traffic_group.draw(window)

    # Score display
    font = pygame.font.Font(None, 24)
    score_text = font.render(f"Score: {score}", True, LINE)
    window.blit(score_text, (10, 10))

    # Game Over
    if game_over:
        window.blit(crash_img, crash_rect)
        pygame.draw.rect(window, DANGER, (0, 50, SCREEN_W, 100))
        over_text = font.render("Game Over. Retry? Y/N", True, LINE)
        window.blit(over_text, (SCREEN_W//2 - over_text.get_width()//2, 100))

        pygame.display.update()

        waiting = True
        while waiting:
            clock.tick(FPS)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                    waiting = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_y:
                        reset_game()
                        waiting = False
                    elif e.key == pygame.K_n:
                        running = False
                        waiting = False

    pygame.display.update()

pygame.quit()
