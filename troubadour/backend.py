from typing import Any, Callable, Generic, Optional, Type, TypeVar

import jsonpickle as jsp
import pyscript
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import js  # type: ignore


def pyscript_version() -> str:
    "Returns the version of pyscript currently running."
    return pyscript.__version__


def onclick(id: str, func: Callable[[Any], None]) -> None:
    """Add on click callback to element.

    Args:
        id (str): html id of element.
        func (Callable[[Any], None]): callback.
    """
    Element(id).element.addEventListener("click", create_proxy(func))


def onload(id: str, func: Callable[[Any], None]) -> None:
    Element(id).element.addEventListener("load", create_proxy(func))


def insert_end(id: str, html: str) -> None:
    Element(id).element.insertAdjacentHTML("beforeend", html)


def set_html(id: str, html: str) -> None:
    Element(id).element.innerHTML = html


def clear(id: str) -> None:
    set_html(id, "")


def click(id: str) -> None:
    Element(id).element.click()


def set_src(id: str, value: str) -> None:
    Element(id).element.src = value


def set_alt(id: str, value: str) -> None:
    Element(id).element.alt = value


def get_value(id: str) -> str:
    return Element(id).element.value


def add_class(id: str, cls: str) -> None:
    Element(id).add_class(cls)


def remove_class(id: str, cls: str) -> None:
    Element(id).remove_class(cls)


def set_display(id: str, display: str) -> None:
    Element(id).element.style.display = display


def scroll_to_bottom(id: str) -> None:
    tgt = Element(id).element
    tgt.scrollTop = tgt.scrollHeight


T = TypeVar("T")


class LocalStorage:
    """Interface to browser local storage. Provides container-style interface (with
    square brackets)."""

    def __getitem__(self, key: str) -> Optional[str]:
        return js.localStorage.getItem(key)

    def __setitem__(self, key: str, value: Any) -> None:
        js.localStorage.setItem(key, jsp.encode(value))

    def has_key(self, key: str) -> bool:
        return self[key] is not None

    def __call__(self, cls: Type[T]) -> "TypedLocalStorage[T]":
        """Helper interface to provided typed access to local storage. Usage is
        local_storage(cls)[key].

        Args:
            cls (Type[T]): expected class of stored item.

        Returns:
            TypedLocalStorage[T]: helper object that provides typed getitem.
        """
        return TypedLocalStorage(cls)


class TypedLocalStorage(Generic[T]):
    """Helper class that provides typed getitem."""

    def __init__(self, cls: Type[T]) -> None:
        self.cls = cls

    def __getitem__(self, key: str) -> T:
        result = js.localStorage.getItem(key)
        if result is not None:
            decoded_result = jsp.decode(result)
            assert isinstance(decoded_result, self.cls)
            return decoded_result
        else:
            raise KeyError()


local_storage = LocalStorage()
"Global local storage object."
