from dataclasses import dataclass, field
from typing import Any, Callable, NewType, Protocol

ElementId = NewType("ElementId", str)
"Id of an element on the page (typically, a HTML tag)."


class State:
    ...


empty_state = State()


class Continuation(Protocol):
    "Inputs are user interface elements"

    def setup(self, target: ElementId, state: State = empty_state) -> None:
        ...


@dataclass
class Context:
    state: State = empty_state
    args: tuple = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


Passage = Callable[[Context], Continuation]
