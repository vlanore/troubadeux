"Various helper functions to load/save games in local storage."

from typing import TypeVar

import jsonpickle as jsp

import troubadour.backend as be
from troubadour.definitions import Game, Eid


def save_game(game: Game) -> None:
    # store in local memory
    be.local_storage["troubadour_state"] = game

    # prepare export button
    setup_export_button(game)


def setup_export_button(game: Game) -> None:
    json_source = jsp.encode(game)
    assert json_source is not None
    be.file_download_button(Eid("export"), json_source, "troubadour.json")


T = TypeVar("T", bound=Game)


def setup_import_button(game_type: type[T]) -> None:
    def load_from_file(extracted_game: T):
        save_game(extracted_game)
        be.refresh_page()

    be.on_file_upload(Eid("import"), load_from_file, game_type)


def setup_reset_button() -> None:
    def perform_reset(_) -> None:
        erase_save()
        be.refresh_page()

    def reset_callback(_) -> None:
        be.set_display(Eid("modal-bg"), "flex")
        be.onclick(Eid("reset-button"), perform_reset)
        be.onclick(
            Eid("reset-cancel-button"),
            lambda _: be.set_display(Eid("modal-bg"), "none"),
        )

    be.onclick(Eid("reset"), reset_callback)


def load_game(game_type: type[T]) -> T:
    return be.local_storage(game_type)["troubadour_state"]


def state_exists() -> bool:
    return be.local_storage.has_key("troubadour_state")


def erase_save() -> None:
    be.local_storage.remove("troubadour_state")
