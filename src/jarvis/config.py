"""Config loading: config.toml merged over built-in defaults."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from jarvis import paths

DEFAULTS: dict[str, Any] = {
    "jarvis": {"name": "Jarvis", "language": "en", "dry_run": True},
    "brain": {"backend": "echo", "model": ""},
    "security": {"forbidden_env": ["ANTHROPIC_API_KEY"]},
    "tools": {"plugin_dir": "", "disabled": []},
    "pc": {"apps": {}},
    "speech": {"tts": "console", "stt": "stdin"},
    "telegram": {"enabled": False, "user_id": 0},
    "dashboard": {"enabled": True, "host": "127.0.0.1", "port": 4330},
    "google": {"enabled": False, "scopes": []},
}


def _merge(base: dict[str, Any], over: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load(path: Path | None = None) -> dict[str, Any]:
    """Returns defaults when the file is missing (so `doctor` can still run)."""
    path = path or paths.config_path()
    if not path.exists():
        return _merge({}, DEFAULTS)
    with path.open("rb") as handle:
        return _merge(DEFAULTS, tomllib.load(handle))
