# tests/models/test_emoji_basic.py
# type: ignore

from __future__ import annotations

from emoji_lexicon.models import Emoji, EmojiCatalog


def test_emoji_str_and_repr():
    e = Emoji(
        id=1,
        char="😀",
        short_name="grinning_face",
        aliases=("grin",),
        tags=("smile",),
        group="Smileys",
        subgroup="face",
        introduced_in="1.0",
        base_id=None,
    )

    assert str(e) == "😀"
    assert "Emoji(" in repr(e)
    assert "char='😀'" in repr(e)
    assert "short_name='grinning_face'" in repr(e)
