# emoji-lexicon

![Tests](https://github.com/kimikato/emoji-lexicon/actions/workflows/tests.yml/badge.svg?branch=main)
[![coverage](https://img.shields.io/codecov/c/github/kimikato/emoji-lexicon/main?label=coverage&logo=codecov)](https://codecov.io/gh/kimikato/emoji-lexicon)
[![PyPI version](https://img.shields.io/pypi/v/emoji-lexicon.svg)](https://pypi.org/project/emoji-lexicon/)
[![Python](https://img.shields.io/pypi/pyversions/emoji-lexicon.svg)](https://pypi.org/project/emoji-lexicon/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🚀 **emoji-lexicon** is a fast, build-time generated emoji lexicon for Python,
powered by Unicode emoji-test and CLDR annotations.

## Features

-   Fast emoji lookup by short name, alias, or tag
-   Designed for CLI, IME, and dictionary tools
-   Unicode / CLDR based canonical data
-   Build-time normalization, runtime zero-cost lookup
-   Optional gemoji-compatible export

## Requirements

-   Python 3.12+

## Installation

```bash
pip install emoji-lexicon
```

## Usage

Basic usage:

```python
from emoji_lexicon import get_catalog

catalog = get_catalog()
```

### `.get()`, `get_by_char()`, `get_all()`

```python
# lookup by short name or alias
catalog.get("smile")
# -> Emoji | None

# Slack / gemoji style
catalog.get(":smile:")

# lookup by emoji character
catalog.get_by_char("😁")
# -> Emoji | None

# get all emojis
catalog.get_all()
```

### `.search()` , `.find()`

```python
# partial match (short_name / alias / tag)
catalog.search("happy")
# -> tuple[Emoji, ...]

# alias of .search()
catalog.find("happy")
# -> tuple[Emoji, ...]
```

`.search()` and `.find()` perform partial matching and return multiple emojis.
`.find()` is a user-facing alias of `.search()`.

### `.groups()`, `.subgroups()`

```python
from emoji_lexicon import get_catalog
catalog = get_catalog()

# available emoji groups
catalog.groups()

# available emoji subgroups
catalog.subgroups()
```

### Misc

```python
# total emoji count
len(catalog)

# iterator
for emoji in catalog:
	print(emoji.char, emoji.short_name)
```

Application examples:

-   Categories UI
-   IME candidate narrowing down
-   emoji picker

## Search behavior

The `.search()` and `.find()` methods perform token-based emoji search.

Search rules:

-   Case-insensitive
-   Supports Slack / gemoji style queries (e.g. `:smile`)
-   Space-separated tokens are combined using AND logic
-   Results are ranked by relevance

Matching priority (high -> low):

1. Exact short name match
2. Exact alias match
3. Exact tag match
4. Prefix match (only for tokens with 3+ characters)

Ranking is deterministic and stable (score-based, then emoji ID)

Example:

```python
catalog.search("smile")
catalog.search("smile face")
catalog.search(":smile:")
```

Notes:

-   Prefix matching is disabled for very short tokens to reduce noise.
-   Result order is deterministic and stable.

## Design philosophy

-   zero-cost at runtime
-   immutable catalog
-   Pythonic & typed

## License

MIT License
© 2026 Kiminori Kato
