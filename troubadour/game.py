"Main troubadour module that implements the Game class."

import datetime
from dataclasses import dataclass, field
from typing import Callable, TypeVar

import troubadour.backend as be
import troubadour.save as sv
from troubadour.definitions import Continuation, Eid, Game, Lid, Output, Target
from troubadour.unique_id import IdProvider, get_unique_element_id

T = TypeVar("T")


@dataclass
class Element(Output):
    local_id: Lid
    game: "GameImpl"

    def paragraph(self, html: str = "", css: dict[str, str] | None = None) -> "Element":
        return self.game.paragraph(html, css=css, target=self.local_id)

    def container(
        self,
        markup: str,
        html: str = "",
        css: dict[str, str] | None = None,
    ) -> "Element":
        return self.game.container(markup, html, css=css, target=self.local_id)

    def raw_html(self, html: str = "") -> None:
        return self.game.raw_html(html, target=self.local_id)

    def img(self, src: str = "") -> None:
        return self.game.img(src, target=self.local_id)

    def continuation(self, continuation: Continuation) -> None:
        self.game.continuation(continuation, target=self.local_id)

    def continuations(self, *continuations: Continuation) -> None:
        self.game.continuations(*continuations, target=self.local_id)

    def columns(self, nb_col: int, html: None | list[str]) -> list[Output]:
        return self.game.columns(nb_col, html, target=self.local_id)


@dataclass
class TimeStamp:
    date: datetime.datetime
    target: Target


@dataclass
class RawHTML:
    html: str
    target: Target


@dataclass
class Image:
    src: str
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


PassageElement = RawHTML | TimeStamp | Container | ContinuationElement | Image


@dataclass
class PassageOutput:
    contents: list[PassageElement] = field(default_factory=list)


@dataclass
class PassageContext:
    output: PassageOutput = field(default_factory=PassageOutput)
    next_lid: int = 0
    lid_to_eid: dict[Lid, Eid] = field(default_factory=dict)
    _id_provider: IdProvider = field(default_factory=IdProvider)

    def new_lid(self) -> Lid:
        return Lid(self._id_provider.get())


