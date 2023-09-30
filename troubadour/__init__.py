"Troubadour is a small browser-based text-based game framework."

try:
    from troubadour.continuations import (  # noqa: F401
        Button,
        TextButton,
    )
    from troubadour.definitions import Game  # noqa: F401
    from troubadour.game import run_game  # noqa: F401

    __all__ = [
        "Game",
        "Button",
        "TextButton",
        "run_game",
    ]
except ImportError:  # if we're not in the browser
    __all__ = []

VERSION = "0.1.3"
