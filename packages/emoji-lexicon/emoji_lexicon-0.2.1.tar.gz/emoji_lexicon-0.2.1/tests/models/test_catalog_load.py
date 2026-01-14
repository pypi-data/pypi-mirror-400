# tests/models/test_catalog_load.py
# type: ignore

from __future__ import annotations

from pathlib import Path
from typing import Any

import msgpack
import pytest

from emoji_lexicon.models import EmojiCatalog


# ----------------------------------------
# write msgpack (internal)
# ----------------------------------------
def _write_msgpack(path: Path, payload: dict[str, Any]) -> None:
    with path.open("wb") as f:
        msgpack.pack(payload, f, use_bin_type=True)


# ----------------------------------------
# load() (success)
# ----------------------------------------
def test_load_from_path_success(tmp_path: Path):
    p = tmp_path / "emoji.msgpack"
    payload: dict[str, Any] = {
        "emojis": [
            {
                "id": 1,
                "char": "😀",
                "short_name": "grinning_face",
                "aliases": ["grin"],
                "group": "Smileys",
                "subgroup": "face",
                "tags": ["smile", "happy"],
                "introduced_in": "1.0",
                "base_id": None,
            },
            {
                "id": 2,
                "char": "😁",
                "short_name": "beaming_face",
                "aliases": ["grin_big"],
                "group": "Smileys",
                "subgroup": "face",
                "tags": ["smile"],
                "introduced_in": "1.0",
                "base_id": None,
            },
        ]
    }

    _write_msgpack(p, payload)

    catalog = EmojiCatalog.load(p)
    assert len(catalog) == 2
    assert catalog.get("grin").id == 1
    assert catalog.get_by_char("😁").id == 2
    assert catalog.groups() == ("Smileys",)


# ----------------------------------------
# load() (failure)
# ----------------------------------------
def test_load_invalid_top_level_type_raises(tmp_path: Path):
    p = tmp_path / "emoji.msgpack"
    _write_msgpack(p, ["-not-a-dict"])

    with pytest.raises(TypeError, match="expected dict"):
        EmojiCatalog.load(p)
