import jsonpickle as jsp

import troubadour.backend as be
import troubadour.definitions as df


def save_game(game: df.Game) -> None:
    # store in local memory
    be.local_storage["troubadour_state"] = game

    # prepare export button
    json_source = jsp.encode(game)
    assert json_source is not None
    be.file_download_button("export", json_source, "save.json")


def load_game() -> df.Game:
    return be.local_storage(df.Game)["troubadour_state"]


def state_exists() -> bool:
    return be.local_storage.has_key("troubadour_state")
