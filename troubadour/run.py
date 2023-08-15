import datetime

import troubadour.backend as be
import troubadour.definitions as df
from troubadour.save import save_state


def run(
    passage: df.Passage,
    context: df.Context,
    *,
    args: dict[str, object] = {},
    timestamp: bool = False,
) -> None:
    if timestamp:
        t = datetime.datetime.now().strftime(r"%Y - %b %d - %H:%M:%S")
        be.insert_end(df.ElementId("output"), f"<div class='timestamp'>{t}</div>")

    be.clear(df.ElementId("input"))
    continuation = passage(context, *args)
    continuation.setup(df.ElementId("input"), context)
    be.scroll_to_bottom(df.ElementId("output"))
    save_state(context)
