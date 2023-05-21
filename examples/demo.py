import troubadour.backend as be

print(f"Advanced demo, running pyscript {be.pyscript_version()}")
be.add_to_body("Hello")
be.add_to_body("world")
