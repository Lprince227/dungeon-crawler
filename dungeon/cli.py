"""Terminal front end: reads typed commands, prints the map and messages."""
from __future__ import annotations

KEYS = {"w": "up", "s": "down", "a": "left", "d": "right"}
ACTIONS = {"save", "load", "quit", "help"}


def parse_command(text: str) -> tuple[str, str | None]:
    """Turn typed input into (action, argument), e.g. 'w' -> ('move', 'up')."""
    word = text.strip().lower()
    if word in KEYS:
        return ("move", KEYS[word])
    if word in ACTIONS:
        return (word, None)
    return ("unknown", None)
