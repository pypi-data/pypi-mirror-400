"""Tests for promptops.utils module."""

import pytest
import time
from datetime import datetime, timezone

from promptops.utils import (
    hash_obj,
    hash_string,
    generate_id,
    generate_timestamp_id,
    truncate,
    slugify,
    sanitize_for_logging,
    mask_sensitive,
    normalize_whitespace,
    extract_json_blocks,
)


class TestHashObj:
    """Tests for hash_obj function."""

    def test_hash_dict(self):
        """Test hashing a dictionary."""
        obj = {"key": "value", "number": 42}
        result = hash_obj(obj)
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 hex length

    def test_hash_list(self):
        """Test hashing a list."""
        obj = [1, 2, 3, "four"]
        result = hash_obj(obj)
        assert isinstance(result, str)

    def test_deterministic_hash(self):
        """Test that same object produces same hash."""
        obj = {"a": 1, "b": 2}
        hash1 = hash_obj(obj)
        hash2 = hash_obj(obj)
        assert hash1 == hash2

    def test_order_independent_dict_hash(self):
        """Test that dict key order doesn't affect hash."""
        obj1 = {"a": 1, "b": 2}
        obj2 = {"b": 2, "a": 1}
        assert hash_obj(obj1) == hash_obj(obj2)

    def test_short_hash(self):
        """Test short hash option."""
        obj = {"key": "value"}
        result = hash_obj(obj, short=True)
        assert len(result) == 12

    def test_different_algorithms(self):
        """Test different hash algorithms."""
        obj = {"test": "data"}
        sha256 = hash_obj(obj, algorithm="sha256")
        sha1 = hash_obj(obj, algorithm="sha1")
        md5 = hash_obj(obj, algorithm="md5")
        
        assert sha256 != sha1 != md5
        assert len(sha256) == 64
        assert len(sha1) == 40
        assert len(md5) == 32

    def test_invalid_algorithm_raises(self):
        """Test that invalid algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            hash_obj({"key": "value"}, algorithm="invalid")


class TestHashString:
    """Tests for hash_string function."""

    def test_hash_string_basic(self):
        """Test hashing a string."""
        result = hash_string("hello world")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_deterministic(self):
        """Test deterministic hashing."""
        assert hash_string("test") == hash_string("test")

    def test_different_strings_different_hash(self):
        """Test different strings produce different hashes."""
        assert hash_string("hello") != hash_string("world")


class TestGenerateId:
    """Tests for generate_id function."""

    def test_basic_id(self):
        """Test generating a basic ID."""
        result = generate_id()
        assert isinstance(result, str)
        assert len(result) == 8

    def test_with_prefix(self):
        """Test ID with prefix."""
        result = generate_id(prefix="prompt_")
        assert result.startswith("prompt_")

    def test_custom_length(self):
        """Test custom length ID."""
        result = generate_id(length=16)
        assert len(result) == 16

    def test_uniqueness(self):
        """Test that generated IDs are unique."""
        ids = [generate_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestGenerateTimestampId:
    """Tests for generate_timestamp_id function."""

    def test_basic_timestamp_id(self):
        """Test generating a timestamp ID."""
        result = generate_timestamp_id()
        assert isinstance(result, str)
        # Format: YYYYMMDDHHMMSS_random
        assert "_" in result

    def test_with_prefix(self):
        """Test timestamp ID with prefix."""
        result = generate_timestamp_id(prefix="run")
        assert result.startswith("run_")

    def test_sortable(self):
        """Test that timestamp IDs are sortable."""
        id1 = generate_timestamp_id()
        time.sleep(0.01)
        id2 = generate_timestamp_id()
        assert id1 < id2


class TestTruncate:
    """Tests for truncate function."""

    def test_no_truncation_needed(self):
        """Test text shorter than max length."""
        result = truncate("hello", max_length=10)
        assert result == "hello"

    def test_truncation_with_suffix(self):
        """Test truncation adds suffix."""
        result = truncate("hello world", max_length=8)
        assert result.endswith("...")
        assert len(result) == 8

    def test_custom_suffix(self):
        """Test custom truncation suffix."""
        result = truncate("hello world", max_length=10, suffix="…")
        assert result.endswith("…")

    def test_word_boundary(self):
        """Test truncation at word boundary."""
        result = truncate("hello beautiful world", max_length=15, word_boundary=True)
        # Should truncate at a word boundary
        assert not result.endswith("beaut...")


class TestSlugify:
    """Tests for slugify function."""

    def test_basic_slug(self):
        """Test basic slugification."""
        result = slugify("Hello World")
        assert result == "hello-world"

    def test_special_characters_removed(self):
        """Test special characters are removed."""
        result = slugify("Hello! World? #test")
        assert "!" not in result
        assert "?" not in result
        assert "#" not in result

    def test_custom_separator(self):
        """Test custom separator."""
        result = slugify("Hello World", separator="_")
        assert result == "hello_world"

    def test_max_length(self):
        """Test max length option."""
        result = slugify("This is a very long title", max_length=10)
        assert len(result) <= 10


class TestSanitizeForLogging:
    """Tests for sanitize_for_logging function."""

    def test_removes_newlines(self):
        """Test newlines are removed."""
        result = sanitize_for_logging("hello\nworld")
        assert "\n" not in result
        assert result == "hello world"

    def test_masks_api_key(self):
        """Test API keys are masked."""
        result = sanitize_for_logging("api_key=sk-12345abcdef")
        assert "sk-12345abcdef" not in result
        assert "***" in result

    def test_truncates_long_text(self):
        """Test long text is truncated."""
        long_text = "a" * 500
        result = sanitize_for_logging(long_text, max_length=200)
        assert len(result) <= 200


class TestMaskSensitive:
    """Tests for mask_sensitive function."""

    def test_masks_email(self):
        """Test emails are masked."""
        result = mask_sensitive("Contact: user@example.com")
        assert "user@example.com" not in result
        assert "***@***.***" in result

    def test_masks_api_key(self):
        """Test API keys are masked."""
        result = mask_sensitive("Key: sk-abcdefghijklmnopqrstuvwxyz123456")
        assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in result
        assert "sk-***" in result

    def test_masks_credit_card(self):
        """Test credit card numbers are masked."""
        result = mask_sensitive("Card: 1234-5678-9012-3456")
        assert "1234-5678-9012-3456" not in result
        assert "****-****-****-****" in result

    def test_masks_ssn(self):
        """Test SSN is masked."""
        result = mask_sensitive("SSN: 123-45-6789")
        assert "123-45-6789" not in result
        assert "***-**-****" in result

    def test_custom_patterns(self):
        """Test custom patterns are masked."""
        result = mask_sensitive("Secret: CUSTOM123", patterns=[r"CUSTOM\d+"])
        assert "CUSTOM123" not in result


class TestNormalizeWhitespace:
    """Tests for normalize_whitespace function."""

    def test_multiple_spaces(self):
        """Test multiple spaces are normalized."""
        result = normalize_whitespace("hello    world")
        assert result == "hello world"

    def test_tabs_and_newlines(self):
        """Test tabs and newlines are normalized."""
        result = normalize_whitespace("hello\t\nworld")
        assert result == "hello world"

    def test_leading_trailing_whitespace(self):
        """Test leading/trailing whitespace is removed."""
        result = normalize_whitespace("  hello world  ")
        assert result == "hello world"


class TestExtractJsonBlocks:
    """Tests for extract_json_blocks function."""

    def test_extract_json_in_code_block(self):
        """Test extracting JSON from code block."""
        text = 'Here is the result:\n```json\n{"key": "value"}\n```'
        result = extract_json_blocks(text)
        assert len(result) == 1
        assert result[0] == {"key": "value"}

    def test_extract_multiple_blocks(self):
        """Test extracting multiple JSON blocks."""
        text = '```json\n{"a": 1}\n```\nSome text\n```json\n{"b": 2}\n```'
        result = extract_json_blocks(text)
        assert len(result) == 2

    def test_no_json_blocks(self):
        """Test text without JSON blocks."""
        text = "Just plain text without any JSON"
        result = extract_json_blocks(text)
        assert result == []

    def test_invalid_json_ignored(self):
        """Test invalid JSON is ignored."""
        text = '```json\n{invalid json}\n```'
        result = extract_json_blocks(text)
        assert result == []
