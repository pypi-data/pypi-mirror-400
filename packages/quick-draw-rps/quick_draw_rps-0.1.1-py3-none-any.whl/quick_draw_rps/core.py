from dataclasses import dataclass
from typing import Literal

Choice = Literal["rock", "paper", "scissors"]


@dataclass
class Result:
    player: Choice
    opponent: Choice
    outcome: Literal["win", "lose", "draw"]


_BEATS = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}


def quick_draw(player: Choice, opponent: Choice) -> Result:
    if player not in _BEATS or opponent not in _BEATS:
        raise ValueError("Choices must be 'rock', 'paper', or 'scissors'")
    if player == opponent:
        outcome = "draw"
    elif _BEATS[player] == opponent:
        outcome = "win"
    else:
        outcome = "lose"
    return Result(player=player, opponent=opponent, outcome=outcome)
