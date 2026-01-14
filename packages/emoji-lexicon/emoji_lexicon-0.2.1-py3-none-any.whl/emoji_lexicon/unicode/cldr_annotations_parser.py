# src/emoji_lexicon/unicode/cldr_annotations_parser.py

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Set, TypedDict

from .normalize import normalize_emoji_name
from .types import CLDREntry


# ----------------------------------------
# _CLDRAccum
# ----------------------------------------
class _CLDRAccum(TypedDict):
    short_name: str | None
    tags: Set[str]


# ----------------------------------------
# parse annotations xml
# ----------------------------------------
def parse_annotations_xml(path: Path) -> dict[str, CLDREntry]:
    tree = ET.parse(path)
    return parse_annotations_root(tree.getroot())


# ----------------------------------------
# parse annotations xml's root
# ----------------------------------------
def parse_annotations_root(root: ET.Element) -> dict[str, CLDREntry]:
    entries: dict[str, _CLDRAccum] = {}

    for ann in root.findall(".//annotation"):
        char = ann.attrib.get("cp")
        if not char:
            continue

        e = entries.setdefault(
            char,
            {"short_name": None, "tags": set()},
        )

        text = (ann.text or "").strip()
        if not text:
            continue

        ann_type = ann.attrib.get("type")
        if ann_type == "tts":
            e["short_name"] = normalize_emoji_name(text)
        else:
            for part in text.split("|"):
                tag = normalize_emoji_name(part)
                if tag:
                    e["tags"].add(tag)
    return {
        char: CLDREntry(
            char=char,
            short_name=data["short_name"],
            tags=tuple(sorted(data["tags"])),
        )
        for char, data in entries.items()
    }
