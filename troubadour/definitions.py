from typing import Generic, NewType, Protocol, TypeVar, Callable

eid = NewType("eid", str)
"Id of an element on the page (typically, a HTML tag)."

lid = NewType("lid", int)
"Local Id of an element inside a passage."

Target = lid | None


class Continuation(Protocol):
    "Inputs are user interface elements"

    def setup(self, game: "AbstractGame", target: "eid" = eid("output")) -> None:
        ...


class Output(Protocol):
    def p(self, html: str = "") -> "Output":
        ...

    # def raw_html(self, html: str = "") -> None:
    #     ...

    def continuation(self, continuation: Continuation) -> None:
        ...


T = TypeVar("T")


class AbstractGame(Output, Protocol, Generic[T]):
    state: T

    def _run_passage(
        self, passage: Callable, *, dialog: bool = False, kwargs: dict[str, object] = {}
    ) -> None:
        ...
