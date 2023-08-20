from dataclasses import dataclass

from troubadour.definitions import Eid


@dataclass
class _IdProvider:
    "Class that provides unique ints on demand through its `get` method."
    next_id: int = 0

    def get(self) -> int:
        "Returns a unique int every time."
        result = self.next_id
        self.next_id += 1
        return result


_global_provider = _IdProvider()
"Global id provider."


def get_unique_id() -> int:
    "Returns a unique int every time."
    return _global_provider.get()


def get_unique_element_id(name: str = "") -> Eid:
    """Returns a unique troubadour element id of the form "troubadour__XY"
    where X is the optional `name` argument, and Y is a unique integer.

    For example, if `name` is "button", this function might
    return the unique identifier `ElementId("troubadour__button17")`.

    Args:
        - name (`str`): optional name for identifier sub-category."""

    to_insert = name + "__" if name != "" else ""
    return Eid(f"troubadour__{to_insert}{get_unique_id()}")
