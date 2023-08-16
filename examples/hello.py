from dataclasses import dataclass

import troubadour.game as tg


@dataclass
class MyState:
    txt: str = "Hello world"


def intro(game: tg.Game[MyState]) -> None:
    game.print("Hello world")


tg.Game.run(MyState, intro)
