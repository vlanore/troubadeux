import click
from jinja2 import Environment, PackageLoader


@click.command()
@click.option("-f", "--flag", is_flag=True)
def main(flag: bool):
    environment = Environment(loader=PackageLoader("troubadour"))
    main_template = environment.get_template("main.html.j2")

    f = open("index.html", "w")
    f.write(main_template.render(message="Hello world!!!"))
    f.close()
