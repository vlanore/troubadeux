from dataclasses import dataclass

import troubadour as tbd


@dataclass
class MyState:
    txt: str = "Hello world"


def intro(game: tbd.Game[MyState]) -> None:
    game.paragraph("Hello world")


tbd.run_game(MyState, intro)
