"""Stub for an LLM-backed brain (e.g. the Claude Agent SDK). Implement `ask` yourself.

Sketch:
  1. start(): open one long-lived session; give it a persona prompt (config [jarvis] name/language).
  2. Expose `registry.all()` to the model as tools (name, description, params).
  3. When the model calls a tool -> `registry.call(name, args, desk)`; write tools go through the desk.
  4. Block every tool that is not in the registry (a pre-tool hook / allowlist).
"""

from __future__ import annotations

from jarvis.brain.base import Brain


class AgentSdkBrain(Brain):
    def __init__(self, registry, desk, model: str = ""):
        self.registry, self.desk, self.model = registry, desk, model

    async def start(self) -> None:
        try:
            import claude_agent_sdk  # noqa: F401  (uv sync --extra brain)
        except ImportError as exc:
            raise RuntimeError("install the SDK: uv sync --extra brain") from exc

    async def ask(self, text: str) -> str:
        raise NotImplementedError("Implement AgentSdkBrain.ask - see the module docstring.")
