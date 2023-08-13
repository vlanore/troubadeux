from dataclasses import dataclass, field
from typing import Any, Callable, NewType, Protocol

ElementId = NewType("ElementId", str)
"Id of an element on the page (typically, a HTML tag)."


class State:
    "Game state 'tag' class that states need to inherit from."
    ...


empty_state = State()
"An empty game state (e.g., to use as a default value)."


@dataclass
class Context:
    state: State = empty_state
    args: dict[str, Any] = field(default_factory=dict)


empty_context = Context(state=empty_state)


class Interface(Protocol):
    "Inputs are user interface elements"

    def setup(self, target: ElementId, context: Context = empty_context) -> None:
        ...


Passage = Callable[[Context], Interface]
