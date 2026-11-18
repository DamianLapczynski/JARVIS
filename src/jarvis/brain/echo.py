"""EchoBrain: a keyword router that exercises the whole tool pipeline without any LLM.

Try:  "what time is it", "note buy milk", "roll 20", "open notepad", "hello Ada",
      "remind 15:30 call mom" (W2: asks for confirmation).
Replace it with a real LLM brain (see agent_sdk.py) and expose registry.all() as its tools.
"""

from __future__ import annotations

import re

from jarvis.brain.base import Brain
from jarvis.security.actions import ActionDesk
from jarvis.tools.registry import ToolRegistry


class EchoBrain(Brain):
    def __init__(self, registry: ToolRegistry, desk: ActionDesk, name: str = "Jarvis"):
        self.registry = registry
        self.desk = desk
        self.name = name

    async def ask(self, text: str) -> str:
        t = text.strip()
        low = t.lower()
        if "time" in low:
            return self._call("clock_now", {})
        if m := re.match(r"note\s+(.+)", t, re.I):
            return self._call("notes_add", {"text": m.group(1)})
        if m := re.match(r"roll\s*(\d+)?", low):
            return self._call("dice_roll", {"sides": m.group(1) or 6})
        if m := re.match(r"open\s+(\w+)", low):
            return self._call("pc_open_app", {"name": m.group(1)})
        if m := re.match(r"remind\s+(\S+)\s+(.+)", t, re.I):
            return self._call("reminder_set", {"when": m.group(1), "text": m.group(2)})
        if low.startswith("hello"):
            return self._call("hello", {"who": t[5:].strip() or "world"})
        if low == "undo":
            return self.desk.undo().message
        return f"{self.name} (echo brain): {t}"

    def _call(self, tool: str, args: dict) -> str:
        if self.registry.get(tool) is None:
            return f"Tool {tool!r} is not available."
        try:
            return self.registry.call(tool, args, self.desk)
        except (ValueError, TypeError) as exc:
            return f"Could not run {tool}: {exc}"
