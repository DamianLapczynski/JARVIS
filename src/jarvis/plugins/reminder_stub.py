"""Example plugin 3: a W2 tool (needs a confirmation). It stores nothing; replace `run`."""

from jarvis.security.actions import Prepared
from jarvis.tools.base import Level, ToolSpec


def reminder_set(when: str, text: str) -> Prepared:
    return Prepared(f"set a reminder for {when}: {text}", lambda: f"Reminder set for {when}.")


def register(registry) -> None:
    registry.register(
        ToolSpec(
            "reminder_set",
            "Set a reminder (asks for confirmation).",
            Level.W2,
            reminder_set,
            {"when": "time, e.g. 15:30", "text": "what to remind about"},
        )
    )
