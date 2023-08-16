import datetime
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable, Generic, Optional, Protocol, TypeVar

import jsonpickle as jsp

import troubadour.backend as be
import troubadour.continuations as tc
import troubadour.definitions as df
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
        be.insert_end(df.ElementId("output"), html)

    def timestamp(self) -> None:
        ts = datetime.datetime.now()
        self.output_state.append(ts)
        t = ts.strftime(r"%Y - %b %d - %H:%M:%S")
        be.insert_end(df.ElementId("output"), f"<div class='timestamp'>{t}</div>")

    @classmethod
    def perform_reset(cls, game: "Game") -> None:
        sv.erase_save()
        be.refresh_page()

    @classmethod
    def cancel_dialog(cls, game: "Game", old_game: "Game") -> None:
        game.input_state = old_game.input_state
        game.output_state = old_game.output_state
        game.state = old_game.state
        print(old_game.input_state)
        game.render()

    @classmethod
    def reset_dialog(cls, game: "Game") -> Interface:
        old_game = deepcopy(game)
        game.print("Are you sure you want to reset?")
        return tc.InterfaceSequence(
            tc.Button("Reset", cls.perform_reset, dialog=True),
            tc.Button(
                "Cancel", cls.cancel_dialog, dialog=True, kwargs=dict(old_game=old_game)
            ),
        )

    @classmethod
    def reset_callback(cls, _) -> None:
        game = sv.load_game()
        game.run_passage(cls.reset_dialog, dialog=True)

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
        be.file_download_button(df.ElementId("export"), game_json, "troubadour.json")

        # reset button
        be.onclick(df.ElementId("reset"), cls.reset_callback)

    def run_passage(
        self, passage: Callable, *, dialog: bool = False, kwargs: dict[str, object] = {}
    ) -> None:
        if not dialog:
            self.timestamp()
        else:
            be.clear(df.ElementId("output"))
        be.clear(df.ElementId("input"))
        continuation: Interface | None = passage(self, **kwargs)
        if continuation is not None:
            self.input_state = continuation
            continuation.setup(self)
        be.scroll_to_bottom(df.ElementId("output"))
        sv.save_game(self)
