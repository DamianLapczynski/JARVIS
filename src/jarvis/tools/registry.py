"""Tool registry + plugin discovery."""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import pkgutil
from pathlib import Path
from typing import Any

from jarvis.security.actions import ActionDesk, Prepared
from jarvis.tools.base import FORBIDDEN_WORDS, Level, ToolSpec


class RegistryError(ValueError):
    pass


class ToolRegistry:
    def __init__(self, disabled: list[str] | None = None):
        self._tools: dict[str, ToolSpec] = {}
        self._disabled = set(disabled or [])

    def register(self, spec: ToolSpec) -> None:
        lowered = spec.name.lower()
        if any(word in lowered for word in FORBIDDEN_WORDS):
            raise RegistryError(f"tool name {spec.name!r} contains a forbidden word")
        if spec.name in self._tools:
            raise RegistryError(f"duplicate tool {spec.name!r}")
        if spec.name in self._disabled:
            return
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def all(self) -> list[ToolSpec]:
        return sorted(self._tools.values(), key=lambda t: t.name)

    def call(self, name: str, args: dict[str, Any], desk: ActionDesk) -> str:
        spec = self._tools.get(name)
        if spec is None:
            return f"Unknown tool: {name}"
        result = spec.handler(**args)
        if spec.level is Level.R:
            return str(result)
        if not isinstance(result, Prepared):
            raise RegistryError(f"write tool {name!r} must return Prepared")
        return desk.execute(result, spec.level.value).message

    # -- discovery -----------------------------------------------------------------

    def load_builtin(self, config: dict[str, Any]) -> None:
        from jarvis.gapi import google
        from jarvis.tools import builtin, pc_control

        builtin.register(self)
        pc_control.register(self, config)
        google.register(self, config)

    def load_plugins(self, config: dict[str, Any]) -> list[str]:
        """Loads jarvis.plugins.*, the optional plugin_dir and `jarvis.tools` entry points.
        Returns human-readable load errors (a broken plugin never stops the assistant)."""
        errors: list[str] = []

        def attach(module: Any, label: str) -> None:
            hook = getattr(module, "register", None)
            if not callable(hook):
                return
            try:
                hook(self)
            except Exception as exc:  # noqa: BLE001 - plugin boundary
                errors.append(f"{label}: {exc}")

        import jarvis.plugins as pkg

        for info in pkgutil.iter_modules(pkg.__path__):
            if not info.name.startswith("_"):
                attach(importlib.import_module(f"jarvis.plugins.{info.name}"), info.name)

        plugin_dir = config.get("tools", {}).get("plugin_dir") or ""
        if plugin_dir:
            for file in sorted(Path(plugin_dir).glob("*.py")):
                spec = importlib.util.spec_from_file_location(f"jarvis_ext_{file.stem}", file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{file.name}: {exc}")
                        continue
                    attach(module, file.name)

        for entry in importlib.metadata.entry_points(group="jarvis.tools"):
            try:
                attach(entry.load(), entry.name)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{entry.name}: {exc}")
        return errors


def build(config: dict[str, Any]) -> tuple[ToolRegistry, list[str]]:
    registry = ToolRegistry(config.get("tools", {}).get("disabled", []))
    registry.load_builtin(config)
    return registry, registry.load_plugins(config)
