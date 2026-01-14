"""
Comprehensive utility functions for PromptOps.

Provides hashing, string manipulation, timing, retry logic, validation,
caching, and async utilities used throughout the library.
"""

import asyncio
import functools
import hashlib
import json
import logging
import os
import re
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

logger = logging.getLogger("promptops.utils")

T = TypeVar("T")
R = TypeVar("R")


# =============================================================================
# Hashing Utilities
# =============================================================================


def hash_obj(obj: Any, algorithm: str = "sha256", short: bool = False) -> str:
    """
    Generate a hash of any JSON-serializable object.

    Args:
        obj: Any JSON-serializable object.
        algorithm: Hash algorithm ('sha256', 'sha1', 'md5', 'blake2b').
        short: If True, return first 12 characters for a shorter identifier.

    Returns:
        Hexadecimal hash string.

    Examples:
        >>> hash_obj({"key": "value"})
        'a1b2c3d4...'
        >>> hash_obj([1, 2, 3], short=True)
        'abc123def456'
    """
    algorithms = {
        "sha256": hashlib.sha256,
        "sha1": hashlib.sha1,
        "md5": hashlib.md5,
        "blake2b": hashlib.blake2b,
    }
    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {list(algorithms.keys())}")

    serialized = json.dumps(obj, sort_keys=True, default=_json_serializer).encode("utf-8")
    digest = algorithms[algorithm](serialized).hexdigest()
    return digest[:12] if short else digest


def hash_string(s: str, algorithm: str = "sha256") -> str:
    """Hash a string directly."""
    algorithms = {
        "sha256": hashlib.sha256,
        "sha1": hashlib.sha1,
        "md5": hashlib.md5,
        "blake2b": hashlib.blake2b,
    }
    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    return algorithms[algorithm](s.encode("utf-8")).hexdigest()


