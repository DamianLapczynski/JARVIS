"""`jarvis` command line."""

from __future__ import annotations

import argparse
import getpass
import json
import shutil
import sys

from jarvis import config as cfg
from jarvis import paths
from jarvis.brain.base import Brain
from jarvis.security import env_guard, secrets
from jarvis.security.actions import ActionDesk
from jarvis.tools import registry as tool_registry


def _brain(config: dict, confirm=None) -> tuple[Brain, tool_registry.ToolRegistry]:
    env_guard.check(config["security"]["forbidden_env"])
    reg, errors = tool_registry.build(config)
    for err in errors:
        print(f"plugin error: {err}", file=sys.stderr)
    desk = ActionDesk(dry_run=config["jarvis"]["dry_run"], confirm=confirm)
    backend = config["brain"]["backend"]
    if backend == "agent_sdk":
        from jarvis.brain.agent_sdk import AgentSdkBrain

        return AgentSdkBrain(reg, desk, config["brain"]["model"]), reg
    from jarvis.brain.echo import EchoBrain

    return EchoBrain(reg, desk, config["jarvis"]["name"]), reg


def cmd_init(_args) -> int:
    target = paths.config_path()
    if target.exists():
        print(f"{target} already exists; not overwriting.")
        return 1
    shutil.copy(paths.home() / "config.example.toml", target)
    print(f"Created {target}. Edit it, then run `jarvis doctor`.")
    return 0


def cmd_doctor(_args) -> int:
    from jarvis import doctor

    return doctor.main()


def cmd_chat(_args) -> int:
    from jarvis.channels import terminal

    config = cfg.load()
    brain, _ = _brain(config, terminal.ask_yes_no)
    terminal.run(brain)
    return 0


def cmd_voice(_args) -> int:
    from jarvis.channels import terminal, voice
    from jarvis.speech import stt, tts

    config = cfg.load()
    brain, _ = _brain(config, terminal.ask_yes_no)
    voice.run(brain, stt.build(config), tts.build(config))
    return 0


def cmd_telegram(_args) -> int:
    from jarvis.channels import telegram

    config = cfg.load()
    brain, _ = _brain(config)  # W2 tools are denied here until you add a chat-based confirmation
    telegram.run(brain, config["telegram"]["user_id"])
    return 0


def cmd_dashboard(_args) -> int:
    from jarvis.channels import dashboard

    config = cfg.load()
    _, reg = _brain(config)
    d = config["dashboard"]
    dashboard.serve(reg, d["host"], d["port"], config["jarvis"]["dry_run"])
    return 0


def cmd_tools(args) -> int:
    config = cfg.load()
    reg, errors = tool_registry.build(config)
    if args.action == "list":
        for t in reg.all():
            print(f"{t.name:18} {t.level.value:3} {t.description}")
        for err in errors:
            print(f"plugin error: {err}", file=sys.stderr)
        return 0
    desk = ActionDesk(dry_run=config["jarvis"]["dry_run"], confirm=lambda q: input(f"{q} [y/N] ").lower() == "y")
    print(reg.call(args.name, json.loads(args.json or "{}"), desk))
    return 0


def cmd_secrets(args) -> int:
    if args.action == "status":
        for name, is_set in secrets.status().items():
            print(f"{name:15} {'set' if is_set else 'not set'}")
        return 0
    secrets.set_(args.name, getpass.getpass(f"Value for {args.name} (hidden): "))
    print("Saved to the OS keyring.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jarvis", description="JARVIS skeleton")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, help_ in (
        ("init", cmd_init, "create config.toml from config.example.toml"),
        ("doctor", cmd_doctor, "environment health check"),
        ("chat", cmd_chat, "terminal chat"),
        ("voice", cmd_voice, "voice loop (stub engines)"),
        ("telegram", cmd_telegram, "Telegram bot"),
        ("dashboard", cmd_dashboard, "local dashboard"),
    ):
        sub.add_parser(name, help=help_).set_defaults(fn=fn)
    t = sub.add_parser("tools", help="list or run tools")
    t.add_argument("action", choices=["list", "run"])
    t.add_argument("name", nargs="?")
    t.add_argument("json", nargs="?", help='arguments as JSON, e.g. \'{"sides": 20}\'')
    t.set_defaults(fn=cmd_tools)
    s = sub.add_parser("secrets", help="manage secrets in the OS keyring")
    s.add_argument("action", choices=["status", "set"])
    s.add_argument("name", nargs="?")
    s.set_defaults(fn=cmd_secrets)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "tools" and args.action == "run" and not args.name:
        print("usage: jarvis tools run <name> ['{json}']")
        return 2
    if args.cmd == "secrets" and args.action == "set" and not args.name:
        print("usage: jarvis secrets set <name>")
        return 2
    try:
        return args.fn(args)
    except (env_guard.ForbiddenEnv, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
