from dataclasses import dataclass

import troubadour.backend as be
import troubadour.definitions as df
from troubadour.continuations import Button, InterfaceSequence
from troubadour.definitions import Context, ElementId
from troubadour.run import run


@dataclass
class MyState(df.State):
    hello: int = 0


def my_passage(context: Context[MyState]) -> df.Interface:
    print("Hello")
    context.state.hello += 1
    be.set_html(ElementId("youpi"), str(context.state.hello))
    return InterfaceSequence(
        Button("Click", my_other_passage), Button("Clack", my_passage)
    )


def my_other_passage(_context: Context) -> df.Interface:
    print("Hi")
    be.insert_end(ElementId("output"), "<p>Hi</p>")

    return Button("Clack", my_passage)


print(f"Advanced demo, running pyscript {be.pyscript_version()}")
be.insert_end(ElementId("output"), "<h1>Hello</h1>World lorem ipsum stuff<p/>\n")
be.insert_end(ElementId("output"), "Hello worlds: <b id='youpi'>0</b>\n")

run(my_passage, Context(state=MyState()))
