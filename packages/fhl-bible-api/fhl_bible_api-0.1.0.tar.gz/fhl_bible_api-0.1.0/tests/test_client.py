"""Unit tests for FHL Bible API Client."""

from unittest.mock import Mock, patch

import httpx
import pytest

from fhl_bible_api import FHLBibleClient
from fhl_bible_api.exceptions import (
    APIConnectionError,
    InvalidBookError,
    InvalidVersionError,
)


@pytest.fixture
def mock_response_data():
    """Sample API response data."""
    return {
        "status": "success",
        "record_count": 1,
        "v_name": None,
        "version": "unv",
        "proc": 0,
        "record": [
            {
                "bid": 1,
                "engs": "Gen",
                "chineses": "創",
                "chap": 1,
                "sec": 1,
                "bible_text": "起初，神創造天地。",
            }
        ],
        "prev": {"bid": 1, "chineses": "創", "engs": "Gen", "chap": 1, "sec": 1},
        "next": {"bid": 1, "chineses": "創", "engs": "Gen", "chap": 1, "sec": 2},
    }


@pytest.fixture
def client():
    """Create a test client."""
    return FHLBibleClient()


def test_client_initialization():
    """Test client initialization."""
    client = FHLBibleClient()
    assert client.base_url == "https://bible.fhl.net/api"
    assert client.timeout == 30.0
    client.close()


def test_client_custom_initialization():
    """Test client initialization with custom parameters."""
    client = FHLBibleClient(base_url="https://example.com/api", timeout=60.0)
    assert client.base_url == "https://example.com/api"
    assert client.timeout == 60.0
    client.close()


def test_context_manager():
    """Test client as context manager."""
    with FHLBibleClient() as client:
        assert client._client is not None
    # Client should be closed after context


def test_validate_book_id(client):
    """Test book ID validation."""
    # Valid book IDs
    client._validate_book_id(1)  # Genesis
    client._validate_book_id(66)  # Revelation
    client._validate_book_id(101)  # Apocrypha
    client._validate_book_id(217)  # Apostolic Fathers

    # Invalid book IDs
    with pytest.raises(InvalidBookError):
        client._validate_book_id(0)

    with pytest.raises(InvalidBookError):
        client._validate_book_id(67)

    with pytest.raises(InvalidBookError):
        client._validate_book_id(300)

    client.close()


def test_validate_version(client):
    """Test version validation."""
    # Valid versions
    client._validate_version("unv")
    client._validate_version("kjv")
    client._validate_version("esv")

    # Invalid version
    with pytest.raises(InvalidVersionError):
        client._validate_version("invalid_version")

    client.close()


