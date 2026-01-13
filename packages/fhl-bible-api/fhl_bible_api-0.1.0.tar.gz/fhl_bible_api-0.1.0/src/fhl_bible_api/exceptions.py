"""Custom exceptions for FHL Bible API."""


class FHLBibleAPIError(Exception):
    """Base exception for FHL Bible API errors."""


class InvalidBookError(FHLBibleAPIError):
    """Raised when an invalid book ID is provided."""


class InvalidChapterError(FHLBibleAPIError):
    """Raised when an invalid chapter number is provided."""


class InvalidVerseError(FHLBibleAPIError):
    """Raised when an invalid verse number is provided."""


class InvalidVersionError(FHLBibleAPIError):
    """Raised when an invalid Bible version is provided."""


class APIConnectionError(FHLBibleAPIError):
    """Raised when unable to connect to the API."""


class APIResponseError(FHLBibleAPIError):
    """Raised when the API returns an unexpected response."""
