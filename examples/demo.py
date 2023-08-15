from dataclasses import dataclass

from troubadour.continuations import Button, InterfaceSequence
from troubadour.game import Game, Interface
from troubadour.run import run_game


@dataclass
class MyState:
    hello: int = 0


def intro(game: Game[MyState]) -> Interface:
    x = game.game_state.hello
    game.print("<h1>Hello</h1>World lorem ipsum stuff<p/>\n")
    game.print(f"Hello worlds: <b id='youpi'>{x}</b>\n")
    return Button("Click", my_other_passage)


def my_passage(game: Game[MyState]) -> Interface:
    game.game_state.hello += 1
    game.print(
        "<p>Praesent leo diam, scelerisque dapibus commodo ut, facilisis sit amet "
        "felis. Donec libero lacus, interdum a tortor sed, vestibulum suipit nunc."
        " Aenean in imperdiet tortor. Curabitur ultricies, elit ut ullamcorper"
        " aliquam, arcu orci rutrum velit, in placerat purus augue sed sem."
        " Donec varius velit ac felis auctor, eu efficitur purus rutrum."
        " Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet porta, tellus"
        " diam pellentesque odio, eu ornare neque felis ac mi.</p>"
    )
    game.print(
        "<p>Donec varius velit ac felis auctor, eu efficitur purus rutrum."
        " Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet porta, tellus"
        " diam pellentesque odio, eu ornare neque felis ac mi.</p>"
    )
    return InterfaceSequence(
        Button("Click", my_other_passage), Button("Clack", my_passage)
    )


def my_other_passage(game: Game[MyState]) -> Interface:
    game.print(f"Hi: <b>{game.game_state.hello}</b>")

    return Button("Clack", my_passage)


run_game(MyState, intro)
