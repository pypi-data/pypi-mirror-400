"""FHL Bible API Client - A Python client for the Faith, Hope, Love Bible API.

This package provides a simple and intuitive interface for querying Bible verses
from the Taiwan-based Faith, Hope, Love (FHL) Bible API.

Copyright Notice:
    All Bible content is provided by 信望愛資訊中心 (Faith, Hope, Love Information Center).
    Website: https://www.fhl.net/
    Bible API: https://bible.fhl.net/

    Users must comply with FHL's terms of service and respect the copyright of
    individual Bible translations. The content is primarily intended for
    non-commercial, educational, and ministry purposes.

    版權聲明：
    所有聖經內容由信望愛資訊中心提供。使用時請遵守信望愛的服務條款
    以及各譯本的版權規定。內容主要供非商業、教育及宗教服事使用。

Example:
    >>> from fhl_bible_api import FHLBibleClient
    >>> client = FHLBibleClient()
    >>> response = client.get_verse(book_id=1, chapter=1, verse=1)
    >>> print(response.records[0].text)
    起初,神創造天地。
"""

__version__ = "0.1.0"

from .client import FHLBibleClient
from .constants import ALL_BOOKS, BIBLE_VERSIONS
from .exceptions import (
    APIConnectionError,
    APIResponseError,
    FHLBibleAPIError,
    InvalidBookError,
    InvalidChapterError,
    InvalidVerseError,
    InvalidVersionError,
)
from .models import (
    BibleQueryResponse,
    BibleReference,
    BibleVerse,
    ParsingResponse,
    WordParsing,
)

__all__ = [
    "FHLBibleClient",
    "BibleQueryResponse",
    "BibleReference",
    "BibleVerse",
    "ParsingResponse",
    "WordParsing",
    "FHLBibleAPIError",
    "InvalidBookError",
    "InvalidChapterError",
    "InvalidVerseError",
    "InvalidVersionError",
    "APIConnectionError",
    "APIResponseError",
    "ALL_BOOKS",
    "BIBLE_VERSIONS",
]
