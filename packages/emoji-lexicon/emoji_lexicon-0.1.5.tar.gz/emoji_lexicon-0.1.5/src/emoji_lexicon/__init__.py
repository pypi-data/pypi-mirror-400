# src/emoji_lexicon/__init__.py

from .api import get_catalog
from .models.emoji import Emoji

__all__ = [
    "get_catalog",
    "Emoji",
]
