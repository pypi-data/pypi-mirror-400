# tests/models/test_catalog_basic.py
# type: ignore

from __future__ import annotations

import pytest

from emoji_lexicon.models import Emoji, EmojiCatalog


# ----------------------------------------
# normalize query
# ----------------------------------------
def test_normalize_query():
    assert EmojiCatalog.normalize_query(" :smile: ") == "smile"
    assert EmojiCatalog.normalize_query("TeSt") == "test"
    assert EmojiCatalog.normalize_query("::OK::") == "ok"


# ----------------------------------------
# __len__, __iter__, get_all()
# ----------------------------------------
def test_len_iter_get_all(mini_catalog):
    assert len(mini_catalog) == 2
    assert [e.id for e in mini_catalog] == [1, 2]

    all_e = mini_catalog.get_all()
    assert isinstance(all_e, tuple)
    assert [e.id for e in all_e] == [1, 2]


# ----------------------------------------
# __str__, __repr__
# ----------------------------------------
def test_str_repr(mini_catalog):
    assert str(mini_catalog) == ""
    r = repr(mini_catalog)
    assert "EmojiCatalog" in r
    assert "size=2" in r
    assert "groups=1" in r


# ----------------------------------------
# get() (short name, alias, tag, miss)
# ----------------------------------------
def test_get_short_name_alias_tag_and_miss(mini_catalog):
    assert mini_catalog.get("grinning_face").id == 1
    assert mini_catalog.get(":grinning_face:").id == 1

    # alias
    assert mini_catalog.get("grin").id == 1

    # tag
    assert mini_catalog.get("happy").id == 1

    # miss
    assert mini_catalog.get("unknown") is None


# ----------------------------------------
# get_by_id(), get_char()
# ----------------------------------------
def test_get_by_id_and_char(mini_catalog):
    assert mini_catalog.get_by_id(2).short_name == "beaming_face"
    assert mini_catalog.get_by_char("😀").id == 1
    assert mini_catalog.get_by_char("❌") is None


# ----------------------------------------
# find()
# ----------------------------------------
def test_find_is_search_alias(mini_catalog):
    assert mini_catalog.find("smile") == mini_catalog.search("smile")


# ----------------------------------------
# groups(), subgroups()
# ----------------------------------------
def test_groups_and_subgroups(mini_catalog):
    assert mini_catalog.groups() == ("Smileys",)
    assert mini_catalog.subgroups() == ("face",)
