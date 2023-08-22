"Global protocol and interface definitions."

from typing import Callable, Generic, NewType, Protocol, TypeVar, runtime_checkable

Eid = NewType("Eid", str)
"Id of an element on the page (typically, a HTML tag)."

Lid = NewType("Lid", int)
"Local Id of an element inside a passage."

Target = Lid | None


class Continuation(Protocol):
    "Inputs are user interface elements"

    def setup(
        self,
        game: "AbstractGame",
        target: "Eid" = Eid("output"),
        disabled: bool = False,
    ) -> None:
        ...


class Output(Protocol):
    def paragraph(self, html: str = "", css: dict[str, str] | None = None) -> "Output":
        ...

    def container(
        self, markup: str, html: str = "", css: dict[str, str] | None = None
    ) -> "Output":
        ...

    def raw_html(self, html: str = "") -> None:
        ...

    def img(self, src: str = "") -> None:
        ...

    def continuation(self, continuation: Continuation) -> None:
        ...

    def columns(self, nb_col: int, html: None | list[str]) -> list["Output"]:
        ...


T = TypeVar("T")


@runtime_checkable
class AbstractGame(Output, Protocol, Generic[T]):
    state: T

    def run_passage(
        self,
        passage: Callable,
        *,
        kwargs: dict[str, object] | None = None,
    ) -> None:
        ...
