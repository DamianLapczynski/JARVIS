"""Google integration stub (Calendar / Gmail). Returns sample data until you implement OAuth.

To implement: `uv sync --extra google`, create an OAuth client in Google Cloud Console,
store the client JSON with `jarvis secrets set google_client`, run the consent flow, keep the
refresh token in the keyring. Request the narrowest scopes (readonly first).
"""

from __future__ import annotations

from jarvis.security import secrets
from jarvis.tools.base import Level, ToolSpec


def configured() -> bool:
    return secrets.get("google_client") is not None


def calendar_today() -> str:
    if not configured():
        return "(sample data) 10:00 Team stand-up; 14:00 Dentist. Google is not configured."
    raise NotImplementedError("calendar_today: call the Calendar API with your stored credentials")


def register(registry, config: dict) -> None:
    if config.get("google", {}).get("enabled"):
        registry.register(ToolSpec("calendar_today", "Today's calendar events.", Level.R, calendar_today))
