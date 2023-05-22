import troubadour.backend as be

print(f"Advanced demo, running pyscript {be.pyscript_version()}")
be.insert_end("body", "<h1>Hello</h1>\n")
be.insert_end("body", f"world!! {be.local_storage.has_key('hello')}")
if be.local_storage.has_key("hello"):
    hello = be.local_storage(int)["hello"]
    be.insert_end("body", f"<div>Hello: <b>{hello}</b></div>")
    be.local_storage["hello"] = hello + 1


def f(_) -> None:
    be.insert_end("body", "<div>hello</div>")


be.insert_end("body", "<button type='button' id='but'>Click!</button>")
be.onclick("but", f)
