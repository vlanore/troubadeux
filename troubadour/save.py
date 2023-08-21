"Various helper functions to load/save games in local storage."

from typing import TypeVar

import jsonpickle as jsp

import troubadour.backend as be
from troubadour.definitions import AbstractGame


def save_game(game: AbstractGame) -> None:
    # store in local memory
    be.local_storage["troubadour_state"] = game

    # prepare export button
    setup_export_button(game)


def setup_export_button(game: AbstractGame) -> None:
    json_source = jsp.encode(game)
    assert json_source is not None
    be.file_download_button("export", json_source, "troubadour.json")


T = TypeVar("T")


def load_game(game_type: type[T]) -> T:
    return be.local_storage(game_type)["troubadour_state"]


def state_exists() -> bool:
    return be.local_storage.has_key("troubadour_state")


def erase_save() -> None:
    be.local_storage.remove("troubadour_state")
