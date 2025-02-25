import cv2
import mediapipe as mp
import pygame
import sys

# Initialize Mediapipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neon Brick Breaker with Hand Control")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
NEON = (0, 255, 204)

# Paddle
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 15
paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
paddle_y = SCREEN_HEIGHT - 50
paddle_speed = 8

# Ball
ball_x = SCREEN_WIDTH // 2
ball_y = paddle_y - 20
ball_radius = 10
ball_dx = 4
ball_dy = -4

# Bricks
BRICK_ROWS = 6
BRICK_COLS = 8
BRICK_WIDTH = SCREEN_WIDTH // BRICK_COLS
BRICK_HEIGHT = 30
bricks = []
for row in range(BRICK_ROWS):
    brick_row = []
    for col in range(BRICK_COLS):
        brick_row.append(pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT))
    bricks.append(brick_row)

# Score and Lives
score = 0
lives = 3
font = pygame.font.Font(None, 36)

# Camera
cap = cv2.VideoCapture(0)

# Functions
def draw_paddle():
    pygame.draw.rect(screen, NEON, (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))

def draw_ball():
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)

def draw_bricks():
    for row in bricks:
        for brick in row:
            if brick:
                pygame.draw.rect(screen, GREEN, brick)
                pygame.draw.rect(screen, WHITE, brick, 2)

def draw_text(text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = SCREEN_WIDTH // 2
    ball_y = paddle_y - 20
    ball_dx = 4
    ball_dy = -4

# Main game loop
running = True
while running:
    # Camera input
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)  # Flip horizontally
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Detect hand and update paddle position
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            x_index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            paddle_x = int(x_index * SCREEN_WIDTH - PADDLE_WIDTH // 2)
            if paddle_x < 0:
                paddle_x = 0
            if paddle_x + PADDLE_WIDTH > SCREEN_WIDTH:
                paddle_x = SCREEN_WIDTH - PADDLE_WIDTH

    # Display the camera feed
    cv2.imshow("Hand Tracking", frame)

    # Game logic
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with walls
    if ball_x - ball_radius < 0 or ball_x + ball_radius > SCREEN_WIDTH:
        ball_dx *= -1
    if ball_y - ball_radius < 0:
        ball_dy *= -1

    # Ball collision with paddle
    if paddle_y < ball_y + ball_radius < paddle_y + PADDLE_HEIGHT and paddle_x < ball_x < paddle_x + PADDLE_WIDTH:
        ball_dy *= -1

    # Ball collision with bricks
    for row in bricks:
        for i, brick in enumerate(row):
            if brick and brick.collidepoint(ball_x, ball_y):
                row[i] = None
                ball_dy *= -1
                score += 10

    # Ball out of bounds
    if ball_y > SCREEN_HEIGHT:
        lives -= 1
        if lives == 0:
            running = False
        reset_ball()

    # Draw everything
    screen.fill(BLACK)
    draw_paddle()
    draw_ball()
    draw_bricks()
    draw_text(f"Score: {score}", 10, 10)
    draw_text(f"Lives: {lives}", SCREEN_WIDTH - 100, 10)

    pygame.display.flip()

    # Exit condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # FPS
    pygame.time.Clock().tick(60)

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