def generate_id(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique identifier.

    Args:
        prefix: Optional prefix for the ID.
        length: Length of the random portion (8-32).

    Returns:
        A unique identifier string.
    """
    length = max(8, min(32, length))
    random_part = uuid.uuid4().hex[:length]
    return f"{prefix}{random_part}" if prefix else random_part


def generate_timestamp_id(prefix: str = "") -> str:
    """Generate a sortable ID with timestamp prefix."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    random_part = uuid.uuid4().hex[:6]
    base = f"{ts}_{random_part}"
    return f"{prefix}_{base}" if prefix else base


# =============================================================================
# String Utilities
# =============================================================================


def truncate(
    text: str,
    max_length: int,
    suffix: str = "...",
    word_boundary: bool = False
) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Input text.
        max_length: Maximum allowed length (including suffix).
        suffix: String to append when truncating.
        word_boundary: If True, truncate at word boundary.

    Returns:
        Truncated string.
    """
    if len(text) <= max_length:
        return text

    target_len = max_length - len(suffix)
    if target_len <= 0:
        return suffix[:max_length]

    truncated = text[:target_len]

    if word_boundary:
        last_space = truncated.rfind(" ")
        if last_space > target_len // 2:
            truncated = truncated[:last_space]

    return truncated.rstrip() + suffix


def slugify(text: str, separator: str = "-", max_length: Optional[int] = None) -> str:
    """
    Convert text to a URL-safe slug.

    Args:
        text: Input text.
        separator: Character to use between words.
        max_length: Optional maximum length for the slug.

    Returns:
        URL-safe slug.
    """
    # Lowercase and replace non-alphanumeric with separator
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", separator, slug)
    slug = re.sub(f"{re.escape(separator)}+", separator, slug)
    slug = slug.strip(separator)

    if max_length and len(slug) > max_length:
        slug = slug[:max_length].rstrip(separator)

    return slug


def sanitize_for_logging(text: str, max_length: int = 200) -> str:
    """Sanitize and truncate text for safe logging."""
    # Remove newlines and extra whitespace
    cleaned = " ".join(text.split())
    # Mask potential secrets
    cleaned = re.sub(r"(api[_-]?key|password|secret|token)[=:\s]+\S+", r"\1=***", cleaned, flags=re.IGNORECASE)
    return truncate(cleaned, max_length)


def mask_sensitive(text: str, patterns: Optional[List[str]] = None) -> str:
    """
    Mask sensitive information in text.

    Args:
        text: Input text.
        patterns: Additional regex patterns to mask.

    Returns:
        Text with sensitive data masked.
    """
    default_patterns = [
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "***@***.***"),  # Email
        (r"\b(?:sk-|pk-)[a-zA-Z0-9]{32,}\b", "sk-***"),  # API keys
        (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "****-****-****-****"),  # Credit card
        (r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****"),  # SSN
    ]
    result = text
    for pattern, replacement in default_patterns:
        result = re.sub(pattern, replacement, result)
    if patterns:
        for pattern in patterns:
            result = re.sub(pattern, "***", result)
    return result


def normalize_whitespace(text: str) -> str:
    """Normalize all whitespace to single spaces."""
    return " ".join(text.split())


def extract_json_blocks(text: str) -> List[Dict[str, Any]]:
    """
    Extract and parse all JSON blocks from text.

    Useful for parsing LLM responses that contain JSON.
    """
    results = []
    
    # First, extract from code blocks (prioritize these)
    code_block_patterns = [
        r"```(?:json)?\s*(\{[\s\S]*?\})\s*```",
        r"```(?:json)?\s*(\[[\s\S]*?\])\s*```",
    ]
    
    extracted_ranges = []
    for pattern in code_block_patterns:
        for match in re.finditer(pattern, text):
            try:
                parsed = json.loads(match.group(1))
                results.append(parsed)
                extracted_ranges.append((match.start(), match.end()))
            except json.JSONDecodeError:
                continue
    
    # Then extract bare JSON, but skip if it overlaps with code blocks
    bare_pattern = r"(?<![`\w])(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})(?![`\w])"
    for match in re.finditer(bare_pattern, text):
        # Check if this match overlaps with any code block
        overlaps = any(
            start <= match.start() < end or start < match.end() <= end
            for start, end in extracted_ranges
        )
        if not overlaps:
            try:
                parsed = json.loads(match.group(1))
                results.append(parsed)
            except json.JSONDecodeError:
                continue
    
    return results


# =============================================================================
# Time Utilities
# =============================================================================


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def timestamp_ms() -> int:
    """Get current timestamp in milliseconds."""
    return int(time.time() * 1000)


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.

    Examples:
        >>> format_duration(0.5)
        '500ms'
        >>> format_duration(65)
        '1m 5s'
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    if seconds < 0:
        return "-" + format_duration(-seconds)
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    if seconds < 60:
        return f"{seconds:.1f}s" if seconds % 1 else f"{int(seconds)}s"

    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def parse_duration(s: str) -> float:
    """
    Parse a duration string to seconds.

    Supports: '100ms', '5s', '2m', '1h', '1h30m', '2d'
    """
    s = s.strip().lower()
    total = 0.0
    pattern = r"(\d+(?:\.\d+)?)\s*(ms|s|m|h|d)?"
    for match in re.finditer(pattern, s):
        value = float(match.group(1))
        unit = match.group(2) or "s"
        multipliers = {"ms": 0.001, "s": 1, "m": 60, "h": 3600, "d": 86400}
        total += value * multipliers.get(unit, 1)
    return total


@contextmanager
def timed(label: str = "", log_level: int = logging.DEBUG) -> Generator[Dict[str, float], None, None]:
    """
    Context manager for timing code blocks.

    Args:
        label: Optional label for the timing.
        log_level: Logging level for the timing message.

    Yields:
        Dict containing 'elapsed' key with timing in seconds.

    Example:
        >>> with timed("database query") as t:
        ...     do_query()
        >>> print(f"Query took {t['elapsed']:.2f}s")
    """
    result: Dict[str, float] = {"elapsed": 0.0}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start
        if label:
            logger.log(log_level, f"{label}: {format_duration(result['elapsed'])}")


class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm.

    Args:
        rate: Number of allowed calls per period.
        period: Time period in seconds.
    """

    def __init__(self, rate: int, period: float = 1.0):
        self.rate = rate
        self.period = period
        self.tokens = rate
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock() if asyncio else None

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.period))
        self.last_update = now

    def acquire(self, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token. Returns True if successful.

        Args:
            block: If True, wait for a token. If False, return immediately.
            timeout: Maximum time to wait for a token.
        """
        start = time.monotonic()
        while True:
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            if not block:
                return False
            if timeout and (time.monotonic() - start) >= timeout:
                return False
            time.sleep(0.01)

    async def acquire_async(self) -> bool:
        """Async version of acquire."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            while True:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
                await asyncio.sleep(0.01)


# =============================================================================
# Retry Utilities
# =============================================================================


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts.
        base_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries.
        exponential_base: Base for exponential backoff.
        jitter: If True, add random jitter to delays.
        retryable_exceptions: Tuple of exception types to retry on.
        on_retry: Optional callback called on each retry with (exception, attempt).

    Example:
        >>> @retry(max_attempts=3, retryable_exceptions=(ConnectionError,))
        ... def fetch_data():
        ...     ...
    """
    import random

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        raise
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random())
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} after {delay:.2f}s: {e}"
                    )
                    if on_retry:
                        on_retry(e, attempt)
                    time.sleep(delay)
            raise last_exception  # type: ignore

        return wrapper

    return decorator


def retry_async(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """Async version of retry decorator."""
    import random

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        raise
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random())
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} after {delay:.2f}s: {e}"
                    )
                    if on_retry:
                        on_retry(e, attempt)
                    await asyncio.sleep(delay)
            raise last_exception  # type: ignore

        return wrapper

    return decorator


# =============================================================================
# Validation Utilities
# =============================================================================


def validate_type(value: Any, expected_type: Type[T], name: str = "value") -> T:
    """
    Validate that a value is of the expected type.

    Raises:
        TypeError: If type doesn't match.
    """
    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be {expected_type.__name__}, got {type(value).__name__}")
    return value


def validate_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    name: str = "value",
) -> Union[int, float]:
    """
    Validate that a value is within the specified range.

    Raises:
        ValueError: If value is out of range.
    """
    if min_val is not None and value < min_val:
        raise ValueError(f"{name} must be >= {min_val}, got {value}")
    if max_val is not None and value > max_val:
        raise ValueError(f"{name} must be <= {max_val}, got {value}")
    return value


def validate_not_empty(value: Any, name: str = "value") -> Any:
    """
    Validate that a value is not None or empty.

    Raises:
        ValueError: If value is None or empty.
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if hasattr(value, "__len__") and len(value) == 0:
        raise ValueError(f"{name} cannot be empty")
    return value


def validate_keys(
    d: Dict[str, Any],
    required: Optional[Set[str]] = None,
    optional: Optional[Set[str]] = None,
    allow_extra: bool = False,
) -> Dict[str, Any]:
    """
    Validate dictionary keys.

    Args:
        d: Dictionary to validate.
        required: Set of required keys.
        optional: Set of optional keys.
        allow_extra: If False, raise on unexpected keys.

    Raises:
        ValueError: If validation fails.
    """
    required = required or set()
    optional = optional or set()

    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"Missing required keys: {missing}")

    if not allow_extra:
        allowed = required | optional
        extra = set(d.keys()) - allowed
        if extra:
            raise ValueError(f"Unexpected keys: {extra}")

    return d


