from dataclasses import dataclass, field
from typing import Any, Callable

import troubadour.backend as be
from troubadour.definitions import eid
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
    dialog: bool = False

    def setup(self, game: Game) -> None:
        id = get_unique_element_id("button")
        be.insert_end(
            eid("input"), f"<button type='button' id='{id}'>{self.txt}</button>"
        )
        be.onclick(
            id,
            lambda _: game.run_passage(
                self.passage, kwargs=self.kwargs, dialog=self.dialog
            ),
        )


@dataclass
class TextButton(Interface):
    txt: str
    passage: Callable
    value_kw: str
    kwargs: dict[str, object] = field(default_factory=dict)
    dialog: bool = False
    convertor: Callable[[Any], str] = str

    def setup(self, game: Game) -> None:
        text_id = get_unique_element_id("textinput")
        button_id = get_unique_element_id("button")
        be.insert_end(eid("input"), f"<input type='text' id='{text_id}'></input>")
        be.insert_end(
            eid("input"), f"<button type='button' id='{button_id}'>{self.txt}</button>"
        )

        def callback(_):
            value = self.convertor(be.get_value(text_id))
            full_kwargs = {self.value_kw: value, **self.kwargs}
            game.run_passage(self.passage, kwargs=full_kwargs, dialog=self.dialog)

        be.onclick(button_id, callback)
