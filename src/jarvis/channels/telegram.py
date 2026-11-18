"""Telegram bot over the plain Bot API (stdlib only, long polling).

Security: a strict allowlist - only [telegram] user_id in a private chat gets answers.
"""

from __future__ import annotations

import asyncio
import json
import urllib.parse
import urllib.request

from jarvis.brain.base import Brain
from jarvis.security import secrets


def _api(token: str, method: str, **params) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=70) as resp:  # noqa: S310
        return json.load(resp)


def is_allowed(update: dict, allowed_user: int) -> bool:
    msg = update.get("message") or {}
    return (
        bool(allowed_user)
        and msg.get("from", {}).get("id") == allowed_user
        and msg.get("chat", {}).get("type") == "private"
        and "text" in msg
    )


def run(brain: Brain, allowed_user: int) -> None:
    token = secrets.get("telegram")
    if not token:
        raise RuntimeError("missing secret: jarvis secrets set telegram")
    offset = 0
    while True:
        for update in _api(token, "getUpdates", offset=offset, timeout=60).get("result", []):
            offset = update["update_id"] + 1  # TODO: persist offset so a crash never repeats an action
            if is_allowed(update, allowed_user):
                reply = asyncio.run(brain.ask(update["message"]["text"]))
                _api(token, "sendMessage", chat_id=update["message"]["chat"]["id"], text=reply)
