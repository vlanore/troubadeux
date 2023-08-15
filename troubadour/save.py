import jsonpickle as jsp

import troubadour.backend as be
import troubadour.definitions as df


def save_state(context: df.Context) -> None:
    be.local_storage["troubadour_state"] = context.state
    json_source = jsp.encode(context.state)
    assert json_source is not None
    be.file_download_button("export", json_source, "save.json")


def load_state() -> df.State:
    return be.local_storage(df.State)["troubadour_state"]


def state_exists() -> bool:
    return be.local_storage.has_key("troubadour_state")
