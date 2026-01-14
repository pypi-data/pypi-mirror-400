"""
Failure tracking store for rollback functionality.

Provides thread-safe, optionally persistent storage for tracking
prompt execution failures with support for TTL, rate limiting,
and comprehensive statistics.
"""

import json
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Deque, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FailureRecord:
    """Detailed record of a single failure event."""
    timestamp: float
    prompt_name: str
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class FailureStats:
    """Statistics about failures for a prompt."""
    prompt_name: str
    total_failures: int
    failures_in_window: int
    first_failure_time: Optional[float]
    last_failure_time: Optional[float]
    failure_rate_per_minute: float
    is_healthy: bool

# Thread lock for concurrent access
_lock = threading.Lock()

# In-memory failure store (simple counts)
_FAILURES: Dict[str, int] = {}

# Detailed failure history with timestamps
_FAILURE_HISTORY: Dict[str, Deque[FailureRecord]] = {}

# Optional persistence file path
_persistence_path: Optional[Path] = None

# Configuration
_max_history_per_prompt: int = 1000
_ttl_seconds: Optional[float] = None  # Time-to-live for failure records
_failure_callbacks: List[Callable[[str, int], None]] = []


def configure(
    persistence_path: Optional[str] = None,
    max_history: int = 1000,
    ttl_seconds: Optional[float] = None,
) -> None:
    """
    Configure the failure store settings.

    Args:
        persistence_path: File path for storing failure data. If None, disables persistence.
        max_history: Maximum number of detailed failure records to keep per prompt.
        ttl_seconds: Time-to-live for failure records in seconds. If None, records never expire.
    """
    global _persistence_path, _max_history_per_prompt, _ttl_seconds
    with _lock:
        _max_history_per_prompt = max_history
        _ttl_seconds = ttl_seconds
        if persistence_path:
            _persistence_path = Path(persistence_path)
            _load_from_disk()
        else:
            _persistence_path = None


def _load_from_disk() -> None:
    """Load failure data from disk if persistence is configured."""
    if _persistence_path and _persistence_path.exists():
        try:
            with open(_persistence_path, "r") as f:
                data = json.load(f)
                _FAILURES.clear()
                _FAILURES.update(data.get("counts", data))  # Support legacy format
                # Load history if available
                if "history" in data:
                    _FAILURE_HISTORY.clear()
                    for name, records in data["history"].items():
                        _FAILURE_HISTORY[name] = deque(
                            [FailureRecord(**r) for r in records],
                            maxlen=_max_history_per_prompt
                        )
            logger.debug(f"Loaded failure data from {_persistence_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load failure data: {e}")


def _save_to_disk() -> None:
    """Save failure data to disk if persistence is configured."""
    if _persistence_path:
        try:
            _persistence_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "counts": _FAILURES,
                "history": {
                    name: [
                        {
                            "timestamp": r.timestamp,
                            "prompt_name": r.prompt_name,
                            "error_type": r.error_type,
                            "error_message": r.error_message,
                            "metadata": r.metadata,
                        }
                        for r in records
                    ]
                    for name, records in _FAILURE_HISTORY.items()
                }
            }
            with open(_persistence_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved failure data to {_persistence_path}")
        except IOError as e:
            logger.warning(f"Failed to save failure data: {e}")


def _cleanup_expired(name: str) -> None:
    """Remove expired failure records for a prompt based on TTL."""
    if _ttl_seconds is None or name not in _FAILURE_HISTORY:
        return
    
    current_time = time.time()
    cutoff_time = current_time - _ttl_seconds
    
    # Remove expired records
    history = _FAILURE_HISTORY[name]
    while history and history[0].timestamp < cutoff_time:
        history.popleft()
    
    # Update count based on remaining records
    _FAILURES[name] = len(history)
    if _FAILURES[name] == 0:
        del _FAILURES[name]
        del _FAILURE_HISTORY[name]


def register_failure_callback(callback: Callable[[str, int], None]) -> None:
    """
    Register a callback to be invoked when a failure is recorded.

    Args:
        callback: A function that takes (prompt_name, new_count) as arguments.
    """
    _failure_callbacks.append(callback)
    logger.debug("Registered failure callback")


def unregister_failure_callback(callback: Callable[[str, int], None]) -> bool:
    """
    Unregister a previously registered failure callback.

    Args:
        callback: The callback function to remove.

    Returns:
        True if the callback was found and removed, False otherwise.
    """
    try:
        _failure_callbacks.remove(callback)
        return True
    except ValueError:
        return False


def record(
    name: str,
    increment: int = 1,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, any]] = None,
) -> int:
    """
    Record a failure for the given prompt name.

    Args:
        name: The name of the prompt that failed.
        increment: Number of failures to add (default: 1).
        error_type: Optional type/class of the error that occurred.
        error_message: Optional error message.
        metadata: Optional additional metadata about the failure.

    Returns:
        The new total failure count for this prompt.
    """
    with _lock:
        _cleanup_expired(name)
        
        current_time = time.time()
        
        # Initialize history if needed
        if name not in _FAILURE_HISTORY:
            _FAILURE_HISTORY[name] = deque(maxlen=_max_history_per_prompt)
        
        # Add detailed records
        for _ in range(increment):
            record = FailureRecord(
                timestamp=current_time,
                prompt_name=name,
                error_type=error_type,
                error_message=error_message,
                metadata=metadata or {},
            )
            _FAILURE_HISTORY[name].append(record)
        
        _FAILURES[name] = _FAILURES.get(name, 0) + increment
        new_count = _FAILURES[name]
        _save_to_disk()
        logger.info(f"Recorded failure for '{name}'. Total failures: {new_count}")
        
        # Invoke callbacks
        for callback in _failure_callbacks:
            try:
                callback(name, new_count)
            except Exception as e:
                logger.error(f"Failure callback error: {e}")
        
        return new_count


