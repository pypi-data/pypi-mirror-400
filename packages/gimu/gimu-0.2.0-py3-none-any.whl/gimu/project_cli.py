import importlib.metadata
from pathlib import Path
from pprint import pprint
import sys

try:
    import tomllib  # Python ≥3.11
except ImportError:
    import tomli as tomllib  # Python <3.11

def get_distribution():
    top_pkg = __package__.split('.')[0] if __package__ else None
    if top_pkg:
        try:
            return importlib.metadata.distribution(top_pkg)
        except importlib.metadata.PackageNotFoundError:
            pass
    return None

def get_project_meta():
    """ return pyproject.toml [project] """
    current_file = Path(__file__).resolve()
    for parent in [current_file.parent] + list(current_file.parents):
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject, "rb") as f:
                data = tomllib.load(f)
            return data.get("project", {})
    return None

def show_help():
    dist = get_distribution()
    name = dist.metadata['Name']
    version = dist.metadata['Version']
    description = dist.metadata['Summary']
    commands = [ep.name for ep in dist.entry_points]

    # meta = get_project_meta()
    # name = meta['name']
    # description = meta['description']

    msg = '\n'.join([
        f"",
        f"    {name} - {description}",
        f"",
        f"    Version: {version}",
        f"",
        f"    Available commands:",
    ] + ["        " + cmd for cmd in sorted(commands)] + [
        f"",
        f"    e.g.:",
        f"        save2incon model_1.save model_2.incon",
        f"",
    ])
    print(msg)

