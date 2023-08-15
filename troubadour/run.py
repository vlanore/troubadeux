import datetime
from typing import Callable

import troubadour.backend as be
import troubadour.definitions as df
from troubadour.save import save_game, state_exists, load_game


def run_game(StateCls: type, start_passage: Callable) -> None:
    if not state_exists():
        game = df.Game(StateCls())
        run_passage(game, start_passage)
    else:
        game = load_game()
        for out in game.output_state:
            t = out.timestamp.strftime(r"%Y - %b %d - %H:%M:%S")
            be.insert_end(df.ElementId("output"), f"<div class='timestamp'>{t}</div>")
            be.insert_end(df.ElementId("output"), out.html)
        if game.input_state is not None:
            game.input_state.setup(game)
        be.scroll_to_bottom(df.ElementId("output"))


def run_passage(
    game: df.Game,
    passage: Callable,
    *,
    args: dict[str, object] = {},
) -> None:
    # timestamp
    ts = datetime.datetime.now()
    t = ts.strftime(r"%Y - %b %d - %H:%M:%S")
    be.insert_end(df.ElementId("output"), f"<div class='timestamp'>{t}</div>")

    be.clear(df.ElementId("input"))
    continuation = passage(game, *args)
    game.input_state = continuation
    game.output_state = [
        df.GameOutput(be.get_html(df.ElementId("output")), datetime.datetime.now())
    ]
    continuation.setup(game)
    be.scroll_to_bottom(df.ElementId("output"))
    save_game(game)
