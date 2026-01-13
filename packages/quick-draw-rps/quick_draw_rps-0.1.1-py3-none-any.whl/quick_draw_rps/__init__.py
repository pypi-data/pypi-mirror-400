import argparse
from .core import quick_draw, Result


def main() -> None:
    parser = argparse.ArgumentParser(description="Rock Paper Scissors Quick Draw")
    parser.add_argument(
        "player", choices=["rock", "paper", "scissors"], help="Your choice"
    )
    parser.add_argument(
        "opponent",
        choices=["rock", "paper", "scissors"],
        nargs="?",
        default="rock",
        help="Opponent's choice (defaults to rock)",
    )

    args = parser.parse_args()
    result = quick_draw(args.player, args.opponent)
    print(result)


__all__ = ["quick_draw", "Result", "main"]
