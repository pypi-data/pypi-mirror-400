# tools/cldr/annotations_parser.py

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from tools.common.normalize import normalize_emoji_name


@dataclass(slots=True)
class CLDREntry:
    char: str
    short_name: str | None
    aliases: List[str]
    tags: List[str]


def parse_annotations_xml(path: Path) -> Dict[str, CLDREntry]:
    """
    Parse CLDR annotations XML (e.g. en.xml).

    Returns:
        dict[str, CLDREntry]
    """
    tree = ET.parse(path)
    root = tree.getroot()

    entries: Dict[str, CLDREntry] = {}

    for ann in root.findall(".//annotation"):
        char = ann.attrib.get("cp")
        if not char:
            continue

        entry = entries.setdefault(
            char,
            CLDREntry(
                char=char,
                short_name=None,
                aliases=[],
                tags=[],
            ),
        )

        text = (ann.text or "").strip()
        if not text:
            continue

        ann_type = ann.attrib.get("type")

        # Short name (tts)
        if ann_type == "tts":
            entry.short_name = normalize_emoji_name(text)
            continue

        # Tags / aliases
        parts = [normalize_emoji_name(p) for p in text.split("|")]
        for p in parts:
            if p and p not in entry.tags:
                entry.tags.append(p)
                entry.aliases.append(p)

    return entries
