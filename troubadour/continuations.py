"Implements a series of simple continuations, such as buttons and simple text fields."

from dataclasses import dataclass, field
from typing import Any, Callable

import troubadour.backend as be
from troubadour.definitions import Game, Continuation, Eid
from troubadour.unique_id import get_unique_element_id


@dataclass
class Button(Continuation):
    txt: str
    passage: Callable
    kwargs: dict[str, object] = field(default_factory=dict)
    dialog: bool = False

    def setup(
        self, game: Game, target: Eid = Eid("output"), disabled: bool = False
    ) -> None:
        button_id = get_unique_element_id("button")
        be.insert_end(
            target, f"<button type='button' id='{button_id}'>{self.txt}</button>"
        )
        if not disabled:
            be.onclick(
                button_id,
                lambda _: game.run_passage(self.passage, kwargs=self.kwargs),
            )
        else:
            be.disable(button_id)


@dataclass
class TextButton(Continuation):
    txt: str
    passage: Callable
    value_kw: str
    kwargs: dict[str, object] = field(default_factory=dict)
    convertor: Callable[[Any], str] = str

    def setup(
        self, game: Game, target: Eid = Eid("output"), disabled: bool = False
    ) -> None:
        text_id = get_unique_element_id("textinput")
        button_id = get_unique_element_id("button")
        be.insert_end(target, f"<input type='text' id='{text_id}'></input>")
        be.insert_end(
            target,
            (
                "<button class='textbutton' type='button' "
                f"id='{button_id}'>{self.txt}</button>"
            ),
        )
        if not disabled:

            def callback(_):
                value = self.convertor(be.get_value(text_id))
                full_kwargs = {self.value_kw: value, **self.kwargs}
                game.run_passage(self.passage, kwargs=full_kwargs)

            be.onclick(button_id, callback)
        else:
            be.disable(button_id)
            be.disable(text_id)
