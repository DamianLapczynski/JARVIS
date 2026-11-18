"""Terminal chat channel."""

from __future__ import annotations

import asyncio

from jarvis.brain.base import Brain


def ask_yes_no(question: str) -> bool:
    return input(f"{question} [y/N] ").strip().lower() in {"y", "yes", "t", "tak"}


def run(brain: Brain) -> None:
    print("Type a message ('/quit' to exit).")
    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text in {"/quit", "/exit"}:
            break
        if text:
            print(asyncio.run(brain.ask(text)))
