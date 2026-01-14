"""
Rollback engine for managing prompt rollback operations.

Provides functionality to check if rollback is needed and execute
rollback operations when failure thresholds are exceeded. Includes
circuit breaker pattern, health monitoring, and rollback history.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol

from .store import count, reset, decrement, get_failure_rate, get_stats

logger = logging.getLogger(__name__)


class RollbackAction(Enum):
    """Defines the possible rollback actions."""
    NONE = "none"
    TRIGGERED = "triggered"
    ALREADY_ROLLED_BACK = "already_rolled_back"
    CIRCUIT_OPEN = "circuit_open"
    RECOVERED = "recovered"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class RollbackResult:
    """Result of a rollback check or operation."""
    action: RollbackAction
    prompt_name: str
    failure_count: int
    threshold: int
    message: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds before trying half-open
    success_threshold: int = 2  # successes needed in half-open to close
    rate_limit_threshold: float = 10.0  # failures per minute to open


@dataclass
class CircuitBreakerState:
    """State of a circuit breaker for a specific prompt."""
    state: CircuitState = CircuitState.CLOSED
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_successes: int = 0
    opened_at: Optional[float] = None


@dataclass
class RollbackHistoryEntry:
    """Entry in the rollback history log."""
    prompt_name: str
    timestamp: float
    action: RollbackAction
    failure_count: int
    threshold: int
    success: bool
    error_message: Optional[str] = None
    duration_ms: Optional[float] = None


class PromptProtocol(Protocol):
    """Protocol defining the expected interface for a prompt object."""
    name: str


class RollbackError(Exception):
    """Exception raised when a rollback operation fails."""
    pass


class CircuitOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    def __init__(self, prompt_name: str, retry_after: float):
        self.prompt_name = prompt_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker open for '{prompt_name}'. Retry after {retry_after:.1f}s"
        )


# Registry for custom rollback handlers
_rollback_handlers: Dict[str, Callable[[str], None]] = {}

# Circuit breaker states per prompt
_circuit_states: Dict[str, CircuitBreakerState] = {}

# Default circuit breaker configuration
_default_circuit_config = CircuitBreakerConfig()

# Rollback history
_rollback_history: List[RollbackHistoryEntry] = []
_max_history_entries: int = 1000

# Event callbacks
_rollback_event_callbacks: List[Callable[[RollbackHistoryEntry], None]] = []
_circuit_event_callbacks: List[Callable[[str, CircuitState, CircuitState], None]] = []


def register_rollback_handler(prompt_name: str, handler: Callable[[str], None]) -> None:
    """
    Register a custom rollback handler for a specific prompt.

    Args:
        prompt_name: The name of the prompt to register the handler for.
        handler: A callable that takes the prompt name and performs the rollback.
    """
    _rollback_handlers[prompt_name] = handler
    logger.debug(f"Registered rollback handler for '{prompt_name}'")


def unregister_rollback_handler(prompt_name: str) -> bool:
    """
    Unregister a rollback handler for a specific prompt.

    Args:
        prompt_name: The name of the prompt to unregister.

    Returns:
        True if a handler was found and removed, False otherwise.
    """
    if prompt_name in _rollback_handlers:
        del _rollback_handlers[prompt_name]
        logger.debug(f"Unregistered rollback handler for '{prompt_name}'")
        return True
    return False


def register_rollback_event_callback(
    callback: Callable[[RollbackHistoryEntry], None]
) -> None:
    """
    Register a callback to be invoked after each rollback operation.

    Args:
        callback: Function that receives RollbackHistoryEntry after each rollback.
    """
    _rollback_event_callbacks.append(callback)


def register_circuit_event_callback(
    callback: Callable[[str, CircuitState, CircuitState], None]
) -> None:
    """
    Register a callback to be invoked when circuit state changes.

    Args:
        callback: Function that receives (prompt_name, old_state, new_state).
    """
    _circuit_event_callbacks.append(callback)


def configure_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 2,
    rate_limit_threshold: float = 10.0,
) -> None:
    """
    Configure the default circuit breaker settings.

    Args:
        failure_threshold: Number of failures before opening the circuit.
        recovery_timeout: Seconds to wait before attempting recovery.
        success_threshold: Successes needed in half-open state to close.
        rate_limit_threshold: Failures per minute that triggers opening.
    """
    global _default_circuit_config
    _default_circuit_config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        success_threshold=success_threshold,
        rate_limit_threshold=rate_limit_threshold,
    )
    logger.info(f"Configured circuit breaker: {_default_circuit_config}")


def rollback_prompt(prompt_name: str, reason: Optional[str] = None) -> RollbackHistoryEntry:
    """
    Execute the rollback operation for a specific prompt.

    If a custom handler is registered, it will be used. Otherwise,
    a default rollback operation is performed.

    Args:
        prompt_name: The name of the prompt to roll back.
        reason: Optional reason for the rollback.

    Returns:
        RollbackHistoryEntry with details of the operation.

    Raises:
        RollbackError: If the rollback operation fails.
    """
    logger.info(f"Executing rollback for prompt '{prompt_name}'")
    start_time = time.time()
    failure_cnt = count(prompt_name)
    
    entry = RollbackHistoryEntry(
        prompt_name=prompt_name,
        timestamp=start_time,
        action=RollbackAction.TRIGGERED,
        failure_count=failure_cnt,
        threshold=_default_circuit_config.failure_threshold,
        success=False,
    )
    
    try:
        if prompt_name in _rollback_handlers:
            _rollback_handlers[prompt_name](prompt_name)
        else:
            _default_rollback(prompt_name)
        
        # Reset failure count after successful rollback
        reset(prompt_name)
        
        # Reset circuit breaker
        if prompt_name in _circuit_states:
            _transition_circuit(prompt_name, CircuitState.CLOSED)
        
        entry.success = True
        entry.duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Successfully rolled back prompt '{prompt_name}'")
        
    except Exception as e:
        entry.success = False
        entry.error_message = str(e)
        entry.duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Rollback failed for prompt '{prompt_name}': {e}")
        
        # Record in history before raising
        _add_history_entry(entry)
        raise RollbackError(f"Failed to rollback prompt '{prompt_name}': {e}") from e
    
    _add_history_entry(entry)
    return entry


def _add_history_entry(entry: RollbackHistoryEntry) -> None:
    """Add an entry to the rollback history."""
    _rollback_history.append(entry)
    
    # Trim history if needed
    while len(_rollback_history) > _max_history_entries:
        _rollback_history.pop(0)
    
    # Invoke callbacks
    for callback in _rollback_event_callbacks:
        try:
            callback(entry)
        except Exception as e:
            logger.error(f"Rollback event callback error: {e}")


def _default_rollback(prompt_name: str) -> None:
    """
    Default rollback behavior when no custom handler is registered.

    Args:
        prompt_name: The name of the prompt being rolled back.
    """
    logger.warning(
        f"No custom rollback handler for '{prompt_name}'. "
        "Using default behavior (logging only)."
    )


def _get_circuit_state(prompt_name: str) -> CircuitBreakerState:
    """Get or create circuit breaker state for a prompt."""
    if prompt_name not in _circuit_states:
        _circuit_states[prompt_name] = CircuitBreakerState()
    return _circuit_states[prompt_name]


def _transition_circuit(prompt_name: str, new_state: CircuitState) -> None:
    """Transition circuit breaker to a new state."""
    state = _get_circuit_state(prompt_name)
    old_state = state.state
    
    if old_state == new_state:
        return
    
    state.state = new_state
    
    if new_state == CircuitState.OPEN:
        state.opened_at = time.time()
        state.consecutive_successes = 0
    elif new_state == CircuitState.CLOSED:
        state.opened_at = None
        state.consecutive_successes = 0
    
    logger.info(f"Circuit breaker for '{prompt_name}': {old_state.value} -> {new_state.value}")
    
    # Invoke callbacks
    for callback in _circuit_event_callbacks:
        try:
            callback(prompt_name, old_state, new_state)
        except Exception as e:
            logger.error(f"Circuit event callback error: {e}")


def check_circuit(prompt_name: str) -> CircuitState:
    """
    Check the current circuit breaker state for a prompt.

    This automatically transitions from OPEN to HALF_OPEN if the
    recovery timeout has elapsed.

    Args:
        prompt_name: The name of the prompt to check.

    Returns:
        The current CircuitState.
    """
    state = _get_circuit_state(prompt_name)
    
    if state.state == CircuitState.OPEN and state.opened_at:
        elapsed = time.time() - state.opened_at
        if elapsed >= _default_circuit_config.recovery_timeout:
            _transition_circuit(prompt_name, CircuitState.HALF_OPEN)
    
    return state.state


def record_success(prompt_name: str) -> CircuitState:
    """
    Record a successful operation for circuit breaker recovery.

    Args:
        prompt_name: The name of the prompt that succeeded.

    Returns:
        The new CircuitState after recording success.
    """
    state = _get_circuit_state(prompt_name)
    state.last_success_time = time.time()
    
    if state.state == CircuitState.HALF_OPEN:
        state.consecutive_successes += 1
        if state.consecutive_successes >= _default_circuit_config.success_threshold:
            _transition_circuit(prompt_name, CircuitState.CLOSED)
            # Decrease failure count on recovery
            decrement(prompt_name)
    
    return state.state


def record_failure_for_circuit(prompt_name: str) -> CircuitState:
    """
    Record a failure for circuit breaker evaluation.

    Args:
        prompt_name: The name of the prompt that failed.

    Returns:
        The new CircuitState after recording failure.
    """
    state = _get_circuit_state(prompt_name)
    state.last_failure_time = time.time()
    state.consecutive_successes = 0
    
    failure_count = count(prompt_name)
    failure_rate = get_failure_rate(prompt_name)
    
    # Check if we should open the circuit
    should_open = (
        failure_count >= _default_circuit_config.failure_threshold or
        failure_rate >= _default_circuit_config.rate_limit_threshold
    )
    
    if should_open and state.state != CircuitState.OPEN:
        _transition_circuit(prompt_name, CircuitState.OPEN)
    elif state.state == CircuitState.HALF_OPEN:
        # Failed during half-open, go back to open
        _transition_circuit(prompt_name, CircuitState.OPEN)
    
    return state.state


def get_circuit_info(prompt_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a circuit breaker.

    Args:
        prompt_name: The name of the prompt.

    Returns:
        Dictionary with circuit breaker details.
    """
    state = _get_circuit_state(prompt_name)
    current_time = time.time()
    
    retry_after = None
    if state.state == CircuitState.OPEN and state.opened_at:
        remaining = _default_circuit_config.recovery_timeout - (current_time - state.opened_at)
        retry_after = max(0, remaining)
    
    return {
        "prompt_name": prompt_name,
        "state": state.state.value,
        "last_failure_time": state.last_failure_time,
        "last_success_time": state.last_success_time,
        "consecutive_successes": state.consecutive_successes,
        "opened_at": state.opened_at,
        "retry_after": retry_after,
        "failure_count": count(prompt_name),
        "failure_rate": get_failure_rate(prompt_name),
    }


