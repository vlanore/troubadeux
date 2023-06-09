from dataclasses import dataclass, field
from typing import Any, Callable, NewType, Protocol

ElementId = NewType("ElementId", str)
"Id of an element on the page (typically, a HTML tag)."


class State:
    ...


empty_state = State()


@dataclass
class Context:
    state: State = empty_state
    args: tuple = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


empty_context = Context(state=empty_state)


class Continuation(Protocol):
    "Inputs are user interface elements"

    def setup(self, target: ElementId, context: Context = empty_context) -> None:
        ...


Passage = Callable[[Context], Continuation]
