import pygame
import sys
import random
import math
from game.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, BLUE, GREEN, GRAY, YELLOW, BLACK, FPS

# Cooperative platformer specific constants
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5
SLIDE_SPEED_MULTIPLIER = 1.5
SLIDE_DURATION = 30  # frames
SLIDE_COOLDOWN = 45  # frames
MOMENTUM_THRESHOLD = 1.5  # seconds of running for meaningful jump boost
MOMENTUM_BUILD_RATE = 1/60  # momentum per frame while running
MOMENTUM_DECAY_RATE = 0.2  # momentum decay rate (reduced from 0.5 for slower decay)
MOMENTUM_JUMP_MULTIPLIER = 0.3  # jump strength bonus per momentum unit
MOMENTUM_MAX = 3.0  # Maximum momentum cap (3 seconds)
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
        
        # Sliding mechanics
        self.is_sliding = False
        self.slide_timer = 0
        self.slide_cooldown = 0
        self.slide_direction = 0  # -1 for left, 1 for right
        
        # Momentum system
        self.momentum = 0.0  # Current momentum in seconds
        self.last_direction = 0  # Last direction moved (-1, 0, 1)
        
        # Edge bouncing
        self.just_bounced = False
        self.bounce_cooldown = 0
        
        # Boost flag to prevent simultaneous jump
        self.boosting = False
        
    def update(self, platforms, other_players, scroll_offset):
        if not self.alive:
            return
            
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Handle cooldowns
        if self.slide_cooldown > 0:
            self.slide_cooldown -= 1
            
        if self.bounce_cooldown > 0:
            self.bounce_cooldown -= 1
            if self.bounce_cooldown == 0:
                self.just_bounced = False
        
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
                    
        # Update momentum based on movement and collision state
        if not self.is_sliding:
            current_direction = 0
            if keys[self.controls['left']]:
                current_direction = -1
            elif keys[self.controls['right']]:
                current_direction = 1
            
            # Build momentum when running on ground or platforms
            if current_direction != 0 and self.on_ground:
                self.momentum += MOMENTUM_BUILD_RATE
                self.momentum = min(self.momentum, MOMENTUM_MAX)  # Cap momentum at maximum
                self.last_direction = current_direction
            else:
                # Decay momentum when not running or in air
                if self.momentum > 0:
                    self.momentum -= MOMENTUM_DECAY_RATE / 60
                    self.momentum = max(0, self.momentum)
        
        # Handle sliding state
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False
                self.slide_direction = 0
                self.momentum = 0  # Reset momentum after slide
        
        # Calculate movement for NEXT frame
        if self.is_sliding:
            # Use momentum-based sliding speed (legacy cooperative slide boost)
            momentum_boost = 1.0 + (self.momentum - MOMENTUM_THRESHOLD) * 0.3
            slide_speed = MOVE_SPEED * SLIDE_SPEED_MULTIPLIER * momentum_boost
            self.vel_x = self.slide_direction * slide_speed
        else:
            # Normal movement with small momentum speed boost
            base_speed = MOVE_SPEED
            if self.momentum > 0:
                speed_boost = 1.0 + (self.momentum * 0.1)  # Small speed boost while building momentum
                base_speed *= speed_boost
                
            self.vel_x = 0
            if keys[self.controls['left']]:
                self.vel_x = -base_speed
            if keys[self.controls['right']]:
                self.vel_x = base_speed
                
        # Handle jumping
        is_jump_pressed = keys[self.controls['jump']]
        is_boost_pressed = keys[self.controls['boost']] if 'boost' in self.controls else False
        
        if is_jump_pressed and self.on_ground and not self.is_sliding and not self.boosting and not is_boost_pressed:
            # Momentum-boosted jumping
            jump_multiplier = 1.0
            if self.momentum > 0:
                jump_multiplier = 1.0 + (self.momentum * MOMENTUM_JUMP_MULTIPLIER)
                # Consume momentum on jump
                self.momentum = 0
            
            self.vel_y = JUMP_STRENGTH * jump_multiplier
        
        # Reset boost flag after processing
        self.boosting = False
                    
        # Screen boundaries with edge bouncing
        previous_x = self.x
        
        if self.x < 0:
            self.x = 0
            if previous_x != self.x and not self.just_bounced and self.vel_x < 0:
                # Bounce off left edge
                bounce_force = abs(self.vel_x) * 0.8  # Preserve 80% of momentum
                self.vel_x = bounce_force
                # Add upward boost proportional to momentum
                vertical_boost = min(self.momentum * 2, 5)  # Cap the boost
                self.vel_y = min(self.vel_y, -vertical_boost)
                # Reduce momentum slightly
                self.momentum *= 0.9
                self.just_bounced = True
                self.bounce_cooldown = 5  # Prevent jitter
                
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            if previous_x != self.x and not self.just_bounced and self.vel_x > 0:
                # Bounce off right edge
                bounce_force = abs(self.vel_x) * 0.8  # Preserve 80% of momentum
                self.vel_x = -bounce_force
                # Add upward boost proportional to momentum
                vertical_boost = min(self.momentum * 2, 5)  # Cap the boost
                self.vel_y = min(self.vel_y, -vertical_boost)
                # Reduce momentum slightly
                self.momentum *= 0.9
                self.just_bounced = True
                self.bounce_cooldown = 5  # Prevent jitter
            
        # Update cooldowns
        if self.boost_cooldown > 0:
            self.boost_cooldown -= 1
            
        # Check for cooperative boost
        self.check_cooperative_boost(other_players)
        
        # Check for slide boost interactions
        self.check_slide_boost(other_players)
        
        # Check if player fell off screen (game over condition)
        if self.y > SCREEN_HEIGHT:
            self.alive = False
            
    def check_collision(self, platform, scroll_offset):
        platform_y = platform.y + scroll_offset
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform_y + platform.height and
                self.y + self.height > platform_y)
                
    def start_slide(self, direction):
        """Initiate sliding in the given direction (-1 for left, 1 for right)"""
        self.is_sliding = True
        self.slide_direction = direction
        self.slide_timer = SLIDE_DURATION
        self.slide_cooldown = SLIDE_COOLDOWN
        
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
                
    def check_slide_boost(self, other_players):
        """Check for cooperative slide boost - sliding into another player gives them speed"""
        if self.is_sliding:
            for other_player in other_players:
                if other_player.player_id != self.player_id and other_player.alive:
                    distance = math.sqrt((self.x - other_player.x)**2 + (self.y - other_player.y)**2)
                    if distance < 40:  # Close contact for slide boost
                        # Give the other player a horizontal speed boost
                        other_player.vel_x = self.slide_direction * MOVE_SPEED * SLIDE_SPEED_MULTIPLIER * 1.2
                        # Add small vertical boost for fun
                        other_player.vel_y = min(other_player.vel_y, JUMP_STRENGTH * 0.5)
                        # End slide after boost
                        self.is_sliding = False
                        self.slide_direction = 0
                        return True
        return False
            
    def boost_other_player(self, other_players):
        if self.can_boost and self.on_ground:  # Still require on_ground for actual boost
            # Set boost flag to prevent jumping this frame
            self.boosting = True
            
            # Always boost other players, never self
            if not other_players:
                return False
                
            # Find the closest alive player to boost
            closest_player = None
            min_distance = float('inf')
            
            print(f"\n=== Player {self.player_id} attempting boost ===")
            print(f"Player {self.player_id} position: ({self.x}, {self.y})")
            
            for other_player in other_players:
                if other_player.player_id != self.player_id and other_player.alive:
                    distance = math.sqrt((self.x - other_player.x)**2 + (self.y - other_player.y)**2)
                    print(f"Distance to player {other_player.player_id}: {distance:.2f} (position: {other_player.x}, {other_player.y})")
                    if distance < 50 and distance < min_distance:
                        min_distance = distance
                        closest_player = other_player
            
            if closest_player:
                print(f"-> Boosting player {closest_player.player_id} (closest at {min_distance:.2f})")
                print(f"Before boost: Player {self.player_id} vel_y: {self.vel_y}, Player {closest_player.player_id} vel_y: {closest_player.vel_y}")
                closest_player.vel_y = JUMP_STRENGTH * 1.5  # Super jump
                print(f"After boost: Player {self.player_id} vel_y: {self.vel_y}, Player {closest_player.player_id} vel_y: {closest_player.vel_y}")
                self.boost_cooldown = 42  # 0.7 second cooldown (30% reduction from 60)
                return True
            else:
                print("-> No valid target to boost (no one within 50 units)")
                # Reset boost flag if no target found
                self.boosting = False
        return False
        
    def draw(self, screen):
        if not self.alive:
            return
            
        # Draw player with sliding effect
        if self.is_sliding:
            # Draw elongated sliding rectangle
            slide_width = int(self.width * 1.5)
            slide_height = int(self.height * 0.7)
            slide_x = self.x - (slide_width - self.width) // 2
            slide_y = self.y + (self.height - slide_height) // 2
            pygame.draw.rect(screen, self.color, (slide_x, slide_y, slide_width, slide_height))
            # Add motion lines
            for i in range(3):
                line_x = slide_x - 10 - i * 5 if self.slide_direction == -1 else slide_x + slide_width + 10 + i * 5
                pygame.draw.line(screen, (*self.color, 128), 
                               (line_x, slide_y + slide_height // 2),
                               (line_x - 5 * self.slide_direction, slide_y + slide_height // 2), 2)
        else:
            # Draw player with momentum glow effect
            if self.momentum >= MOMENTUM_THRESHOLD * 0.8:
                # Draw glow effect for high momentum
                glow_size = 2
                glow_color = (*self.color, 50)
                for i in range(glow_size):
                    pygame.draw.rect(screen, glow_color, 
                                   (self.x - (i+1)*2, self.y - (i+1)*2, 
                                    self.width + (i+1)*4, self.height + (i+1)*4), 2)
            
            # Draw bounce effect
            if self.just_bounced:
                # Draw bounce flash
                pygame.draw.rect(screen, (255, 255, 255, 100), 
                               (self.x - 3, self.y - 3, self.width + 6, self.height + 6), 3)
            
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # Draw momentum indicator
            if self.momentum > 0 and not self.is_sliding:
                bar_width = 30
                bar_height = 4
                bar_x = self.x + (self.width - bar_width) // 2
                bar_y = self.y - 8
                # Background
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                # Momentum fill
                fill_width = int((self.momentum / MOMENTUM_THRESHOLD) * bar_width)
                fill_color = (0, 255, 255) if self.momentum >= MOMENTUM_THRESHOLD * 0.8 else (255, 165, 0)
                pygame.draw.rect(screen, fill_color, (bar_x, bar_y, min(fill_width, bar_width), bar_height))
        
        # Draw boost indicator
        if self.can_boost:
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.x + self.width//2), int(self.y - 15)), 5)
            # Draw boost prompt with background to prevent flicker
            font_small = pygame.font.Font(None, 20)
            boost_key_map = {1: "S", 2: "DOWN", 3: "K"}
            boost_key = boost_key_map.get(self.player_id, "?")
            prompt_text = font_small.render(f"Press {boost_key}", True, YELLOW)
            # Create a small background rectangle for the text
            text_rect = prompt_text.get_rect()
            text_rect.topleft = (self.x - 10, self.y - 35)
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
    print(f"After init: player1 ID: {player1.player_id}, color: {player1.color}, controls: {player1.controls}")
    
    # Add second player if num_players is 2
    if num_players > 1:
        player2 = Player(500, 480, RED, 
                        {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'boost': pygame.K_DOWN}, 2)
        players.append(player2)
        print(f"After init: player2 ID: {player2.player_id}, color: {player2.color}, controls: {player2.controls}")
    
    
    
    # Add third player if num_players is 3
    if num_players > 2:
        player3 = Player(400, 480, GREEN, 
                        {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_i, 'boost': pygame.K_k}, 3)
        players.append(player3)
        print(f"After init: player3 ID: {player3.player_id}, color: {player3.color}, controls: {player3.controls}")
    
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
                    # Find player 1 by ID (should be the blue player)
                    player1 = None
                    for p in players:
                        if p.player_id == 1:
                            player1 = p
                            break
                    if player1:
                        print(f"S key pressed - calling boost on player1 (ID: {player1.player_id})")
                        if player1.boost_other_player(players):
                            score += 50
                elif event.key == pygame.K_DOWN and num_players > 1:  # Player 2 boost
                    # Find player 2 by ID (should be the red player)
                    player2 = None
                    for p in players:
                        if p.player_id == 2:
                            player2 = p
                            break
                    if player2:
                        print(f"DOWN key pressed - calling boost on player2 (ID: {player2.player_id})")
                        if player2.boost_other_player(players):
                            score += 50
                elif event.key == pygame.K_k and num_players == 3:  # Player 3 boost
                    # Find player 3 by ID (should be the green player)
                    player3 = None
                    for p in players:
                        if p.player_id == 3:
                            player3 = p
                            break
                    if player3:
                        print(f"K key pressed - calling boost on player3 (ID: {player3.player_id})")
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
                # Calculate dynamic scroll speed based on score
                # 0.1% increase per point (base speed 2, so 0.002 per point)
                speed_multiplier = 1 + (score * 0.001)
                dynamic_scroll_speed = SCROLL_SPEED * speed_multiplier
                
                # Cap the maximum scroll speed to prevent it from becoming impossible
                max_scroll_speed = SCROLL_SPEED * 5  # Maximum 5x base speed
                dynamic_scroll_speed = min(dynamic_scroll_speed, max_scroll_speed)
                
                scroll_offset += dynamic_scroll_speed
            
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
        for i, player_a in enumerate(players):
            for player_b in players[i+1:]:
                if player_a.alive and player_b.alive:
                    distance = math.sqrt((player_a.x - player_b.x)**2 + (player_a.y - player_b.y)**2)
                    if distance < 50:
                        pygame.draw.line(screen, (100, 255, 100), 
                                       (player_a.x + player_a.width//2, player_a.y + player_a.height//2),
                                       (player_b.x + player_b.width//2, player_b.y + player_b.height//2), 2)
        
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
        
        # Momentum instructions
        momentum_text = font_small.render("Build momentum for super jumps & edge bounces!", True, (0, 255, 255))
        screen.blit(momentum_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 25))
        
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
    
    # Generate just enough platforms for the starting screen (8-10 platforms)
    last_x = SCREEN_WIDTH // 2
    last_y = 500
    
    # Generate platforms to fill about 2 screens worth of initial gameplay
    # 20% more platforms at lower levels (increased from 9 to 11)
    target_platforms = 11
    for i in range(target_platforms):
        # Use lane-based horizontal positioning for better distribution
        lanes = [150, 300, 450, 600]  # 4 horizontal lanes
        target_lane = random.choice(lanes)
        
        # Add some randomness to the lane position
        x = target_lane + random.randint(-30, 30)
        x = max(50, min(SCREEN_WIDTH - PLATFORM_WIDTH - 50, x))
        
        # Vertical spacing with consistent density (about 70 units apart)
        y_offset = random.randint(60, 80)
        y = last_y - y_offset
        
        # Calculate platform width based on height (wider at lower levels)
        height_factor = max(0, 500 - y) / 1000  # 0 to 0.5 based on height
        width_multiplier = 1.8 - height_factor * 0.5  # 1.8x at bottom (30% wider), 1.3x at top
        platform_width = int(PLATFORM_WIDTH * width_multiplier)
        platform_width = max(90, min(platform_width, 180))  # Clamp between 90 and 180
        
        # Check for overlaps with existing platforms
        valid_position = True
        for platform in platforms:
            if (abs(x - platform.x) < platform_width + 20 and 
                abs(y - platform.y) < PLATFORM_HEIGHT + 20):
                valid_position = False
                break
        
        if valid_position:
            platform_type = 'cooperative' if random.random() < 0.15 else 'normal'
            platforms.append(Platform(x, y, platform_width, PLATFORM_HEIGHT, platform_type))
            last_x = x
            last_y = y
        else:
            # Try again if position is invalid
            i -= 1

def generate_new_platforms(platforms, scroll_offset):
    # Rolling window approach: maintain platforms within viewable range
    # Spawn platforms only when needed, based on highest player position
    
    # Find the highest platform
    if not platforms:
        return
    
    highest_platform = min(platforms, key=lambda p: p.y)
    highest_platform_y = highest_platform.y
    
    # Check if we need to spawn more platforms
    # Spawn when highest platform is less than 200 units above the top of screen
    # At lower levels, spawn more frequently (20% more density)
    # At higher levels, spawn even faster to keep up with climbing
    spawn_threshold = -scroll_offset + 150  # Reduced from 200 for faster spawning
    
    # Adjust spawn threshold based on height for dynamic platform density
    if highest_platform_y > 0:  # Still in lower half
        spawn_threshold = -scroll_offset + 200  # Spawn earlier at lower levels
    elif highest_platform_y < -500:  # Higher levels - spawn much faster
        spawn_threshold = -scroll_offset + 80  # Spawn much earlier at high levels
    elif highest_platform_y < -200:  # Mid-high levels
        spawn_threshold = -scroll_offset + 100  # Spawn earlier at mid-high levels
    
    if highest_platform_y > spawn_threshold:
        # Spawn 1-2 platforms at a time to maintain consistent density
        # Increased chance for 2 platforms for even faster spawning
        platforms_to_spawn = 2 if random.random() < 0.6 else 1  # 60% chance for 2 platforms
        
        for _ in range(platforms_to_spawn):
            # Use lane-based system for consistent horizontal distribution
            lanes = [150, 300, 450, 600]  # 4 horizontal lanes
            target_lane = random.choice(lanes)
            
            # Add some randomness to the lane position
            x = target_lane + random.randint(-30, 30)
            x = max(50, min(SCREEN_WIDTH - PLATFORM_WIDTH - 50, x))
            
            # Vertical spacing based on target density (70 units on average)
            y_offset = random.randint(60, 80)
            y = highest_platform_y - y_offset
            
            # Calculate platform width based on height (wider at lower levels)
            # Use absolute height from starting position
            absolute_height = 500 + y  # Convert to world coordinates
            height_factor = max(0, absolute_height) / 2000  # 0 to 0.5 based on height
            width_multiplier = 1.8 - height_factor * 0.5  # 1.8x at bottom (30% wider), 1.3x higher up
            platform_width = int(PLATFORM_WIDTH * width_multiplier)
            platform_width = max(80, min(platform_width, 180))  # Clamp between 80 and 180
            
            # Check for overlaps with existing platforms
            valid_position = True
            for platform in platforms:
                if (abs(x - platform.x) < platform_width + 20 and 
                    abs(y - platform.y) < PLATFORM_HEIGHT + 20):
                    valid_position = False
                    break
            
            if valid_position:
                platform_type = 'cooperative' if random.random() < 0.15 else 'normal'
                platforms.append(Platform(x, y, platform_width, PLATFORM_HEIGHT, platform_type))
                highest_platform_y = y  # Update for next platform

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