def count(name: str, apply_ttl: bool = True) -> int:
    """
    Get the current failure count for a prompt.

    Args:
        name: The name of the prompt to check.
        apply_ttl: If True, expired records are cleaned up first.

    Returns:
        The number of recorded failures for this prompt.
    """
    with _lock:
        if apply_ttl:
            _cleanup_expired(name)
        return _FAILURES.get(name, 0)


def count_in_window(name: str, window_seconds: float) -> int:
    """
    Get the failure count within a specific time window.

    Args:
        name: The name of the prompt to check.
        window_seconds: The time window in seconds to consider.

    Returns:
        The number of failures within the time window.
    """
    with _lock:
        if name not in _FAILURE_HISTORY:
            return 0
        
        cutoff_time = time.time() - window_seconds
        return sum(1 for r in _FAILURE_HISTORY[name] if r.timestamp >= cutoff_time)


def get_failure_rate(name: str, window_seconds: float = 60.0) -> float:
    """
    Calculate the failure rate (failures per minute) for a prompt.

    Args:
        name: The name of the prompt to check.
        window_seconds: The time window to calculate the rate over.

    Returns:
        The failure rate as failures per minute.
    """
    with _lock:
        if name not in _FAILURE_HISTORY or not _FAILURE_HISTORY[name]:
            return 0.0
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        failures_in_window = sum(
            1 for r in _FAILURE_HISTORY[name] if r.timestamp >= cutoff_time
        )
        
        # Convert to per-minute rate
        minutes = window_seconds / 60.0
        return failures_in_window / minutes if minutes > 0 else 0.0


def decrement(name: str, amount: int = 1) -> int:
    """
    Decrease the failure count for a prompt (e.g., after successful recovery).

    Args:
        name: The name of the prompt.
        amount: The amount to decrease by (default: 1).

    Returns:
        The new failure count (never goes below 0).
    """
    with _lock:
        if name not in _FAILURES:
            return 0
        
        _FAILURES[name] = max(0, _FAILURES[name] - amount)
        
        # Remove oldest records from history
        if name in _FAILURE_HISTORY:
            for _ in range(min(amount, len(_FAILURE_HISTORY[name]))):
                if _FAILURE_HISTORY[name]:
                    _FAILURE_HISTORY[name].popleft()
        
        new_count = _FAILURES[name]
        if new_count == 0:
            del _FAILURES[name]
            if name in _FAILURE_HISTORY:
                del _FAILURE_HISTORY[name]
        
        _save_to_disk()
        logger.info(f"Decremented failure count for '{name}'. New count: {new_count}")
        return new_count


def reset(name: str) -> bool:
    """
    Reset the failure count for a specific prompt.

    Args:
        name: The name of the prompt to reset.

    Returns:
        True if the prompt was found and reset, False otherwise.
    """
    with _lock:
        found = False
        if name in _FAILURES:
            del _FAILURES[name]
            found = True
        if name in _FAILURE_HISTORY:
            del _FAILURE_HISTORY[name]
            found = True
        if found:
            _save_to_disk()
            logger.info(f"Reset failure count for '{name}'")
        return found


def clear_all() -> int:
    """
    Clear all failure records.

    Returns:
        The number of records that were cleared.
    """
    with _lock:
        cleared_count = len(_FAILURES)
        _FAILURES.clear()
        _FAILURE_HISTORY.clear()
        _save_to_disk()
        logger.info(f"Cleared all failure records ({cleared_count} entries)")
        return cleared_count


def list_failures() -> Dict[str, int]:
    """
    Get a copy of all current failure records.

    Returns:
        A dictionary mapping prompt names to their failure counts.
    """
    with _lock:
        return dict(_FAILURES)


def get_prompts_above_threshold(threshold: int) -> Dict[str, int]:
    """
    Get all prompts with failure counts at or above the given threshold.

    Args:
        threshold: The minimum failure count to include.

    Returns:
        A dictionary of prompt names and counts that meet the threshold.
    """
    with _lock:
        return {name: cnt for name, cnt in _FAILURES.items() if cnt >= threshold}


