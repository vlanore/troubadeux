from dataclasses import dataclass

import troubadour.backend as be
import troubadour.definitions as df
import troubadour.save as sv
from troubadour.continuations import Button, InterfaceSequence
from troubadour.definitions import Context, ElementId
from troubadour.run import run


@dataclass
class MyState(df.State):
    hello: int = 0


def intro(context: Context[MyState]) -> df.Interface:
    x = context.state.hello
    be.insert_end(ElementId("output"), "<h1>Hello</h1>World lorem ipsum stuff<p/>\n")
    be.insert_end(ElementId("output"), f"Hello worlds: <b id='youpi'>{x}</b>\n")
    return Button("Click", my_other_passage)


def my_passage(context: Context[MyState]) -> df.Interface:
    print("Hello")
    context.state.hello += 1
    be.insert_end(
        ElementId("output"),
        (
            "<p>Praesent leo diam, scelerisque dapibus commodo ut, facilisis sit amet "
            "felis. Donec libero lacus, interdum a tortor sed, vestibulum suipit nunc."
            " Aenean in imperdiet tortor. Curabitur ultricies, elit ut ullamcorper"
            " aliquam, arcu orci rutrum velit, in placerat purus augue sed sem."
            " Donec varius velit ac felis auctor, eu efficitur purus rutrum."
            " Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
            " congue sem. Proin consectetur, lacus quis aliquet porta, tellus"
            " diam pellentesque odio, eu ornare neque felis ac mi.</p>"
        ),
    )
    be.insert_end(
        ElementId("output"),
        (
            "<p>Donec varius velit ac felis auctor, eu efficitur purus rutrum."
            " Fusce id pharetra lacus. Nullam quis dignissim sapien, pulvinar"
            " congue sem. Proin consectetur, lacus quis aliquet porta, tellus"
            " diam pellentesque odio, eu ornare neque felis ac mi.</p>"
        ),
    )
    be.set_html(ElementId("youpi"), str(context.state.hello))
    return InterfaceSequence(
        Button("Click", my_other_passage), Button("Clack", my_passage)
    )


def my_other_passage(_context: Context) -> df.Interface:
    print("Hi")
    be.insert_end(ElementId("output"), "<p>Hi</p>")

    return Button("Clack", my_passage)


print(f"Advanced demo, running pyscript {be.pyscript_version()}")

if not sv.state_exists():
    run(intro, Context(state=MyState()), timestamp=True)
else:
    run(intro, Context(state=sv.load_state()), timestamp=True)
