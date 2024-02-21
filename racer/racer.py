import pygame
import sys
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER1_COLOR, PLAYER2_COLOR, GRAY

PLAYER_SIZE = 50
PLAYER_SPEED = 0.5
FINISH_LINE = SCREEN_WIDTH - PLAYER_SIZE
BG_COLOR = (0, 255, 0)  # Green


class Player:
    def __init__(self, position_x, position_y):
        self.position_x = position_x
        self.position_y = position_y
        self.speed = 0
        self.angle = 0
        self.rotation = 0

    def move(self):
        self.position_x += self.speed * math.cos(self.angle)
        self.position_y += self.speed * math.sin(self.angle)
        self.angle += self.rotation


def race_game(screen):
    # Initialize Pygame
    pygame.init()

    # Define the player cars
    player1 = Player(0, SCREEN_WIDTH / 3)
    player2 = Player(0, 2 * SCREEN_HEIGHT / 3)

    # Create a font object
    font = pygame.font.Font(None, 50)

    # Define the track
    track = pygame.Rect(0, SCREEN_WIDTH / 3, SCREEN_WIDTH, SCREEN_HEIGHT / 3)

    # Game loop
    while True:
        # Fill the game window
        screen.fill(BG_COLOR)

        # Draw the track
        pygame.draw.rect(screen, GRAY, track)

        # Draw the player cars
        pygame.draw.rect(screen, PLAYER1_COLOR,
                         pygame.Rect(player1.position_x, player1.position_y, PLAYER_SIZE, PLAYER_SIZE))
        pygame.draw.rect(screen, PLAYER2_COLOR,
                         pygame.Rect(player2.position_x, player2.position_y, PLAYER_SIZE, PLAYER_SIZE))

        # Update the game display
        pygame.display.flip()

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                speed = PLAYER_SPEED
                if event.key == pygame.K_w:
                    if not track.colliderect(pygame.Rect(player1.position_x, player1.position_y, PLAYER_SIZE, PLAYER_SIZE)):
                        speed /= 2  # Decrease speed while on green
                    player1.speed = speed
                elif event.key == pygame.K_s:
                    player1.speed = -speed
                elif event.key == pygame.K_a:
                    player1.rotation = -5
                elif event.key == pygame.K_d:
                    player1.rotation = 5
                elif event.key == pygame.K_UP:
                    if not track.colliderect(pygame.Rect(player2.position_x, player2.position_y, PLAYER_SIZE, PLAYER_SIZE)):
                        speed /= 2  # Decrease speed while on green
                    player2.speed = speed
                elif event.key == pygame.K_DOWN:
                    player2.speed = -speed
                elif event.key == pygame.K_LEFT:
                    player2.rotation = -5
                elif event.key == pygame.K_RIGHT:
                    player2.rotation = 5
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_d):
                    player1.rotation = 0
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    player2.rotation = 0

        # Update player positions
        player1.move()
        player2.move()

        # Check if any player has reached the finish line
        if player1.position_x >= FINISH_LINE or player2.position_x >= FINISH_LINE:
            winner_text_str = ''
            if player1.position_x >= FINISH_LINE:
                winner_text_str = "Player 1 wins!"
            elif player2.position_x >= FINISH_LINE:
                winner_text_str = "Player 2 wins!"
            winner_text = font.render(winner_text_str, True, (255, 0, 0))  # Red
            for _ in range(4):
                screen.blit(winner_text, (
                SCREEN_WIDTH / 2 - winner_text.get_width() / 2, SCREEN_HEIGHT / 2 - winner_text.get_height() / 2))
                pygame.display.flip()
                pygame.time.wait(500)
                screen.fill(BG_COLOR)
                pygame.display.flip()
                pygame.time.wait(500)
            return
