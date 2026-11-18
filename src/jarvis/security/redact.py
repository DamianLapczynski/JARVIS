"""Mask likely secrets before anything is logged."""

from __future__ import annotations

import re

_PATTERNS = [
    re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{30,}\b"),            # Telegram-style bot token
    re.compile(r"\b(?:sk|pk|key|tok)[-_][A-Za-z0-9_-]{16,}\b"),  # generic API-key-looking strings
    re.compile(r"(?i)(authorization:\s*bearer\s+)\S+"),
]


def redact(text: str) -> str:
    for pattern in _PATTERNS:
        text = pattern.sub(lambda m: (m.group(1) if m.groups() else "") + "[REDACTED]", text)
    return text
