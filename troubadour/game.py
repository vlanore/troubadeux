import datetime
from dataclasses import dataclass, field
from typing import Callable, TypeVar

import jsonpickle as jsp

import troubadour.backend as be
import troubadour.continuations as tc
import troubadour.save as sv
from troubadour.definitions import AbstractGame, Continuation, Output, Target, Eid, Lid
from troubadour.unique_id import get_unique_element_id

T = TypeVar("T")


class ResetDialog:
    @classmethod
    def perform_reset(cls, _game: "Game") -> None:
        sv.erase_save()
        be.refresh_page()

    @classmethod
    def dialog(cls, _game: "Game") -> None:
        be.insert_end(
            Eid("output"),
            (
                "<h1>Game reset</h1>"
                "<p>Are you sure you want to reset?</p>"
                "<p>This will <b>erase all game data</b>."
            ),
        )

        tc.Button("Reset", cls.perform_reset, dialog=True).setup(_game)
        tc.Button("Cancel", Game.cancel_dialog, dialog=True).setup(_game)

    @classmethod
    def callback(cls, _) -> None:
        game = sv.load_game()
        game.run_passage(cls.dialog, dialog=True)


@dataclass
class Element(Output):
    local_id: Lid
    game: "Game"

    def p(self, html: str = "") -> "Element":
        return self.game.p(html, target=self.local_id)

    def continuation(self, continuation: Continuation) -> None:
        self.game.continuation(continuation, target=self.local_id)


@dataclass
class TimeStamp:
    date: datetime.datetime
    target: Target


@dataclass
class RawHTML:
    html: str
    target: Target


@dataclass
class Container:
    markup: str
    html: str
    css: dict[str, str]
    target: Target
    local_id: Lid


@dataclass
class ContinuationElement:
    continuation: Continuation
    target: Target


PassageElement = RawHTML | TimeStamp | Container | ContinuationElement


@dataclass
class PassageOutput:  # FIXME remove next_lid + lid_to_eid
    contents: list[PassageElement] = field(default_factory=list)
    next_lid: int = 0
    lid_to_eid: dict[Lid, Eid] = field(default_factory=dict)

    def new_lid(self) -> Lid:
        result = self.next_lid
        self.next_lid += 1
        return Lid(result)


@dataclass
class Game(AbstractGame[T]):
    state: T
    output_state: list[PassageOutput] = field(default_factory=list)
    current_passage: PassageOutput = field(default_factory=PassageOutput)
    max_output_len: int = 10

    def print(self, html: str, target: Target = None) -> None:
        self.current_passage.contents.append(RawHTML(html, target))

    def p(
        self, html: str = "", target: Target = None, css: dict[str, str] = {}
    ) -> Element:
        local_id = self.current_passage.new_lid()
        self.current_passage.contents.append(
            Container("p", html, css, target, local_id)
        )
        return Element(local_id, self)

    def continuation(self, continuation: Continuation, target: Target = None) -> None:
        self.current_passage.contents.append(
            ContinuationElement(continuation, target=target)
        )

    def continuations(
        self, *continuations: Continuation, target: Target = None
    ) -> None:
        zone = self.p(css={"class": "'inputzone'"}, target=target)
        for continuation in continuations:
            zone.continuation(continuation)

    def _timestamp(self) -> None:
        timestamp = datetime.datetime.now()
        self.current_passage.contents.append(TimeStamp(timestamp, target=None))

    def _render_passage(self, passage: PassageOutput) -> None:
        passage.lid_to_eid = {}
        for out in passage.contents:
            eid_target = (
                passage.lid_to_eid[out.target]
                if out.target is not None
                else Eid("output")
            )
            match out:
                case TimeStamp(date=date):
                    t = date.strftime(r"%Y - %b %d - %H:%M:%S")
                    be.insert_end(eid_target, f"<div class='timestamp'>{t}</div>")
                case RawHTML(html=html):
                    be.insert_end(eid_target, html)
                case Container(markup=markup, html=html, css=css, local_id=local_id):
                    element_id = get_unique_element_id("container")
                    passage.lid_to_eid[local_id] = element_id
                    rcss = " ".join(f"{key}={value}" for key, value in css.items())
                    be.insert_end(
                        eid_target,
                        f"<{markup} {rcss} id='{element_id}'>{html}</{markup}>",
                    )
                case ContinuationElement(continuation=continuation):
                    continuation.setup(self, eid_target)

    def _render(self) -> None:
        be.clear(Eid("output"))
        for passage in self.output_state:
            self._render_passage(passage)
        be.scroll_to_bottom(Eid("output-container"))

    @classmethod
    def cancel_dialog(cls, game: "Game") -> None:
        game._render()  # pylint: disable=W0212

    @classmethod
    def run(
        cls, StateCls: type, start_passage: Callable  # pylint: disable=C0103
    ) -> None:
        if not sv.state_exists():
            game = Game(StateCls())
            game.run_passage(start_passage)
        else:
            game = sv.load_game()
            game._render()  # pylint: disable=W0212

        # export button
        game_json = jsp.encode(game)
        assert game_json is not None
        be.file_download_button(Eid("export"), game_json, "troubadour.json")

        # reset button
        be.onclick(Eid("reset"), ResetDialog.callback)

    def _trim_output(self) -> None:
        if len(self.output_state) > self.max_output_len:
            trim_index = -self.max_output_len
            self.output_state = self.output_state[trim_index:]
            self._render()

    def run_passage(
        self,
        passage: Callable,
        *,
        dialog: bool = False,
        kwargs: dict[str, object] | None = None,
    ) -> None:
        # new empty passage
        self.current_passage = PassageOutput()

        if not dialog:
            self._timestamp()
        else:
            be.clear(Eid("output"))  # if dialog then need to clear whole output
        passage(self, **(kwargs if kwargs is not None else {}))

        # render the passage and scroll to bottom of page
        self._render_passage(self.current_passage)
        be.scroll_to_bottom(Eid("output-container"))

        if not dialog:
            self.output_state.append(self.current_passage)
            self.current_passage = PassageOutput()
            self._trim_output()
            sv.save_game(self)
