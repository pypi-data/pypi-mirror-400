# tests/build/test_merge.py
# type: ignore

import pytest

from emoji_lexicon.build import merge_emoji
from emoji_lexicon.models import Emoji
from emoji_lexicon.unicode import CLDREntry, EmojiTestEntry


# ----------------------------------------
# fixtures (minimal)
# ----------------------------------------
def make_emoji_test_entry() -> EmojiTestEntry:
    return EmojiTestEntry(
        codepoints=["1F600"],
        char="😀",
        name="grinning face",
        group="Smileys & Emotion",
        subgroup="face-smiling",
        qualification="fully-qualified",
        introduced_in="1.0",
    )


def make_cldr_entry() -> CLDREntry:
    return CLDREntry(
        char="😀",
        short_name="grinning_face",
        tags=("smile", "happy"),
    )


# ----------------------------------------
# Tests
# ----------------------------------------
def test_merge_with_cldr():
    entry = make_emoji_test_entry()
    cldr = make_cldr_entry()

    emoji = merge_emoji(entry, cldr, emoji_id=1)

    assert isinstance(emoji, Emoji)
    assert emoji.id == 1
    assert emoji.char == "😀"
    assert emoji.short_name == "grinning_face"
    assert emoji.tags == ("smile", "happy")
    assert emoji.introduced_in == "1.0"
    assert emoji.base_id is None


def test_merge_without_cldr():
    entry = make_emoji_test_entry()

    emoji = merge_emoji(entry, None, emoji_id=42)

    assert emoji.id == 42
    assert emoji.short_name == "grinning_face"
    assert emoji.tags == ()
    assert emoji.introduced_in == "1.0"


def test_short_name_always_from_emoji_test():
    entry = make_emoji_test_entry()
    cldr = CLDREntry(
        char="😀",
        short_name="some_other_name",
        tags=("x",),
    )

    emoji = merge_emoji(entry, cldr, emoji_id=0)

    # emoji-test name is canonical
    assert emoji.short_name == "grinning_face"


def test_tags_are_deterministic():
    entry = make_emoji_test_entry()
    cldr = CLDREntry(
        char="😀",
        short_name="grinning_face",
        tags=("happy", "smile"),
    )

    emoji = merge_emoji(entry, cldr, emoji_id=0)

    # order must be preserved as given (already sorted upstream)
    assert emoji.tags == ("happy", "smile")
