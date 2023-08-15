import datetime
from dataclasses import dataclass, field
from typing import Generic, Optional, Protocol, TypeVar

import troubadour.backend as be
import troubadour.definitions as df

T = TypeVar("T")


class Interface(Protocol):
    "Inputs are user interface elements"

    def setup(self, game: "Game") -> None:
        ...


@dataclass
class GameOutput:
    html: str
    timestamp: datetime.datetime


@dataclass
class Game(Generic[T]):
    game_state: T
    input_state: Optional[Interface] = None
    output_state: list[str | datetime.datetime] = field(default_factory=list)

    def print(self, html: str) -> None:
        self.output_state.append(html)
        be.insert_end(df.ElementId("output"), html)

    def timestamp(self) -> None:
        ts = datetime.datetime.now()
        self.output_state.append(ts)
        t = ts.strftime(r"%Y - %b %d - %H:%M:%S")
        be.insert_end(df.ElementId("output"), f"<div class='timestamp'>{t}</div>")
