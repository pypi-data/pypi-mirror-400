# tests/unicode/test_cldr_annotations_parser.py
# type: ignore

from __future__ import annotations

from pathlib import Path

from emoji_lexicon.unicode.cldr_annotations_parser import parse_annotations_xml

FIXTURE = Path(__file__).parent / "data" / "cldr-annotations-mini.xml"


def test_parse_cldr_basic():
    data = parse_annotations_xml(FIXTURE)

    assert isinstance(data, dict)
    assert "😀" in data
    assert "😀" in data


def test_short_name_from_tts():
    data = parse_annotations_xml(FIXTURE)

    e = data["😀"]
    assert e.short_name == "grinning_face"


def test_tags_parsed_and_normalized():
    data = parse_annotations_xml(FIXTURE)

    e = data["😀"]
    assert set(e.tags) == {"smile", "happy"}


def test_duplicate_tags_removed():
    data = parse_annotations_xml(FIXTURE)

    e = data["😀"]
    assert e.tags.count("smile") == 1


def test_entry_without_tts():
    data = parse_annotations_xml(FIXTURE)

    e = data["❓"]
    assert e.short_name is None
    assert e.tags == ("question",)


def test_invalid_annotation_ignored():
    data = parse_annotations_xml(FIXTURE)

    # annotation without cp should be ignored
    assert all(e.char for e in data.values())
