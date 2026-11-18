"""PC control stub: open an application from an ALLOWLIST (W1).

Design rules worth keeping when you extend this:
  * the model supplies only a NAME; the URI comes from config ([pc.apps]);
  * only URIs with a scheme from SAFE_SCHEMES are accepted;
  * never go through a shell (no subprocess with shell=True, no `cmd /c`).
"""

from __future__ import annotations

import os
import sys
from typing import Any
from urllib.parse import urlparse

from jarvis.security.actions import Prepared
from jarvis.tools.base import Level, ToolSpec

SAFE_SCHEMES = frozenset({"ms-notepad", "calculator", "ms-settings-bluetooth", "spotify", "https"})


def is_safe_uri(uri: str) -> bool:
    return urlparse(uri).scheme.lower() in SAFE_SCHEMES


def make_open_app(apps: dict[str, str]):
    def pc_open_app(name: str) -> Prepared:
        uri = apps.get(name.lower())
        if uri is None:
            raise ValueError(f"unknown app {name!r}; allowed: {', '.join(sorted(apps)) or '(none)'}")
        if not is_safe_uri(uri):
            raise ValueError(f"URI scheme not allowed for {name!r}")

        def run() -> str:
            if sys.platform != "win32":
                return f"(stub) would open {uri} - implement for your OS"
            os.startfile(uri)  # noqa: S606 - allowlisted URI, never a shell
            return f"Opened {name}."

        return Prepared(f"open application {name}", run)

    return pc_open_app


def register(registry, config: dict[str, Any]) -> None:
    apps = {k.lower(): v for k, v in config.get("pc", {}).get("apps", {}).items()}
    registry.register(
        ToolSpec(
            "pc_open_app",
            "Open an allowlisted application by name.",
            Level.W1,
            make_open_app(apps),
            {"name": "application name from [pc.apps]"},
        )
    )
