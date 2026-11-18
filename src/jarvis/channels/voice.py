"""Voice loop skeleton: STT -> brain -> TTS. Add wake word, VAD, barge-in and a push-to-talk key here."""

from __future__ import annotations

import asyncio

from jarvis.brain.base import Brain
from jarvis.speech.stt import STT
from jarvis.speech.tts import TTS


def run(brain: Brain, stt: STT, tts: TTS) -> None:
    while (heard := stt.listen()) is not None:
        if heard:
            tts.speak(asyncio.run(brain.ask(heard)))
