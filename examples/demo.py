import troubadour.backend as be
import troubadour.definitions as df
from troubadour.definitions import Context, ElementId
from troubadour.run import run
from troubadour.continuations import Button, ContinuationList


def my_passage(_context: Context) -> df.Continuation:
    print("Hello")
    return ContinuationList(
        Button("Click", my_other_passage), Button("Clack", my_passage)
    )


def my_other_passage(_context: Context) -> df.Continuation:
    print("Hi")
    return Button("Clack", my_passage)


run(my_passage, Context())


print(f"Advanced demo, running pyscript {be.pyscript_version()}")
be.insert_end(ElementId("body"), "<h1>Hello</h1>\n")
be.insert_end(ElementId("body"), f"world!! {be.local_storage.has_key('hello')}")
if be.local_storage.has_key("hello"):
    hello = be.local_storage(int)["hello"]
    be.insert_end(ElementId("body"), f"<div>Hello: <b>{hello}</b></div>")
    be.local_storage["hello"] = hello + 1
