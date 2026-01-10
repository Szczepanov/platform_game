import pygame
import sys
import random
import math
from game.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, BLUE, GREEN, GRAY, YELLOW, BLACK, FPS

# Cooperative platformer specific constants
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
PLAYER_SIZE = 30
SCROLL_SPEED = 2  # Auto-scroll speed

class Player:
    def __init__(self, x, y, color, controls, player_id):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.controls = controls  # {'left': key, 'right': key, 'jump': key}
        self.player_id = player_id
        self.score = 0
        self.can_boost = False
        self.boost_cooldown = 0
        self.alive = True
        self.boost_display_timer = 0  # Timer to stabilize boost display
        
    def update(self, platforms, other_players, scroll_offset):
        if not self.alive:
            return
            
        # Handle input
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        if keys[self.controls['left']]:
            self.vel_x = -MOVE_SPEED
        if keys[self.controls['right']]:
            self.vel_x = MOVE_SPEED
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Limit fall speed
        if self.vel_y > 20:
            self.vel_y = 20
            
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Check collisions with platforms
        self.on_ground = False
        for platform in platforms:
            if self.check_collision(platform, scroll_offset):
                # Landing on top of platform
                if self.vel_y > 0 and self.y < platform.y + scroll_offset:
                    self.y = platform.y + scroll_offset - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    
        # Screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Update cooldowns
        if self.boost_cooldown > 0:
            self.boost_cooldown -= 1
            
        # Check for cooperative boost
        self.check_cooperative_boost(other_players)
        
        # Check if player fell off screen (game over condition)
        if self.y > SCREEN_HEIGHT:
            self.alive = False
            
    def check_collision(self, platform, scroll_offset):
        platform_y = platform.y + scroll_offset
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform_y + platform.height and
                self.y + self.height > platform_y)
                
    def check_cooperative_boost(self, other_players):
        # Check if any nearby player is close enough for boost (display only)
        new_can_boost = False
        for other_player in other_players:
            if other_player.player_id != self.player_id and other_player.alive:
                distance = math.sqrt((self.x - other_player.x)**2 + (self.y - other_player.y)**2)
                if distance < 50 and self.boost_cooldown == 0:
                    new_can_boost = True
                    break
        
        # Update can_boost immediately if this is the first check or if state is stable
        if self.boost_display_timer == 0 or new_can_boost == self.can_boost:
            self.can_boost = new_can_boost
            self.boost_display_timer = 0
        else:
            # Wait for stability before changing state
            self.boost_display_timer += 1
            if self.boost_display_timer > 5:  # Wait 5 frames before changing
                self.can_boost = new_can_boost
                self.boost_display_timer = 0
            
    def boost_other_player(self, other_players):
        if self.can_boost and self.on_ground:  # Still require on_ground for actual boost
            # Find the closest alive player to boost
            closest_player = None
            min_distance = float('inf')
            
            for other_player in other_players:
                if other_player.player_id != self.player_id and other_player.alive:
                    distance = math.sqrt((self.x - other_player.x)**2 + (self.y - other_player.y)**2)
                    if distance < 50 and distance < min_distance:
                        min_distance = distance
                        closest_player = other_player
            
            if closest_player:
                closest_player.vel_y = JUMP_STRENGTH * 1.5  # Super jump
                self.boost_cooldown = 60  # 1 second cooldown
                return True
        return False
        
    def draw(self, screen):
        if not self.alive:
            return
            
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw boost indicator
        if self.can_boost:
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.x + self.width//2), int(self.y - 10)), 5)
            # Draw boost prompt with background to prevent flicker
            font_small = pygame.font.Font(None, 20)
            boost_key_map = {1: "S", 2: "DOWN", 3: "K"}
            boost_key = boost_key_map.get(self.player_id, "?")
            prompt_text = font_small.render(f"Press {boost_key}", True, YELLOW)
            # Create a small background rectangle for the text
            text_rect = prompt_text.get_rect()
            text_rect.topleft = (self.x - 10, self.y - 30)
            pygame.draw.rect(screen, BLACK, text_rect.inflate(4, 2))  # Black background
            screen.blit(prompt_text, text_rect)

