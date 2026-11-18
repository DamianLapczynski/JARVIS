import asyncio

import pytest

from jarvis import cli, config as cfg, doctor
from jarvis.brain.echo import EchoBrain
from jarvis.security import env_guard
from jarvis.security.actions import ActionDesk, Prepared
from jarvis.security.redact import redact
from jarvis.tools import registry as tr
from jarvis.tools.base import Level, ToolSpec
from jarvis.tools.pc_control import is_safe_uri


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("JARVIS_HOME", str(tmp_path))
    return tmp_path


def build(dry_run=True, confirm=None):
    config = cfg.load()
    reg, errors = tr.build(config)
    assert not errors
    return reg, ActionDesk(dry_run, confirm)


def test_plugins_are_discovered():
    reg, _ = build()
    assert {"clock_now", "notes_add", "hello", "dice_roll", "reminder_set", "pc_open_app"} <= {t.name for t in reg.all()}


def test_forbidden_tool_name_is_rejected():
    with pytest.raises(tr.RegistryError):
        tr.ToolRegistry().register(ToolSpec("run_shell", "x", Level.W1, lambda: None))


def test_dry_run_writes_nothing(home):
    reg, desk = build(dry_run=True)
    reg.call("notes_add", {"text": "x"}, desk)
    assert not (home / "data" / "notes.md").exists()


def test_w1_runs_and_undoes(home):
    reg, desk = build(dry_run=False)
    reg.call("notes_add", {"text": "milk"}, desk)
    assert "- milk" in (home / "data" / "notes.md").read_text()
    assert desk.undo().executed
    assert "milk" not in (home / "data" / "notes.md").read_text()


def test_w2_needs_confirmation():
    reg, desk = build(dry_run=False, confirm=lambda q: False)
    assert "Cancelled" in reg.call("reminder_set", {"when": "9", "text": "x"}, desk)
    reg, desk = build(dry_run=False, confirm=lambda q: True)
    assert "Reminder set" in reg.call("reminder_set", {"when": "9", "text": "x"}, desk)


def test_write_tool_must_return_prepared():
    reg = tr.ToolRegistry()
    reg.register(ToolSpec("bad_write", "x", Level.W1, lambda: "oops"))
    with pytest.raises(tr.RegistryError):
        reg.call("bad_write", {}, ActionDesk(False))


def test_pc_control_allowlist():
    assert is_safe_uri("ms-notepad:") and not is_safe_uri("file:///c:/x.exe") and not is_safe_uri("cmd:")


def test_echo_brain_roundtrip():
    reg, desk = build()
    brain = EchoBrain(reg, desk)
    assert "Hello, Ada" in asyncio.run(brain.ask("hello Ada"))
    assert "Rolled d20" in asyncio.run(brain.ask("roll 20"))


def test_env_guard(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    with pytest.raises(env_guard.ForbiddenEnv):
        env_guard.check(["ANTHROPIC_API_KEY"])


def test_redact():
    assert "REDACTED" in redact("token 123456789:" + "A" * 35)


def test_doctor_passes_on_clean_env(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert all(c.ok for c in doctor.run() if c.required)


def test_cli_tools_list(capsys):
    assert cli.main(["tools", "list"]) == 0
    assert "dice_roll" in capsys.readouterr().out
