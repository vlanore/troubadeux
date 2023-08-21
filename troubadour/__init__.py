"Troubadour is a small browser-based text-based game framework."

try:
    from troubadour.game import Game  # noqa: F401
    from troubadour.continuations import (  # noqa: F401
        Button,
        TextButton,
        InterfaceSequence,
    )

    __all__ = [
        "Game",
        "Button",
        "TextButton",
        "InterfaceSequence",
    ]
except ImportError:  # if we're not in the browser
    __all__ = []

VERSION = "0.1.2"
