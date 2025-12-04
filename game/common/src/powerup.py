from dataclasses import dataclass


@dataclass(frozen=True)
class PowerUpType:
    """
    Represents a type of power-up.

    Attributes:
        name (str): The name of the power-up.
    """
    name: str
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
