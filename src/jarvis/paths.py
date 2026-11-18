"""Project paths. Everything is relative to JARVIS_HOME (default: current directory)."""

from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    return Path(os.environ.get("JARVIS_HOME", Path.cwd())).resolve()


def config_path() -> Path:
    return home() / "config.toml"


def data_dir() -> Path:
    return home() / "data"


def ensure_dirs() -> None:
    data_dir().mkdir(parents=True, exist_ok=True)
