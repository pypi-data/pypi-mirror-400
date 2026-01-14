# tools/unicode/emoji_test_parser.py

from __future__ import annotations

import re
from pathlib import Path

from .types import EmojiTestData, EmojiTestEntry

# ----------------------------------------
# Regexp pattern
# ----------------------------------------
_VERSION_RE = re.compile(r"#\s*Version:\s*(?P<version>[\d.]+)")
_GROUP_RE = re.compile(r"#\s*group:\s*(?P<group>.+)")
_SUBGROUP_RE = re.compile(r"#\s*subgroup:\s*(?P<subgroup>.+)")
_EMOJI_LINE_RE = re.compile(
    r"""
    ^(?P<codepoints>[0-9A-Fa-f ]+)\s*;
    \s*(?P<qualification>[^\#\s]+)\s*\#
    \s*(?P<char>\S+)
    \s+[Ee](?P<introduced_in>[\d.]+)
    \s+(?P<name>.+)$
    """,
    re.VERBOSE,
)


# ----------------------------------------
# Parser
# ----------------------------------------
def parse_emoji_test(path: Path) -> EmojiTestData:
    """
    Parse unicode emoji-testtxt file.

    This parser extracts:
    - Unicode emoji version (from header)
    - Emoji entries with group / subgroup information
    - Introduced emoji version (E1.0, E2.0, ...)

    Parameters:
    ------------
    path:
        Path to emoji-test.txt

    Returns:
    ---------
    EmojiTestData
        Parsed emoji test data.
    """
    path = Path(path)

    emoji_version: str | None = None
    entries: list[EmojiTestEntry] = []

    current_group: str | None = None
    current_subgroup: str | None = None

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Version
            if emoji_version is None:
                m = _VERSION_RE.match(line)
                if m:
                    emoji_version = m.group("version")
                    continue

            # Group
            m = _GROUP_RE.match(line)
            if m:
                current_group = m.group("group")
                continue

            # Subgroup
            m = _SUBGROUP_RE.match(line)
            if m:
                current_subgroup = m.group("subgroup")
                continue

            # Emoji entry
            m = _EMOJI_LINE_RE.match(line)
            if not m:
                continue

            if current_group is None or current_subgroup is None:
                raise ValueError(
                    "Emoji entry found before group/subgroup definition"
                )

            codepoints: list[str] = m.group("codepoints").split()

            entry = EmojiTestEntry(
                codepoints=codepoints,
                char=m.group("char"),
                name=m.group("name"),
                group=current_group,
                subgroup=current_subgroup,
                qualification=m.group("qualification"),
                introduced_in=m.group("introduced_in"),
            )
            entries.append(entry)

    if emoji_version is None:
        raise ValueError("Unicode emoji version not found in emoji-test.txt")

    return EmojiTestData(
        emoji_version=emoji_version,
        entries=entries,
    )
