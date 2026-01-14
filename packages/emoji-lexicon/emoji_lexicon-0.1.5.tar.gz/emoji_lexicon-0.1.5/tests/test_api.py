# tests/test_api.py
# type: ignore

from emoji_lexicon import Emoji, get_catalog


def test_get_catalog_basic():
    catalog = get_catalog()

    assert len(catalog) > 0


def test_basic_lookup():
    catalog = get_catalog()

    emoji = catalog.get("smile")
    assert emoji is not None
    assert isinstance(emoji.char, str)

    same = catalog.get_by_char(emoji.char)
    assert same == emoji


def test_get_by_id():
    catalog = get_catalog()
    emoji = catalog.get("smile")
    same = catalog.get_by_id(emoji.id)

    assert same == emoji


def test_search_smile():
    catalog = get_catalog()
    results = catalog.search("smile")

    assert isinstance(results, tuple)
    assert len(results) > 0


def test_groups_and_subgroups():
    catalog = get_catalog()
    assert "Smileys & Emotion" in catalog.groups()
    assert "face-smiling" in catalog.subgroups()


def test_emoji_char():
    catalog = get_catalog()
    emoji = catalog.get("smile")
    assert "😀" == str(emoji)


def test_emoji_repr():
    catalog = get_catalog()
    emoji = catalog.get("smile")
    assert "Emoji(char='😀', short_name='grinning_face')" == repr(emoji)


def test_catalog_str():
    catalog = get_catalog()
    assert "" == str(catalog)


def test_catalog_repr():
    catalog = get_catalog()
    assert (
        f"<EmojiCatalog size={len(catalog)!r}, groups={len(catalog.groups())!r}>"
        == repr(catalog)
    )


def test_normalize_query():
    catalog = get_catalog()
    assert "smile" == catalog.normalize_query(":smile:")


def test_get_all():
    catalog = get_catalog()
    all_emojis = catalog.get_all()

    assert isinstance(all_emojis, tuple)
    assert len(all_emojis) == len(catalog)

    assert all(isinstance(e, Emoji) for e in all_emojis)
    assert all(hasattr(e, "char") for e in all_emojis)


def test_find_smile():
    catalog = get_catalog()
    results = catalog.find("smile")

    assert isinstance(results, tuple)
    assert len(results) > 0
