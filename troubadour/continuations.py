from dataclasses import dataclass, field

import troubadour.backend as be
from troubadour.definitions import (
    Context,
    Interface,
    ElementId,
    Passage,
    empty_context,
)
from troubadour.run import run
from troubadour.unique_id import get_unique_element_id


class InterfaceSequence:
    def __init__(self, *continuations: Interface):
        self.lst = [*continuations]

    def setup(self, target: ElementId, context: Context = empty_context) -> None:
        for cont in self.lst:
            cont.setup(target, context)


@dataclass
class Button(Interface):
    txt: str
    passage: Passage
    args: dict[str, object] = field(default_factory=dict)

    def setup(self, target: ElementId, context: Context = empty_context) -> None:
        id = get_unique_element_id("button")
        be.insert_end(target, f"<button type='button' id='{id}'>{self.txt}</button>")
        be.onclick(id, lambda _: run(self.passage, Context()))
