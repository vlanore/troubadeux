"Small troubadour demo and test file."

from dataclasses import dataclass

from troubadour.continuations import Button, TextButton
from troubadour.game import Game


@dataclass
class MyState:
    hello: int = 0


def intro(game: Game[MyState]) -> None:
    x = game.state.hello
    game.p("<h1>Hello</h1>World lorem ipsum stuff<p/>\n")
    game.p(f"Hello worlds: <b id='youpi'>{x}</b>\n")
    game.continuations(Button("Click", my_other_passage, dict(msg="Youpi")))


def my_passage(game: Game[MyState]) -> None:
    game.state.hello += 1
    game.p(
        "Praesent leo diam, scelerisque dapibus commodo ut, facilisis sit amet "
        "felis. Donec libero lacus, interdum a tortor sed, vestibulum suipit nunc."
        " Aenean in imperdiet tortor. Curabitur ultricies, elit ut ullamcorper"
        " aliquam, arcu orci rutrum velit, in placerat purus augue sed sem."
        " Donec varius velit ac felis auctor, eu efficitur purus rutrum."
        " Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet porta, tellus"
        " diam pellentesque odio, eu ornare neque felis ac mi."
    )
    game.p(
        "Donec varius velit ac felis auctor, eu efficitur purus rutrum."
        " Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet porta, tellus"
        " diam pellentesque odio, eu ornare neque felis ac mi."
    )
    game.continuations(
        Button("Click", my_other_passage, dict(msg="Tralala")),
        Button("Clack", my_passage),
    )


def my_other_passage(game: Game[MyState], msg: str) -> None:
    game.p(f"Hi: <b>{game.state.hello}</b>")
    game.p(
        "Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet."
    )
    my_p = game.p(f"This is a message: <i>{msg}</i>")
    my_p.p("test")

    game.continuations(
        Button("Clack", my_passage),
        TextButton("Display", display_stuff, "msg"),
    )


def display_stuff(game: Game[MyState], msg: str) -> None:
    game.p(
        "Nullam quis dignissim sapien, pulvinar congue sem. Proin consectetur,"
        f" lacus quis aliquet: <i>{msg}</i>"
    )

    game.continuations(Button("Click", my_other_passage, {"msg": "hello world"}))


Game.run(MyState, intro)
