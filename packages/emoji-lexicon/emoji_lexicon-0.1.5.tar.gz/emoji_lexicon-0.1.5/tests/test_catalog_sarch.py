# tests/test_catalog_search.py
# type: ignore


from emoji_lexicon import Emoji, get_catalog


def test_search_empty():
    catalog = get_catalog()
    assert catalog.search("") == ()
    assert catalog.search(" ") == ()
    assert catalog.search(":") == ()


def test_search_short_token_exact_only():
    catalog = get_catalog()

    # "ok" exists as token
    exact = catalog.search("go")
    assert len(exact) > 0

    # "o" doesn't explode search volume
    short = catalog.search("g")
    print(short)
    assert short == ()


def test_search_prefix_match():
    catalog = get_catalog()

    results = catalog.search("smi")
    assert len(results) > 0

    # All contain something of "smi"
    assert all(
        "smi" in e.short_name or any("smi" in t for t in e.tags)
        for e in results
    )


def test_search_exact_always_works():
    catalog = get_catalog()

    assert len(catalog.search("ok")) > 0
    assert len(catalog.search("<3")) > 0
    assert len(catalog.search("+1")) > 0


def test_search_prefix_match():
    catalog = get_catalog()

    results = catalog.search("smi")
    assert len(results) > 0
    assert any("smile" in e.short_name for e in results)


def test_search_prefix_too_short():
    catalog = get_catalog()

    results = catalog.search("sm")
    assert results == ()


def test_search_exact_short_token():
    catalog = get_catalog()

    results = catalog.search("ok")
    # "ok" exists as token
    assert isinstance(results, tuple)


def test_search_multi_token_and():
    catalog = get_catalog()

    results = catalog.search("smile face")
    assert len(results) > 0
    for e in results:
        assert "face" in e.short_name or "face" in e.tags


def test_search_multi_token_no_match():
    catalog = get_catalog()

    results = catalog.search("smile tocket")
    assert results == ()


def test_search_result_order():
    catalog = get_catalog()

    results = catalog.search("smile")
    scores = []

    for e in results:
        score = 0
        if "smile" in e.short_name or "smile" in e.tags:
            if "smile" == e.short_name:
                score += 100
            else:
                score += 10
        scores.append(score)

    # relevance order (desc)
    assert scores == sorted(scores, reverse=True)

    def test_search_ranking_exact_first():
        catalog = get_catalog()

        results = catalog.search("smile")
        assert len(results) > 1

        # exact short_name hit should be first
        assert results[0].short_name == "grinning_face"


def test_search_ranking_alias_over_tag():
    catalog = get_catalog()

    results = catalog.search("happy")
    assert results[0].short_name == "grinning_face"
