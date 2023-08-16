import datetime
from dataclasses import dataclass, field
from typing import Callable, Generic, Optional, Protocol, TypeVar

import jsonpickle as jsp

import troubadour.backend as be
import troubadour.definitions as df
import troubadour.save as sv

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
    state: T
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

    @classmethod
    def reset(cls, _) -> None:
        sv.erase_save()
        be.refresh_page()

    def render(self) -> None:
        be.clear(df.ElementId("output"))
        be.clear(df.ElementId("input"))
        for out in self.output_state:
            match out:
                case datetime.datetime():
                    t = out.strftime(r"%Y - %b %d - %H:%M:%S")
                    be.insert_end(
                        df.ElementId("output"), f"<div class='timestamp'>{t}</div>"
                    )
                case str():
                    be.insert_end(df.ElementId("output"), out)
        if self.input_state is not None:
            self.input_state.setup(self)
        be.scroll_to_bottom(df.ElementId("output"))

    @classmethod
    def run_game(cls, StateCls: type, start_passage: Callable) -> None:
        if not sv.state_exists():
            game = Game(StateCls())
            game.run_passage(start_passage)
        else:
            game = sv.load_game()
            game.render()

        # export button
        game_json = jsp.encode(game)
        assert game_json is not None
        be.file_download_button(df.ElementId("export"), game_json, "troubadour.json")

        # reset button
        be.onclick(df.ElementId("reset"), cls.reset)

    def run_passage(self, passage: Callable, **kwargs: object) -> None:
        self.timestamp()
        be.clear(df.ElementId("input"))
        continuation = passage(self, **kwargs)
        self.input_state = continuation
        continuation.setup(self)
        be.scroll_to_bottom(df.ElementId("output"))
        sv.save_game(self)
