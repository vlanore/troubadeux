import datetime
from dataclasses import dataclass, field
from typing import Generic, NewType, Optional, Protocol, TypeVar

ElementId = NewType("ElementId", str)
"Id of an element on the page (typically, a HTML tag)."

T = TypeVar("T")


@dataclass
class GameOutput:
    html: str
    timestamp: datetime.datetime


@dataclass
class Game(Generic[T]):
    game_state: T
    input_state: Optional["Interface"] = None
    output_state: list[GameOutput] = field(default_factory=list)


class Interface(Protocol):
    "Inputs are user interface elements"

    def setup(self, game: Game) -> None:
        ...


# Passage = Callable[[Game], Interface]
