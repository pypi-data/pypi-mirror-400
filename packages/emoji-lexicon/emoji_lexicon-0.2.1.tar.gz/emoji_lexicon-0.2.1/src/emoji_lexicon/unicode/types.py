# src/emoji_lexicom/unicode/types.py

from __future__ import annotations

from dataclasses import dataclass


# ----------------------------------------
# EmojiTestData
# ----------------------------------------
@dataclass(slots=True)
class EmojiTestData:
    emoji_version: str
    entries: list[EmojiTestEntry]


# ----------------------------------------
# EmojiTestEntry
# ----------------------------------------
@dataclass(slots=True)
class EmojiTestEntry:
    codepoints: list[str]
    char: str
    name: str
    group: str
    subgroup: str
    qualification: str
    introduced_in: str


# ----------------------------------------
# CLDREntry
# ----------------------------------------
@dataclass(slots=True)
class CLDREntry:
    char: str
    short_name: str | None
    tags: tuple[str, ...]
