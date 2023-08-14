import troubadour.backend as be
import troubadour.definitions as df


def run(passage: df.Passage, context: df.Context, args: dict[str, object] = {}) -> None:
    be.clear(df.ElementId("input"))
    continuation = passage(context, *args)
    continuation.setup(df.ElementId("input"), context)
    be.scroll_to_bottom(df.ElementId("output"))
