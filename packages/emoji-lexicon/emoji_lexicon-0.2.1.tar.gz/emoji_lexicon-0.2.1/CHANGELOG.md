# Changelog

## [0.2.1] - 2026-01-09

### Fixed

-   Renamed internal module directory from `build/` to `build_data/` to avoid `.gitignore` conflicts
-   Fixed packaging issue where build-time modules were not included in source distribution

### Notes

-   No public API changes
-   This release only affects internal build-time structure

## [0.2.0] - 2026-01-09

### Highlights

-   Rebuilt build pipeline with clear separation of concerns
-   Introduced deterministic emoji merge logic
-   Added comprehensive test coverage (≈98%)
-   Guaranteed schema compatibility between generator and loader

### Added

-   Added `EmojiTestData` to represent emoji-test dataset metadata
-   Added Unicode version metadata to `EmojiCatalog`
-   Added CLDR version metadata to `EmojiCatalog`

### Improved

-   Improved catalog introspection and debugging support
-   Improved robustness by detecting multiple edge cases via tests
    (schema mismatches, cache-related paths)

### Changed

-   Renamed `EmojiTestEntry.unicode_version` to `introduced_in`

### Notes

-   No breaking API changes
-   Foundation for upcoming i18n (CLDR multi-locale) and skin tone support

## [0.1.5] - 2026-01-08

### Fixed

-   Fixed flake8 E501 (line too long) lint error

## [0.1.4] - 2026-01-08

### Improved

-   Improved `.search()` / `.find()` with token-based AND logic and relevance ranking
-   Documented search behavior and ranking rules in README

## [0.1.3] - 2026-01-07

### Improved

-   Improved search to use inverted index

## [0.1.2] - 2026-01-06

### Added

-   Added `EmojiCatalog.find()` as a user-facing alias of `search()`
-   Added `EmojiCatalog.get_all()` to retrieve all emojis as an immutable tuple
-   Added `EmojiCatalog.groups()` and `subgroups()` helpers
-   Added `EmojiCatalog.normalize_query()` for consistent query normalization
-   Added `__str__` and `__repr__` to `EmojiCatalog` for better introspection

### Improved

-   Improved search normalization (case-insensitive, `:smile:` style support)
-   Improved API ergonomics for CLI / IME / picker use cases
-   Improved README with clearer usage examples and API documentation

### Testing

-   Added comprehensive API tests for lookup, search, groups, and helpers
-   Enabled Codecov coverage reporting via GitHub Actions

### Notes

-   API is now considered stable for `0.1.x`
-   Performance optimizations are planned for future releases

## [0.1.1] - 2026-01-06

### Added

-   Added `.search()` method for partial matching by short name, alias, or tag
-   Added group and subgroup metadata support
-   Added basic public API via `emoji_lexicon.get_catalog()`

### Improved

-   Improved internal indexing for aliases and tags
-   Improved documentation and README badges
-   Improved test coverage and CI reliability

### Fixed

-   Fixed query handling edge cases
-   Fixed minor type annotation issues

## [0.1.0] - 2026-01-05

### Added

-   Initial public release 🎉
-   Build-time generated emoji catalog based on:
    -   Unicode `emoji-test.txt`
    -   CLDR annotations (aliases and tags)
-   Fast runtime lookup by:
    -   short name
    -   alias
    -   emoji character
-   Immutable `EmojiCatalog` design
-   Typed `Emoji` model
-   Python 3.12+ support

### Notes

-   This release establishes the core data model and build pipeline
-   API expected to evolve during `0.1.x`
