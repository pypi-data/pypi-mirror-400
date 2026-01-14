# src/emoji_lexicon/build/merge.py

from __future__ import annotations

from emoji_lexicon.models import Emoji
from emoji_lexicon.unicode import (
    CLDREntry,
    EmojiTestEntry,
    normalize_emoji_name,
)


# ----------------------------------------
# merge emoji data
# ----------------------------------------
def merge_emoji(
    entry: EmojiTestEntry,
    cldr: CLDREntry | None,
    emoji_id: int,
) -> Emoji:
    short_name = normalize_emoji_name(entry.name)

    tags: tuple[str, ...] = ()
    if cldr:
        tags = cldr.tags

    return Emoji(
        id=emoji_id,
        char=entry.char,
        short_name=short_name,
        aliases=(),
        group=entry.group,
        subgroup=entry.subgroup,
        tags=tags,
        introduced_in=entry.introduced_in,
        base_id=None,
    )
