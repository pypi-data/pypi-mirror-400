"""Implementation of the 'airops init' command."""

from __future__ import annotations

import re
from pathlib import Path

from airops import __version__
from airops.cli.templates import render


def sanitize_name(name: str) -> str:
    """Convert a string to a valid Python identifier.

    Args:
        name: Raw name string.

    Returns:
        Sanitized name suitable for Python identifiers.
    """
    name = re.sub(r"[-\s]+", "_", name)
    name = re.sub(r"[^\w]", "", name)
    if name and name[0].isdigit():
        name = f"tool_{name}"
    return name.lower() or "my_tool"


def run_init(path: str, name: str | None, force: bool) -> int:
    """Initialize a new AirOps tool project.

    Args:
        path: Directory to initialize.
        name: Tool name (or None to derive from directory).
        force: Whether to overwrite existing files.

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    target = Path(path).resolve()

    if not target.exists():
        target.mkdir(parents=True)
        print(f"Created directory: {target}")
    elif not target.is_dir():
        print(f"Error: {target} exists and is not a directory")
        return 1

    name = sanitize_name(target.name if name is None else name)

    files = {
        "tool.py": render("tool.py.jinja", name=name),
        "Dockerfile": render("dockerfile.jinja"),
        ".dockerignore": render("dockerignore.jinja"),
        ".env.example": render("env_example.jinja"),
        "pyproject.toml": render("pyproject.toml.jinja", name=name, airops_version=__version__),
        "README.md": render("readme.md.jinja", name=name),
        "AGENTS.md": render("agents.md.jinja", name=name),
        "CLAUDE.md": render("claude.md.jinja", name=name),
        "tests/__init__.py": "",
        "tests/test_tool.py": render("test_tool.py.jinja", name=name),
    }

    existing = []
    for filename in files:
        filepath = target / filename
        if filepath.exists():
            existing.append(filename)

    if existing and not force:
        print("Error: The following files already exist:")
        for f in existing:
            print(f"  - {f}")
        print("\nUse --force to overwrite existing files.")
        return 1

    created = []
    for filename, content in files.items():
        filepath = target / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        created.append(filename)

    print(f"\nInitialized AirOps tool '{name}' in {target}\n")
    print("Created files:")
    for f in sorted(created):
        print(f"  {f}")

    print("\nNext steps:")
    step = 1
    if path != ".":
        print(f"  {step}. cd {path}")
        step += 1
    print(f"  {step}. cp .env.example .env  # add your AIROPS_API_TOKEN")
    print(f"  {step + 1}. airops run")
    print("\nThe development server will start at http://localhost:8080")

    return 0
