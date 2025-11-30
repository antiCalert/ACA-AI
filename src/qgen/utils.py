"""Utility helpers used across the qgen package.

This module provides small convenience functions for Jinja template rendering
and strict JSON decoding used by the generator and client layers.
"""

import json
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def build_env(templates_dir: str) -> Environment:
    """Create and return a pre-configured Jinja2 Environment.

    Args:
        templates_dir: Path to the directory containing Jinja templates.

    Returns:
        A configured ``jinja2.Environment`` with strict undefined handling.
    """
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        undefined=StrictUndefined,  # force explicit variables
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def render_template(env: Environment, name: str, **context: Any) -> str:
    """Render a template by name using the provided environment.

    Args:
        env: Jinja2 environment returned from :func:`build_env`.
        name: Template filename.
        **context: Context variables passed to the template.

    Returns:
        Rendered template as a string.
    """
    tpl = env.get_template(name)
    # expose a 'tojson' filter if needed (Jinja has built-in |tojson in modern versions)
    return tpl.render(**context)


def json_loads_strict(s: str) -> Dict[str, Any]:
    """Parse a JSON string and return the resulting mapping.

    This is a small wrapper around ``json.loads`` kept for clarity and
    to provide a single place to add stricter parsing rules later.
    """
    return json.loads(s)
