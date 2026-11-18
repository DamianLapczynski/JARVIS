"""Speech-to-text. `stdin` types instead of listening, so the voice loop is testable without a mic."""

from __future__ import annotations

from typing import Protocol


class STT(Protocol):
    def listen(self) -> str | None:
        """Block until one utterance is recognised. None = stop listening."""


class StdinSTT:
    def listen(self) -> str | None:
        try:
            return input("you (stdin-stt)> ").strip() or ""
        except EOFError:
            return None


def build(config: dict) -> STT:
    # Add your engine here (Whisper, Groq, Vosk, ...) keyed by config["speech"]["stt"].
    return StdinSTT()
