import troubadour.definitions as df


def run(passage: df.Passage, context: df.Context) -> None:
    continuation = passage(context)
    continuation.setup(df.ElementId("input"), context)
