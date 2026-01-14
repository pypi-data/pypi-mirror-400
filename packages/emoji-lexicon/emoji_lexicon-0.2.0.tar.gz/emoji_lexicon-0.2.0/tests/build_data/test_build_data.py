# tests/build_data/test_build_data.py
# type: ignore

from __future__ import annotations

from pathlib import Path

import pytest
from msgpack import pack

from emoji_lexicon.build import merge_emoji
from emoji_lexicon.models import EmojiCatalog
from emoji_lexicon.unicode import parse_annotations_xml, parse_emoji_test

# ----------------------------------------
# Paths
# ----------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "tools" / "data"
EMOJI_TEST_TXT = DATA_DIR / "emoji-test.txt"
CLDR_XML = DATA_DIR / "cldr" / "common" / "annotations" / "en.xml"


# ----------------------------------------
# Tests
# ----------------------------------------
def test_build_data_smoke(tmp_path: Path):
    print(f"DATA_DIR: {DATA_DIR}")
    # input data
    emoji_tests = parse_emoji_test(EMOJI_TEST_TXT)
    cldr = parse_annotations_xml(CLDR_XML)

    emojis = []
    emoji_id = 0

    for entry in emoji_tests.entries:
        if entry.qualification != "fully-qualified":
            continue
        emojis.append(merge_emoji(entry, cldr.get(entry.char), emoji_id))
        emoji_id += 1

    # msgpack output (Equivalent to 'build-data.py')
    output_file = tmp_path / "emoji.msgpack"
    print(f"Output file: {output_file}")

    with output_file.open("wb") as f:
        pack(
            {
                "emojis": [
                    {
                        "id": e.id,
                        "char": e.char,
                        "short_name": e.short_name,
                        "aliases": list(e.aliases),
                        "group": e.group,
                        "subgroup": e.subgroup,
                        "tags": list(e.tags),
                        "introduced_in": e.introduced_in,
                        "base_id": e.base_id,
                    }
                    for e in emojis
                ]
            },
            f,
            use_bin_type=True,
        )

    catalog = EmojiCatalog.load(output_file)
    assert len(catalog) > 0
