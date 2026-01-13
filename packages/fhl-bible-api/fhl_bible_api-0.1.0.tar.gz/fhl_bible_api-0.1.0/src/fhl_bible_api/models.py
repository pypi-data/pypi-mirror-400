"""Data models for FHL Bible API."""

from dataclasses import dataclass
from typing import Any


@dataclass
class BibleVerse:
    """Represents a single Bible verse."""

    bid: int  # Book ID
    english_abbr: str  # English abbreviation (e.g., "Gen")
    chinese_abbr: str  # Chinese abbreviation (e.g., "創")
    chapter: int  # Chapter number
    verse: int  # Verse number
    text: str  # Bible text content
    strong_numbers: list[str] | None = None  # Strong's numbers if requested

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self.chinese_abbr} {self.chapter}:{self.verse} - {self.text}"

    def get_reference(self, use_english: bool = False) -> str:
        """Get the verse reference.

        Args:
            use_english: If True, use English abbreviation; otherwise Chinese

        Returns:
            Formatted reference string (e.g., "創 1:1" or "Gen 1:1")
        """
        abbr = self.english_abbr if use_english else self.chinese_abbr
        return f"{abbr} {self.chapter}:{self.verse}"


@dataclass
class BibleReference:
    """Represents a reference to adjacent Bible verses."""

    bid: int
    chinese_abbr: str
    english_abbr: str
    chapter: int
    verse: int

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self.chinese_abbr} {self.chapter}:{self.verse}"


@dataclass
class BibleQueryResponse:
    """Response from Bible verse query."""

    status: str  # "success" or "error"
    version: str  # Bible version code
    record_count: int  # Number of verses returned
    records: list[BibleVerse]  # List of verse records
    prev_verse: BibleReference | None = None  # Previous verse reference
    next_verse: BibleReference | None = None  # Next verse reference
    error_message: str | None = None  # Error message if status is "error"
    raw_response: dict[str, Any] | None = None  # Raw API response

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        if self.status != "success":
            return f"Error: {self.error_message}"

        verses_text = "\n".join(str(verse) for verse in self.records)
        return f"Version: {self.version}\n{verses_text}"


@dataclass
class WordParsing:
    """Represents word parsing information (原文字彙分析)."""

    id: int  # Absolute verse ID
    bid: int  # Book ID
    english_abbr: str  # English abbreviation
    chinese_abbr: str  # Chinese abbreviation
    chapter: int  # Chapter number
    verse: int  # Verse number
    word_id: int  # Word sequence number (wid)
    word: str  # Original text word
    strong_number: str | None = None  # Strong's number (sn)
    part_of_speech: str | None = None  # Part of speech (pro)
    word_form: str | None = None  # Word form analysis (wform)
    original_form: str | None = None  # Original/base form (orig)
    explanation: str | None = None  # Chinese explanation (exp)
    remark: str | None = None  # Additional notes
    full_name: str | None = None  # Full Chinese book name (chinesef)

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        parts = [f"{self.chinese_abbr} {self.chapter}:{self.verse}"]
        if self.word_id > 0:
            parts.append(f"字序 {self.word_id}: {self.word}")
            if self.strong_number:
                parts.append(f"[{self.strong_number}]")
        else:
            # wid=0 represents full verse parsing
            parts.append(f"原文: {self.word}")
        return " ".join(parts)


@dataclass
class ParsingResponse:
    """Response from word parsing query."""

    status: str  # "success" or "error"
    record_count: int  # Number of parsing records returned
    testament: int | None = None  # 0=New Testament, 1=Old Testament (N field)
    records: list[WordParsing] = None  # List of parsing records
    prev_verse: BibleReference | None = None  # Previous verse reference
    next_verse: BibleReference | None = None  # Next verse reference
    error_message: str | None = None  # Error message if status is "error"
    raw_response: dict[str, Any] | None = None  # Raw API response

    def __post_init__(self) -> None:
        """Initialize records list if None."""
        if self.records is None:
            self.records = []

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        if self.status != "success":
            return f"Error: {self.error_message}"

        testament_str = "新約" if self.testament == 0 else "舊約" if self.testament == 1 else "未知"
        parsing_text = "\n".join(str(word) for word in self.records)
        return f"Testament: {testament_str}\nRecord Count: {self.record_count}\n{parsing_text}"
