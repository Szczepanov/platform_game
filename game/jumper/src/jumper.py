import pygame
import sys
import random
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, BLUE, GRAY, YELLOW, GREEN, PLAYERS

class Bird:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.velocity = 0
        self.color = color
        self.controls = controls
        self.size = 30
        self.gravity = 0.5
        self.jump_strength = -8
        self.alive = True
        
    def update(self):
        if self.alive:
            self.velocity += self.gravity
            self.y += self.velocity
            
            # Keep bird on screen
            if self.y < 0:
                self.y = 0
                self.velocity = 0
            elif self.y > SCREEN_HEIGHT - self.size:
                self.y = SCREEN_HEIGHT - self.size
                self.velocity = 0
                
    def jump(self):
        if self.alive:
            self.velocity = self.jump_strength
            
    def draw(self, screen, invincibility_timer=0):
        if self.alive:
            # Flash during invincibility
            if invincibility_timer > 0 and invincibility_timer % 10 < 5:
                return  # Skip drawing every few frames for flashing effect
            
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
            # Draw eye
            pygame.draw.circle(screen, WHITE, (int(self.x + 5), int(self.y - 5)), 3)
            
            # Draw invincibility shield
            if invincibility_timer > 0:
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size // 2 + 5, 2)

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type  # "extra_life" or "invincibility"
        self.size = 25
        self.speed = 3
        self.collected = False
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        if not self.collected:
            if self.type == "extra_life":
                # Draw heart shape for extra life
                pygame.draw.circle(screen, RED, (int(self.x - 5), int(self.y)), 8)
                pygame.draw.circle(screen, RED, (int(self.x + 5), int(self.y)), 8)
                pygame.draw.polygon(screen, RED, [
                    (int(self.x - 12), int(self.y - 2)),
                    (int(self.x), int(self.y + 12)),
                    (int(self.x + 12), int(self.y - 2))
                ])
            elif self.type == "invincibility":
                # Draw shield shape for invincibility
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size // 2, 3)
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 5)
                
    def collides_with(self, bird):
        if self.collected or not bird.alive:
            return False
            
        bird_rect = pygame.Rect(bird.x - bird.size // 2, bird.y - bird.size // 2, bird.size, bird.size)
        powerup_rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        
        return bird_rect.colliderect(powerup_rect)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 80
        self.gap = 200
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 100 - self.gap)
        self.speed = 3
        self.passed = False
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.gap_y))
        # Draw bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.gap_y + self.gap, self.width, SCREEN_HEIGHT - self.gap_y - self.gap))
        
    def collides_with(self, bird):
        if not bird.alive:
            return False
            
        bird_rect = pygame.Rect(bird.x - bird.size // 2, bird.y - bird.size // 2, bird.size, bird.size)
        top_pipe_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_pipe_rect = pygame.Rect(self.x, self.gap_y + self.gap, self.width, SCREEN_HEIGHT - self.gap_y - self.gap)
        
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)

