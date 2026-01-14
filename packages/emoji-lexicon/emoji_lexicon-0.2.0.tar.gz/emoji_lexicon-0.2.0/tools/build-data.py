# tools/build-data.py
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

from __future__ import annotations

from pathlib import Path
from typing import Any

import msgpack

from emoji_lexicon.build import merge_emoji
from emoji_lexicon.models import Emoji
from emoji_lexicon.unicode import parse_annotations_xml, parse_emoji_test

# ----------------------------------------
# Paths
# ----------------------------------------
ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "tools" / "data"
EMOJI_TEST_TXT = DATA_DIR / "emoji-test.txt"
CLDR_XML = DATA_DIR / "cldr" / "common" / "annotations" / "en.xml"

OUTPUT_DIR = ROOT / "src" / "emoji_lexicon" / "data"
OUTPUT_FILE = OUTPUT_DIR / "emoji.msgpack"


# ----------------------------------------
# Build
# ----------------------------------------
def build() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parse inputs
    emoji_tests = parse_emoji_test(EMOJI_TEST_TXT)
    cldr_entries = parse_annotations_xml(CLDR_XML)

    emojis: list[Emoji] = []

    emoji_id = 0
    for entry in emoji_tests.entries:
        # Only fully-qualified emojis
        if entry.qualification != "fully-qualified":
            continue

        cldr = cldr_entries.get(entry.char)

        emoji = merge_emoji(
            entry=entry,
            cldr=cldr,
            emoji_id=emoji_id,
        )
        emojis.append(emoji)
        emoji_id += 1

    # Serialize payload
    payload = {
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
    }

    with OUTPUT_FILE.open("wb") as f:
        msgpack.pack(payload, f, use_bin_type=True)

    print(f"✨ Generated emoji lexicon: {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
