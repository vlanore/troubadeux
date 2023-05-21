from importlib.util import find_spec
import shutil
import subprocess
from pathlib import Path

import click
from jinja2 import Environment, PackageLoader


@click.group()
def main():
    pass


# -~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~
@main.command()
@click.option("-p", "--port", type=int, default=8765)
def server(port: int):
    "Runs a development server for a locally built project."
    subprocess.run("cd _site && python -m http.server 8765", shell=True)


# -~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~
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

    # Copy troubadour lib to dest folder
    troubadour_dest_dir = output_path / "troubadour"
    troubadour_spec = find_spec("troubadour")
    assert troubadour_spec is not None and troubadour_spec.origin is not None
    troubadour_module_dir = Path(troubadour_spec.origin).parent

    troubadour_files = troubadour_module_dir.rglob("*.py")
    troubadour_filtered_files = [
        f for f in troubadour_files if str(f)[:5] != "__pyc" and "cli.py" not in str(f)
    ]
    if troubadour_dest_dir.exists():
        shutil.rmtree(troubadour_dest_dir)
    troubadour_dest_dir.mkdir(parents=True)

    for f in troubadour_filtered_files:
        shutil.copyfile(f, troubadour_dest_dir / f.relative_to(troubadour_module_dir))
    troubadour_files_to_fetch = [
        troubadour_dest_dir / f.relative_to(troubadour_module_dir)
        for f in troubadour_filtered_files
    ]

    # Generate file contents from Jinja templates
    environment = Environment(loader=PackageLoader("troubadour"))
    main_template = environment.get_template("main.html.j2")
    main_source = main_template.render(entrypoint=entry_point)
    toml_file_list = ",\n    ".join(
        [f'"{p.relative_to(src_dir)}"' for p in sources]
        + [f'"{p.relative_to(output_path)}"' for p in troubadour_files_to_fetch]
    )
    toml_source = f"[[fetch]]\nfiles = [\n    {toml_file_list}\n]"

    # Make dest folder
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy source files
    for f in sources:
        shutil.copyfile(f, output_path / f.relative_to(src_dir))

    # Write to files
    main_html_path.write_text(main_source)
    toml_path.write_text(toml_source)
