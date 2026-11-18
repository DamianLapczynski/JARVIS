"""`jarvis doctor`: environment health check. Exit code 1 when a required check fails."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass

from jarvis import config as cfg
from jarvis import paths
from jarvis.security import env_guard, secrets
from jarvis.tools import registry


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = True


def run() -> list[Check]:
    config = cfg.load()
    checks: list[Check] = []

    ok = sys.version_info >= (3, 11)
    checks.append(Check("python >= 3.11", ok, sys.version.split()[0]))

    exists = paths.config_path().exists()
    checks.append(Check("config.toml", exists, "found" if exists else "missing: run `jarvis init`", False))

    bad = env_guard.offending(config["security"]["forbidden_env"])
    checks.append(Check("environment guard", not bad, ", ".join(bad) if bad else "clean"))

    try:
        paths.ensure_dirs()
        probe = paths.data_dir() / ".probe"
        probe.write_text("ok")
        probe.unlink()
        checks.append(Check("data directory writable", True, str(paths.data_dir())))
    except OSError as exc:
        checks.append(Check("data directory writable", False, str(exc)))

    reg, errors = registry.build(config)
    checks.append(Check("tools", not errors, f"{len(reg.all())} registered" + (f"; errors: {errors}" if errors else "")))
    checks.append(Check("dry-run", True, "ON (write tools only log)" if config["jarvis"]["dry_run"] else "OFF", False))

    for name, is_set in secrets.status().items():
        checks.append(Check(f"secret: {name}", is_set, "set" if is_set else "not set", False))

    for module, extra in (("keyring", "secrets"), ("claude_agent_sdk", "brain"), ("sounddevice", "voice")):
        found = importlib.util.find_spec(module) is not None
        checks.append(Check(f"optional: {module}", found, "installed" if found else f"uv sync --extra {extra}", False))
    return checks


def main() -> int:
    checks = run()
    for c in checks:
        mark = "OK  " if c.ok else ("FAIL" if c.required else "warn")
        print(f"[{mark}] {c.name}: {c.detail}")
    return 0 if all(c.ok or not c.required for c in checks) else 1
