# tests/models/test_catalog_search.py
# type: ignore

import pytest

from emoji_lexicon.models import Emoji, EmojiCatalog


# ----------------------------------------
# empty query
# ----------------------------------------
def test_search_empty(mini_catalog):
    assert mini_catalog.search("") == ()


# ----------------------------------------
# short name exact match
# ----------------------------------------
def test_search_exact_short_name(mini_catalog):
    r = mini_catalog.search("grinning_face")
    assert [e.id for e in r] == [1]


# ----------------------------------------
# alias exact match
# ----------------------------------------
def test_search_alias_exact_is_prioritized(mini_catalog):
    r = mini_catalog.search("grin")

    assert r
    assert r[0].id == 1


# ----------------------------------------
# tag exact match
# ----------------------------------------
def test_search_exact_tag(mini_catalog):
    r = mini_catalog.search("happy")
    assert [e.id for e in r] == [1]


# ----------------------------------------
# prefix match (len >= 3)
# ----------------------------------------
def test_search_prefix(mini_catalog):
    r = mini_catalog.search("smi")
    assert [e.id for e in r] == [1, 2]


# ----------------------------------------
# prefix match disabled (len < 3)
# ----------------------------------------
def test_search_prefix_too_short(mini_catalog):
    assert mini_catalog.search("sm") == ()


# ----------------------------------------
# AND merge
# ----------------------------------------
def test_search_and_merge(mini_catalog):
    r = mini_catalog.search("smile happy")
    assert [e.id for e in r] == [1]


# ----------------------------------------
# Ranking
# ----------------------------------------
def test_search_ranking(mini_catalog):
    r = mini_catalog.search("smile")
    assert [e.id for e in r] == [1, 2]
