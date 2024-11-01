import pygame
import sys
import random
import time
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, GREEN, VIOLET, ORANGE, PLAYERS)
from typing import Optional, List, Dict, Any


class PowerUpType:
    def __init__(self, name):
        self.name = name


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


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)  # Yellow color
        self.rect = self.image.get_rect(center=(x, y))


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
        self.power_up = None  # The current power-up
        self.power_up_start_time = None  # The time when the power-up was collected
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
            if isinstance(self.power_up, DoubleScore) and time.time() - self.power_up_start_time <= 10:
                coin = Coin(coin_x, coin_y)
                coin.image.fill(ORANGE)
            else:
                coin = Coin(coin_x, coin_y)
            # Check if coin is spawned inside a platform
            if not any(coin.rect.colliderect(platform.rect) for platform in self.platforms):
                self.coins.append(coin)
                self.coin_spawn_time = time.time()

    def spawn_power_ups(self):
        # Spawn power-ups
        if time.time() - self.power_up_spawn_time > 10 and len(self.power_ups) < 1:  # Spawn a power-up every 10 seconds
            power_up_x = random.randint(0, SCREEN_WIDTH)
            power_up_y = random.randint(0, SCREEN_HEIGHT)
            power_up = PowerUp(power_up_x, power_up_y, random.choice([DoubleScore(), Invincibility(), SwitchPlayers(), ShapeShift()]))
            self.power_ups.append(power_up)
            self.power_up_spawn_time = time.time()

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
        for player in self.players:
            player.controls = player.original_controls

    def update(self):
        self.spawn_platforms()

        # Update each platform's blinking state
        for platform in self.platforms:
            platform.update()

        for player_nr, player in enumerate(self.players):
            player.update()
            for platform in self.platforms:
                if pygame.sprite.collide_rect(player, platform):
                    # Only reset the game if the platform is not blinking
                    if not platform.blinking and not (isinstance(self.power_up, Invincibility) and time.time() - self.power_up_start_time <= 10):
                        self.reset_game()
            for power_up in self.power_ups:
                if pygame.sprite.collide_rect(player, power_up):
                    for coin in self.coins:
                        coin.image.fill(YELLOW)
                    self.reset_player_controls()
                    self.power_up = power_up.powerup_type  # Collect the power-up
                    self.power_up_start_time = time.time()  # Start the timer

                    # Apply the power-up effects
                    if isinstance(self.power_up, Invincibility):
                        for p in self.players:
                            p.change_color(WHITE)
                    elif isinstance(self.power_up, SwitchPlayers):
                        self.switch_player_controls()
                    elif isinstance(self.power_up, DoubleScore):
                        if time.time() - self.power_up_start_time <= 10:
                            for coin in self.coins:
                                coin.image.fill(ORANGE)
                    elif isinstance(self.power_up, ShapeShift):
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

                    self.power_ups.remove(power_up)
            # Handle power-up durations
            if isinstance(self.power_up, SwitchPlayers) and time.time() - self.power_up_start_time > 10:
                self.reset_player_controls()
            if isinstance(self.power_up, DoubleScore) and time.time() - self.power_up_start_time > 10:
                for coin in self.coins:
                    coin.image.fill(YELLOW)
            if isinstance(self.power_up, Invincibility) and time.time() - self.power_up_start_time > 10 or (
                    not isinstance(self.power_up, Invincibility) and player.current_color == WHITE):
                for p in self.players:
                    p.reset_color()
            if isinstance(self.power_up, ShapeShift) and time.time() - self.power_up_start_time > 10:
                for p in self.players:
                    p.reset_shape_and_size()
                self.power_up = None  # Reset current power-up

            for coin in self.coins:
                if pygame.sprite.collide_rect(player, coin):
                    if isinstance(self.power_up, DoubleScore) and time.time() - self.power_up_start_time <= 10:
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
        self.power_up = None  # The current power-up
        self.power_up_start_time = None  # The time when the power-up was collected
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



def platformer_game(screen):
    # Create sprites
    players = [Player(SCREEN_WIDTH // random.randint(1, 8),
                      SCREEN_HEIGHT // 3, p_controls, p_color)
               for p_color, p_controls in PLAYERS.items()]
    # Font for displaying score
    font = pygame.font.Font(None, 36)

    # Create game instance
    game = Game(players=players)
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

        # Draw power-up timer
        if isinstance(game.power_up, PowerUpType):
            remaining_time = 10 - int(time.time() - game.power_up_start_time)
            if remaining_time > 0:
                timer_text = font.render(f"{str(game.power_up)}: {remaining_time}s", True, YELLOW)
                screen.blit(timer_text, (10, 10))

        level_text = font.render(f"Level: {game.level}", True, YELLOW)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        best_text = font.render(f"Best: {game.best_score}", True, YELLOW)
        screen.blit(best_text, (SCREEN_WIDTH - 150 - score_text.get_width() - 10, 10))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()