def coerce_type(value: Any, target_type: Type[T], strict: bool = False) -> T:
    """
    Attempt to coerce a value to a target type.

    Args:
        value: Value to coerce.
        target_type: Desired type.
        strict: If True, raise on failure. If False, return original.

    Returns:
        Coerced value or original if coercion fails and not strict.
    """
    if isinstance(value, target_type):
        return value
    try:
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")  # type: ignore
        return target_type(value)  # type: ignore
    except (ValueError, TypeError) as e:
        if strict:
            raise TypeError(f"Cannot coerce {type(value).__name__} to {target_type.__name__}") from e
        return value  # type: ignore


# =============================================================================
# Serialization Utilities
# =============================================================================


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for common types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, set):
        return list(obj)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def to_json(obj: Any, pretty: bool = False, **kwargs: Any) -> str:
    """
    Serialize object to JSON string with extended type support.

    Args:
        obj: Object to serialize.
        pretty: If True, format with indentation.
        **kwargs: Additional kwargs for json.dumps.

    Returns:
        JSON string.
    """
    return json.dumps(
        obj,
        default=_json_serializer,
        indent=2 if pretty else None,
        sort_keys=True,
        ensure_ascii=False,
        **kwargs,
    )


def from_json(s: str, default: Any = None) -> Any:
    """
    Parse JSON string with error handling.

    Args:
        s: JSON string.
        default: Value to return if parsing fails.

    Returns:
        Parsed object or default.
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error: {e}")
        return default


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary.
        override: Dictionary to merge in (takes precedence).

    Returns:
        Merged dictionary.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def flatten_dict(d: Dict[str, Any], separator: str = ".", prefix: str = "") -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Example:
        >>> flatten_dict({"a": {"b": 1, "c": 2}})
        {"a.b": 1, "a.c": 2}
    """
    items: List[Tuple[str, Any]] = []
    for key, value in d.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, separator, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """
    Unflatten a flattened dictionary.

    Example:
        >>> unflatten_dict({"a.b": 1, "a.c": 2})
        {"a": {"b": 1, "c": 2}}
    """
    result: Dict[str, Any] = {}
    for key, value in d.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
    return result


# =============================================================================
# Caching Utilities
# =============================================================================


