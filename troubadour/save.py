import troubadour.backend as be
import troubadour.definitions as df


def save_state(context: df.Context) -> None:
    be.local_storage["troubadour_state"] = context.state


def load_state() -> df.State:
    return be.local_storage(df.State)["troubadour_state"]


def state_exists() -> bool:
    return be.local_storage.has_key("troubadour_state")
