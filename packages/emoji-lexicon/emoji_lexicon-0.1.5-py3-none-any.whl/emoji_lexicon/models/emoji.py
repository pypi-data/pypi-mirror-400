# src/emoji_lexicon/models/emoji.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class Emoji:
    """
    Immutable emoji data model.

    This class represents a single emoji entry i the emoji lexicon.
    All instances are expected to be generated at build-time and treated
    as read-only during runtime.
    """

    # Internal numeric identifier (used for fast indexing)
    id: int

    # The actual emoji character (may be a multi-codepoint sequence)
    char: str

    # Canonical short name (snake_case, without colons)
    short_name: str

    # Alternative names (aliases), normalized
    aliases: Sequence[str]

    # Unicode grouping
    group: str
    subgroup: str

    # Searchable tags (typically from CLDR annotations)
    tags: Sequence[str]

    # Unicode version when this emoji was introduced
    unicode_version: str

    # Optional base emoji id (for skin tone variants, etc.)
    base_id: int | None = None

    def __str__(self) -> str:
        return self.char

    def __repr__(self) -> str:
        return f"Emoji(char={self.char!r}, short_name={self.short_name!r})"
