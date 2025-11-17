# qgen/utils.py
import json
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from typing import Any, Dict

def build_env(templates_dir: str) -> Environment:
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        undefined=StrictUndefined,  # force explicit variables
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env

def render_template(env: Environment, name: str, **vars: Any) -> str:
    tpl = env.get_template(name)
    # expose a 'tojson' filter if needed (Jinja has built-in |tojson in modern versions)
    return tpl.render(**vars)

def json_loads_strict(s: str) -> Dict[str, Any]:
    return json.loads(s)
