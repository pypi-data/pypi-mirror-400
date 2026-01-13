# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-07

### Changed
- Reorganized project structure: moved example files to `examples/` directory
- Updated comprehensive verse analysis example to use proper Bible versions:
  - 原文 (bhs for OT, extracted from parsing for NT)
  - 原文直譯 (cbol)
  - 中文和合本 (unv)
  - 呂振中譯本 (lcc)
- Removed navigation section from verse analysis example for cleaner output

### Fixed
- Fixed New Testament original text display in comprehensive example
- Improved original text extraction for NT books using word parsing API

## [Unreleased]

### Added
- Word parsing (原文字彙分析) functionality via `qp.php` API
- `FHLBibleClient.get_word_parsing()` - Get detailed word-level analysis
- Support for Strong's numbers in word parsing
- Part of speech and morphology information
- Original language text (Hebrew/Greek) with word forms
- Chinese explanations for original words
- WordParsing and ParsingResponse data models
- Apocrypha verse retrieval via `qsub.php` API
- `FHLBibleClient.get_apocrypha_verse()` - Query Apocrypha verses (books 101-115)
- `FHLBibleClient.get_apocrypha_chapter()` - Get entire Apocrypha chapters
- Support for 1933年聖公會出版 version of Apocrypha
- Apostolic Fathers writings retrieval via `qaf.php` API
- `FHLBibleClient.get_apostolic_fathers_verse()` - Query Apostolic Fathers verses (books 201-217)
- `FHLBibleClient.get_apostolic_fathers_chapter()` - Get entire Apostolic Fathers chapters
- Support for 黃錫木主編《使徒教父著作》 version
- Bible commentary retrieval via `sc.php` API
- `FHLBibleClient.get_commentary()` - Query Bible commentary (books 1-66)
- Support for 信望愛站註釋 commentary
- Commentary and CommentaryResponse data models
- `v_name` field in BibleQueryResponse for version Chinese name
- 28 additional unit tests (45 tests total)
- Comprehensive examples for all new features in documentation
- Code coverage: 86%

### Planned
- Async/await support for API calls
- Batch verse retrieval optimization
- Caching mechanism for frequently accessed verses
- Additional search capabilities

## [0.1.0] - 2026-01-05

### Added
- Initial release of FHL Bible API Client
- Basic verse retrieval functionality (`get_verse`)
- Chapter retrieval functionality (`get_chapter`)
- Support for 66 canonical books
- Support for Apocrypha books (101-115)
- Support for Apostolic Fathers (201-217)
- Multiple Bible version support (Chinese, English, and other languages)
- Strong's concordance numbers support
- Simplified/Traditional Chinese support
- Book information and search functionality
- Comprehensive error handling with custom exceptions
- Type hints and full typing support
- Unit tests with 88% code coverage
- Complete documentation and examples
- MIT License

### API Endpoints
- `FHLBibleClient.get_verse()` - Get a specific verse
- `FHLBibleClient.get_chapter()` - Get all verses from a chapter
- `FHLBibleClient.get_book_info()` - Get book information
- `FHLBibleClient.get_available_versions()` - List all Bible versions
- `FHLBibleClient.get_all_books()` - List all available books
- `FHLBibleClient.search_book_by_name()` - Search for books

### Dependencies
- httpx >= 0.27.0

### Development Tools
- pytest >= 8.0.0
- pytest-cov >= 4.1.0
- ruff >= 0.8.0
- mypy >= 1.8.0

[Unreleased]: https://github.com/arick/fhl-bible-api/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/arick/fhl-bible-api/releases/tag/v0.1.0
