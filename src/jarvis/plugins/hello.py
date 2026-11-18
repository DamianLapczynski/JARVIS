"""Example plugin 1: the smallest possible read-only tool."""

from jarvis.tools.base import Level, ToolSpec


def hello(who: str = "world") -> str:
    return f"Hello, {who}! This answer came from a plugin."


def register(registry) -> None:
    registry.register(ToolSpec("hello", "Greets someone.", Level.R, hello, {"who": "name to greet"}))