def require_circuit_closed(prompt_name: str) -> None:
    """
    Check if circuit is closed, raise if open.

    Use this as a guard before executing a prompt.

    Args:
        prompt_name: The name of the prompt to check.

    Raises:
        CircuitOpenError: If the circuit is open.
    """
    state = check_circuit(prompt_name)
    
    if state == CircuitState.OPEN:
        circuit_state = _get_circuit_state(prompt_name)
        retry_after = 0.0
        if circuit_state.opened_at:
            retry_after = max(
                0,
                _default_circuit_config.recovery_timeout - 
                (time.time() - circuit_state.opened_at)
            )
        raise CircuitOpenError(prompt_name, retry_after)


def maybe_rollback(
    prompt: PromptProtocol,
    policy: Dict[str, Any],
    auto_execute: bool = False,
) -> RollbackResult:
    """
    Check if a prompt should be rolled back based on its failure count and policy.

    Args:
        prompt: The prompt object to check. Must have a 'name' attribute.
        policy: A dictionary containing rollback policy settings.
            - 'failures': The failure threshold (default: 3).
            - 'enabled': Whether rollback is enabled (default: True).
        auto_execute: If True, automatically execute the rollback when triggered.

    Returns:
        RollbackResult containing the action taken and relevant details.

    Example:
        >>> result = maybe_rollback(prompt, {"failures": 3})
        >>> if result.action == RollbackAction.TRIGGERED:
        ...     print(f"Rolled back: {result.message}")
    """
    prompt_name = prompt.name
    threshold = policy.get("failures", 3)
    enabled = policy.get("enabled", True)
    current_count = count(prompt_name)
    
    if not enabled:
        logger.debug(f"Rollback disabled for '{prompt_name}' by policy")
        return RollbackResult(
            action=RollbackAction.NONE,
            prompt_name=prompt_name,
            failure_count=current_count,
            threshold=threshold,
            message="Rollback disabled by policy",
        )
    
    if current_count >= threshold:
        logger.warning(
            f"Prompt '{prompt_name}' has reached failure threshold "
            f"({current_count}/{threshold})"
        )
        
        if auto_execute:
            rollback_prompt(prompt_name)
        
        return RollbackResult(
            action=RollbackAction.TRIGGERED,
            prompt_name=prompt_name,
            failure_count=current_count,
            threshold=threshold,
            message=f"Rolling back prompt '{prompt_name}' "
                    f"(failures: {current_count}, threshold: {threshold})",
        )
    
    logger.debug(
        f"Prompt '{prompt_name}' below threshold ({current_count}/{threshold})"
    )
    return RollbackResult(
        action=RollbackAction.NONE,
        prompt_name=prompt_name,
        failure_count=current_count,
        threshold=threshold,
        message=f"Prompt '{prompt_name}' is healthy "
                f"(failures: {current_count}, threshold: {threshold})",
    )


