"""Assertion functions for testing prompt outputs."""

import re
from typing import Any, List, Optional, Union


class AssertionError(Exception):
    """Custom assertion error with details."""
    def __init__(self, message: str, expected: Any = None, actual: Any = None):
        super().__init__(message)
        self.expected = expected
        self.actual = actual


def max_words(text: str, limit: int) -> None:
    """Assert text has at most `limit` words."""
    word_count = len(text.split())
    if word_count > limit:
        raise AssertionError(
            f"Too many words: {word_count} > {limit}",
            expected=f"<= {limit} words",
            actual=f"{word_count} words"
        )


def min_words(text: str, limit: int) -> None:
    """Assert text has at least `limit` words."""
    word_count = len(text.split())
    if word_count < limit:
        raise AssertionError(
            f"Too few words: {word_count} < {limit}",
            expected=f">= {limit} words",
            actual=f"{word_count} words"
        )


def must_include(text: str, phrase: Union[str, List[str]], case_sensitive: bool = False) -> None:
    """Assert text contains phrase(s)."""
    phrases = [phrase] if isinstance(phrase, str) else phrase
    check_text = text if case_sensitive else text.lower()
    
    for p in phrases:
        check_phrase = p if case_sensitive else p.lower()
        if check_phrase not in check_text:
            raise AssertionError(f"Missing phrase: {p}", expected=p, actual=text[:100])


def must_exclude(text: str, phrase: Union[str, List[str]], case_sensitive: bool = False) -> None:
    """Assert text does not contain phrase(s)."""
    phrases = [phrase] if isinstance(phrase, str) else phrase
    check_text = text if case_sensitive else text.lower()
    
    for p in phrases:
        check_phrase = p if case_sensitive else p.lower()
        if check_phrase in check_text:
            raise AssertionError(f"Forbidden phrase found: {p}", expected=f"not {p}", actual=p)


def matches_pattern(text: str, pattern: str, flags: int = 0) -> None:
    """Assert text matches regex pattern."""
    if not re.search(pattern, text, flags):
        raise AssertionError(f"Pattern not matched: {pattern}", expected=pattern, actual=text[:100])


def is_json(text: str) -> None:
    """Assert text is valid JSON."""
    import json
    try:
        json.loads(text)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON: {e}", expected="valid JSON", actual=text[:100])


def max_chars(text: str, limit: int) -> None:
    """Assert text has at most `limit` characters."""
    if len(text) > limit:
        raise AssertionError(f"Too many characters: {len(text)} > {limit}")


def min_chars(text: str, limit: int) -> None:
    """Assert text has at least `limit` characters."""
    if len(text) < limit:
        raise AssertionError(f"Too few characters: {len(text)} < {limit}")


def starts_with(text: str, prefix: str) -> None:
    """Assert text starts with prefix."""
    if not text.startswith(prefix):
        raise AssertionError(f"Does not start with: {prefix}", expected=prefix, actual=text[:50])


def ends_with(text: str, suffix: str) -> None:
    """Assert text ends with suffix."""
    if not text.endswith(suffix):
        raise AssertionError(f"Does not end with: {suffix}", expected=suffix, actual=text[-50:])


def contains_number(text: str) -> None:
    """Assert text contains at least one number."""
    if not re.search(r'\d', text):
        raise AssertionError("No numbers found", expected="contains number", actual=text[:100])


def no_profanity(text: str, custom_words: Optional[List[str]] = None) -> None:
    """Assert text contains no profanity."""
    banned = custom_words or ["hate", "idiot", "stupid"]
    text_lower = text.lower()
    for word in banned:
        if word in text_lower:
            raise AssertionError(f"Profanity detected: {word}")


def sentiment_positive(text: str) -> None:
    """Basic positive sentiment check."""
    negative = ["bad", "terrible", "awful", "hate", "worst", "horrible"]
    positive = ["good", "great", "excellent", "love", "best", "amazing"]
    text_lower = text.lower()
    neg_count = sum(1 for w in negative if w in text_lower)
    pos_count = sum(1 for w in positive if w in text_lower)
    if neg_count > pos_count:
        raise AssertionError("Negative sentiment detected")
