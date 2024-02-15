import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (255, 0, 0)
BLUE_COLOR = (0, 0, 255)
YELLOW_COLOR = (255, 255, 0)
GREEN_COLOR = (0, 255, 0)
VIOLET_COLOR = (128, 0, 128)
PLAYER1_COLOR = RED_COLOR
PLAYER2_COLOR = BLUE_COLOR


class PowerUpType:
    def __init__(self, name):
        self.name = name


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


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW_COLOR)  # Yellow color
        self.rect = self.image.get_rect(center=(x, y))


# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN_COLOR)  # Green color
        self.rect = self.image.get_rect(topleft=(x, y))


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(VIOLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = type  # The type of power-up


class Game:
    def __init__(self, players=None, power_ups=None, coins=None, platforms=None):
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
        if time.time() - self.coin_spawn_time > 0.8 and len(self.coins) < 5:
            coin_x = random.randint(0, SCREEN_WIDTH)
            coin_y = random.randint(0, SCREEN_HEIGHT)
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
            power_up = PowerUp(power_up_x, power_up_y, random.choice([DoubleScore(), Invincibility()]))
            self.power_ups.append(power_up)
            self.power_up_spawn_time = time.time()

    def spawn_platforms(self):
        if self.total_score // 20 > self._last_score // 20:
            self.platforms.append(Platform(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 100, 10))
            self._last_score = self.total_score

    def update(self):
        self.spawn_platforms()
        for player in self.players:
            player.update()
            for platform in self.platforms:
                if pygame.sprite.collide_rect(player, platform):
                    if not (isinstance(self.power_up, Invincibility) and time.time() - self.power_up_start_time <= 10):
                        self.reset_game()
                        main_menu()
            for power_up in self.power_ups:
                if pygame.sprite.collide_rect(player, power_up):
                    self.power_up = power_up.type  # Collect the power-up
                    self.power_up_start_time = time.time()  # Start the timer
                    if isinstance(self.power_up, Invincibility):
                        for p in self.players:
                            p.change_color(WHITE_COLOR)
                    self.power_ups.remove(power_up)
            if (isinstance(self.power_up, Invincibility) and time.time() - self.power_up_start_time > 10) or (
                    isinstance(self.power_up, DoubleScore) and player.current_color == WHITE_COLOR):
                for p in self.players:
                    p.reset_color()
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
        # Reset player attributes
        for player in self.players:
            player.image.fill(player.original_color)  # Reset player color
            player.rect.x = SCREEN_WIDTH // 2
            player.rect.y = SCREEN_HEIGHT // 2
            player.vel_y = 0

        # Clear coins and power-ups
        self.coins.clear()
        self.power_ups.clear()
        self.platforms.clear()

        # Reset spawn timers
        self.power_up_spawn_time = time.time()
        self.coin_spawn_time = time.time()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, color):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.original_color = color
        self.current_color = color
        self.image.fill(self.current_color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 0
        self.controls = controls

    def change_color(self, color):
        self.current_color = color
        self.image.fill(self.current_color)

    def reset_color(self):
        self.current_color = self.original_color
        self.image.fill(self.current_color)

    def update(self):
        self.vel_y += 0.5  # Gravity
        self.rect.y += int(self.vel_y)  # Convert self.vel_y to an integer

        # Move left/right
        keys = pygame.key.get_pressed()
        if keys[self.controls['left']]:
            self.rect.x -= 5
        if keys[self.controls['right']]:
            self.rect.x += 5

        # Jump
        if keys[self.controls['up']]:
            self.vel_y = - 10

        # Check if player is at the edge of the screen
        if self.rect.left < -int(self.rect.width / 2):
            self.rect.left = -int(self.rect.width / 2)
        if self.rect.right > int(SCREEN_WIDTH + self.rect.width / 2):
            self.rect.right = int(SCREEN_WIDTH + self.rect.width / 2)
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


def main_menu():
    menu_font = pygame.font.Font(None, 50)
    label = menu_font.render("Press any key to start", 1, YELLOW_COLOR)
    while True:
        screen.fill((0, 0, 0))
        screen.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, SCREEN_HEIGHT / 2 - label.get_height() / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return


def main():
    # Create sprites
    player1 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                     {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP}, PLAYER1_COLOR)
    player2 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                     {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w}, PLAYER2_COLOR)
    # Font for displaying score
    font = pygame.font.Font(None, 36)

    # Create game instance
    game = Game(players=[player1, player2])
    last_platform_score = 0
    # Call the main_menu function before the game loop
    main_menu()
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
        score_text = font.render(f"Coins: {game.total_score}", True, YELLOW_COLOR)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        # Draw power-up timer
        if isinstance(game.power_up, PowerUpType):
            remaining_time = 10 - int(time.time() - game.power_up_start_time)
            if remaining_time > 0:
                timer_text = font.render(f"{str(game.power_up)}: {remaining_time}s", True, YELLOW_COLOR)
                screen.blit(timer_text, (10, 10))

        level_text = font.render(f"Level: {game.level}", True, YELLOW_COLOR)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        best_text = font.render(f"Best: {game.best_score}", True, YELLOW_COLOR)
        screen.blit(best_text, (SCREEN_WIDTH - 150 - score_text.get_width() - 10, 10))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
