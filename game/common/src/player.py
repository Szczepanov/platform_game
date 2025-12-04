from dataclasses import dataclass
from pygame.sprite import Sprite
from typing import Any

@dataclass
class Player(Sprite):
    x: int
    y: int
    controls: dict[str, Any]
    color: str