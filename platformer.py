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


class PowerUpType:
    def __init__(self, name):
        self.name = name


class DoubleScore(PowerUpType):
    def __init__(self):
        super().__init__(name='Double Score')

    def __repr__(self):
        return self.name

    # Coin class


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0))  # Yellow color
        self.rect = self.image.get_rect(center=(x, y))


# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))  # Green color
        self.rect = self.image.get_rect(topleft=(x, y))


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((128, 0, 128))
        self.rect = self.image.get_rect(center=(x, y))
        self.type = type  # The type of power-up


class Game:
    def __init__(self):
        self.level = 1
        self.power_up = None  # The current power-up
        self.power_up_start_time = None  # The time when the power-up was collected

    def update_level(self, player_score):
        self.level = player_score // 20 + 1

    def reset_game(self, players, coins, power_ups, platforms):
        # Reset player attributes
        for player in players:
            player.rect.x = SCREEN_WIDTH // 2
            player.rect.y = SCREEN_HEIGHT // 2
            player.vel_y = 0
            player.jumps = 0
            player.score = 0

        # Clear coins and power-ups
        coins.clear()
        power_ups.clear()
        platforms.clear()

        # Reset spawn timers
        global power_up_spawn_time
        global coin_spawn_time
        power_up_spawn_time = time.time()
        coin_spawn_time = time.time()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, color):
        super().__init__()
        self.power_up_start_time = None
        self.image = pygame.Surface((50, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 0
        self.jumps = 0
        self.controls = controls
        self.score = 0
        self.level = 1

    def update(self, platforms, coins, power_ups):
        self.vel_y += 0.5  # Gravity
        self.rect.y += int(self.vel_y)  # Convert self.vel_y to an integer

        # Check for collision with platforms
        on_ground = False
        for player in [player1, player2]:
            for platform in platforms:
                if pygame.sprite.collide_rect(player, platform):
                    game.reset_game([player1, player2], coins, power_ups, platforms)
                    main_menu()

        if on_ground or self.rect.bottom >= SCREEN_HEIGHT:
            self.jumps = 0  # Reset jumps when the player lands

        # Move left/right
        keys = pygame.key.get_pressed()
        if keys[self.controls['left']]:
            self.rect.x -= 5
        if keys[self.controls['right']]:
            self.rect.x += 5

        # Jump
        if keys[self.controls['up']]:
            self.vel_y = - 10
            self.jumps = self.jumps + 1

        # Check if player is at the edge of the screen
        if self.rect.left < -int(self.rect.width / 2):
            self.rect.left = -int(self.rect.width / 2)
        if self.rect.right > int(SCREEN_WIDTH + self.rect.width / 2):
            self.rect.right = int(SCREEN_WIDTH + self.rect.width / 2)
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # Collect coins
        for coin in coins:
            if pygame.sprite.collide_rect(self, coin):
                if isinstance(game.power_up, DoubleScore) and time.time() - game.power_up_start_time <= 10:
                    self.score += 2  # Double the score for each coin
                else:
                    self.score += 1  # Normal score for each coin
                coins.remove(coin)

        # Collect power-ups
        for power_up in power_ups:
            if pygame.sprite.collide_rect(player1, power_up) or pygame.sprite.collide_rect(player2, power_up):
                game.power_up = power_up.type  # Collect the power-up
                if isinstance(game.power_up, DoubleScore):
                    game.power_up_start_time = time.time()  # Start the timer
                power_ups.remove(power_up)


# Create sprites
player1 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                 {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP}, (255, 0, 0))
player2 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                 {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w}, (0, 0, 255))
platforms_count = 0
platforms = [Platform(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 100, 20) for _ in
             range(platforms_count)]

coins = []

# Power-up spawn timer
power_up_spawn_time = time.time()
# Coin spawn timer
coin_spawn_time = time.time()

# Font for displaying score
font = pygame.font.Font(None, 36)

# Create sprites
power_ups = []  # List of power-ups
# Create game instance
game = Game()


def main_menu():
    menu_font = pygame.font.Font(None, 50)
    label = menu_font.render("Press any key to start", 1, (255, 255, 0))
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


total_players_score = 0
last_platform_score = 0
# Call the main_menu function before the game loop
main_menu()
# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    player1.update(platforms, coins, power_ups)
    player2.update(platforms, coins, power_ups)
    game.update_level(total_players_score)
    total_players_score = player1.score + player2.score

    if total_players_score // 20 > last_platform_score // 20:
        platforms_count += 1
        platforms = [Platform(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 100, 20) for _ in
                     range(platforms_count)]
        last_platform_score = total_players_score

    # Spawn power-ups
    if time.time() - power_up_spawn_time > 10 and len(power_ups) < 1:  # Spawn a power-up every 10 seconds
        power_up_x = random.randint(0, SCREEN_WIDTH)
        power_up_y = random.randint(0, SCREEN_HEIGHT)
        power_up = PowerUp(power_up_x, power_up_y, DoubleScore())  # Create a new power-up
        power_ups.append(power_up)
        power_up_spawn_time = time.time()

    # Spawn coins
    if time.time() - coin_spawn_time > 1 and len(coins) < 4:
        coin_x = random.randint(0, SCREEN_WIDTH)
        coin_y = random.randint(0, SCREEN_HEIGHT)
        coin = Coin(coin_x, coin_y)
        # Check if coin is spawned inside a platform
        if not any(coin.rect.colliderect(platform.rect) for platform in platforms):
            coins.append(coin)
            coin_spawn_time = time.time()

    # Draw
    screen.fill((0, 0, 0))  # Black background
    screen.blit(player1.image, player1.rect)
    screen.blit(player2.image, player2.rect)
    for power_up in power_ups:
        screen.blit(power_up.image, power_up.rect)
    for platform in platforms:
        screen.blit(platform.image, platform.rect)
    for coin in coins:
        screen.blit(coin.image, coin.rect)

    # Draw score
    score_text = font.render(f"Coins: {total_players_score}", True, (255, 255, 0))
    screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

    # Draw power-up timer
    if isinstance(game.power_up, DoubleScore):
        remaining_time = 10 - int(time.time() - game.power_up_start_time)
        if remaining_time > 0:
            timer_text = font.render(f"{str(game.power_up)}: {remaining_time}s", True, (255, 255, 0))
            screen.blit(timer_text, (10, 10))

    level_text = font.render(f"Level: {game.level}", True, (255, 255, 0))
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
