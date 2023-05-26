from dataclasses import dataclass

import troubadour.backend as be
from troubadour.definitions import (
    Context,
    Continuation,
    ElementId,
    Passage,
    State,
    empty_state,
)
from troubadour.run import run
from troubadour.unique_id import get_unique_element_id


class ContinuationList(Continuation):
    def __init__(self, *continuations: Continuation):
        self.lst = [*continuations]

    def setup(self, target: ElementId, state: State = empty_state) -> None:
        for cont in self.lst:
            cont.setup(target, state)


@dataclass
class Button(Continuation):
    txt: str
    passage: Passage

    def setup(self, target: ElementId, state: State = empty_state) -> None:
        id = get_unique_element_id("button")
        be.insert_end(target, f"<button type='button' id='{id}'>{self.txt}</button>")
        be.onclick(id, lambda _: run(self.passage, Context()))
