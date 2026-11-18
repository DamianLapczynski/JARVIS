"""Action desk: the ONLY place where write tools actually execute.

W1 runs immediately (and may offer undo). W2 needs an explicit "yes" from the user.
With dry_run=True nothing runs; the desk just reports what it would have done.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from jarvis.security.redact import redact


@dataclass
class Prepared:
    """What a write tool returns: a human description plus the function that does the work."""

    description: str                       # e.g. "Add note: buy milk"
    run: Callable[[], str]
    undo: Callable[[], str] | None = None


@dataclass
class Outcome:
    executed: bool
    message: str


class ActionDesk:
    def __init__(self, dry_run: bool = True, confirm: Callable[[str], bool] | None = None):
        self.dry_run = dry_run
        self._confirm = confirm or (lambda _question: False)  # deny by default
        self.log: list[str] = []
        self._last_undo: Callable[[], str] | None = None

    def execute(self, prepared: Prepared, level: str) -> Outcome:
        if self.dry_run:
            self.log.append(redact(f"[dry-run] {prepared.description}"))
            return Outcome(False, f"(dry run) would do: {prepared.description}")
        if level == "W2" and not self._confirm(f"Shall I {prepared.description}?"):
            return Outcome(False, "Cancelled: no confirmation.")
        message = prepared.run()
        self._last_undo = prepared.undo
        self.log.append(redact(f"[done] {prepared.description}"))
        return Outcome(True, message)

    def undo(self) -> Outcome:
        if self._last_undo is None:
            return Outcome(False, "Nothing to undo.")
        message, self._last_undo = self._last_undo(), None
        return Outcome(True, message)
