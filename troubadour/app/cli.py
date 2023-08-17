import shutil
import subprocess
from importlib.util import find_spec
from pathlib import Path

import click
from jinja2 import Environment, PackageLoader


@click.group()
def main():
    pass


# -~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~
@main.command(short_help="Runs a development server for a locally built project.")
@click.option("-p", "--port", type=int, default=8765)
def server(port: int):
    """Runs a development server for a locally built project
    (expects _site folder to be present)."""
    subprocess.run(f"cd _site && python -m http.server {port}", shell=True)


# -~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~=~-~
@main.command(short_help="Generates the files for your troubadour project.")
@click.option("-p", "--path", default="./_site", help="Path to store project files.")
@click.option(
    "-e",
    "--entry-point",
    default="index.py",
    help="Location of the main file of the project, relative to the source directory.",
)
@click.argument("src")
def build(path: str, entry_point: str, src: str) -> None:
    """Generates the files for your troubadour project. Needs SRC, the path to the
    directory containing the project source files."""

    # Paths
    src_dir = Path(src)
    print("Building project from folder", src_dir)
    sources = list(src_dir.rglob("*.py"))
    print(f"Found {len(sources)} source files")
    assert src_dir / entry_point in sources, "Entry point not in source files!"
    print(f"Entry point {entry_point} found in sources")
    output_path = Path(path)
    user_module = output_path / src_dir.absolute().name
    print(f"Output folder is {output_path}")
    main_html_path = output_path / "index.html"
    toml_path = output_path / "config.toml"
    css_path = output_path / "troubadour.css"

    # Copy troubadour lib to dest folder
    troubadour_dest_dir = output_path / "troubadour"
    troubadour_spec = find_spec("troubadour")
    assert troubadour_spec is not None and troubadour_spec.origin is not None
    troubadour_module_dir = Path(troubadour_spec.origin).parent
    print(
        f"Copying troubadour library from {troubadour_module_dir}"
        f" to {troubadour_dest_dir}"
    )

    troubadour_files = troubadour_module_dir.rglob("*.py")
    troubadour_filtered_files = [
        f
        for f in troubadour_files
        if str(f)[:5] != "__pyc" and "app/" not in str(f) and "templates/" not in str(f)
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
    print("Done")

    # Generate file contents from Jinja templates
    print("Generating project files from jinja template")
    environment = Environment(loader=PackageLoader("troubadour"))
    main_template = environment.get_template("main.html.j2")
    main_source = main_template.render(entrypoint=f"{user_module.name}/{entry_point}")

    css_template = environment.get_template("troubadour.css.j2")
    css_source = css_template.render()

    toml_template = environment.get_template("config.toml.j2")
    package_list = ["jsonpickle"]
    toml_package_list = ",\n    ".join(f'"{package}"' for package in package_list)
    toml_file_list = ",\n    ".join(
        [f'"{p.relative_to(src_dir.parent)}"' for p in sources]
        + [f'"{p.relative_to(output_path)}"' for p in troubadour_files_to_fetch]
    )
    toml_source = toml_template.render(packages=toml_package_list, fetch=toml_file_list)
    print("Done")

    # Make dest folder and module folder
    output_path.mkdir(parents=True, exist_ok=True)
    user_module.mkdir(exist_ok=True)

    # Copy source files
    print("Copying source files")
    for f in sources:
        shutil.copyfile(f, user_module / f.relative_to(src_dir))

    # Write to files
    print("Writing generated files")
    main_html_path.write_text(main_source)
    toml_path.write_text(toml_source)
    css_path.write_text(css_source)