def get_stats(name: str, window_seconds: float = 300.0) -> FailureStats:
    """
    Get comprehensive statistics for a prompt's failures.

    Args:
        name: The name of the prompt.
        window_seconds: Time window for rate calculations (default: 5 minutes).

    Returns:
        FailureStats object with detailed statistics.
    """
    with _lock:
        _cleanup_expired(name)
        
        total = _FAILURES.get(name, 0)
        history = _FAILURE_HISTORY.get(name, deque())
        
        first_time = history[0].timestamp if history else None
        last_time = history[-1].timestamp if history else None
        
        cutoff_time = time.time() - window_seconds
        failures_in_window = sum(1 for r in history if r.timestamp >= cutoff_time)
        
        rate = (failures_in_window / (window_seconds / 60.0)) if window_seconds > 0 else 0.0
        
        return FailureStats(
            prompt_name=name,
            total_failures=total,
            failures_in_window=failures_in_window,
            first_failure_time=first_time,
            last_failure_time=last_time,
            failure_rate_per_minute=rate,
            is_healthy=total == 0,
        )


def get_all_stats(window_seconds: float = 300.0) -> Dict[str, FailureStats]:
    """
    Get statistics for all tracked prompts.

    Args:
        window_seconds: Time window for rate calculations.

    Returns:
        Dictionary mapping prompt names to their FailureStats.
    """
    with _lock:
        names = list(_FAILURES.keys())
    
    # Release lock and get stats individually to avoid long lock holds
    return {name: get_stats(name, window_seconds) for name in names}


def get_failure_history(
    name: str,
    limit: Optional[int] = None,
    since: Optional[float] = None,
) -> List[FailureRecord]:
    """
    Get detailed failure history for a prompt.

    Args:
        name: The name of the prompt.
        limit: Maximum number of records to return (most recent first).
        since: Only return records after this timestamp.

    Returns:
        List of FailureRecord objects, most recent first.
    """
    with _lock:
        if name not in _FAILURE_HISTORY:
            return []
        
        history = list(_FAILURE_HISTORY[name])
        
        if since is not None:
            history = [r for r in history if r.timestamp >= since]
        
        # Reverse to get most recent first
        history = list(reversed(history))
        
        if limit is not None:
            history = history[:limit]
        
        return history


def record_batch(failures: List[Tuple[str, Optional[str], Optional[str]]]) -> Dict[str, int]:
    """
    Record multiple failures at once efficiently.

    Args:
        failures: List of tuples (prompt_name, error_type, error_message).

    Returns:
        Dictionary mapping prompt names to their new failure counts.
    """
    results = {}
    with _lock:
        current_time = time.time()
        
        for prompt_name, error_type, error_message in failures:
            _cleanup_expired(prompt_name)
            
            if prompt_name not in _FAILURE_HISTORY:
                _FAILURE_HISTORY[prompt_name] = deque(maxlen=_max_history_per_prompt)
            
            failure_record = FailureRecord(
                timestamp=current_time,
                prompt_name=prompt_name,
                error_type=error_type,
                error_message=error_message,
            )
            _FAILURE_HISTORY[prompt_name].append(failure_record)
            
            _FAILURES[prompt_name] = _FAILURES.get(prompt_name, 0) + 1
            results[prompt_name] = _FAILURES[prompt_name]
        
        _save_to_disk()
        logger.info(f"Recorded batch of {len(failures)} failures")
        
        # Invoke callbacks for each unique prompt
        for prompt_name, new_count in results.items():
            for callback in _failure_callbacks:
                try:
                    callback(prompt_name, new_count)
                except Exception as e:
                    logger.error(f"Failure callback error: {e}")
    
    return results


def create_snapshot() -> Dict[str, any]:
    """
    Create a snapshot of the current failure state.

    Returns:
        A dictionary containing the current state that can be restored later.
    """
    with _lock:
        return {
            "counts": dict(_FAILURES),
            "history": {
                name: [
                    {
                        "timestamp": r.timestamp,
                        "prompt_name": r.prompt_name,
                        "error_type": r.error_type,
                        "error_message": r.error_message,
                        "metadata": r.metadata,
                    }
                    for r in records
                ]
                for name, records in _FAILURE_HISTORY.items()
            },
            "snapshot_time": time.time(),
        }


def restore_snapshot(snapshot: Dict[str, any]) -> None:
    """
    Restore failure state from a previously created snapshot.

    Args:
        snapshot: A snapshot dictionary created by create_snapshot().
    """
    with _lock:
        _FAILURES.clear()
        _FAILURES.update(snapshot.get("counts", {}))
        
        _FAILURE_HISTORY.clear()
        for name, records in snapshot.get("history", {}).items():
            _FAILURE_HISTORY[name] = deque(
                [FailureRecord(**r) for r in records],
                maxlen=_max_history_per_prompt
            )
        
        _save_to_disk()
        logger.info(f"Restored snapshot from {snapshot.get('snapshot_time', 'unknown time')}")
