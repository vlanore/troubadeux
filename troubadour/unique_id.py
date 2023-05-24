from dataclasses import dataclass

from troubadour.definitions import ElementId


@dataclass
class IdProvider:
    next_id: int = 0

    def get(self) -> int:
        result = self.next_id
        self.next_id += 1
        return result


_global_provider = IdProvider()


def get_unique_id() -> int:
    global _global_provider
    return _global_provider.get()


def get_unique_element_id(name: str = "") -> ElementId:
    to_insert = name + "__" if name != "" else ""
    return ElementId(f"troubadour__{to_insert}{get_unique_id()}")
