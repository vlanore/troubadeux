import datetime
from typing import Callable

import jsonpickle as jsp

import troubadour.backend as be
import troubadour.definitions as df
import troubadour.game as tg
from troubadour.save import erase_save, load_game, save_game, state_exists


def reset(_) -> None:
    erase_save()
    be.refresh_page()


def run_game(StateCls: type, start_passage: Callable) -> None:
    if not state_exists():
        game = tg.Game(StateCls())
        run_passage(game, start_passage)
    else:
        game = load_game()
        for out in game.output_state:
            match out:
                case datetime.datetime():
                    t = out.strftime(r"%Y - %b %d - %H:%M:%S")
                    be.insert_end(
                        df.ElementId("output"), f"<div class='timestamp'>{t}</div>"
                    )
                case str():
                    be.insert_end(df.ElementId("output"), out)
        if game.input_state is not None:
            game.input_state.setup(game)
        be.scroll_to_bottom(df.ElementId("output"))

    # export button
    game_json = jsp.encode(game)
    assert game_json is not None
    be.file_download_button(df.ElementId("export"), game_json, "troubadour.json")

    # reset button
    be.onclick(df.ElementId("reset"), reset)


def run_passage(
    game: tg.Game,
    passage: Callable,
    *,
    args: dict[str, object] = {},
) -> None:
    game.timestamp()
    be.clear(df.ElementId("input"))
    continuation = passage(game, *args)
    game.input_state = continuation
    continuation.setup(game)
    be.scroll_to_bottom(df.ElementId("output"))
    save_game(game)
