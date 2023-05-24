import troubadour.backend as be
import troubadour.definitions as df


def run(passage: df.Passage, context: df.Context) -> None:
    be.clear("input")
    continuation = passage(context)
    continuation.setup(df.ElementId("input"), context)
