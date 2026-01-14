# tests/models/conftest.py
# type: ignore

from __future__ import annotations

import pytest

from emoji_lexicon.models import Emoji, EmojiCatalog


# ----------------------------------------
# minimam fixture
# ----------------------------------------
@pytest.fixture
def mini_catalog():
    e1 = Emoji(
        id=1,
        char="😀",
        short_name="grinning_face",
        aliases=("grin",),
        tags=("smile", "happy"),
        group="Smileys",
        subgroup="face",
        introduced_in="1.0",
        base_id=None,
    )
    e2 = Emoji(
        id=2,
        char="😁",
        short_name="beaming_face",
        aliases=("grin_big",),
        tags=("smile",),
        group="Smileys",
        subgroup="face",
        introduced_in="1.0",
        base_id=None,
    )

    return EmojiCatalog(
        [e1, e2],
        by_id={1: e1, 2: e2},
        by_short_name={
            "grinning_face": e1,
            "beaming_face": e2,
        },
        by_alias={
            "grin": [e1],
            "grin_big": [e2],
        },
        by_char={
            "😀": e1,
            "😁": e2,
        },
    )
