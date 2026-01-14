"""Template rendering for airops init scaffolding."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_templates_dir = Path(__file__).parent
_env = Environment(loader=FileSystemLoader(_templates_dir), keep_trailing_newline=True)


def render(template_name: str, **kwargs: str) -> str:
    """Render a template file with the given variables.

    Args:
        template_name: Name of the template file (e.g., "tool.py.jinja").
        **kwargs: Variables to substitute in the template.

    Returns:
        Rendered template content.
    """
    return _env.get_template(template_name).render(**kwargs)
