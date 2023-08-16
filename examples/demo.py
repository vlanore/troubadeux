from dataclasses import dataclass

from troubadour.continuations import Button, InterfaceSequence, TextButton
from troubadour.game import Game, Interface


@dataclass
class MyState:
    hello: int = 0


def intro(game: Game[MyState]) -> Interface:
    x = game.state.hello
    game.print("<h1>Hello</h1>World lorem ipsum stuff<p/>\n")
    game.print(f"Hello worlds: <b id='youpi'>{x}</b>\n")
    return Button("Click", my_other_passage, dict(msg="Youpi"))


def my_passage(game: Game[MyState]) -> Interface:
    game.state.hello += 1
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
        Button("Click", my_other_passage, dict(msg="Tralala")),
        Button("Clack", my_passage),
    )


def my_other_passage(game: Game[MyState], msg: str) -> Interface:
    game.print(f"Hi: <b>{game.state.hello}</b>")
    game.print(
        "<p>Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet.</p>"
    )
    game.print(f"<p>This is a message: <i>{msg}</i></p>")

    return InterfaceSequence(
        Button("Clack", my_passage),
        TextButton("Display", display_stuff, "msg"),
    )


def display_stuff(game: Game[MyState], msg: str) -> Interface:
    game.print(
        "<p>Nullam quis dignissim sapien, pulvinar congue sem. Proin consectetur,"
        f" lacus quis aliquet: <i>{msg}</i></p>"
    )

    return Button("Click", my_other_passage, dict(msg="hello world"))


Game.run(MyState, intro)
