import troubadour.backend as be
import troubadour.definitions as df
from troubadour.definitions import Context, ElementId
from troubadour.run import run
from troubadour.continuations import Button, InterfaceSequence


def my_passage(_context: Context) -> df.Interface:
    print("Hello")
    return InterfaceSequence(
        Button("Click", my_other_passage), Button("Clack", my_passage)
    )


def my_other_passage(_context: Context) -> df.Interface:
    print("Hi")

    hello = be.local_storage(int)["hello"]
    hello += 1
    be.local_storage["hello"] = hello
    be.set_html(ElementId("youpi"), str(be.local_storage(int)["hello"]))

    return Button("Clack", my_passage)


run(my_passage, Context())


print(f"Advanced demo, running pyscript {be.pyscript_version()}")
be.insert_end(ElementId("body"), "<h1>Hello</h1>\n")
be.insert_end(ElementId("body"), f"world!! {be.local_storage.has_key('hello')}")
if not be.local_storage.has_key("hello"):
    be.local_storage["hello"] = 0
hello = be.local_storage(int)["hello"]
hello += 1
be.insert_end(ElementId("body"), f"<div>Hello: <b id='youpi'>{hello}</b></div>")
be.local_storage["hello"] = hello