def memoize(
    maxsize: Optional[int] = 128,
    ttl: Optional[float] = None,
    key_func: Optional[Callable[..., str]] = None,
):
    """
    Memoization decorator with optional TTL.

    Args:
        maxsize: Maximum cache size. None for unlimited.
        ttl: Time-to-live in seconds for cached values.
        key_func: Custom function to generate cache keys.

    Example:
        >>> @memoize(ttl=60)
        ... def expensive_computation(x, y):
        ...     return x + y
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        cache: Dict[str, Tuple[R, float]] = {}
        order: List[str] = []

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = hash_obj((args, tuple(sorted(kwargs.items()))), short=True)

            now = time.time()

            # Check cache
            if key in cache:
                value, timestamp = cache[key]
                if ttl is None or (now - timestamp) < ttl:
                    return value
                else:
                    del cache[key]
                    order.remove(key)

            # Compute and cache
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            order.append(key)

            # Enforce maxsize
            while maxsize and len(order) > maxsize:
                old_key = order.pop(0)
                cache.pop(old_key, None)

            return result

        wrapper.cache_clear = lambda: (cache.clear(), order.clear())  # type: ignore
        wrapper.cache_info = lambda: {"size": len(cache), "maxsize": maxsize, "ttl": ttl}  # type: ignore
        return wrapper

    return decorator


# =============================================================================
# Collection Utilities
# =============================================================================


def chunk(iterable: Iterable[T], size: int) -> Generator[List[T], None, None]:
    """
    Split an iterable into chunks of specified size.

    Example:
        >>> list(chunk([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
    """
    batch: List[T] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def unique(iterable: Iterable[T], key: Optional[Callable[[T], Any]] = None) -> List[T]:
    """
    Return unique elements preserving order.

    Args:
        iterable: Input iterable.
        key: Optional function to extract comparison key.

    Example:
        >>> unique([1, 2, 2, 3, 1])
        [1, 2, 3]
    """
    seen: Set[Any] = set()
    result: List[T] = []
    for item in iterable:
        k = key(item) if key else item
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


def first(
    iterable: Iterable[T],
    predicate: Optional[Callable[[T], bool]] = None,
    default: Optional[T] = None,
) -> Optional[T]:
    """
    Return first element matching predicate, or default.

    Example:
        >>> first([1, 2, 3], lambda x: x > 1)
        2
    """
    for item in iterable:
        if predicate is None or predicate(item):
            return item
    return default


def group_by(iterable: Iterable[T], key: Callable[[T], Any]) -> Dict[Any, List[T]]:
    """
    Group elements by key function.

    Example:
        >>> group_by([1, 2, 3, 4], lambda x: x % 2)
        {1: [1, 3], 0: [2, 4]}
    """
    result: Dict[Any, List[T]] = {}
    for item in iterable:
        k = key(item)
        result.setdefault(k, []).append(item)
    return result


# =============================================================================
# Environment Utilities
# =============================================================================


def get_env_bool(name: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.environ.get(name, "").lower()
    if not value:
        return default
    return value in ("true", "1", "yes", "on")


def get_env_int(name: str, default: int = 0) -> int:
    """Get integer environment variable."""
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Invalid integer for {name}: {value}, using default {default}")
        return default


def get_env_list(name: str, separator: str = ",", default: Optional[List[str]] = None) -> List[str]:
    """Get list environment variable."""
    value = os.environ.get(name)
    if not value:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


# =============================================================================
# Async Utilities
# =============================================================================


async def gather_with_concurrency(
    limit: int,
    *coros,
    return_exceptions: bool = False,
) -> List[Any]:
    """
    Run coroutines with concurrency limit.

    Args:
        limit: Maximum concurrent coroutines.
        *coros: Coroutines to run.
        return_exceptions: If True, return exceptions instead of raising.

    Returns:
        List of results in order.
    """
    semaphore = asyncio.Semaphore(limit)

    async def limited_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(
        *(limited_coro(c) for c in coros),
        return_exceptions=return_exceptions,
    )


async def timeout_wrapper(
    coro,
    timeout_seconds: float,
    default: Any = None,
) -> Any:
    """
    Wrap a coroutine with a timeout.

    Args:
        coro: Coroutine to wrap.
        timeout_seconds: Timeout in seconds.
        default: Value to return on timeout.

    Returns:
        Coroutine result or default on timeout.
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Timeout after {timeout_seconds}s")
        return default


# =============================================================================
# Deprecated (kept for backward compatibility)
# =============================================================================

# Original hash_obj signature support - the function now accepts additional params
# but calling with just obj still works identically
