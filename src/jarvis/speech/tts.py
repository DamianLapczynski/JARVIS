"""Text-to-speech engines. `console` works out of the box; `piper` and `azure` are stubs."""

from __future__ import annotations

import shutil
import subprocess
from typing import Protocol


class TTS(Protocol):
    def speak(self, text: str) -> None: ...


class ConsoleTTS:
    def speak(self, text: str) -> None:
        print(f"[tts] {text}")


class PiperTTS:
    """Local offline TTS via the `piper` binary. Implement audio playback for your OS."""

    def __init__(self, binary: str, model: str):
        self.binary, self.model = binary, model

    def speak(self, text: str) -> None:
        if shutil.which(self.binary) is None:
            raise RuntimeError(f"{self.binary!r} not found on PATH")
        # TODO: pipe `text` to piper (`--model`, `--output_file`) and play the WAV.
        subprocess.run([self.binary, "--help"], capture_output=True, check=False)
        raise NotImplementedError("PiperTTS.speak: wire piper output to your audio player")


class AzureTTS:
    """Cloud TTS over REST. Key: `jarvis secrets set azure_speech`. Add a Piper fallback on errors."""

    def __init__(self, region: str, voice: str):
        self.region, self.voice = region, voice

    def speak(self, text: str) -> None:
        raise NotImplementedError("AzureTTS.speak: POST SSML to the regional TTS endpoint")


def build(config: dict) -> TTS:
    s = config.get("speech", {})
    engine = s.get("tts", "console")
    if engine == "piper":
        return PiperTTS(s.get("piper_binary", "piper"), s.get("piper_model", ""))
    if engine == "azure":
        return AzureTTS(s.get("azure_region", ""), s.get("azure_voice", ""))
    return ConsoleTTS()
