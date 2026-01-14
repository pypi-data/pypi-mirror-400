"""
Rollback module for managing prompt failure tracking and automatic rollback.

This module provides functionality to:
- Track prompt execution failures with TTL and persistence
- Trigger automatic rollback when failure thresholds are exceeded
- Circuit breaker pattern for protecting failing prompts
- Comprehensive failure statistics and health monitoring
- Rollback history and audit logging
"""

from .engine import (
    # Core rollback functionality
    maybe_rollback,
    rollback_prompt,
    check_all_prompts,
    # Rollback actions and results
    RollbackAction,
    RollbackResult,
    RollbackError,
    RollbackHistoryEntry,
    # Circuit breaker
    CircuitState,
    CircuitBreakerConfig,
    CircuitOpenError,
    check_circuit,
    require_circuit_closed,
    record_success,
    record_failure_for_circuit,
    get_circuit_info,
    configure_circuit_breaker,
    reset_all_circuits,
    # Handler registration
    register_rollback_handler,
    unregister_rollback_handler,
    register_rollback_event_callback,
    register_circuit_event_callback,
    # History and health
    get_rollback_history,
    clear_rollback_history,
    get_health_summary,
    validate_policy,
    # Context manager
    RollbackContext,
)

from .store import (
    # Core failure tracking
    record,
    count,
    reset,
    clear_all,
    list_failures,
    # Configuration
    configure,
    # Enhanced counting
    count_in_window,
    get_failure_rate,
    decrement,
    # Statistics
    get_stats,
    get_all_stats,
    get_prompts_above_threshold,
    # History
    get_failure_history,
    record_batch,
    # Snapshot/restore
    create_snapshot,
    restore_snapshot,
    # Callbacks
    register_failure_callback,
    unregister_failure_callback,
    # Data classes
    FailureRecord,
    FailureStats,
)

__all__ = [
    # Engine - Core
    "maybe_rollback",
    "rollback_prompt",
    "check_all_prompts",
    # Engine - Types
    "RollbackAction",
    "RollbackResult",
    "RollbackError",
    "RollbackHistoryEntry",
    # Engine - Circuit breaker
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "check_circuit",
    "require_circuit_closed",
    "record_success",
    "record_failure_for_circuit",
    "get_circuit_info",
    "configure_circuit_breaker",
    "reset_all_circuits",
    # Engine - Handlers
    "register_rollback_handler",
    "unregister_rollback_handler",
    "register_rollback_event_callback",
    "register_circuit_event_callback",
    # Engine - History/Health
    "get_rollback_history",
    "clear_rollback_history",
    "get_health_summary",
    "validate_policy",
    # Engine - Context manager
    "RollbackContext",
    # Store - Core
    "record",
    "count",
    "reset",
    "clear_all",
    "list_failures",
    # Store - Config
    "configure",
    # Store - Enhanced
    "count_in_window",
    "get_failure_rate",
    "decrement",
    # Store - Statistics
    "get_stats",
    "get_all_stats",
    "get_prompts_above_threshold",
    # Store - History
    "get_failure_history",
    "record_batch",
    # Store - Snapshot
    "create_snapshot",
    "restore_snapshot",
    # Store - Callbacks
    "register_failure_callback",
    "unregister_failure_callback",
    # Store - Types
    "FailureRecord",
    "FailureStats",
]
