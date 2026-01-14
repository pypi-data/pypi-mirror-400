# tools/common/normalize.py

from __future__ import annotations


def normalize_emoji_name(text: str) -> str:
    """
    Normalize emoji name / alias / tag to snake_case.

    Rules:
    - lower case
    - replace '&' -> 'and'
    - normalize space / hyphens
    """
    return (
        text.strip()
        .lower()
        .replace("&", "and")
        .replace("-", " ")
        .replace("  ", " ")
        .replace(" ", "_")
    )
