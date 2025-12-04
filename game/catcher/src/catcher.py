import pygame
import sys
import random
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, BLUE, GRAY, YELLOW, GREEN, PLAYERS, BLACK, VIOLET

class CatcherPlayer:
    def __init__(self, x, y, color, controls, player_id):
        self.x = x
        self.y = y
        self.original_width = 50
        self.width = self.original_width
        self.height = 50
        self.color = color
        self.controls = controls
        self.original_velocity = 5
        self.velocity = self.original_velocity
        self.score = 0
        self.player_id = player_id
        
        # Powerup states
        self.powerups = {
            'speed': 0,
            'size': 0,
            'double': 0
        }

    def update(self):
        # Update powerup timers
        for p_type in list(self.powerups.keys()):
            if self.powerups[p_type] > 0:
                self.powerups[p_type] -= 1
                if self.powerups[p_type] == 0:
                    self.remove_powerup(p_type)

        keys = pygame.key.get_pressed()
        if keys[self.controls['left']]:
            self.x -= self.velocity
        if keys[self.controls['right']]:
            self.x += self.velocity

        # Keep player on screen
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def apply_powerup(self, p_type, duration):
        self.powerups[p_type] = duration
        if p_type == 'speed':
            self.velocity = self.original_velocity * 1.5
        elif p_type == 'size':
            center_x = self.x + self.width // 2
            self.width = self.original_width * 1.5
            self.x = center_x - self.width // 2 # Keep centered
        # 'double' is handled in scoring logic

    def remove_powerup(self, p_type):
        if p_type == 'speed':
            self.velocity = self.original_velocity
        elif p_type == 'size':
            center_x = self.x + self.width // 2
            self.width = self.original_width
            self.x = center_x - self.width // 2 # Keep centered

    def draw(self, screen):
        # Draw player as a bucket/basket shape (U shape)
        
        # Visual effect for powerups
        draw_color = self.color
        if self.powerups['double'] > 0:
            # Flash or change color slightly
             if (self.powerups['double'] // 10) % 2 == 0:
                 draw_color = VIOLET

        # Base
        pygame.draw.rect(screen, draw_color, (self.x, self.y + self.height - 10, self.width, 10))
        # Left side
        pygame.draw.rect(screen, draw_color, (self.x, self.y, 10, self.height))
        # Right side
        pygame.draw.rect(screen, draw_color, (self.x + self.width - 10, self.y, 10, self.height))
        
        # Draw score above player
        font = pygame.font.Font(None, 24)
        score_text = font.render(str(self.score), True, WHITE)
        screen.blit(score_text, (self.x + self.width//2 - score_text.get_width()//2, self.y - 20))

class FallingItem:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - 30)
        self.y = -30
        self.size = 30
        self.speed = random.randint(3, 7)
        self.type = random.choice(['coin', 'coin', 'coin', 'bomb']) # 75% coin, 25% bomb
        
    def update(self):
        self.y += self.speed

    def draw(self, screen):
        if self.type == 'coin':
            color = YELLOW
            pygame.draw.circle(screen, color, (self.x + self.size//2, int(self.y + self.size//2)), self.size//2)
            # Inner circle for detail
            pygame.draw.circle(screen, (255, 215, 0), (self.x + self.size//2, int(self.y + self.size//2)), self.size//2 - 5, 2)
        else: # bomb
            color = BLACK
            pygame.draw.circle(screen, color, (self.x + self.size//2, int(self.y + self.size//2)), self.size//2)
            # Fuse
            pygame.draw.line(screen, RED, (self.x + self.size//2, self.y), (self.x + self.size//2 + 5, self.y - 10), 2)

    def collides_with(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        item_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        return player_rect.colliderect(item_rect)

class PowerUp(FallingItem):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['speed', 'size', 'double'])
        self.speed = random.randint(4, 6)
        
    def draw(self, screen):
        if self.type == 'speed':
            color = BLUE
            label = "S"
        elif self.type == 'size':
            color = GREEN
            label = "L"
        else: # double
            color = VIOLET
            label = "2x"
            
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size), border_radius=5)
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size), 2, border_radius=5)
        
        font = pygame.font.Font(None, 24)
        text = font.render(label, True, WHITE)
        screen.blit(text, (self.x + self.size//2 - text.get_width()//2, self.y + self.size//2 - text.get_height()//2))


def catcher_game(screen, num_players=2):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Initialize players
    players = []
    colors = [RED, BLUE, GRAY]
    player_controls = list(PLAYERS.values())
    
    start_x = SCREEN_WIDTH // (num_players + 1)
    
    for i in range(num_players):
        x_pos = start_x * (i + 1) - 25
        y_pos = SCREEN_HEIGHT - 60
        player = CatcherPlayer(x_pos, y_pos, colors[i], player_controls[i], i+1)
        players.append(player)
    
    items = []
    item_timer = 0
    powerup_timer = 0
    game_duration = 30 * 60 # 60 seconds at 60 FPS
    time_left = game_duration
    game_over = False
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if game_over and event.key == pygame.K_SPACE:
                    return catcher_game(screen, num_players)

        if not game_over:
            time_left -= 1
            if time_left <= 0:
                game_over = True
            
            # Update players
            for player in players:
                player.update()
            
            # Spawn items
            item_timer += 1
            if item_timer > 30: # Spawn every 0.5 seconds
                items.append(FallingItem())
                item_timer = 0
                
            # Spawn powerups
            powerup_timer += 1
            if powerup_timer > 600: # Spawn every ~10 seconds
                items.append(PowerUp())
                powerup_timer = 0
            
            # Update items
            items_to_remove = []
            for item in items:
                item.update()
                
                # Check collision
                for player in players:
                    if item.collides_with(player):
                        if isinstance(item, PowerUp):
                            player.apply_powerup(item.type, 600) # 10 seconds
                        elif item.type == 'coin':
                            points = 1
                            if player.powerups['double'] > 0:
                                points *= 2
                            player.score += points
                        else: # bomb
                            player.score = max(0, player.score - 2) # Bomb penalty
                        items_to_remove.append(item)
                        break # Item consumed
                
                if item.y > SCREEN_HEIGHT:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                if item in items:
                    items.remove(item)
        
        # Draw
        screen.fill((135, 206, 250)) # Light Sky Blue
        
        # Draw floor
        pygame.draw.rect(screen, (34, 139, 34), (0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10)) # Forest Green
        
        for item in items:
            item.draw(screen)
            
        for player in players:
            player.draw(screen)
            
        # Draw UI
        time_text = font.render(f"Time: {time_left // 60}", True, WHITE)
        screen.blit(time_text, (10, 10))
        
        # Draw controls info
        controls_y = 50
        for i, player in enumerate(players):
            control_text = pygame.font.Font(None, 24).render(
                f"P{i+1}: {pygame.key.name(player.controls['left']).upper()}/{pygame.key.name(player.controls['right']).upper()}", 
                True, player.color
            )
            screen.blit(control_text, (10, controls_y + i * 25))

        if game_over:
            # Find winner
            max_score = -1
            winners = []
            for player in players:
                if player.score > max_score:
                    max_score = player.score
                    winners = [player]
                elif player.score == max_score:
                    winners.append(player)
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("GAME OVER!", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            
            if len(winners) == 1:
                winner_text = font.render(f"Player {winners[0].player_id} Wins!", True, winners[0].color)
            elif len(winners) > 1:
                winner_text = font.render("It's a Tie!", True, WHITE)
            else:
                winner_text = font.render("No Winners!", True, WHITE)
                
            screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            restart_text = font.render("Press SPACE to restart or ESC to exit", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
