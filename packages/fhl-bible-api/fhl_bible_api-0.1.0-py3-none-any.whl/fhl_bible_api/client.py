"""FHL Bible API Client for querying Bible verses."""

from typing import Any
from urllib.parse import urlencode

import httpx

from .constants import (
    ALL_BOOKS,
    API_BASE_URL,
    API_PARSING_ENDPOINT,
    API_QUERY_ENDPOINT,
    BIBLE_VERSIONS,
    DEFAULT_VERSION,
)
from .exceptions import (
    APIConnectionError,
    APIResponseError,
    InvalidBookError,
    InvalidVersionError,
)
from .models import BibleQueryResponse, BibleReference, BibleVerse, ParsingResponse, WordParsing


class FHLBibleClient:
    """Client for interacting with the FHL Bible API.

    This client provides methods to query Bible verses from the
    Taiwan-based Faith, Hope, Love (FHL) Bible API.

    Attributes:
        base_url: The base URL for the API
        timeout: Request timeout in seconds
        client: HTTP client instance
    """

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        """Initialize the FHL Bible API client.

        Args:
            base_url: Base URL for the API (default: https://bible.fhl.net/api)
            timeout: Request timeout in seconds (default: 30.0)
            client: Optional httpx.Client instance for custom configuration
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = client or httpx.Client(timeout=timeout)
        self._owns_client = client is None

    def __enter__(self) -> "FHLBibleClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client if owned by this instance."""
        if self._owns_client and self._client:
            self._client.close()

    def _validate_book_id(self, book_id: int) -> None:
        """Validate that the book ID is valid.

        Args:
            book_id: Book ID to validate

        Raises:
            InvalidBookError: If the book ID is not valid
        """
        if book_id not in ALL_BOOKS:
            raise InvalidBookError(
                f"Invalid book ID: {book_id}. "
                f"Valid range: 1-66 (Bible), 101-115 (Apocrypha), 201-217 (Apostolic Fathers)"
            )

    def _validate_version(self, version: str) -> None:
        """Validate that the Bible version is valid.

        Args:
            version: Version code to validate

        Raises:
            InvalidVersionError: If the version is not valid
        """
        if version not in BIBLE_VERSIONS:
            raise InvalidVersionError(
                f"Invalid version: {version}. "
                f"Use get_available_versions() to see all available versions."
            )

    def _parse_response(self, data: dict[str, Any]) -> BibleQueryResponse:
        """Parse the API response into a BibleQueryResponse object.

        Args:
            data: Raw API response data

        Returns:
            Parsed BibleQueryResponse object
        """
        status = data.get("status", "unknown")

        if status != "success":
            return BibleQueryResponse(
                status=status,
                version=data.get("version", ""),
                record_count=0,
                records=[],
                error_message=f"API returned status: {status}",
                raw_response=data,
            )

        records = []
        for record in data.get("record", []):
            verse = BibleVerse(
                bid=record.get("bid", 0),
                english_abbr=record.get("engs", ""),
                chinese_abbr=record.get("chineses", ""),
                chapter=record.get("chap", 0),
                verse=record.get("sec", 0),
                text=record.get("bible_text", ""),
                strong_numbers=record.get("strong", []) if "strong" in record else None,
            )
            records.append(verse)

        prev_verse = None
        if "prev" in data and data["prev"]:
            prev_data = data["prev"]
            prev_verse = BibleReference(
                bid=prev_data.get("bid", 0),
                chinese_abbr=prev_data.get("chineses", ""),
                english_abbr=prev_data.get("engs", ""),
                chapter=prev_data.get("chap", 0),
                verse=prev_data.get("sec", 0),
            )

        next_verse = None
        if "next" in data and data["next"]:
            next_data = data["next"]
            next_verse = BibleReference(
                bid=next_data.get("bid", 0),
                chinese_abbr=next_data.get("chineses", ""),
                english_abbr=next_data.get("engs", ""),
                chapter=next_data.get("chap", 0),
                verse=next_data.get("sec", 0),
            )

        return BibleQueryResponse(
            status=status,
            version=data.get("version", ""),
            record_count=data.get("record_count", len(records)),
            records=records,
            prev_verse=prev_verse,
            next_verse=next_verse,
            raw_response=data,
        )

    def get_verse(
        self,
        book_id: int,
        chapter: int,
        verse: int,
        version: str = DEFAULT_VERSION,
        include_strong: bool = False,
        simplified: bool = False,
    ) -> BibleQueryResponse:
        """Get a specific Bible verse.

        Args:
            book_id: Book ID (1-66 for Bible, 101-115 for Apocrypha, 201-217 for Apostolic Fathers)
            chapter: Chapter number
            verse: Verse number
            version: Bible version code (default: "unv" - 和合本)
            include_strong: Include Strong's numbers (default: False)
            simplified: Use simplified Chinese (default: False)

        Returns:
            BibleQueryResponse containing the verse data

        Raises:
            InvalidBookError: If book_id is invalid
            InvalidVersionError: If version is invalid
            APIConnectionError: If unable to connect to API
            APIResponseError: If API returns invalid response
        """
        self._validate_book_id(book_id)
        self._validate_version(version)

        params = {
            "bid": book_id,
            "chap": chapter,
            "sec": verse,
            "version": version,
            "strong": 1 if include_strong else 0,
            "gb": 1 if simplified else 0,
        }

        url = f"{self.base_url}{API_QUERY_ENDPOINT}?{urlencode(params)}"

        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIConnectionError(f"HTTP error occurred: {e}") from e
        except httpx.RequestError as e:
            raise APIConnectionError(f"Request error occurred: {e}") from e

        try:
            data = response.json()
        except Exception as e:
            raise APIResponseError(f"Failed to parse API response: {e}") from e

        return self._parse_response(data)

    def _parse_parsing_response(self, data: dict[str, Any]) -> ParsingResponse:
        """Parse the parsing API response into a ParsingResponse object.

        Args:
            data: Raw API response data

        Returns:
            Parsed ParsingResponse object
        """
        status = data.get("status", "unknown")

        if status != "success":
            return ParsingResponse(
                status=status,
                record_count=0,
                records=[],
                error_message=f"API returned status: {status}",
                raw_response=data,
            )

        records = []
        for record in data.get("record", []):
            parsing = WordParsing(
                id=record.get("id", 0),
                bid=record.get("bid", 0),
                english_abbr=record.get("engs", ""),
                chinese_abbr=record.get("chineses", ""),
                chapter=record.get("chap", 0),
                verse=record.get("sec", 0),
                word_id=record.get("wid", 0),
                word=record.get("word", ""),
                strong_number=record.get("sn") if "sn" in record else None,
                part_of_speech=record.get("pro") if "pro" in record else None,
                word_form=record.get("wform") if "wform" in record else None,
                original_form=record.get("orig") if "orig" in record else None,
                explanation=record.get("exp") if "exp" in record else None,
                remark=record.get("remark") if "remark" in record else None,
                full_name=record.get("chinesef") if "chinesef" in record else None,
            )
            records.append(parsing)

        prev_verse = None
        if "prev" in data and data["prev"]:
            prev_data = data["prev"]
            prev_verse = BibleReference(
                bid=prev_data.get("bid", 0),
                chinese_abbr=prev_data.get("chineses", ""),
                english_abbr=prev_data.get("engs", ""),
                chapter=prev_data.get("chap", 0),
                verse=prev_data.get("sec", 0),
            )

        next_verse = None
        if "next" in data and data["next"]:
            next_data = data["next"]
            next_verse = BibleReference(
                bid=next_data.get("bid", 0),
                chinese_abbr=next_data.get("chineses", ""),
                english_abbr=next_data.get("engs", ""),
                chapter=next_data.get("chap", 0),
                verse=next_data.get("sec", 0),
            )

        return ParsingResponse(
            status=status,
            record_count=data.get("record_count", len(records)),
            testament=data.get("N") if "N" in data else None,
            records=records,
            prev_verse=prev_verse,
            next_verse=next_verse,
            raw_response=data,
        )

    def get_word_parsing(
        self,
        book_id: int,
        chapter: int = 0,
        verse: int = 0,
        simplified: bool = False,
    ) -> ParsingResponse:
        """Get word parsing (原文字彙分析) for a Bible verse.

        This method retrieves detailed word-level analysis including:
        - Original language text (Greek/Hebrew)
        - Strong's numbers
        - Part of speech
        - Word form analysis
        - Chinese explanations

        Args:
            book_id: Book ID (1-66 for Bible)
            chapter: Chapter number (default: 0 for all)
            verse: Verse number (default: 0 for all verses in chapter)
            simplified: Use simplified Chinese (default: False)

        Returns:
            ParsingResponse containing word parsing data

        Raises:
            InvalidBookError: If book_id is invalid
            APIConnectionError: If unable to connect to API
            APIResponseError: If API returns invalid response

        Example:
            >>> client = FHLBibleClient()
            >>> response = client.get_word_parsing(book_id=43, chapter=3, verse=16)
            >>> for word in response.records:
            ...     print(f"{word.word} [{word.strong_number}]: {word.explanation}")
        """
        self._validate_book_id(book_id)

        params = {
            "bid": book_id,
            "chap": chapter,
            "sec": verse,
            "gb": 1 if simplified else 0,
        }

        url = f"{self.base_url}{API_PARSING_ENDPOINT}?{urlencode(params)}"

        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIConnectionError(f"HTTP error occurred: {e}") from e
        except httpx.RequestError as e:
            raise APIConnectionError(f"Request error occurred: {e}") from e

        try:
            data = response.json()
        except Exception as e:
            raise APIResponseError(f"Failed to parse API response: {e}") from e

        return self._parse_parsing_response(data)

    def get_chapter(
        self,
        book_id: int,
        chapter: int,
        version: str = DEFAULT_VERSION,
        include_strong: bool = False,
        simplified: bool = False,
    ) -> list[BibleQueryResponse]:
        """Get all verses from a specific chapter.

        Note: This method makes multiple API calls, one per verse.
        The FHL API doesn't provide a direct endpoint for full chapters.

        Args:
            book_id: Book ID
            chapter: Chapter number
            version: Bible version code
            include_strong: Include Strong's numbers
            simplified: Use simplified Chinese

        Returns:
            List of BibleQueryResponse objects, one per verse
        """
        results = []
        verse_num = 1
        max_attempts = 200  # Safety limit

        while verse_num <= max_attempts:
            try:
                response = self.get_verse(
                    book_id=book_id,
                    chapter=chapter,
                    verse=verse_num,
                    version=version,
                    include_strong=include_strong,
                    simplified=simplified,
                )

                if response.status == "success" and response.records:
                    results.append(response)
                    verse_num += 1
                else:
                    # No more verses in this chapter
                    break
            except Exception:
                # End of chapter or error
                break

        return results

    def get_book_info(self, book_id: int) -> dict[str, str]:
        """Get information about a Bible book.

        Args:
            book_id: Book ID

        Returns:
            Dictionary with book information (chinese, english, full_name)

        Raises:
            InvalidBookError: If book_id is invalid
        """
        self._validate_book_id(book_id)
        return ALL_BOOKS[book_id].copy()

    def get_available_versions(self) -> dict[str, str]:
        """Get all available Bible versions.

        Returns:
            Dictionary mapping version codes to version names
        """
        return BIBLE_VERSIONS.copy()

    def get_all_books(self) -> dict[int, dict[str, str]]:
        """Get all available books.

        Returns:
            Dictionary mapping book IDs to book information
        """
        return ALL_BOOKS.copy()

    def search_book_by_name(self, name: str) -> list[tuple[int, dict[str, str]]]:
        """Search for books by name (supports Chinese or English).

        Args:
            name: Search term (can be Chinese abbreviation, English abbreviation, or full name)

        Returns:
            List of tuples (book_id, book_info) matching the search term
        """
        name_lower = name.lower()
        results = []

        for book_id, info in ALL_BOOKS.items():
            if (
                name in info["chinese"]
                or name_lower in info["english"].lower()
                or name in info["full_name"]
            ):
                results.append((book_id, info.copy()))

        return results
