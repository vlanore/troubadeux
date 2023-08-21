"Small troubadour demo and test file."

from dataclasses import dataclass

from troubadour import Button, TextButton, Game


@dataclass
class MyState:
    hello: int = 0


def intro(game: Game[MyState]) -> None:
    x = game.state.hello
    game.paragraph("<h1>Hello</h1>World lorem ipsum stuff<p/>\n")
    game.paragraph(f"Hello worlds: <b id='youpi'>{x}</b>\n")
    game.continuations(Button("Click", my_other_passage, dict(msg="Youpi")))


def my_passage(game: Game[MyState]) -> None:
    game.state.hello += 1
    game.paragraph(
        "Praesent leo diam, scelerisque dapibus commodo ut, facilisis sit amet "
        "felis. Donec libero lacus, interdum a tortor sed, vestibulum suipit nunc."
        " Aenean in imperdiet tortor. Curabitur ultricies, elit ut ullamcorper"
        " aliquam, arcu orci rutrum velit, in placerat purus augue sed sem."
        " Donec varius velit ac felis auctor, eu efficitur purus rutrum."
        " Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet porta, tellus"
        " diam pellentesque odio, eu ornare neque felis ac mi."
    )
    game.paragraph(
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
    game.paragraph(f"Hi: <b>{game.state.hello}</b>")
    game.paragraph(
        "Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
        " congue sem. Proin consectetur, lacus quis aliquet."
    )
    my_p = game.paragraph(f"This is a message: <i>{msg}</i>")
    my_p.paragraph("test")

    game.continuations(
        Button("Clack", my_passage),
        TextButton("Display", display_stuff, "msg"),
    )


def display_stuff(game: Game[MyState], msg: str) -> None:
    game.paragraph(
        "Nullam quis dignissim sapien, pulvinar congue sem. Proin consectetur,"
        f" lacus quis aliquet: <i>{msg}</i>"
    )

    game.continuations(Button("Click", my_other_passage, dict(msg="hello world")))


Game.run(MyState, intro)
