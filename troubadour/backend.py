import pyscript  # type:ignore
from pyscript import display  # type:ignore


def pyscript_version() -> str:
    "Returns the version of pyscript currently running."
    return pyscript.__version__


def add_to_body(text: str) -> None:
    """Add text to the end of the document body.

    Arguments:
        * text (`str`): the text to add.
    """
    display(text, append=True, target="body")
