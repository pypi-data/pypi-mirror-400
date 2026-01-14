# tests/test_unicode_normalize.py
# type: ignore

import pytest

from emoji_lexicon.unicode.normalize import normalize_emoji_name


@pytest.mark.parametrize(
    "text, expected",
    [
        # basic
        ("grinning face", "grinning_face"),
        ("Grinning Face", "grinning_face"),
        # strip
        ("  grinning face  ", "grinning_face"),
        # ampersand
        ("man & woman", "man_and_woman"),
        ("rock&roll", "rockandroll"),
        # hyphen
        ("woman-technologist", "woman_technologist"),
        # mixed space and hyphen
        ("woman - technologist", "woman__technologist"),
        # already normalized
        ("grinning_face", "grinning_face"),
        # multiple words
        ("face with tears of joy", "face_with_tears_of_joy"),
    ],
)
def test_normalize_emoji_name(text: str, expected: str):
    assert normalize_emoji_name(text) == expected


def test_multiple_spaces_are_partially_normalized():
    text = "grinning   face"
    assert normalize_emoji_name(text) == "grinning__face"


def test_empty_string():
    assert normalize_emoji_name("") == ""


def test_only_spaces():
    assert normalize_emoji_name("   ") == ""