class Platform:
    def __init__(self, x, y, width=PLATFORM_WIDTH, height=PLATFORM_HEIGHT, 
                 platform_type='normal'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.platform_type = platform_type
        self.color = GRAY if platform_type == 'normal' else GREEN
        
    def draw(self, screen, scroll_offset):
        draw_y = self.y + scroll_offset
        if -50 < draw_y < SCREEN_HEIGHT + 50:
            pygame.draw.rect(screen, self.color, (self.x, draw_y, self.width, self.height))
            if self.platform_type == 'cooperative':
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.x + self.width//2), int(draw_y + self.height//2)), 8)

def cooperative_platformer_game(screen, num_players=1):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Initialize players (spawn just above the starting platform)
    player1 = Player(300, 480, BLUE, 
                     {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'boost': pygame.K_s}, 1)
    players = [player1]
    # Add second player if num_players is 2
    if num_players > 1:
        player2 = Player(500, 480, RED, 
                        {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'boost': pygame.K_DOWN}, 2)
        players.append(player2)
    
    
    
    # Add third player if num_players is 3
    if num_players > 2:
        player3 = Player(400, 480, GREEN, 
                        {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_i, 'boost': pygame.K_k}, 3)
        players.append(player3)
    
    # Game state
    platforms = []
    scroll_offset = 0  # How much the screen has scrolled
    score = 0
    coop_bonus = 1
    game_over = False
    shared_lives = 3  # Following existing project pattern
    game_started = False  # Flag to control when scrolling starts
    
    # Initialize platforms
    generate_initial_platforms(platforms)
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_ESCAPE:
                    return
                # Cooperative boost mechanics
                elif event.key == pygame.K_s:  # Player 1 boost
                    if player1.boost_other_player(players):
                        score += 50
                elif event.key == pygame.K_DOWN:  # Player 2 boost
                    if player2.boost_other_player(players):
                        score += 50
                elif event.key == pygame.K_k and num_players == 3:  # Player 3 boost
                    if player3.boost_other_player(players):
                        score += 50
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    return cooperative_platformer_game(screen, num_players)
                elif event.key == pygame.K_ESCAPE:
                    return
        
        if not game_over:
            # Check if game should start scrolling (when any player reaches 75% screen height)
            if not game_started:
                highest_player = min(players, key=lambda p: p.y)
                if highest_player.y < SCREEN_HEIGHT * 0.25:  # 75% of screen height means top 25%
                    game_started = True
            
            # Update scroll offset (auto-scrolling) only after game has started
            if game_started:
                scroll_offset += SCROLL_SPEED
            
            # Update players
            for player in players:
                other_players = [p for p in players if p != player]
                player.update(platforms, other_players, scroll_offset)
            
            # Check if any player died
            if not all(player.alive for player in players):
                shared_lives -= 1
                if shared_lives <= 0:
                    game_over = True
                else:
                    # Reset players and continue
                    for i, player in enumerate(players):
                        player.x = 300 + i * 200
                        player.y = 480  # Match new spawn height
                        player.vel_x = 0
                        player.vel_y = 0
                        player.alive = True
                    scroll_offset = 0
                    game_started = False  # Reset scrolling flag
                    platforms.clear()
                    generate_initial_platforms(platforms)
            
            # Generate new platforms as needed
            generate_new_platforms(platforms, scroll_offset)
            
            # Remove platforms that are too far above screen
            platforms = [p for p in platforms if p.y + scroll_offset < SCREEN_HEIGHT + 100]
            
            # Check cooperative platforms for bonus
            coop_bonus = check_cooperative_platforms(players, platforms, scroll_offset)
            
            # Update score based on height
            height_score = int(scroll_offset * 0.1)
            total_player_score = sum(p.score for p in players)
            score = (height_score + total_player_score) * coop_bonus
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw platforms
        for platform in platforms:
            platform.draw(screen, scroll_offset)
        
        # Draw players
        for player in players:
            player.draw(screen)
        
        # Draw connection lines when players can boost
        for i, player1 in enumerate(players):
            for player2 in players[i+1:]:
                if player1.alive and player2.alive:
                    distance = math.sqrt((player1.x - player2.x)**2 + (player1.y - player2.y)**2)
                    if distance < 50:
                        pygame.draw.line(screen, (100, 255, 100), 
                                       (player1.x + player1.width//2, player1.y + player1.height//2),
                                       (player2.x + player2.width//2, player2.y + player2.height//2), 2)
        
        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font.render(f"Lives: {shared_lives}", True, WHITE if shared_lives > 1 else RED)
        screen.blit(lives_text, (10, 50))
        
        # Cooperative bonus indicator
        if coop_bonus > 1:
            bonus_text = font.render(f"COOP x{coop_bonus}!", True, YELLOW)
            screen.blit(bonus_text, (10, 90))
        
        # Controls
        font_small = pygame.font.Font(None, 24)
        controls1 = font_small.render("P1: A/D to move, W to jump, S to boost", True, BLUE)
        controls2 = font_small.render("P2: Arrows to move, Up to jump, Down to boost", True, RED)
        screen.blit(controls1, (10, SCREEN_HEIGHT - 50))
        screen.blit(controls2, (10, SCREEN_HEIGHT - 25))
        
        if num_players == 3:
            controls3 = font_small.render("P3: J/L to move, I to jump, K to boost", True, GREEN)
            screen.blit(controls3, (10, SCREEN_HEIGHT - 75))
        
        if game_over:
            game_over_text = font.render("GAME OVER!", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            restart_text = font.render("Press SPACE to restart or ESC to return to menu", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    return

def generate_initial_platforms(platforms):
    # Starting platform - full width to prevent immediate falls
    platforms.append(Platform(0, 500, SCREEN_WIDTH, PLATFORM_HEIGHT))
    
    # Generate initial platforms with better spacing and no overlaps
    last_x = SCREEN_WIDTH // 2
    last_y = 500
    
    for i in range(30):  # Increased from 20 to 30 platforms
        # Generate platform with minimum distance checks
        attempts = 0
        while attempts < 50:  # Try up to 50 times to find valid position
            # Horizontal spacing: ensure forward progress with reasonable gaps
            x_offset = random.randint(50, 200)  # Only forward, no backward
            new_x = last_x + x_offset
            
            # Wrap around screen to prevent platforms drifting off right edge
            if new_x > SCREEN_WIDTH - PLATFORM_WIDTH - 50:
                new_x = random.randint(50, 200)  # Reset to left side
            
            x = max(50, min(SCREEN_WIDTH - PLATFORM_WIDTH - 50, new_x))
            
            # Vertical spacing: tighter for more platforms
            y_offset = random.randint(40, 70)  # Reduced from 60-100
            y = last_y - y_offset
            
            # Check for overlaps with existing platforms
            valid_position = True
            for platform in platforms:
                if (abs(x - platform.x) < PLATFORM_WIDTH + 20 and 
                    abs(y - platform.y) < PLATFORM_HEIGHT + 20):
                    valid_position = False
                    break
            
            if valid_position:
                platform_type = 'cooperative' if random.random() < 0.15 else 'normal'
                platforms.append(Platform(x, y, platform_type=platform_type))
                last_x = x
                last_y = y
                break
            
            attempts += 1

def generate_new_platforms(platforms, scroll_offset):
    # Generate platforms as screen scrolls
    highest_visible_y = -scroll_offset - 100
    if highest_visible_y < min(p.y for p in platforms):
        last_x = platforms[0].x if platforms else SCREEN_WIDTH // 2
        last_y = min(p.y for p in platforms) if platforms else 0
        
        for i in range(15):  # Increased from 5 to 15 platforms
            # Generate platform with minimum distance checks
            attempts = 0
            while attempts < 50:  # Try up to 50 times to find valid position
                # Horizontal spacing: ensure forward progress with reasonable gaps
                x_offset = random.randint(50, 200)  # Only forward, no backward
                new_x = last_x + x_offset
                
                # Wrap around screen to prevent platforms drifting off right edge
                if new_x > SCREEN_WIDTH - PLATFORM_WIDTH - 50:
                    new_x = random.randint(50, 200)  # Reset to left side
                
                x = max(50, min(SCREEN_WIDTH - PLATFORM_WIDTH - 50, new_x))
                
                # Vertical spacing: tighter for more platforms
                y_offset = random.randint(40, 70)  # Reduced from 60-100
                y = last_y - y_offset - (i * random.randint(20, 40))  # Stagger platforms
                
                # Check for overlaps with existing platforms
                valid_position = True
                for platform in platforms:
                    if (abs(x - platform.x) < PLATFORM_WIDTH + 20 and 
                        abs(y - platform.y) < PLATFORM_HEIGHT + 20):
                        valid_position = False
                        break
                
                if valid_position:
                    platform_type = 'cooperative' if random.random() < 0.15 else 'normal'
                    platforms.append(Platform(x, y, platform_type=platform_type))
                    last_x = x
                    last_y = y
                    break
                
                attempts += 1

def check_cooperative_platforms(players, platforms, scroll_offset):
    # Check if all players are on cooperative platforms for bonus
    players_on_coop = 0
    for player in players:
        if player.alive and any(p.platform_type == 'cooperative' and player.check_collision(p, scroll_offset) 
                              for p in platforms):
            players_on_coop += 1
    
    if len([p for p in players if p.alive]) > 1 and players_on_coop == len([p for p in players if p.alive]):
        return 2  # 2x bonus if all alive players are on cooperative platforms
    else:
        return 1
