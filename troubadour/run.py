import troubadour.backend as be
import troubadour.definitions as df


def run(passage: df.Passage, context: df.Context) -> None:
    be.clear(df.ElementId("input"))
    continuation = passage(context)
    continuation.setup(df.ElementId("input"), context)
