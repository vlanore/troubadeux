from typing import NewType, Protocol


class Output(Protocol):
    def p(self, html: str = "") -> "Output":
        ...


eid = NewType("eid", str)
"Id of an element on the page (typically, a HTML tag)."

lid = NewType("lid", int)
"Local Id of an element inside a passage."

Target = lid | None
