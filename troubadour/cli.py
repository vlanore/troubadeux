from pathlib import Path
import shutil
import subprocess

import click
from jinja2 import Environment, PackageLoader


@click.group()
def main():
    pass


@main.command()
@click.option("-p", "--port", type=int, default=8765)
def server(port: int):
    subprocess.run("python -m http.server 8765", shell=True)


@main.command()
@click.option("-p", "--path", default="./_site", help="Path to store project files.")
@click.option(
    "-e",
    "--entry-point",
    default="index.py",
    help="Location of the main file of the project, relative to the source directory.",
)
@click.argument("src")
def build(path: str, entry_point: str, src: str) -> None:
    """Generates the files for your troubadour project."""

    # Paths
    src_dir = Path(src)
    sources = list(src_dir.rglob("*.py"))
    assert src_dir / entry_point in sources, "Entry point not in source files!"
    output_path = Path(path)
    main_html_path = output_path / "index.html"
    toml_path = output_path / "config.toml"

    # Generate file contents from Jinja templates
    environment = Environment(loader=PackageLoader("troubadour"))
    main_template = environment.get_template("main.html.j2")
    main_source = main_template.render(entrypoint=entry_point)
    toml_file_list = ", ".join(f'"{p.relative_to(src_dir)}"' for p in sources)
    toml_source = f"[[fetch]]\nfiles = [{toml_file_list}]"

    # Make dest folder
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy source files
    for f in sources:
        shutil.copyfile(f, output_path / (f.relative_to(src_dir)))

    # Write to files
    main_html_path.write_text(main_source)
    toml_path.write_text(toml_source)
