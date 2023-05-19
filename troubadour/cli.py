from pathlib import Path

import click
from jinja2 import Environment, PackageLoader


@click.command()
@click.option("-p", "--path", default="./_site")
def main(path: str) -> None:
    environment = Environment(loader=PackageLoader("troubadour"))
    main_template = environment.get_template("main.html.j2")

    Path(path).mkdir(parents=True, exist_ok=True)
    main_path = Path(path) / "index.html"
    main_source = main_template.render(message="Hello world!!!")
    main_path.write_text(main_source)
