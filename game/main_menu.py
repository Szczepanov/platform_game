import sys

import pygame

from utils.constants import SCREEN_WIDTH, YELLOW, SCREEN_HEIGHT, WHITE
from racer.racer import race_game
from platformer import platformer_game
from jumper import jumper_game
from catcher import catcher_game
from cooperative import cooperative_platformer_game


def main_menu(screen):
    menu_font = pygame.font.Font(None, 50)
    options = ["Start the Platformer Game",
               "Start the Race Game",
               "Start the Jump Game",
               "Start the Catcher Game",
               "Start the Jumpy Tower",
               "Quit"]
    selected_option = 0
    num_players = 2  # Default to 2 players
    while True:
        screen.fill((0, 0, 0))
        
        # Draw player count selector
        player_text = menu_font.render(f"Players: {num_players}", 1, WHITE)
        screen.blit(player_text, (50, 50))
        controls_text = pygame.font.Font(None, 30).render("Use LEFT/RIGHT arrows to change", 1, YELLOW)
        screen.blit(controls_text, (50, 100))
        
        # Draw menu options
        for i, option in enumerate(options):
            if i == selected_option:
                label = menu_font.render("> " + option, 1, YELLOW)
            else:
                label = menu_font.render(option, 1, WHITE)
            screen.blit(label,
                        (SCREEN_WIDTH / 2 - label.get_width() / 2, SCREEN_HEIGHT / 2 - label.get_height() / 2 + i * 50))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_LEFT:
                    num_players = max(1, num_players - 1)
                elif event.key == pygame.K_RIGHT:
                    num_players = min(3, num_players + 1)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        platformer_game(screen, num_players)
                    elif selected_option == 1:
                        race_game(screen, num_players)
                    elif selected_option == 2:
                        jumper_game(screen, num_players)
                    elif selected_option == 3:
                        catcher_game(screen, num_players)
                    elif selected_option == 4:
                        cooperative_platformer_game(screen, num_players)
                    else:
                        pygame.quit()
                        sys.exit()
