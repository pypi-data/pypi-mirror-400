# tests/test_api.py
# type: ignore

import pytest

from emoji_lexicon import get_catalog


def test_get_catalog_is_cached():
    c1 = get_catalog()
    c2 = get_catalog()

    # lru_cache makes it the same instance
    assert c1 is c2
