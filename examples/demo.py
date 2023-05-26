from dataclasses import dataclass
import troubadour.backend as be
import troubadour.definitions as df
from troubadour.definitions import Context, ElementId
from troubadour.run import run
from troubadour.unique_id import get_unique_element_id


@dataclass
class Button(df.Continuation):
    txt: str
    passage: df.Passage

    def setup(self, target: ElementId, state: df.State = df.empty_state) -> None:
        id = get_unique_element_id("button")
        be.insert_end(target, f"<button type='button' id='{id}'>{self.txt}</button>")
        be.onclick(id, lambda _: run(self.passage, Context()))


def my_passage(context: Context) -> df.Continuation:
    print("Hello")
    return Button("Click", my_other_passage)


def my_other_passage(context: Context) -> df.Continuation:
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
