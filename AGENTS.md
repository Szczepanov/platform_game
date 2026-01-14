# Agentic Coding Instructions

This file contains instructions for AI agents working on this codebase.

## Project Overview

This is a Pygame-based "Arcade" collection containing multiple minigames. The project is structured to act as a hub (`main_menu.py`) launching different independent game modules.

## Project Structure

- `game/`: Root directory for source code.
    - `main.py`: Entry point. Initializes Pygame and launches the main menu.
    - `main_menu.py`: Handles the main menu loop, player selection, and launching specific games.
    - `utils/`: Shared utilities and constants (e.g., `SCREEN_WIDTH`, colors).
    - `[game_name]/`: Each game resides in its own subdirectory (e.g., `platformer`, `racer`, `catcher`).

## Development Guidelines

### Adding a New Game

1.  **Create Directory**: Create a new directory in `game/<game_name>`.
2.  **Implementation**: Create your game logic. The main game function MUST accept `screen` (pygame Surface) and `num_players` (int) as arguments.
    ```python
    def my_new_game(screen, num_players):
        # Game loop here
        pass
    ```
3.  **Registration**:
    - Import your game function in `game/main_menu.py`.
    - Add a new entry to the `options` list in `main_menu()`.
    - Add a new condition in the `pygame.K_RETURN` handling block to call your function.

### Code Style

- The project uses `ruff` for linting and formatting.
- Check `pyproject.toml` for configuration.
- Helper constants (colors, screen dimensions) should be imported from `utils.constants` when possible to maintain consistency.

### Running the Project

- The project is designed to be run as a module or script from the root directory.
- Command: `python game/main.py`
