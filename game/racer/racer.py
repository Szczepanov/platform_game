import pygame
from utils.constants import (
    WHITE, RED, BLUE, BLACK, GREEN, GRAY,
    WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_MOVE_DISTANCE,
    PLAYERS_START_Y, PLAYERS_START_X,
    RACER_PLAYERS,
    FINISH_LINE_X, FPS, WINNER_DISPLAY_TIME,
    initialize_racer_keys
)

class Player:
    def __init__(self, x, y, color, keys):
        self.pos = x
        self.y = y
        self.color = color
        self.keys = keys
        self.current_key = 0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
    
    def move(self, distance):
        self.pos += distance
        self.current_key = (self.current_key + 1) % len(self.keys)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos, self.y, self.width, self.height))
    
    def get_next_key(self):
        return self.keys[self.current_key]
    
    def is_correct_key(self, key):
        return key == self.keys[self.current_key]

class RacerGame:
    def __init__(self, screen, num_players=2):
        pygame.init()
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = screen
        pygame.display.set_caption(GAME_TITLE)
        
        # Initialize racer keys after pygame is properly initialized
        initialize_racer_keys()
        
        # Initialize players
        player_colors = [RED, BLUE, GRAY]
        self.players = [Player(PLAYERS_START_X, PLAYERS_START_Y[i], player_colors[i], RACER_PLAYERS[i])
                       for i in range(num_players)]
        
        # Finish line
        self.finish_line = FINISH_LINE_X

    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw players
        for player in self.players:
            player.draw(self.screen)
        
        # Draw finish line
        pygame.draw.line(self.screen, BLACK, (self.finish_line, 0), (self.finish_line, self.height), 2)
        
        # Display next keys to press
        font = pygame.font.Font(None, 36)
        for i, player in enumerate(self.players):
            text = font.render(f"Player {i+1}: Press {pygame.key.name(player.get_next_key())}", True, player.color)
            text_x = player.pos - text.get_width() // 4
            text_y = player.y - 30  # Position text above rectangle
            self.screen.blit(text, (text_x, text_y))
        
        pygame.display.flip()

    def run(self):
        running = True
        winner = None
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    # Handle player keys
                    for player in self.players:
                        if player.is_correct_key(event.key):
                            player.move(PLAYER_MOVE_DISTANCE)
            
            # Check for winner
            for i, player in enumerate(self.players):
                if player.pos >= self.finish_line and not winner:
                    winner = f"Player {i+1}"
            
            if winner:
                font = pygame.font.Font(None, 74)
                text = font.render(f"{winner} wins!", True, GREEN)
                self.screen.blit(text, (self.width//2 - 150, self.height//2))
                pygame.display.flip()
                pygame.time.wait(WINNER_DISPLAY_TIME)
                running = False
            
            self.draw()
            pygame.time.Clock().tick(FPS)
        
        pygame.quit()
        return

def race_game(screen, num_players=2):
    game = RacerGame(screen, num_players)
    game.run()
