# tools/unicode/emoji_test_parser.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(slots=True)
class EmojiTestEntry:
    codepoints: list[str]
    char: str
    name: str
    group: str
    subgroup: str
    qualification: str
    unicode_version: str | None


def parse_emoji_test(path: Path) -> Iterator[EmojiTestEntry]:
    group: str = ""
    subgroup: str = ""

    for line in path.read_text(encoding="UTF-8").splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("# group:"):
            group = line.split(":", 1)[1].strip()
            continue

        if line.startswith("# subgroup:"):
            subgroup = line.split(":", 1)[1].strip()
            continue

        if line.startswith("#"):
            continue

        # Example:
        # 1F600 : fully-qualified # 😀 grinning face E1.0
        left, comment = line.split("#", 1)
        code_and_qual = left.split(";")
        codepoints = code_and_qual[0].strip().split()
        qualification = code_and_qual[1].strip()

        comment_parts = comment.strip().split()
        char = comment_parts[0]
        name_parts = comment_parts[1:]

        unicode_version = None
        if name_parts and name_parts[-1].startswith("E"):
            unicode_version = name_parts[-1][1:]
            name_parts = name_parts[:-1]

        name = " ".join(name_parts)

        yield EmojiTestEntry(
            codepoints=codepoints,
            char=char,
            name=name,
            group=group,
            subgroup=subgroup,
            qualification=qualification,
            unicode_version=unicode_version,
        )
