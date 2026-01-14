# tests/unicode/test_emoji_test_parser.py
# type: ignore

from __future__ import annotations

from pathlib import Path

import pytest

from emoji_lexicon.unicode import (
    EmojiTestData,
    EmojiTestEntry,
    parse_emoji_test,
)

FIXTURE = Path(__file__).parent / "data" / "emoji-test-mini.txt"


def test_parse_returns_data_object():
    data = parse_emoji_test(FIXTURE)

    assert isinstance(data, EmojiTestData)


def test_parse_unicode_version():
    data = parse_emoji_test(FIXTURE)

    assert data.emoji_version == "17.0"


def test_parse_entries_basic_fields():
    data = parse_emoji_test(FIXTURE)

    assert len(data.entries) == 3

    e = data.entries[0]
    assert isinstance(e, EmojiTestEntry)

    assert e.char == "😀"
    assert e.name == "grinning face"
    assert e.qualification == "fully-qualified"
    assert e.introduced_in == "1.0"


def test_group_and_subgroup_assignment():
    data = parse_emoji_test(FIXTURE)

    e1 = data.entries[0]
    e2 = data.entries[1]
    e3 = data.entries[2]

    assert e1.group == "Smileys & Emotion"
    assert e1.subgroup == "face-smiling"

    assert e2.subgroup == "face-smiling"
    assert e3.subgroup == "face-affection"


def test_codepoints_parsed():
    data = parse_emoji_test(FIXTURE)

    e = data.entries[0]
    assert e.codepoints == ["1F600"]


def test_missing_unicode_version_raises(tmp_path: Path):
    p = tmp_path / "emoji-test.txt"
    p.write_text(
        """
# group: Smileys & Emotion
# subgroup: face-smiling
1F600 ; fully-qualified # 😀 E1.0 grinning face
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError, match="Unicode emoji version not found in emoji-test.txt"
    ):
        parse_emoji_test(p)


def test_emoji_before_group_raises(tmp_path: Path):
    p = tmp_path / "emoji-test.txt"
    p.write_text(
        """
# Version 17.0
1F600 ; fully-qualified # 😀 E1.0 grinning face
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Emoji entry found before group/subgroup definition",
    ):
        parse_emoji_test(p)


def test_unmatched_lines_are_ignored(tmp_path: Path):
    p = tmp_path / "emoji-test.txt"
    p.write_text(
        """
# Version: 17.0
# group: Smileys & Emotion
# subgroup: face-smiling

THIS IS NOT AN EMOJI LINE
1F600 ; fully-qualified # 😀 E1.0 grinning face
""",
        encoding="utf-8",
    )

    data = parse_emoji_test(p)

    assert len(data.entries) == 1
    assert data.entries[0].name == "grinning face"


def test_only_first_version_is_used(tmp_path: Path):
    p = tmp_path / "emoji-test.txt"
    p.write_text(
        """
# Version: 16.0
# Version: 17.0
# group: Smileys & Emotion
# subgroup: face-smiling
1F600 ; fully-qualified # 😀 E1.0 grinning face
""",
        encoding="utf-8",
    )

    data = parse_emoji_test(p)

    assert data.emoji_version == "16.0"


def test_multiple_codepoints_are_split(tmp_path: Path):
    p = tmp_path / "emoji-test.txt"
    p.write_text(
        """
# Version: 17.0
# group: Smileys & Emotion
# subgroup: family
1F468 200D 1F469 ; fully-qualified # 👨‍👩 E2.0 family
""",
        encoding="utf-8",
    )

    data = parse_emoji_test(p)
    e = data.entries[0]

    assert e.codepoints == ["1F468", "200D", "1F469"]
