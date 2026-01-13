# FHL Bible API Client

[![Python Version](https://img.shields.io/pypi/pyversions/fhl-bible-api)](https://pypi.org/project/fhl-bible-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for the [Faith, Hope, Love (FHL) Bible API](https://bible.fhl.net/), a comprehensive Chinese Bible resource provided by the Taiwan Bible Society.

台灣信望愛聖經 API 的 Python 客戶端函式庫，提供簡單易用的介面來查詢聖經經文。

## Features

- 🔍 Query Bible verses by book, chapter, and verse
- 📚 Support for 66 canonical books, Apocrypha (101-115), and Apostolic Fathers (201-217)
- 🌏 Multiple Bible versions (Chinese, English, and other languages)
- 📖 Strong's concordance numbers support
- 🔄 Simplified and Traditional Chinese support
- ✨ Type hints and full typing support
- 🧪 Comprehensive unit tests
- 📦 Zero heavy dependencies (only httpx)

## Installation

```bash
pip install fhl-bible-api
```

Or using uv:

```bash
uv add fhl-bible-api
```

## Quick Start

```python
from fhl_bible_api import FHLBibleClient

# Create a client instance
client = FHLBibleClient()

# Get a specific verse (Genesis 1:1)
response = client.get_verse(book_id=1, chapter=1, verse=1)
print(response.records[0].text)
# Output: 起初,神創造天地。

# Get verse with Strong's numbers
response = client.get_verse(
    book_id=43,  # John
    chapter=3,
    verse=16,
    include_strong=True
)

# Use different Bible version (KJV)
response = client.get_verse(
    book_id=1,
    chapter=1,
    verse=1,
    version="kjv"
)

# Get all verses from a chapter
chapter_verses = client.get_chapter(book_id=1, chapter=1)
for verse_response in chapter_verses:
    print(verse_response.records[0].text)

# Clean up
client.close()
```

## Using Context Manager

```python
from fhl_bible_api import FHLBibleClient

# Automatically handles resource cleanup
with FHLBibleClient() as client:
    response = client.get_verse(book_id=1, chapter=1, verse=1)
    print(response.records[0].text)
```

## Advanced Usage

### Search for Books

```python
# Search by Chinese abbreviation
results = client.search_book_by_name("創")

# Search by English abbreviation
results = client.search_book_by_name("Gen")

# Search by full name
results = client.search_book_by_name("創世記")

for book_id, book_info in results:
    print(f"{book_id}: {book_info['full_name']}")
```

### Get Book Information

```python
# Get information about a specific book
info = client.get_book_info(1)
print(info)
# Output: {'chinese': '創', 'english': 'Gen', 'full_name': '創世記'}
```

### List Available Versions

```python
# Get all available Bible versions
versions = client.get_available_versions()
for code, name in versions.items():
    print(f"{code}: {name}")
```

### Access Verse Details

```python
response = client.get_verse(book_id=1, chapter=1, verse=1)
verse = response.records[0]

print(f"Book ID: {verse.bid}")
print(f"Chapter: {verse.chapter}")
print(f"Verse: {verse.verse}")
print(f"Text: {verse.text}")
print(f"Reference: {verse.get_reference()}")  # 創 1:1
print(f"Reference (EN): {verse.get_reference(use_english=True)}")  # Gen 1:1
```

### Word Parsing (字彙分析)

Get detailed word-level analysis including original language text, Strong's numbers, and morphology:

```python
# Get word parsing for John 3:16
response = client.get_word_parsing(book_id=43, chapter=3, verse=16)

print(f"Testament: {'New Testament' if response.testament == 0 else 'Old Testament'}")

for word in response.records:
    if word.word_id > 0:  # Skip the summary record (wid=0)
        print(f"\nWord #{word.word_id}: {word.word}")
        print(f"  Strong's Number: {word.strong_number}")
        print(f"  Part of Speech: {word.part_of_speech}")
        print(f"  Original Form: {word.original_form}")
        print(f"  Explanation: {word.explanation}")

# Output example:
# Word #1: Οὕτως
#   Strong's Number: 3779
#   Part of Speech: Adv
#   Original Form: οὕτω(ς)
#   Explanation: 如此, 這樣
```

## Supported Bible Versions

### Chinese Versions
- `unv` - 和合本 (Union Version) - Default
- `rcuv` - 和合本2010
- `tcv95` - 現代中文譯本1995版
- `tcv2019` - 現代中文譯本2019版
- `ncv` - 新譯本
- And many more...

### English Versions
- `kjv` - King James Version
- `esv` - English Standard Version
- `asv` - American Standard Version
- `web` - World English Bible
- And more...

### Other Languages
- Korean, Japanese, Vietnamese, Russian, Indonesian, Tibetan
- Indigenous Taiwan languages (Bunun, Amis, Atayal, etc.)

Use `client.get_available_versions()` to see the complete list.

## Book IDs

- **1-39**: Old Testament (創世記 to 瑪拉基書)
- **40-66**: New Testament (馬太福音 to 啟示錄)
- **101-115**: Apocrypha (次經)
- **201-217**: Apostolic Fathers (使徒教父著作)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/arick/fhl-bible-api.git
cd fhl-bible-api

# Install dependencies with uv
uv sync --all-extras

# Or with pip
pip install -e ".[dev,test]"
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=fhl_bible_api --cov-report=html

# Run specific test file
uv run pytest tests/test_client.py
```

### Code Quality

```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking with mypy
uv run mypy src/fhl_bible_api
```

## API Response Structure

```python
BibleQueryResponse(
    status='success',
    version='unv',
    record_count=1,
    records=[
        BibleVerse(
            bid=1,
            english_abbr='Gen',
            chinese_abbr='創',
            chapter=1,
            verse=1,
            text='起初,神創造天地。',
            strong_numbers=None
        )
    ],
    prev_verse=BibleReference(...),
    next_verse=BibleReference(...),
    error_message=None,
    raw_response={...}
)
```

## Error Handling

```python
from fhl_bible_api import (
    FHLBibleClient,
    InvalidBookError,
    InvalidVersionError,
    APIConnectionError,
)

try:
    client = FHLBibleClient()
    response = client.get_verse(book_id=999, chapter=1, verse=1)
except InvalidBookError as e:
    print(f"Invalid book ID: {e}")
except InvalidVersionError as e:
    print(f"Invalid version: {e}")
except APIConnectionError as e:
    print(f"Connection error: {e}")
finally:
    client.close()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [信望愛資訊中心 (Faith, Hope, Love Information Center)](https://www.fhl.net/) for providing the Bible API and content
- Taiwan Bible Society (台灣聖經公會) for Bible translations
- All Bible translation publishers and copyright holders

**特別感謝**：
- 信望愛資訊中心提供聖經 API 服務
- 台灣聖經公會及各譯本出版者的翻譯工作

## Related Links

- [FHL Bible API Documentation](https://bible.fhl.net/api/)
- [FHL Website](https://bible.fhl.net/)
- [FHL Terms of Use](https://www.fhl.net/main/fhl/fhl8.html)
- [PyPI Package](https://pypi.org/project/fhl-bible-api/)
- [Copyright Notice](COPYRIGHT.md) - 詳細版權聲明- [Publishing Guide](PUBLISHING.md) - 完整發布指南
- [Quick Publishing Guide](PUBLISH_QUICK.md) - 快速發布步驟
## Copyright and Attribution

### Bible Content Copyright

All Bible content accessed through this API is provided by **信望愛資訊中心 (Faith, Hope, Love Information Center)**:

- **Website**: https://www.fhl.net/
- **Bible API**: https://bible.fhl.net/

The Bible texts, translations, and related content are copyrighted by their respective publishers and translators:
- 和合本聖經 © 聖經公會
- 現代中文譯本 © 台灣聖經公會
- 其他譯本版權歸屬其各自出版者所有

### Usage Terms

When using this library and the FHL Bible API:

1. **Attribution Required**: Always acknowledge that the Bible content is provided by 信望愛資訊中心 (FHL)
2. **Non-Commercial Use**: The content is primarily intended for non-commercial, educational, and ministry purposes
3. **Respect Copyright**: Each Bible translation has its own copyright terms that must be respected
4. **No Redistribution**: Do not redistribute the Bible content separately from its intended use through this API

### API Usage Guidelines

Please visit https://www.fhl.net/main/fhl/fhl8.html for detailed terms and conditions.

**版權聲明**：本軟體使用信望愛資訊中心提供之聖經資料。使用時請遵守以下原則：
- 註明資料來源為「信望愛資訊中心」
- 尊重各譯本之版權
- 以非商業、教育、服事為主要用途
- 不得擅自轉載或重製聖經內容

## Disclaimer

This is an **unofficial client library**. All Bible content is provided by the Faith, Hope, Love (FHL) Bible API. Users of this library are responsible for complying with FHL's terms of service and the copyright terms of individual Bible translations.

本套件為**非官方**客戶端函式庫。所有聖經內容由信望愛聖經 API 提供。使用者需自行遵守信望愛的服務條款以及各聖經譯本的版權規定。
