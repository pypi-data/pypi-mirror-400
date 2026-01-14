import os
from pathlib import Path
from typing import cast

import yaml


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        msg = f"Expected environment variable: {name}"
        raise ValueError(msg)
    return value


def _load_yaml_from_path(env_var_name: str) -> dict[str, dict[str, dict[str, str]]]:
    source_path = _get_env(env_var_name)
    text = Path(source_path).read_text(encoding="utf-8")
    return cast("dict[str, dict[str, dict[str, str]]]", yaml.safe_load(text))


DEFINES_VULNERABILITIES = _load_yaml_from_path("CRITERIA_VULNERABILITIES")
DEFINES_REQUIREMENTS = _load_yaml_from_path("CRITERIA_REQUIREMENTS")
