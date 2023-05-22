import troubadour.backend as be

print(f"Advanced demo, running pyscript {be.pyscript_version()}")
be.insert_end("body", "<h1>Hello</h1>\n")
be.insert_end("body", "world!!a")
