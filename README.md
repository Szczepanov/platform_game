# Platformer Game

This is a simple platformer game implemented in Python using the Pygame library.

## Features

- Two players with different controls.
- Players can collect power-ups that provide temporary benefits.
- Players can collect coins to increase their score.
- The game includes a level system, where the level increases as the score increases.
- The game includes a main menu and a game loop.
- The game includes a score display, power-up timer, and level display.

## Game Classes

The game is structured around several classes:

- `PowerUpType`: Represents a type of power-up. There are two types of power-ups: `DoubleScore` and `Invincibility`.
- `Coin`: Represents a coin that players can collect to increase their score.
- `Platform`: Represents a platform that players can collide with.
- `PowerUp`: Represents a power-up that players can collect to gain temporary benefits.
- `Game`: Represents the game itself. It handles game updates, level updates, and game resets.
- `Player`: Represents a player. It handles player updates and color changes.

## Controls

Player 1:
- Move left: Left arrow key
- Move right: Right arrow key
- Jump: Up arrow key

Player 2:
- Move left: 'A' key
- Move right: 'D' key
- Jump: 'W' key

## Requirements

- Python
- Pygame
- pip

## How to Run

To run the game, simply execute the `platformer.py` script with Python.

```bash
python platformer.py
```

## Future Improvements

- Add more types of power-ups.
- Add more types of platforms.
- Add enemies or obstacles.
- Add a multiplayer mode over network.
- Improve the graphics and sound effects.