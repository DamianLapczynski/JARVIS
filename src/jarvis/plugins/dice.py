"""Example plugin 2: a read-only tool with a validated argument."""

import random

from jarvis.tools.base import Level, ToolSpec


def dice_roll(sides: int = 6) -> str:
    sides = int(sides)
    if not 2 <= sides <= 1000:
        raise ValueError("sides must be between 2 and 1000")
    return f"Rolled d{sides}: {random.randint(1, sides)}"


def register(registry) -> None:
    registry.register(ToolSpec("dice_roll", "Roll a die.", Level.R, dice_roll, {"sides": "number of sides"}))
