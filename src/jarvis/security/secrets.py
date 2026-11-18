"""Secrets live in the OS keyring (service "jarvis"), never in config.toml, the repo or logs.

Fallback for CI/containers: environment variable JARVIS_SECRET_<NAME>.
"""

from __future__ import annotations

import os

SERVICE = "jarvis"
KNOWN = ("telegram", "azure_speech", "google_client", "groq")  # names shown by `secrets status`


def _keyring():
    try:
        import keyring  # optional extra: uv sync --extra secrets
        return keyring
    except ImportError:
        return None


def get(name: str) -> str | None:
    env = os.environ.get(f"JARVIS_SECRET_{name.upper()}")
    if env:
        return env
    kr = _keyring()
    return kr.get_password(SERVICE, name) if kr else None


def set_(name: str, value: str) -> None:
    kr = _keyring()
    if kr is None:
        raise RuntimeError("keyring is not installed: run `uv sync --extra secrets`")
    kr.set_password(SERVICE, name, value)


def status() -> dict[str, bool]:
    """Which secrets are set. Never returns values."""
    return {name: get(name) is not None for name in KNOWN}
