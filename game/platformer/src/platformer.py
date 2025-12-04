import pygame
import sys
import random
import time
from utils.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, GREEN, VIOLET, ORANGE, PLAYERS, POWERUP_SPAWN_INTERVAL, MAX_POWERUPS)
from typing import Optional, List, Dict, Any
from common import PowerUpType 


class SwitchPlayers(PowerUpType):
    def __init__(self):
        super().__init__(name='Switch Players')

    def __repr__(self):
        return self.name


class DoubleScore(PowerUpType):
    def __init__(self):
        super().__init__(name='Double Score')

    def __repr__(self):
        return self.name


class Invincibility(PowerUpType):
    def __init__(self):
        super().__init__(name='Invincibility')

    def __repr__(self):
        return self.name


class ShapeShift(PowerUpType):
    def __init__(self):
        super().__init__(name='Shape Shift')

    def __repr__(self):
        return self.name


class CoinSize(PowerUpType):
    def __init__(self):
        super().__init__(name='Coin Size')

    def __repr__(self):
        return self.name


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor=1.0):
        super().__init__()
        self.base_size = 20
        self.scale_factor = scale_factor
        self.update_size()
        self.rect = self.image.get_rect(center=(x, y))
    
    def update_size(self):
        """Update coin surface based on current scale_factor"""
        new_size = int(self.base_size * self.scale_factor)
        self.image = pygame.Surface((new_size, new_size))
        self.image.fill(YELLOW)  # Yellow color
    
    def set_scale(self, scale_factor):
        """Set new scale factor and update coin size"""
        self.scale_factor = scale_factor
        self.update_size()
        # Update rect to maintain center position
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.original_image = pygame.Surface((width, height))
        self.original_image.fill(GREEN)  # Green color
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

        # Blinking attributes
        self.blinking = True
        self.blink_start_time = time.time()
        self.blink_duration = 2  # seconds
        self.blink_interval = 0.5  # seconds
        self.last_blink_time = self.blink_start_time
        self.visible = True

    def update(self):
        if self.blinking:
            current_time = time.time()

            # Check if blinking duration is over
            if current_time - self.blink_start_time >= self.blink_duration:
                self.blinking = False
                self.image = self.original_image
                self.visible = True
            else:
                # Toggle visibility based on blink_interval
                if current_time - self.last_blink_time >= self.blink_interval:
                    self.visible = not self.visible
                    self.last_blink_time = current_time
                    if self.visible:
                        self.image = self.original_image
                    else:
                        # Make the platform semi-transparent or invisible
                        self.image = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
                        self.image.fill((0, 0, 0, 0))  # Fully transparent
        else:
            # Ensure the platform is fully visible when not blinking
            self.image = self.original_image
            self.visible = True


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(VIOLET)
        self.rect = self.image.get_rect(center=(x, y))
        self.powerup_type = powerup_type  # The type of power-up


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls: Dict[str, Any], color):
        super().__init__()
        self.original_color = color
        self.current_color = color
        self.original_width = 50
        self.original_height = 50
        self.image = pygame.Surface((self.original_width, self.original_height), pygame.SRCALPHA)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 0
        self.controls = controls
        self.original_controls = controls
        self.key_pressed = {key: False for key in controls.values()}
        self.shape = 'rectangle'  # Default shape
        self.scale_factor = 1.0    # Default scale

        self.update_image()  # Initialize the image with the default shape

    def change_color(self, color):
        self.current_color = color
        self.update_image()

    def set_controls(self, new_controls):
        """Update the player's controls and reset key_pressed."""
        self.controls = new_controls
        self.key_pressed = {key: False for key in self.controls.values()}

    def reset_color(self):
        self.current_color = self.original_color
        self.update_image()

    def change_shape_and_size(self, shape: str, scale_factor: float):
        """Change the player's shape and size."""
        self.shape = shape
        self.scale_factor = scale_factor
        self.update_image()

    def reset_shape_and_size(self):
        """Reset the player's shape and size to original."""
        self.shape = 'rectangle'
        self.scale_factor = 1.0
        self.update_image()

    def update_image(self):
        """Redraw the player's image based on the current shape and size."""
        # Calculate new size
        width = int(self.original_width * self.scale_factor)
        height = int(self.original_height * self.scale_factor)

        # Create a new surface with the calculated size
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw the current shape
        if self.shape == 'circle':
            pygame.draw.circle(self.image, self.current_color, (width // 2, height // 2), min(width, height) // 2)
        elif self.shape == 'triangle':
            points = [
                (width // 2, 0),
                (0, height),
                (width, height)
            ]
            pygame.draw.polygon(self.image, self.current_color, points)
        else:  # Default rectangle
            self.image.fill(self.current_color)

        # Update the rect to maintain the center position
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.vel_y += 0.5  # Gravity
        self.rect.y += int(self.vel_y)

        # Move left/right
        keys = pygame.key.get_pressed()
        if keys[self.controls['left']]:
            self.rect.x -= 5
        if keys[self.controls['right']]:
            self.rect.x += 5

        # Jump
        if keys[self.controls['up']] and not self.key_pressed.get(self.controls['up']):
            self.vel_y = - 10

        for control in self.controls.values():
            if keys[control]:
                if not self.key_pressed.get(control, False):
                    self.key_pressed[control] = True
            else:
                self.key_pressed[control] = False

        if self.rect.left < -int(self.rect.width / 2):
            self.rect.left = -int(self.rect.width / 2)
        if self.rect.right > int(SCREEN_WIDTH + self.rect.width / 2):
            self.rect.right = int(SCREEN_WIDTH + self.rect.width / 2)
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Game:
    def __init__(self, players: List[Player] = None, power_ups: List[PowerUp] = None, coins: List[Coin] = None,
                 platforms: List[Platform] = None):
        self.level = 1
        self.active_powerups = {}  # Dictionary to track multiple active powerups {powerup_type: start_time}
        self.total_score = 0
        self.best_score = self.total_score
        self.players = [] if players is None else players
        self.power_ups = [] if power_ups is None else power_ups
        self.coins = [] if coins is None else coins
        self.platforms = [] if platforms is None else platforms
        self.power_up_spawn_time = time.time()
        self.coin_spawn_time = time.time()
        self._last_score = 0

    def spawn_coins(self):
        # Spawn coins
        if time.time() - self.coin_spawn_time > 0.2 and len(self.coins) < 10:
            coin_x = random.randint(0, SCREEN_WIDTH)
            coin_y = random.randint(0, SCREEN_HEIGHT)
            # Check if DoubleScore is active
            double_score_active = any(isinstance(powerup_instance, DoubleScore) and time.time() - start_time <= 10 
                                     for powerup_instance, start_time in self.active_powerups.items())
            # Check if CoinSize is active
            coin_size_active = any(isinstance(powerup_instance, CoinSize) and time.time() - start_time <= 10 
                                     for powerup_instance, start_time in self.active_powerups.items())
            
            # Create coin with appropriate scale
            coin_scale = 3.0 if coin_size_active else 1.0
            coin = Coin(coin_x, coin_y, scale_factor=coin_scale)
            
            if double_score_active:
                coin.image.fill(ORANGE)
            else:
                coin.image.fill(YELLOW)
            # Check if coin is spawned inside a platform
            if not any(coin.rect.colliderect(platform.rect) for platform in self.platforms):
                self.coins.append(coin)
                self.coin_spawn_time = time.time()

    def spawn_power_ups(self):
        # Spawn power-ups
        if time.time() - self.power_up_spawn_time > POWERUP_SPAWN_INTERVAL and len(self.power_ups) < MAX_POWERUPS:
            # Try to find a non-overlapping position
            max_attempts = 10
            for _ in range(max_attempts):
                power_up_x = random.randint(0, SCREEN_WIDTH)
                power_up_y = random.randint(0, SCREEN_HEIGHT)
                
                # Check if position overlaps with existing powerups
                new_powerup_rect = pygame.Rect(power_up_x, power_up_y, 30, 30)  # Assuming powerup size is 30x30
                overlaps = any(new_powerup_rect.colliderect(power_up.rect) for power_up in self.power_ups)
                
                if not overlaps:
                    power_up = PowerUp(power_up_x, power_up_y, random.choice([DoubleScore(), Invincibility(), SwitchPlayers(), ShapeShift(), CoinSize()]))
                    self.power_ups.append(power_up)
                    self.power_up_spawn_time = time.time()
                    break  # Exit loop after successful spawn

    def spawn_platforms(self):
        if self.total_score // 20 > self._last_score // 20:
            self.platforms.append(Platform(random.randint(0, SCREEN_WIDTH - 100),
                                           random.randint(0, SCREEN_HEIGHT - 10),
                                           100,
                                           10))
            self._last_score = self.total_score

    def switch_player_controls(self):
        temp_controls = self.players[-1].controls.copy()
        for i in range(len(self.players) - 1, 0, -1):
            self.players[i].set_controls(self.players[i-1].controls.copy())
        self.players[0].set_controls(temp_controls.copy())

    def reset_player_controls(self):
        """Reset all player controls to their original values."""
        for player in self.players:
            player.controls = player.original_controls

    def update(self):
        """Advances game state by spawning platforms, updating entities, and handling collisions and power-ups."""
        self.spawn_platforms()

        # Update each platform's blinking state
        for platform in self.platforms:
            platform.update()

        for player_nr, player in enumerate(self.players):
            player.update()
            for platform in self.platforms:
                if pygame.sprite.collide_rect(player, platform):
                    # Check if Invincibility is active
                    invincibility_active = any(isinstance(powerup_instance, Invincibility) and time.time() - start_time <= 10 
                                             for powerup_instance, start_time in self.active_powerups.items())
                    # Only reset the game if the platform is not blinking and player is not invincible
                    if not platform.blinking and not invincibility_active:
                        self.reset_game()
            for power_up in self.power_ups:
                if pygame.sprite.collide_rect(player, power_up):
                    self.active_powerups[power_up.powerup_type] = time.time()  # Store powerup instance as key

                    # Apply the power-up effects for newly collected powerup only
                    if isinstance(power_up.powerup_type, Invincibility):
                        for p in self.players:
                            p.change_color(WHITE)
                    elif isinstance(power_up.powerup_type, SwitchPlayers):
                        self.switch_player_controls()
                    elif isinstance(power_up.powerup_type, DoubleScore):
                        for coin in self.coins:
                            coin.image.fill(ORANGE)
                    elif isinstance(power_up.powerup_type, CoinSize):
                        for coin in self.coins:
                            coin.set_scale(3.0)
                    elif isinstance(power_up.powerup_type, ShapeShift):
                        # Choose random shape
                        shape = random.choice(['circle', 'triangle'])
                        # Choose size adjustment
                        size_change = random.choice(['increase', 'decrease'])
                        if size_change == 'increase':
                            scale_factor = 1.1  # Increase size by 10%
                        else:
                            scale_factor = 0.7  # Decrease size by 30%
                        # Apply to all players
                        for p in self.players:
                            p.change_shape_and_size(shape, scale_factor)
                    
                    # After applying new powerup effects, ensure CoinSize coins stay 3x bigger and DoubleScore coins stay orange if still active
                    double_score_active = any(isinstance(powerup_instance, DoubleScore) for powerup_instance in self.active_powerups.keys())
                    coin_size_active = any(isinstance(powerup_instance, CoinSize) for powerup_instance in self.active_powerups.keys())
                    
                    # Apply scaling first
                    if coin_size_active:
                        for coin in self.coins:
                            coin.set_scale(3.0)
                    
                    # Apply color last to prevent overwriting
                    if double_score_active:
                        for coin in self.coins:
                            coin.image.fill(ORANGE)

                    self.power_ups.remove(power_up)
            # Handle power-up durations
            expired_powerups = []
            for powerup_type, start_time in self.active_powerups.items():
                if time.time() - start_time > 10:
                    expired_powerups.append(powerup_type)
                    
            # Remove expired powerups and reset their effects
            for powerup_instance in expired_powerups:
                if isinstance(powerup_instance, SwitchPlayers):
                    self.reset_player_controls()
                elif isinstance(powerup_instance, DoubleScore):
                    for coin in self.coins:
                        coin.image.fill(YELLOW)
                elif isinstance(powerup_instance, CoinSize):
                    for coin in self.coins:
                        coin.set_scale(1.0)
                elif isinstance(powerup_instance, Invincibility):
                    for p in self.players:
                        p.reset_color()
                elif isinstance(powerup_instance, ShapeShift):
                    for p in self.players:
                        p.reset_shape_and_size()
                del self.active_powerups[powerup_instance]

            for coin in self.coins:
                if pygame.sprite.collide_rect(player, coin):
                    # Check if DoubleScore is active
                    double_score_active = any(isinstance(powerup_instance, DoubleScore) and time.time() - start_time <= 10 
                                             for powerup_instance, start_time in self.active_powerups.items())
                    if double_score_active:
                        self.total_score += 2  # Double the score for each coin
                    else:
                        self.total_score += 1  # Normal score for each coin
                    self.coins.remove(coin)
        self.best_score = max(self.best_score, self.total_score)
        self.update_level()

    def update_level(self):
        self.level = self.total_score // 20 + 1

    def reset_game(self):
        self.level = 1
        self.active_powerups.clear()  # Clear all active powerups
        self.total_score = 0
        self._last_score = 0
        # Reset player attributes
        for player in self.players:
            player.reset_color()  # Reset player color
            player.reset_shape_and_size()  # Reset shape and size
            player.rect.x = SCREEN_WIDTH // 2
            player.rect.y = SCREEN_HEIGHT // 2
            player.vel_y = 0
            if player.controls != player.original_controls:
                player.controls = player.original_controls
        # Clear coins and power-ups
        self.coins.clear()
        self.power_ups.clear()
        self.platforms.clear()

        # Reset spawn timers
        self.power_up_spawn_time = time.time()
        self.coin_spawn_time = time.time()



def platformer_game(screen, num_players=2):
    # Create sprites
    players_list = list(PLAYERS.items())
    players = [Player(SCREEN_WIDTH // random.randint(1, 8),
                      SCREEN_HEIGHT // 3, p_controls, p_color)
               for p_color, p_controls in players_list[:num_players]]
    # Font for displaying score
    font = pygame.font.Font(None, 36)

    # Create game instance
    game = Game(players=players)
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        game.update()

        game.spawn_power_ups()
        game.spawn_coins()

        # Draw
        screen.fill((0, 0, 0))  # Black background
        for player in game.players:
            screen.blit(player.image, player.rect)
        for power_up in game.power_ups:
            screen.blit(power_up.image, power_up.rect)
        for platform in game.platforms:
            screen.blit(platform.image, platform.rect)
        for coin in game.coins:
            screen.blit(coin.image, coin.rect)

        # Draw score
        score_text = font.render(f"Coins: {game.total_score}", True, YELLOW)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        # Draw power-up timers
        for i, (powerup_type, start_time) in enumerate(game.active_powerups.items()):
            remaining_time = 10 - int(time.time() - start_time)
            if remaining_time > 0:
                timer_text = font.render(f"{str(powerup_type)}: {remaining_time}s", True, YELLOW)
                screen.blit(timer_text, (10, 10 + i * 30))

        level_text = font.render(f"Level: {game.level}", True, YELLOW)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        best_text = font.render(f"Best: {game.best_score}", True, YELLOW)
        screen.blit(best_text, (SCREEN_WIDTH - 150 - score_text.get_width() - 10, 10))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()
