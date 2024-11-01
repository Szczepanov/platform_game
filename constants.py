# Constants
import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (100, 120, 155)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
VIOLET = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
PLAYERS = {RED: {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP},
           BLUE: {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w},
           # GRAY: {'left': pygame.K_j, 'right': pygame.K_l, 'up': pygame.K_i}
           }
