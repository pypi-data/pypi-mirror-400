# tools/build-data.py
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import msgpack

from tools.cldr.annotations_parser import parse_annotations_xml
from tools.common.normalize import normalize_emoji_name
from tools.unicode.emoji_test_parser import parse_emoji_test

if TYPE_CHECKING:
    from tools.cldr.annotations_parser import CLDREntry

OUTPUT_DIR = Path("src/emoji_lexicon/data")
OUTPUT_FILE = OUTPUT_DIR / "emoji.msgpack"

CLDR_XML = Path("tools/data/cldr/common/annotations/en.xml")
if not CLDR_XML.exists():
    raise RuntimeError("Missing CLDR annotations XML: en.xml")


def build() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    emojis: list[dict[str, Any]] = []
    by_id: dict[str, int] = {}
    by_short_name: dict[str, int] = {}
    by_alias: dict[str, list[int]] = {}
    by_char: dict[str, int] = {}

    emoji_id: int = 0

    emoji_test_path = Path("tools/data/emoji-test.txt")

    # parse CLDR annotations XML
    cldr_entries: dict[str, CLDREntry] = parse_annotations_xml(CLDR_XML)

    for entry in parse_emoji_test(emoji_test_path):
        # Process only data with a qualification that matches "fully-qualified"
        if entry.qualification != "fully-qualified":
            continue

        # get CLDR
        cldr = cldr_entries.get(entry.char)

        # Short name
        if cldr and cldr.short_name:
            short_name = cldr.short_name
        else:
            short_name = normalize_emoji_name(entry.name)

        # aliases / tags
        if cldr:
            aliases = list(cldr.aliases)
            tags = list(cldr.tags)
        else:
            aliases = []
            tags = []

        emoji: dict[str, Any] = {
            "id": emoji_id,
            "char": entry.char,
            "short_name": short_name,
            "aliases": aliases,
            "group": entry.group,
            "subgroup": entry.subgroup,
            "tags": tags,
            "unicode_version": entry.unicode_version,
            "base_id": None,
        }

        emojis.append(emoji)
        by_id[str(emoji_id)] = emoji_id
        for alias in aliases:
            by_alias.setdefault(alias, []).append(emoji_id)
        by_short_name[short_name] = emoji_id
        by_char[entry.char] = emoji_id

        emoji_id += 1

    payload: dict[str, Any] = {
        "meta": {"version": "0.1.0"},
        "emojis": emojis,
        "indexes": {
            "by_id": by_id,
            "by_short_name": by_short_name,
            "by_alias": by_alias,
            "by_char": by_char,
        },
    }

    with OUTPUT_FILE.open("wb") as f:
        msgpack.pack(payload, f, use_bin_type=True)

    print(f"Generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
