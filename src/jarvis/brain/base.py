"""Brain interface. Channels (terminal, voice, Telegram, dashboard) talk to this and nothing else."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Brain(ABC):
    @abstractmethod
    async def ask(self, text: str) -> str:
        """One user utterance in, one reply out. Streaming/events are an easy extension:
        make this an async iterator and update the channels."""

    async def start(self) -> None:  # optional lifecycle hooks
        return None

    async def stop(self) -> None:
        return None