def check_all_prompts(
    prompts: list,
    policy: Dict[str, Any],
) -> list[RollbackResult]:
    """
    Check multiple prompts for rollback conditions.

    Args:
        prompts: List of prompt objects to check.
        policy: The rollback policy to apply.

    Returns:
        List of RollbackResult for each prompt.
    """
    results = []
    for prompt in prompts:
        result = maybe_rollback(prompt, policy)
        results.append(result)
    return results


def get_rollback_history(
    prompt_name: Optional[str] = None,
    limit: int = 100,
    since: Optional[float] = None,
    success_only: Optional[bool] = None,
) -> List[RollbackHistoryEntry]:
    """
    Get rollback history entries.

    Args:
        prompt_name: Filter by specific prompt (None for all).
        limit: Maximum number of entries to return.
        since: Only return entries after this timestamp.
        success_only: Filter by success status (None for all).

    Returns:
        List of RollbackHistoryEntry, most recent first.
    """
    entries = list(reversed(_rollback_history))
    
    if prompt_name:
        entries = [e for e in entries if e.prompt_name == prompt_name]
    
    if since is not None:
        entries = [e for e in entries if e.timestamp >= since]
    
    if success_only is not None:
        entries = [e for e in entries if e.success == success_only]
    
    return entries[:limit]


