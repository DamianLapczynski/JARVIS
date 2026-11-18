"""Tool definitions. Safety levels live in CODE, not in the prompt.

R  = read only, runs freely.
W1 = reversible write: runs at once through the ActionDesk (undo offered).
W2 = write needing explicit user confirmation.
X  = dangerous (shell, delete-all, send money ...): NOT REPRESENTABLE. There is no X level,
     and the registry rejects tool names matching FORBIDDEN_WORDS.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Level(str, Enum):
    R = "R"
    W1 = "W1"
    W2 = "W2"


# Tool names containing these words are refused at registration time.
FORBIDDEN_WORDS = ("shell", "exec", "eval", "sudo", "rm_rf", "send_money", "delete_all")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    level: Level
    handler: Callable[..., Any]         # R: returns str. W1/W2: returns security.actions.Prepared
    params: dict[str, str] = field(default_factory=dict)   # {"arg": "what it means"}
