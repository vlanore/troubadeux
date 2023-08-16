import datetime
from dataclasses import dataclass, field
from typing import Callable, Generic, Optional, Protocol, TypeVar

import jsonpickle as jsp

import troubadour.backend as be
import troubadour.continuations as tc
from troubadour.definitions import eid
import troubadour.save as sv

T = TypeVar("T")


class Interface(Protocol):
    "Inputs are user interface elements"

    def setup(self, game: "Game") -> None:
        ...


@dataclass
class Game(Generic[T]):
    state: T
    input_state: Optional[Interface] = None
    output_state: list[str | datetime.datetime] = field(default_factory=list)

    def print(self, html: str) -> None:
        self.output_state.append(html)
        be.insert_end(eid("output"), html)

    def timestamp(self) -> None:
        ts = datetime.datetime.now()
        self.output_state.append(ts)
        t = ts.strftime(r"%Y - %b %d - %H:%M:%S")
        be.insert_end(eid("output"), f"<div class='timestamp'>{t}</div>")

    @classmethod
    def perform_reset(cls, game: "Game") -> None:
        sv.erase_save()
        be.refresh_page()

    @classmethod
    def cancel_dialog(cls, game: "Game") -> None:
        game.render()

    @classmethod
    def reset_dialog(cls, game: "Game") -> Interface:
        be.insert_end(
            eid("output"),
            ("<h1>Game reset</h1>" "<p>Are you sure you want to reset?</p>"),
        )
        return tc.InterfaceSequence(
            tc.Button("Reset", cls.perform_reset, dialog=True),
            tc.Button("Cancel", cls.cancel_dialog, dialog=True),
        )

    @classmethod
    def reset_callback(cls, _) -> None:
        game = sv.load_game()
        game.run_passage(cls.reset_dialog, dialog=True)

    def render(self) -> None:
        be.clear(eid("output"))
        be.clear(eid("input"))
        for out in self.output_state:
            match out:
                case datetime.datetime():
                    t = out.strftime(r"%Y - %b %d - %H:%M:%S")
                    be.insert_end(eid("output"), f"<div class='timestamp'>{t}</div>")
                case str():
                    be.insert_end(eid("output"), out)
        if self.input_state is not None:
            self.input_state.setup(self)
        be.scroll_to_bottom(eid("output"))

    @classmethod
    def run(cls, StateCls: type, start_passage: Callable) -> None:
        if not sv.state_exists():
            game = Game(StateCls())
            game.run_passage(start_passage)
        else:
            game = sv.load_game()
            game.render()

        # export button
        game_json = jsp.encode(game)
        assert game_json is not None
        be.file_download_button(eid("export"), game_json, "troubadour.json")

        # reset button
        be.onclick(eid("reset"), cls.reset_callback)

    def run_passage(
        self, passage: Callable, *, dialog: bool = False, kwargs: dict[str, object] = {}
    ) -> None:
        if not dialog:
            self.timestamp()
        else:
            be.clear(eid("output"))
        be.clear(eid("input"))
        continuation: Interface | None = passage(self, **kwargs)
        if continuation is not None:
            if not dialog:
                self.input_state = continuation
            continuation.setup(self)
        be.scroll_to_bottom(eid("output"))
        if not dialog:
            sv.save_game(self)