def get_health_summary() -> Dict[str, Any]:
    """
    Get a health summary of all tracked prompts.

    Returns:
        Dictionary with overall health metrics and per-prompt status.
    """
    from .store import list_failures, get_all_stats
    
    failures = list_failures()
    stats = get_all_stats()
    
    # Get circuit breaker states
    circuits = {
        name: get_circuit_info(name)
        for name in set(failures.keys()) | set(_circuit_states.keys())
    }
    
    healthy_count = sum(1 for s in stats.values() if s.is_healthy)
    unhealthy_count = len(stats) - healthy_count
    open_circuits = sum(1 for c in circuits.values() if c["state"] == "open")
    
    # Recent rollbacks
    recent_rollbacks = get_rollback_history(limit=10)
    recent_failures = sum(1 for r in recent_rollbacks if not r.success)
    
    return {
        "total_prompts_tracked": len(failures),
        "healthy_prompts": healthy_count,
        "unhealthy_prompts": unhealthy_count,
        "open_circuits": open_circuits,
        "recent_rollbacks": len(recent_rollbacks),
        "recent_rollback_failures": recent_failures,
        "prompts": {
            name: {
                "failures": failures.get(name, 0),
                "circuit_state": circuits.get(name, {}).get("state", "closed"),
                "failure_rate": stats.get(name, get_stats(name)).failure_rate_per_minute,
            }
            for name in set(failures.keys()) | set(_circuit_states.keys())
        },
    }


