"""Built-in example tools: one read-only (R) and one reversible write (W1)."""

from __future__ import annotations

from datetime import datetime

from jarvis import paths
from jarvis.security.actions import Prepared
from jarvis.tools.base import Level, ToolSpec


def clock_now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def notes_add(text: str) -> Prepared:
    file = paths.data_dir() / "notes.md"

    def run() -> str:
        paths.ensure_dirs()
        with file.open("a", encoding="utf-8") as handle:
            handle.write(f"- {text}\n")
        return f"Noted: {text}"

    def undo() -> str:
        lines = file.read_text(encoding="utf-8").splitlines()
        if lines and lines[-1] == f"- {text}":
            file.write_text("\n".join(lines[:-1]) + ("\n" if lines[:-1] else ""), encoding="utf-8")
        return "Note removed."

    return Prepared(f"add note: {text}", run, undo)


def register(registry) -> None:
    registry.register(ToolSpec("clock_now", "Current local date and time.", Level.R, clock_now))
    registry.register(
        ToolSpec("notes_add", "Append a note to data/notes.md.", Level.W1, notes_add, {"text": "note text"})
    )
