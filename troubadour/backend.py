"Module that provides many functions to interact with the web page."

from typing import Any, Callable, Generic, Optional, Type, TypeVar

import js  # type: ignore
import jsonpickle as jsp
import pyscript
from pyodide.code import run_js  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import Element  # type: ignore

from troubadour.definitions import Eid


def pyscript_version() -> str:
    "Returns the version of pyscript currently running."
    return pyscript.__version__


def onclick(id: Eid, func: Callable[[Any], None]) -> None:
    """Add on click callback to element.

    Args:
        id (str): html id of element.
        func (Callable[[Any], None]): callback.
    """
    Element(id).element.addEventListener("click", create_proxy(func))


def onload(id: Eid, func: Callable[[Any], None]) -> None:
    Element(id).element.addEventListener("load", create_proxy(func))


def insert_end(id: Eid, html: str) -> None:
    Element(id).element.insertAdjacentHTML("beforeend", html)


def set_html(id: Eid, html: str) -> None:
    Element(id).element.innerHTML = html


def get_html(id: Eid) -> str:
    return Element(id).element.innerHTML


def clear(id: Eid) -> None:
    set_html(id, "")


def click(id: Eid) -> None:
    Element(id).element.click()


def set_src(id: Eid, value: str) -> None:
    Element(id).element.src = value


def set_alt(id: Eid, value: str) -> None:
    Element(id).element.alt = value


def get_value(id: Eid) -> str:
    return Element(id).element.value


def add_class(id: Eid, cls: str) -> None:
    Element(id).add_class(cls)


def remove_class(id: Eid, cls: str) -> None:
    Element(id).remove_class(cls)


def set_display(id: Eid, display: str) -> None:
    Element(id).element.style.display = display


def scroll_to_bottom(id: Eid) -> None:
    tgt = Element(id).element
    tgt.scrollTop = tgt.scrollHeight


def refresh_page() -> None:
    run_js("location.reload();")


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

    def remove(self, key: str) -> None:
        js.localStorage.removeItem(key)

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


def file_download_button(id: str, content: str, filename: str) -> None:
    run_js(
        f"""
const blob = new Blob(
    [`{content.encode("unicode_escape").decode("utf-8")}`], {{type: 'text/json'}});
const button = document.getElementById("{id}");
button.href = URL.createObjectURL(blob);
button.download = "{filename}";
        """
    )
    # FIXME revoke url


def on_file_upload(
    id: Eid,
    callback: Callable[[str], None] | Callable[[T], None],
    cls: Optional[Type[T]] = None,
) -> None:
    async def event_handler(event: Any, cb: Callable = callback) -> None:
        file_list = event.target.files.to_py()
        for f in file_list:
            raw = await f.text()
            if cls is None:
                cb(raw)
            else:
                decoded = jsp.decode(raw)
                assert isinstance(decoded, cls)
                cb(decoded)
        Element(id).element.value = ""

    Element(id).element.addEventListener("change", create_proxy(event_handler))