@dataclass
class GameImpl(Game[T]):
    """The core troubadour class: encapsulates game and output state and provides
    methods to output text. All passages should take a Game as first parameter and
    the class method `run` should be called to run the game."""

    state: T
    max_output_len: int = 15
    _output: list[PassageOutput] = field(default_factory=list)
    _current_passage: PassageContext = field(default_factory=PassageContext)
    _last_passage: Eid | None = None

    def paragraph(
        self, html: str = "", css: dict[str, str] | None = None, target: Target = None
    ) -> Element:
        return self.container("p", html=html, css=css, target=target)

    def container(
        self,
        markup: str,
        html: str = "",
        css: dict[str, str] | None = None,
        target: Target = None,
    ) -> Element:
        local_id = self._current_passage.new_lid()
        self._current_passage.output.contents.append(
            Container(markup, html, (css if css is not None else {}), target, local_id)
        )
        return Element(local_id, self)

    def columns(
        self, nb_col: int, html: None | list[str], target: Target = None
    ) -> list[Output]:
        container = self.container("div", css={"class": '"columns"'}, target=target)
        assert html is None or len(html) == nb_col
        return [
            container.container(
                "div",
                html=html[col_id] if html is not None else "",
                css={"class": '"column"'},
            )
            for col_id in range(nb_col)
        ]

    def raw_html(self, html: str = "", target: Target = None) -> None:
        self._current_passage.output.contents.append(RawHTML(html, target))

    def img(self, src: str = "", target: Target = None) -> None:
        self._current_passage.output.contents.append(Image(src, target))

    def continuation(self, continuation: Continuation, target: Target = None) -> None:
        self._current_passage.output.contents.append(
            ContinuationElement(continuation, target=target)
        )

    def continuations(
        self, *continuations: Continuation, target: Target = None
    ) -> None:
        zone = self.paragraph(css={"class": "'inputzone'"}, target=target)
        for continuation in continuations:
            zone.continuation(continuation)

    def _timestamp(self) -> None:
        timestamp = datetime.datetime.now()
        self._current_passage.output.contents.append(TimeStamp(timestamp, target=None))

    def _render_passage(self, passage: PassageOutput, disabled: bool = False) -> None:
        context = PassageContext(passage)
        passage_id = get_unique_element_id("passage")
        self._last_passage = passage_id
        be.insert_end(Eid("output"), f"<div class='passage' id={passage_id}>")
        for out in passage.contents:
            eid_target = (
                context.lid_to_eid[out.target]
                if out.target is not None
                else Eid(passage_id)
            )
            match out:
                case TimeStamp(date=date):
                    t = date.strftime(r"%Y - %b %d - %H:%M:%S")
                    be.insert_end(eid_target, f"<div class='timestamp'>{t}</div>")
                case RawHTML(html=html):
                    be.insert_end(eid_target, html)
                case Container(markup=markup, html=html, css=css, local_id=local_id):
                    element_id = get_unique_element_id("container")
                    context.lid_to_eid[local_id] = element_id
                    rcss = " ".join(f"{key}={value}" for key, value in css.items())
                    be.insert_end(
                        eid_target,
                        f"<{markup} {rcss} id='{element_id}'>{html}</{markup}>",
                    )
                case ContinuationElement(continuation=continuation):
                    continuation.setup(self, eid_target, disabled)
                case Image(src=src):
                    img_id = get_unique_element_id("image")
                    be.insert_end(eid_target, f"<img id='{img_id}' src='{src}' />")
                    be.onload(
                        img_id, lambda _: be.scroll_to_bottom(Eid("output-container"))
                    )

    def _render(self) -> None:
        be.clear(Eid("output"))
        for passage in self._output[:-1]:
            self._render_passage(passage, disabled=True)
        self._render_passage(self._output[-1])
        be.scroll_to_bottom(Eid("output-container"))

    def _trim_output(self) -> None:
        if len(self._output) > self.max_output_len:
            trim_index = -self.max_output_len
            self._output = self._output[trim_index:]
            self._render()

    def run_passage(
        self,
        passage: Callable,
        *,
        kwargs: dict[str, object] | None = None,
    ) -> None:
        # disable previous passage
        if self._last_passage is not None:
            be.remove(self._last_passage)
            self._render_passage(self._output[-1], disabled=True)

        # new empty passage
        self._current_passage = PassageContext()

        anchor_id = get_unique_element_id("anchor")
        self.raw_html(f"<span id='{anchor_id}'>")
        self._timestamp()
        passage(self, **(kwargs if kwargs is not None else {}))

        # render the passage and scroll to bottom of page
        self._render_passage(self._current_passage.output)
        be.scroll_into_view(Eid(anchor_id))
        # be.scroll_to_bottom(Eid("output-container"))

        self._output.append(self._current_passage.output)
        self._current_passage = PassageContext()
        self._trim_output()
        sv.save_game(self)


def run_game(StateCls: type, start_passage: Callable) -> None:  # pylint: disable=C0103
    """Depending on the presence of a game state in local storage, either load from
    storage or start a new game at passage `start_passage` with starting state
    `StateCls`.

    Args:
        `StateCls` (`type`): state class to instantiate (should support 0 params) to
            start a new game.
        `start_passage` (`Callable`): passage to run at the start of the new game.
    """
    if not sv.state_exists():  # if there is no state in storage, start new game
        game = GameImpl(StateCls())
        game.run_passage(start_passage)
    else:  # otherwise try to start from stored state
        try:
            game = sv.load_game(GameImpl)
            game._render()  # pylint: disable=W0212
        except Exception:  # pylint: disable=W0718
            # if something went wrong during loading, display a massage and offer
            # the option to restart
            be.insert_end(
                Eid("output"),
                (
                    "<h1> Something went wrong during loading</h1>"
                    "<p>You can try resetting the game "
                    "(this will remove all progress).</p>"
                ),
            )
            sv.setup_reset_button()
            be.remove(Eid("import-label"))
            be.remove(Eid("export"))
            return  # return to avoid setting up import/export buttons

    # setting up buttons
    sv.setup_export_button(game)
    sv.setup_import_button(GameImpl)
    sv.setup_reset_button()
