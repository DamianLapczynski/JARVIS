# JARVIS skeleton

[Polski](#polski) | [English](#english)

---

## English

A minimal, **runnable** skeleton for building your own voice assistant in the style of an elegant butler.
It keeps an architecture proven in a real personal assistant (engine, voice, Telegram bot, dashboard,
PC-control tools, Google integration) but contains **only stubs and examples**, no real logic, secrets or data.

### Architecture

```
            +-------------------- channels --------------------+
 you  --->  | terminal | voice (STT/TTS) | Telegram | dashboard |
            +---------------------------+-----------------------+
                                        |  text in / text out
                                   +----v----+
                                   |  Brain  |  echo (stub)  |  agent_sdk (you implement)
                                   +----+----+
                                        |  tool calls
                                +-------v--------+
                                | ToolRegistry   |  built-ins + plugins + entry points
                                +-------+--------+
                       R (read) --------+-------- W1/W2 (write)
                                                      |
                                              +-------v-------+
                                              |  ActionDesk   |  dry-run, confirmation, undo
                                              +---------------+
```

| Path | What it is |
|---|---|
| `src/jarvis/brain/` | `Brain` interface, `EchoBrain` keyword router (no LLM), `AgentSdkBrain` stub |
| `src/jarvis/tools/` | `ToolSpec`, safety levels, registry + plugin discovery, built-ins, `pc_control` (allowlisted app launcher) |
| `src/jarvis/plugins/` | example plugins: `hello` (R), `dice` (R), `reminder_stub` (W2) |
| `src/jarvis/speech/` | `TTS` / `STT` protocols; console + stdin engines work, Piper/Azure are stubs |
| `src/jarvis/channels/` | terminal chat, voice loop, Telegram (Bot API, allowlist), local dashboard |
| `src/jarvis/gapi/` | Google integration stub (sample data until you implement OAuth) |
| `src/jarvis/security/` | keyring secrets, env guard, action desk, log redaction |
| `src/jarvis/doctor.py` | `jarvis doctor` health check |

**Safety is in code, not in the prompt.** Levels: `R` read, `W1` reversible write (runs at once, undo offered),
`W2` write needing confirmation. There is no `X` level; tool names containing words like `shell` or `exec`
are refused by the registry. With `dry_run = true` (default) write tools only log what they would do.

### Requirements

- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- Optional extras: `keyring` (secrets), an LLM SDK (brain), `sounddevice` (voice), Google client libs

### Install

```bash
uv sync                       # core has no runtime dependencies
uv sync --extra secrets       # optional: OS keyring support
uv run jarvis init            # creates config.toml from config.example.toml
uv run jarvis doctor
uv run jarvis chat
```

### `jarvis doctor`

Checks Python version, `config.toml`, the environment guard (`ANTHROPIC_API_KEY` by default), a writable
`data/` directory, tool/plugin loading, dry-run state, which secrets are set (names only, never values)
and optional dependencies. Exit code is `1` when a required check fails.

### Other commands

```bash
uv run jarvis tools list
uv run jarvis tools run dice_roll '{"sides": 20}'
uv run jarvis secrets status
uv run jarvis secrets set telegram     # hidden prompt, stored in the OS keyring
uv run jarvis voice | telegram | dashboard
uv run pytest
```

Try in `jarvis chat`: `what time is it`, `note buy milk`, `undo`, `roll 20`, `open notepad`, `remind 15:30 call mom`.
Set `dry_run = false` in `config.toml` to let write tools act.

### Adding your own tool

1. Create `src/jarvis/plugins/my_tool.py` (or any `.py` in the directory set by `[tools] plugin_dir`):

```python
from jarvis.security.actions import Prepared
from jarvis.tools.base import Level, ToolSpec

def greet(name: str) -> str:                      # R tool: just return text
    return f"Good evening, {name}."

def save_todo(text: str) -> Prepared:             # W1/W2 tool: return Prepared, never act directly
    return Prepared(f"save todo: {text}", run=lambda: "Saved.", undo=lambda: "Removed.")

def register(registry) -> None:
    registry.register(ToolSpec("greet", "Greet someone.", Level.R, greet, {"name": "who"}))
    registry.register(ToolSpec("todo_save", "Save a todo.", Level.W1, save_todo, {"text": "todo text"}))
```

2. `uv run jarvis tools list` shows it; `uv run jarvis doctor` reports plugin load errors.
3. Packaged plugins: expose a module with `register(registry)` under the entry-point group `jarvis.tools`.
4. Add a test (see `tests/test_skeleton.py`). Wire an LLM by exposing `registry.all()` as its tool list.

### Security notes

Never commit `config.toml`, `.env`, tokens or OAuth JSON files (all git-ignored). Keep secrets in the keyring.
Never expose the dashboard beyond `127.0.0.1` without authentication. Allowlist who may talk to the Telegram bot.

### License

MIT, see [LICENSE](LICENSE).

---

## Polski

Minimalny, **działający** szkielet do zbudowania własnego asystenta głosowego w stylu eleganckiego kamerdynera.
Zachowuje architekturę sprawdzoną w prawdziwym osobistym asystencie (silnik, głos, bot Telegrama, dashboard,
narzędzia sterowania komputerem, integracja z Google), ale zawiera **wyłącznie stuby i przykłady**: bez prawdziwej
logiki, sekretów i danych.

### Architektura

Schemat jest w sekcji angielskiej powyżej. W skrócie: **kanały** (terminal, głos STT/TTS, Telegram, dashboard)
rozmawiają z interfejsem `Brain` (domyślnie `EchoBrain` bez modelu, a własny mózg z LLM implementujesz w
`brain/agent_sdk.py`). Mózg woła narzędzia z `ToolRegistry` (wbudowane, wtyczki i punkty wejścia `jarvis.tools`).
Narzędzia zapisu przechodzą przez `ActionDesk`: tryb próbny, potwierdzenie i cofanie.

**Bezpieczeństwo jest w kodzie, nie w prompcie.** Poziomy: `R` odczyt, `W1` odwracalny zapis (od razu, z „cofnij”),
`W2` zapis po potwierdzeniu. Poziomu `X` nie ma, a rejestr odrzuca nazwy narzędzi z `shell`, `exec` itp.
Przy `dry_run = true` (domyślnie) narzędzia zapisu tylko logują, co by zrobiły.

### Wymagania

- Python 3.11+ i [uv](https://docs.astral.sh/uv/)
- Opcjonalnie: `keyring` (sekrety), SDK modelu (mózg), `sounddevice` (głos), biblioteki Google

### Instalacja

```bash
uv sync                       # rdzeń nie ma zależności uruchomieniowych
uv sync --extra secrets       # opcjonalnie: keyring systemowy
uv run jarvis init            # tworzy config.toml z config.example.toml
uv run jarvis doctor
uv run jarvis chat
```

### `jarvis doctor`

Sprawdza wersję Pythona, `config.toml`, straż środowiska (domyślnie `ANTHROPIC_API_KEY`), zapisywalny katalog
`data/`, ładowanie narzędzi i wtyczek, tryb próbny, które sekrety są ustawione (tylko nazwy, nigdy wartości) oraz
zależności opcjonalne. Kod wyjścia `1`, gdy nie przejdzie wymagana kontrola.

### Dodawanie własnego narzędzia

1. Utwórz `src/jarvis/plugins/moje_narzedzie.py` (albo dowolny `.py` w katalogu z `[tools] plugin_dir`) wzorem
   przykładu z sekcji angielskiej: funkcja `register(registry)` rejestruje `ToolSpec`.
2. Narzędzie `R` zwraca tekst. Narzędzie `W1`/`W2` zwraca `Prepared(opis, run, undo)` i nigdy nie działa samo.
3. `uv run jarvis tools list` pokaże narzędzie, a `jarvis doctor` zgłosi błędy ładowania wtyczek.
4. Dodaj test (wzór: `tests/test_skeleton.py`). Aby podłączyć model, wystaw `registry.all()` jako jego narzędzia.

### Uwagi o bezpieczeństwie

Nie commituj `config.toml`, `.env`, tokenów ani plików OAuth (wszystko jest w `.gitignore`). Sekrety trzymaj w
keyring (`uv run jarvis secrets set <nazwa>`). Nie wystawiaj dashboardu poza `127.0.0.1` bez uwierzytelniania.
Ogranicz bota Telegrama białą listą użytkownika.

### Licencja

MIT, zob. [LICENSE](LICENSE).