def test_get_verse_success(client, mock_response_data):
    """Test successful verse retrieval."""
    with patch.object(client._client, "get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        response = client.get_verse(book_id=1, chapter=1, verse=1)

        assert response.status == "success"
        assert response.version == "unv"
        assert response.record_count == 1
        assert len(response.records) == 1

        verse = response.records[0]
        assert verse.bid == 1
        assert verse.chinese_abbr == "創"
        assert verse.english_abbr == "Gen"
        assert verse.chapter == 1
        assert verse.verse == 1
        assert verse.text == "起初，神創造天地。"

        assert response.prev_verse is not None
        assert response.next_verse is not None

    client.close()


def test_get_verse_with_options(client, mock_response_data):
    """Test verse retrieval with options."""
    with patch.object(client._client, "get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client.get_verse(
            book_id=1, chapter=1, verse=1, version="kjv", include_strong=True, simplified=True
        )

        # Verify the URL contains correct parameters
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert "version=kjv" in url
        assert "strong=1" in url
        assert "gb=1" in url

    client.close()


def test_get_verse_invalid_book_id(client):
    """Test verse retrieval with invalid book ID."""
    with pytest.raises(InvalidBookError):
        client.get_verse(book_id=999, chapter=1, verse=1)

    client.close()


def test_get_verse_invalid_version(client):
    """Test verse retrieval with invalid version."""
    with pytest.raises(InvalidVersionError):
        client.get_verse(book_id=1, chapter=1, verse=1, version="invalid")

    client.close()


def test_get_verse_connection_error(client):
    """Test verse retrieval with connection error."""
    with patch.object(client._client, "get") as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed", request=Mock())

        with pytest.raises(APIConnectionError):
            client.get_verse(book_id=1, chapter=1, verse=1)

    client.close()


def test_get_verse_http_error(client):
    """Test verse retrieval with HTTP error."""
    with patch.object(client._client, "get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=Mock()
        )
        mock_get.return_value = mock_response

        with pytest.raises(APIConnectionError):
            client.get_verse(book_id=1, chapter=1, verse=1)

    client.close()


def test_get_book_info(client):
    """Test getting book information."""
    info = client.get_book_info(1)
    assert info["chinese"] == "創"
    assert info["english"] == "Gen"
    assert info["full_name"] == "創世記"

    with pytest.raises(InvalidBookError):
        client.get_book_info(999)

    client.close()


def test_get_available_versions(client):
    """Test getting available versions."""
    versions = client.get_available_versions()
    assert "unv" in versions
    assert "kjv" in versions
    assert "esv" in versions
    assert versions["unv"] == "和合本"

    client.close()


def test_get_all_books(client):
    """Test getting all books."""
    books = client.get_all_books()
    assert 1 in books  # Genesis
    assert 66 in books  # Revelation
    assert 101 in books  # Apocrypha
    assert 217 in books  # Apostolic Fathers

    client.close()


def test_search_book_by_name(client):
    """Test searching books by name."""
    # Search by Chinese abbreviation
    results = client.search_book_by_name("創")
    assert len(results) > 0
    assert results[0][0] == 1

    # Search by English abbreviation
    results = client.search_book_by_name("Gen")
    assert len(results) > 0
    assert results[0][0] == 1

    # Search by full name
    results = client.search_book_by_name("創世記")
    assert len(results) > 0
    assert results[0][0] == 1

    # No results
    results = client.search_book_by_name("不存在的書")
    assert len(results) == 0

    client.close()


def test_bible_verse_str():
    """Test BibleVerse string representation."""
    from fhl_bible_api.models import BibleVerse

    verse = BibleVerse(
        bid=1,
        english_abbr="Gen",
        chinese_abbr="創",
        chapter=1,
        verse=1,
        text="起初，神創造天地。",
    )

    assert str(verse) == "創 1:1 - 起初，神創造天地。"
    assert verse.get_reference() == "創 1:1"
    assert verse.get_reference(use_english=True) == "Gen 1:1"


def test_bible_query_response_str():
    """Test BibleQueryResponse string representation."""
    from fhl_bible_api.models import BibleQueryResponse, BibleVerse

    verse = BibleVerse(
        bid=1,
        english_abbr="Gen",
        chinese_abbr="創",
        chapter=1,
        verse=1,
        text="起初，神創造天地。",
    )

    response = BibleQueryResponse(status="success", version="unv", record_count=1, records=[verse])

    output = str(response)
    assert "Version: unv" in output
    assert "起初，神創造天地。" in output

@pytest.fixture
def mock_parsing_response_data():
    """Sample word parsing API response data."""
    return {
        "status": "success",
        "record_count": 3,
        "N": 0,  # 0=NT, 1=OT
        "record": [
            {
                "id": 1,
                "bid": 43,
                "engs": "John",
                "chineses": "約",
                "chap": 3,
                "sec": 16,
                "wid": 0,
                "word": "Οὕτως",
                "chinesef": "約翰福音",
            },
            {
                "id": 2,
                "bid": 43,
                "engs": "John",
                "chineses": "約",
                "chap": 3,
                "sec": 16,
                "wid": 1,
                "word": "Οὕτως",
                "sn": "3779",
                "pro": "Adv",
                "wform": "Adv",
                "orig": "οὕτω(ς)",
                "exp": "如此, 這樣",
                "remark": "",
            },
            {
                "id": 3,
                "bid": 43,
                "engs": "John",
                "chineses": "約",
                "chap": 3,
                "sec": 16,
                "wid": 2,
                "word": "γὰρ",
                "sn": "1063",
                "pro": "Conj",
                "wform": "Conj",
                "orig": "γάρ",
                "exp": "因為",
                "remark": "",
            },
        ],
        "prev": {"bid": 43, "chineses": "約", "engs": "John", "chap": 3, "sec": 15},
        "next": {"bid": 43, "chineses": "約", "engs": "John", "chap": 3, "sec": 17},
    }


def test_get_word_parsing_success(client, mock_parsing_response_data):
    """Test successful word parsing retrieval."""
    with patch.object(client._client, "get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_parsing_response_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = client.get_word_parsing(book_id=43, chapter=3, verse=16)

        assert result.status == "success"
        assert result.record_count == 3
        assert result.testament == 0  # NT
        assert len(result.records) == 3

        # Check first word (wid=0, full verse info)
        first_word = result.records[0]
        assert first_word.word_id == 0
        assert first_word.word == "Οὕτως"
        assert first_word.strong_number is None

        # Check second word (wid=1, detailed parsing)
        second_word = result.records[1]
        assert second_word.word_id == 1
        assert second_word.strong_number == "3779"
        assert second_word.part_of_speech == "Adv"
        assert second_word.word_form == "Adv"
        assert second_word.original_form == "οὕτω(ς)"
        assert second_word.explanation == "如此, 這樣"

        # Check navigation
        assert result.prev_verse is not None
        assert result.prev_verse.verse == 15
        assert result.next_verse is not None
        assert result.next_verse.verse == 17

        mock_get.assert_called_once()
        url = mock_get.call_args[0][0]
        assert "qp.php" in url
        assert "bid=43" in url
        assert "chap=3" in url
        assert "sec=16" in url


def test_get_word_parsing_with_simplified_chinese(client, mock_parsing_response_data):
    """Test word parsing with simplified Chinese."""
    with patch.object(client._client, "get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_parsing_response_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client.get_word_parsing(book_id=43, chapter=3, verse=16, simplified=True)

        url = mock_get.call_args[0][0]
        assert "gb=1" in url


def test_get_word_parsing_default_chapter_verse(client, mock_parsing_response_data):
    """Test word parsing with default chapter and verse."""
    with patch.object(client._client, "get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_parsing_response_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client.get_word_parsing(book_id=43)

        url = mock_get.call_args[0][0]
        assert "chap=0" in url
        assert "sec=0" in url


def test_get_word_parsing_invalid_book_id(client):
    """Test word parsing with invalid book ID."""
    with pytest.raises(InvalidBookError):
        client.get_word_parsing(book_id=999)


def test_get_word_parsing_connection_error(client):
    """Test word parsing with connection error."""
    with patch.object(client._client, "get") as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with pytest.raises(APIConnectionError):
            client.get_word_parsing(book_id=43, chapter=3, verse=16)


def test_get_word_parsing_http_error(client):
    """Test word parsing with HTTP error."""
    with patch.object(client._client, "get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=Mock(), response=Mock()
        )
        mock_get.return_value = mock_response

        with pytest.raises(APIConnectionError):
            client.get_word_parsing(book_id=43, chapter=3, verse=16)


def test_parse_parsing_response_no_records(client):
    """Test parsing response with no records."""
    data = {
        "status": "success",
        "record_count": 0,
        "N": 0,
        "record": [],
    }

    result = client._parse_parsing_response(data)

    assert result.status == "success"
    assert result.record_count == 0
    assert len(result.records) == 0


def test_parse_parsing_response_failed_status(client):
    """Test parsing response with failed status."""
    data = {
        "status": "error",
        "record_count": 0,
    }

    result = client._parse_parsing_response(data)

    assert result.status == "error"
    assert result.error_message == "API returned status: error"
    assert len(result.records) == 0