def validate_policy(policy: Dict[str, Any]) -> List[str]:
    """
    Validate a rollback policy configuration.

    Args:
        policy: The policy dictionary to validate.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []
    
    if "failures" in policy:
        if not isinstance(policy["failures"], int) or policy["failures"] < 1:
            errors.append("'failures' must be a positive integer")
    
    if "enabled" in policy:
        if not isinstance(policy["enabled"], bool):
            errors.append("'enabled' must be a boolean")
    
    if "rate_limit" in policy:
        if not isinstance(policy["rate_limit"], (int, float)) or policy["rate_limit"] <= 0:
            errors.append("'rate_limit' must be a positive number")
    
    if "recovery_timeout" in policy:
        if not isinstance(policy["recovery_timeout"], (int, float)) or policy["recovery_timeout"] < 0:
            errors.append("'recovery_timeout' must be a non-negative number")
    
    return errors


def reset_all_circuits() -> int:
    """
    Reset all circuit breakers to closed state.

    Returns:
        Number of circuits that were reset.
    """
    count = 0
    for prompt_name in list(_circuit_states.keys()):
        if _circuit_states[prompt_name].state != CircuitState.CLOSED:
            _transition_circuit(prompt_name, CircuitState.CLOSED)
            count += 1
    
    logger.info(f"Reset {count} circuit breakers")
    return count


def clear_rollback_history() -> int:
    """
    Clear the rollback history.

    Returns:
        Number of entries that were cleared.
    """
    count = len(_rollback_history)
    _rollback_history.clear()
    logger.info(f"Cleared {count} rollback history entries")
    return count


class RollbackContext:
    """
    Context manager for automatic failure tracking and circuit breaker integration.

    Example:
        >>> with RollbackContext("my_prompt") as ctx:
        ...     result = execute_prompt()
        ...     ctx.mark_success()
    """
    
    def __init__(self, prompt_name: str, check_circuit: bool = True):
        """
        Initialize the rollback context.

        Args:
            prompt_name: The name of the prompt being executed.
            check_circuit: If True, check circuit breaker on entry.
        """
        self.prompt_name = prompt_name
        self.check_circuit = check_circuit
        self._success = False
        self._error: Optional[Exception] = None
    
    def __enter__(self) -> "RollbackContext":
        if self.check_circuit:
            require_circuit_closed(self.prompt_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self._error = exc_val
            self._record_failure(exc_type, exc_val)
        elif not self._success:
            # No explicit success, treat as implicit failure
            self._record_failure(None, None)
        
        return False  # Don't suppress exceptions
    
    def mark_success(self) -> None:
        """Mark the operation as successful."""
        self._success = True
        record_success(self.prompt_name)
    
    def _record_failure(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
    ) -> None:
        """Record a failure internally."""
        from .store import record as store_record
        
        error_type = exc_type.__name__ if exc_type else None
        error_message = str(exc_val) if exc_val else None
        
        store_record(
            self.prompt_name,
            error_type=error_type,
            error_message=error_message,
        )
        record_failure_for_circuit(self.prompt_name)
