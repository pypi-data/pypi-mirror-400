"""Tests for rollback module."""

import pytest
import time
from promptops.rollback.engine import (
    RollbackAction,
    RollbackResult,
    RollbackHistoryEntry,
    RollbackError,
    RollbackContext,
    rollback_prompt,
    get_rollback_history,
)
from promptops.rollback.store import (
    record,
    count,
    reset,
    get_failure_history,
    FailureRecord,
)


class TestRollbackAction:
    """Test RollbackAction enum."""
    
    def test_action_values(self):
        """Test rollback action values."""
        assert RollbackAction.NONE.value == "none"
        assert RollbackAction.TRIGGERED.value == "triggered"
        assert RollbackAction.CIRCUIT_OPEN.value == "circuit_open"


class TestRollbackResult:
    """Test RollbackResult dataclass."""
    
    def test_result_creation(self):
        """Test creating rollback result."""
        result = RollbackResult(
            action=RollbackAction.TRIGGERED,
            prompt_name="test",
            failure_count=3,
            threshold=5,
            message="Testing rollback",
        )
        assert result.action == RollbackAction.TRIGGERED
        assert result.prompt_name == "test"
        assert result.failure_count == 3
        assert result.threshold == 5
        assert "Testing" in result.message


class TestRollbackHistoryEntry:
    """Test RollbackHistoryEntry dataclass."""
    
    def test_entry_creation(self):
        """Test creating history entry."""
        now = time.time()
        entry = RollbackHistoryEntry(
            prompt_name="test",
            timestamp=now,
            action=RollbackAction.TRIGGERED,
            failure_count=10,
            threshold=5,
            success=False,
            error_message="Testing",
            duration_ms=12.3,
        )
        assert entry.prompt_name == "test"
        assert entry.timestamp == now
        assert entry.error_message == "Testing"


class TestRollbackContext:
    """Test RollbackContext context manager."""
    
    def test_context_creation(self):
        """Test creating rollback context."""
        ctx = RollbackContext("test_prompt", check_circuit=False)
        assert ctx.prompt_name == "test_prompt"
        assert ctx.check_circuit is False
    
    def test_context_manager(self):
        """Test using as context manager."""
        with RollbackContext("test", check_circuit=False) as ctx:
            assert ctx.prompt_name == "test"
            ctx.mark_success()


class TestFailureStore:
    """Test FailureStore class."""
    
    def test_record_failure(self):
        """Test recording a failure."""
        reset("test_prompt")
        record("test_prompt", error_message="Test error")
        
        failures = get_failure_history("test_prompt", limit=1)
        assert len(failures) > 0
        assert failures[0].prompt_name == "test_prompt"
    
    def test_failure_count(self):
        """Test getting failure count."""
        reset("test")
        record("test", error_message="Error 1")
        record("test", error_message="Error 2")
        
        total = count("test")
        assert total == 2
    
    def test_clear_failures(self):
        """Test clearing failures."""
        reset("test")
        record("test", error_message="Error")
        reset("test")
        
        total = count("test")
        assert total == 0


class TestFailureRecord:
    """Test FailureRecord dataclass."""
    
    def test_record_creation(self):
        """Test creating failure record."""
        now = time.time()
        record = FailureRecord(
            prompt_name="test",
            error_message="Test error",
            timestamp=now,
        )
        assert record.prompt_name == "test"
        assert record.error_message == "Test error"
        assert record.timestamp == now
