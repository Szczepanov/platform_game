# Constants
import pygame
import random
import string

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
           GRAY: {'left': pygame.K_j, 'right': pygame.K_l, 'up': pygame.K_i}
           }
PLAYER_SIZE = 50
PLAYER_SPEED = 0.5
FINISH_LINE = SCREEN_WIDTH - PLAYER_SIZE
BG_COLOR = (0, 255, 0)  # Green

# Player settings
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 20
PLAYER_MOVE_DISTANCE = 20
PLAYERS_START_Y = [100, 200, 300]
PLAYERS_START_X = 50

# Racer Game Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
GAME_TITLE = "Racer!"

# Generate random keys for players (a-z, 0-9) - lazy initialization
AVAILABLE_KEYS = []
PLAYER1_KEYS = []
PLAYER2_KEYS = []
PLAYER3_KEYS = []
RACER_PLAYERS = []

def initialize_racer_keys():
    """Initialize racer keys after pygame is properly initialized"""
    global AVAILABLE_KEYS, PLAYER1_KEYS, PLAYER2_KEYS, PLAYER3_KEYS, RACER_PLAYERS
    
    if AVAILABLE_KEYS:  # Already initialized
        return
    
    # Generate keys and mutate lists in place
    new_keys = [pygame.key.key_code(c) for c in string.ascii_lowercase + string.digits]
    AVAILABLE_KEYS.extend(new_keys)
    
    all_keys = random.sample(AVAILABLE_KEYS, len(AVAILABLE_KEYS))
    third = len(all_keys) // 3
    
    PLAYER1_KEYS.extend(all_keys[:third])  # First third for player 1
    PLAYER2_KEYS.extend(all_keys[third:2*third])  # Second third for player 2
    PLAYER3_KEYS.extend(all_keys[2*third:])  # Third third for player 3
    
    RACER_PLAYERS.extend([PLAYER1_KEYS, PLAYER2_KEYS, PLAYER3_KEYS])

# Racer Game settings
FINISH_LINE_X = 670
FPS = 60
WINNER_DISPLAY_TIME = 2000  # milliseconds

# Platformer Game settings
POWERUP_SPAWN_INTERVAL = 3
MAX_POWERUPS = 3  # Maximum number of powerups that can be on screen simultaneously