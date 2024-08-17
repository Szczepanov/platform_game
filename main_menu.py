import sys

import pygame

from constants import SCREEN_WIDTH, YELLOW, SCREEN_HEIGHT, WHITE
from racer.racer import race_game
from platformer.platformer import platformer_game


def main_menu(screen):
    menu_font = pygame.font.Font(None, 50)
    options = ["Start the Platformer Game", "Start the Race Game", "Quit"]
    selected_option = 0
    while True:
        screen.fill((0, 0, 0))
        for i, option in enumerate(options):
            if i == selected_option:
                label = menu_font.render("> " + option, 1, YELLOW)
            else:
                label = menu_font.render(option, 1, WHITE)
            screen.blit(label,
                        (SCREEN_WIDTH / 2 - label.get_width() / 2, SCREEN_HEIGHT / 2 - label.get_height() / 2 + i * 60))
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
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        platformer_game(screen)
                    elif selected_option == 1:
                        race_game(screen)
                    elif selected_option == 2:
                        pygame.quit()
                        sys.exit()
