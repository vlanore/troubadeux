"Global protocol and interface definitions."

from typing import Generic, NewType, Protocol, TypeVar, Callable

Eid = NewType("Eid", str)
"Id of an element on the page (typically, a HTML tag)."

Lid = NewType("Lid", int)
"Local Id of an element inside a passage."

Target = Lid | None


class Continuation(Protocol):
    "Inputs are user interface elements"

    def setup(self, game: "AbstractGame", target: "Eid" = Eid("output")) -> None:
        ...


class Output(Protocol):
    def paragraph(self, html: str = "", css: dict[str, str] | None = None) -> "Output":
        ...

    # def raw_html(self, html: str = "") -> None:
    #     ...

    def continuation(self, continuation: Continuation) -> None:
        ...


T = TypeVar("T")


class AbstractGame(Output, Protocol, Generic[T]):
    state: T

    def run_passage(
        self,
        passage: Callable,
        *,
        kwargs: dict[str, object] | None = None,
    ) -> None:
        ...
