# src/emoji_lexicon/api.py

from __future__ import annotations

from functools import lru_cache

from .models.catalog import EmojiCatalog


@lru_cache(maxsize=1)
def get_catalog() -> EmojiCatalog:
    """
    Get the default emoji catalog.

    The catalog is loaded once and cached for the lifetime
    of the process.
    """
    return EmojiCatalog.load()
