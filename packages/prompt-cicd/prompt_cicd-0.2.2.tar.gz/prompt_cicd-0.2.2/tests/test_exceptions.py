"""Tests for promptops.exceptions module."""

import pytest
import json
from datetime import datetime

from promptops.exceptions import (
    PromptOpsError,
    SafetyViolation,
    ApprovalRequired,
    ApprovalExpired,
    ApprovalRejected,
)


class TestPromptOpsError:
    """Tests for the base PromptOpsError class."""

    def test_basic_creation(self):
        """Test creating a basic error with just a message."""
        error = PromptOpsError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.details == {}
        assert error.cause is None
        assert isinstance(error.timestamp, datetime)

    def test_creation_with_details(self):
        """Test creating an error with details."""
        details = {"key": "value", "count": 42}
        error = PromptOpsError("Error with details", details=details)
        assert error.details == details

    def test_creation_with_cause(self):
        """Test creating an error with a cause exception."""
        cause = ValueError("Original error")
        error = PromptOpsError("Wrapped error", cause=cause)
        assert error.cause is cause

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = PromptOpsError("Test error", details={"foo": "bar"})
        result = error.to_dict()
        
        assert result["error_type"] == "PromptOpsError"
        assert result["message"] == "Test error"
        assert result["details"] == {"foo": "bar"}
        assert "timestamp" in result
        assert result["cause"] is None

    def test_to_dict_with_cause(self):
        """Test to_dict includes cause information."""
        cause = ValueError("Root cause")
        error = PromptOpsError("Wrapped", cause=cause)
        result = error.to_dict()
        assert result["cause"] == "Root cause"

    def test_to_json(self):
        """Test converting error to JSON string."""
        error = PromptOpsError("JSON test")
        json_str = error.to_json()
        parsed = json.loads(json_str)
        assert parsed["message"] == "JSON test"

    def test_str_representation(self):
        """Test string representation of error."""
        error = PromptOpsError("String test")
        result = str(error)
        assert "PromptOpsError" in result
        assert "String test" in result

    def test_str_with_details(self):
        """Test string representation includes details."""
        error = PromptOpsError("Detailed error", details={"info": "extra"})
        result = str(error)
        assert "Details:" in result

    def test_str_with_cause(self):
        """Test string representation includes cause."""
        cause = Exception("Root")
        error = PromptOpsError("With cause", cause=cause)
        result = str(error)
        assert "Caused by:" in result


class TestSafetyViolation:
    """Tests for SafetyViolation exception."""

    def test_basic_creation(self):
        """Test creating a safety violation."""
        error = SafetyViolation("Unsafe content detected")
        assert error.message == "Unsafe content detected"
        assert error.findings == []
        assert error.risk_score is None

    def test_with_findings(self):
        """Test safety violation with findings."""
        findings = ["PII detected", "Injection attempt"]
        error = SafetyViolation("Unsafe", findings=findings)
        assert error.findings == findings
        assert error.details["findings"] == findings

    def test_with_risk_score(self):
        """Test safety violation with risk score."""
        error = SafetyViolation("Risky", risk_score=0.85)
        assert error.risk_score == 0.85
        assert error.details["risk_score"] == 0.85


class TestApprovalRequired:
    """Tests for ApprovalRequired exception."""

    def test_basic_creation(self):
        """Test creating an approval required error."""
        error = ApprovalRequired("Approval needed")
        assert error.message == "Approval needed"
        assert error.prompt_name is None
        assert error.environment is None

    def test_with_prompt_info(self):
        """Test approval required with prompt information."""
        error = ApprovalRequired(
            "Needs approval",
            prompt_name="my-prompt",
            environment="prod"
        )
        assert error.prompt_name == "my-prompt"
        assert error.environment == "prod"
        assert error.details["prompt_name"] == "my-prompt"
        assert error.details["environment"] == "prod"


class TestApprovalExpired:
    """Tests for ApprovalExpired exception."""

    def test_is_approval_required_subclass(self):
        """Test that ApprovalExpired is a subclass of ApprovalRequired."""
        error = ApprovalExpired("Approval expired")
        assert isinstance(error, ApprovalRequired)
        assert isinstance(error, PromptOpsError)


class TestApprovalRejected:
    """Tests for ApprovalRejected exception."""

    def test_with_rejection_reason(self):
        """Test rejection with reason."""
        error = ApprovalRejected("Rejected", reason="Policy violation")
        assert error.rejection_reason == "Policy violation"
        assert error.details["rejection_reason"] == "Policy violation"
