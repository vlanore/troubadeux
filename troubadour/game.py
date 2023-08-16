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


class ResetDialog:
    @classmethod
    def perform_reset(cls, _game: "Game") -> None:
        sv.erase_save()
        be.refresh_page()

    @classmethod
    def dialog(cls, _game: "Game") -> Interface:
        be.insert_end(
            eid("output"),
            (
                "<h1>Game reset</h1>"
                "<p>Are you sure you want to reset?</p>"
                "<p>This will <b>erase all game data</b>."
            ),
        )
        return tc.InterfaceSequence(
            tc.Button("Reset", cls.perform_reset, dialog=True),
            tc.Button("Cancel", Game.cancel_dialog, dialog=True),
        )

    @classmethod
    def callback(cls, _) -> None:
        game = sv.load_game()
        game.run_passage(cls.dialog, dialog=True)


@dataclass
class Game(Generic[T]):
    state: T
    input_state: Optional[Interface] = None
    output_state: list[str | datetime.datetime] = field(default_factory=list)
    max_output_len: int = 50

    def print(self, html: str) -> None:
        self.output_state.append(html)
        be.insert_end(eid("output"), html)

    def timestamp(self) -> None:
        ts = datetime.datetime.now()
        self.output_state.append(ts)
        t = ts.strftime(r"%Y - %b %d - %H:%M:%S")
        be.insert_end(eid("output"), f"<div class='timestamp'>{t}</div>")

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
    def cancel_dialog(cls, game: "Game") -> None:
        game.render()

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
        be.onclick(eid("reset"), ResetDialog.callback)

    def trim_output(self) -> None:
        if len(self.output_state) > self.max_output_len:
            trim_index = -self.max_output_len
            self.output_state = self.output_state[trim_index:]
            self.render()

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
            self.trim_output()
            sv.save_game(self)
