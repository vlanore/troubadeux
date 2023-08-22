"Main troubadour module that implements the Game class."

import datetime
from dataclasses import dataclass, field
from typing import Callable, TypeVar

import troubadour.backend as be
import troubadour.save as sv
from troubadour.definitions import AbstractGame, Continuation, Output, Target, Eid, Lid
from troubadour.unique_id import get_unique_element_id

T = TypeVar("T")


@dataclass
class Element(Output):
    local_id: Lid
    game: "Game"

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

    def new_lid(self) -> Lid:
        result = self.next_lid
        self.next_lid += 1
        return Lid(result)


@dataclass
class Game(AbstractGame[T]):
    state: T
    max_output_len: int = 15
    _output: list[PassageOutput] = field(default_factory=list)
    _current_passage: PassageContext = field(default_factory=PassageContext)
    _last_passage: Eid | None = None

    def print(self, html: str, target: Target = None) -> None:
        self._current_passage.output.contents.append(RawHTML(html, target))

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
            try:
                game = sv.load_game(Game)
                game._render()  # pylint: disable=W0212
            except Exception:  # pylint: disable=W0718
                be.insert_end(
                    Eid("output"),
                    (
                        "<h1> Something went wrong during loading</h1>"
                        "<p>You can try resetting the game "
                        "(this will remove all progress).</p>"
                    ),
                )
                cls._setup_reset_button()  # pylint: disable=W0212
                be.remove(Eid("import-label"))
                be.remove(Eid("export"))
                return

        # export button
        sv.setup_export_button(game)

        # import button
        def load_from_file(extracted_game: Game):
            sv.save_game(extracted_game)
            be.refresh_page()

        be.on_file_upload(Eid("import"), load_from_file, Game)

        # reset button
        cls._setup_reset_button()  # pylint: disable=W0212

    @classmethod
    def _setup_reset_button(cls) -> None:
        def perform_reset(_) -> None:
            sv.erase_save()
            be.refresh_page()

        def reset_callback(_) -> None:
            be.set_display(Eid("modal-bg"), "flex")
            be.onclick(Eid("reset-button"), perform_reset)
            be.onclick(
                Eid("reset-cancel-button"),
                lambda _: be.set_display(Eid("modal-bg"), "none"),
            )

        be.onclick(Eid("reset"), reset_callback)

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