def floppy_bird_game(screen, num_players=2):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Initialize birds
    birds = []
    colors = [RED, BLUE, GRAY]
    start_x = SCREEN_WIDTH // 4
    
    for i in range(num_players):
        y_pos = SCREEN_HEIGHT // 2 + (i - num_players // 2) * 60
        bird = Bird(start_x, y_pos, colors[i], list(PLAYERS.values())[i])
        birds.append(bird)
    
    pipes = []
    powerups = []
    pipe_timer = 0
    score = 0
    game_over = False
    shared_lives = 3
    max_lives = 6
    invincibility_timer = 0
    powerup_spawn_counter = 0
    collection_message = ""
    collection_message_timer = 0
    
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
                for bird in birds:
                    if event.key == bird.controls['up']:
                        bird.jump()
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    return floppy_bird_game(screen, num_players)
                elif event.key == pygame.K_ESCAPE:
                    return
        
        if not game_over:
            # Update cooldowns and timers
            if invincibility_timer > 0:
                invincibility_timer -= 1
            if collection_message_timer > 0:
                collection_message_timer -= 1
            
            # Update birds
            for bird in birds:
                bird.update()
            
            # Generate pipes
            pipe_timer += 1
            if pipe_timer > 90:  # Generate pipe every 1.5 seconds at 60 FPS
                pipes.append(Pipe(SCREEN_WIDTH))
                pipe_timer = 0
                
                # Increment powerup counter when spawning pipes
                powerup_spawn_counter += 1
                if powerup_spawn_counter >= 5:  # Every 5 pipes, spawn a powerup
                    powerup_spawn_counter = 0
                    if len(pipes) >= 2:
                        # Calculate midpoint between the last two pipes
                        last_pipe = pipes[-1]
                        second_last_pipe = pipes[-2]
                        powerup_x = (last_pipe.x + second_last_pipe.x) // 2
                        
                        # Spawn powerup in safe area (middle of screen, no pipes above/below)
                        powerup_y = SCREEN_HEIGHT // 2  # Center of screen is always safe
                        powerup_type = random.choice(["extra_life", "invincibility"])
                        powerups.append(PowerUp(powerup_x, powerup_y, powerup_type))
            
            # Update pipes and powerups
            pipes_to_remove = []
            powerups_to_remove = []
            
            # Update powerups
            for powerup in powerups:
                powerup.update()
                
                # Check powerup collisions
                for bird in birds:
                    if powerup.collides_with(bird):
                        powerup.collected = True
                        if powerup.type == "extra_life":
                            if shared_lives < max_lives:
                                shared_lives += 1
                                collection_message = "EXTRA LIFE!"
                                collection_message_timer = 120
                            else:
                                collection_message = "MAX LIVES!"
                                collection_message_timer = 60
                        elif powerup.type == "invincibility":
                            invincibility_timer += 180  # Add 3 seconds at 60 FPS
                            collection_message = "INVINCIBILITY!"
                            collection_message_timer = 120
                        powerups_to_remove.append(powerup)
                        break
                
                # Remove off-screen powerups
                if powerup.x + powerup.size < 0:
                    powerups_to_remove.append(powerup)
            
            for pipe in pipes:
                pipe.update()
                
                # Check collisions (only if not invincible)
                if invincibility_timer == 0:
                    collision_occurred = False
                    for bird in birds:
                        if pipe.collides_with(bird):
                            shared_lives -= 1
                            invincibility_timer = 90  # 1.5 seconds of invincibility
                            collision_occurred = True
                            if shared_lives <= 0:
                                game_over = True
                            else:
                                # Reset bird positions and mark pipes for removal
                                for i, b in enumerate(birds):
                                    b.y = SCREEN_HEIGHT // 2 + (i - len(birds) // 2) * 60
                                    b.velocity = 0
                            break
                    
                    if collision_occurred:
                        # Clear pipes that are too close to the starting position
                        pipes_to_remove = [pipe for pipe in pipes if pipe.x <= start_x + 100]
                        # Clear powerups that are too close to the starting position
                        powerups_to_remove.extend([powerup for powerup in powerups if powerup.x <= start_x + 100])
                        break
                
                # Check if pipe passed birds
                if not pipe.passed and pipe.x + pipe.width < start_x:
                    pipe.passed = True
                    score += 1
                
                # Mark off-screen pipes for removal
                if pipe.x + pipe.width < 0:
                    pipes_to_remove.append(pipe)
            
            # Remove marked pipes and powerups
            for pipe in pipes_to_remove:
                if pipe in pipes:
                    pipes.remove(pipe)
            for powerup in powerups_to_remove:
                if powerup in powerups:
                    powerups.remove(powerup)
        
        # Draw everything
        screen.fill((135, 206, 235))  # Sky blue
        
        # Draw pipes
        for pipe in pipes:
            pipe.draw(screen)
            
        # Draw powerups
        for powerup in powerups:
            powerup.draw(screen)
        
        # Draw birds
        for bird in birds:
            bird.draw(screen, invincibility_timer)
        
        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font.render(f"Lives: {shared_lives}", True, WHITE if shared_lives > 1 else RED)
        screen.blit(lives_text, (10, 50))
        
        # Draw player controls
        controls_y = 100
        for i, bird in enumerate(birds):
            control_text = pygame.font.Font(None, 24).render(
                f"Player {i+1}: {pygame.key.name(bird.controls['up']).upper()}", 
                True, bird.color
            )
            screen.blit(control_text, (10, controls_y + i * 25))
        
        # Draw collection message
        if collection_message_timer > 0:
            message_font = pygame.font.Font(None, 48)
            message_color = RED if "EXTRA LIFE" in collection_message else YELLOW if "INVINCIBILITY" in collection_message else ORANGE
            message_text = message_font.render(collection_message, True, message_color)
            screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, SCREEN_HEIGHT // 3))
        
        if game_over:
            game_over_text = font.render("GAME OVER!", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            restart_text = font.render("Press SPACE to restart or ESC to return to menu", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    return

def jumper_game(screen, num_players=2):
    floppy_bird_game(screen, num_players)
