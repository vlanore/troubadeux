from dataclasses import dataclass, field
from typing import Callable

import troubadour.backend as be
from troubadour.definitions import ElementId
from troubadour.game import Game, Interface
from troubadour.unique_id import get_unique_element_id


class InterfaceSequence:
    def __init__(self, *continuations: Interface):
        self.lst = [*continuations]

    def setup(self, game: Game) -> None:
        for cont in self.lst:
            cont.setup(game)


@dataclass
class Button(Interface):
    txt: str
    passage: Callable
    kwargs: dict[str, object] = field(default_factory=dict)

    def setup(self, game: Game) -> None:
        id = get_unique_element_id("button")
        be.insert_end(
            ElementId("input"), f"<button type='button' id='{id}'>{self.txt}</button>"
        )
        be.onclick(id, lambda _: game.run_passage(self.passage, **self.kwargs))
