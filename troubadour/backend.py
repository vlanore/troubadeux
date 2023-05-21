import pyscript  # type:ignore
import js


def pyscript_version() -> str:
    "Returns the version of pyscript currently running."
    return pyscript.__version__


def add_to_body(text: str) -> None:
    pyscript.Element("body").write(text, append=True)
