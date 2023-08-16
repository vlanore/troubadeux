from __future__ import annotations

import jsonpickle as jsp

import troubadour.backend as be
import troubadour.game as tg


def save_game(game: tg.Game) -> None:
    # store in local memory
    be.local_storage["troubadour_state"] = game

    # prepare export button
    json_source = jsp.encode(game)
    assert json_source is not None
    be.file_download_button("export", json_source, "save.json")


def load_game() -> tg.Game:
    return be.local_storage(tg.Game)["troubadour_state"]


def state_exists() -> bool:
    return be.local_storage.has_key("troubadour_state")


def erase_save() -> None:
    be.local_storage.remove("troubadour_state")
