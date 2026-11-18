"""Refuse to start when a forbidden environment variable is present."""

from __future__ import annotations

import os


class ForbiddenEnv(RuntimeError):
    pass


def offending(forbidden: list[str]) -> list[str]:
    return [name for name in forbidden if os.environ.get(name)]


def check(forbidden: list[str]) -> None:
    bad = offending(forbidden)
    if bad:
        raise ForbiddenEnv(
            f"Environment variable(s) set: {', '.join(bad)}. Unset them or edit [security] forbidden_env."
        )
