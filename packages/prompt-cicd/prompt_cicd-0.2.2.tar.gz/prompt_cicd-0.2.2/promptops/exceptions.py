"""
Exception hierarchy for PromptOps.

Provides detailed, structured exceptions for all PromptOps operations.
"""

from typing import Any, Dict, Optional
from datetime import datetime, timezone
import json


class PromptOpsError(Exception):
    """Base exception for all PromptOps errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None
        }
    
    def to_json(self) -> str:
        """Convert exception to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        base = f"{self.__class__.__name__}: {self.message}"
        if self.details:
            base += f"\nDetails: {self.details}"
        if self.cause:
            base += f"\nCaused by: {self.cause}"
        return base


# Safety-related exceptions
class SafetyViolation(PromptOpsError):
    """Raised when safety checks fail."""
    
    def __init__(
        self,
        message: str,
        findings: Optional[list] = None,
        risk_score: Optional[float] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["findings"] = findings or []
        details["risk_score"] = risk_score
        super().__init__(message, details, kwargs.get("cause"))
        self.findings = findings or []
        self.risk_score = risk_score


# Approval-related exceptions
class ApprovalRequired(PromptOpsError):
    """Raised when approval is required but not granted."""
    
    def __init__(
        self,
        message: str,
        prompt_name: Optional[str] = None,
        environment: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["prompt_name"] = prompt_name
        details["environment"] = environment
        super().__init__(message, details, kwargs.get("cause"))
        self.prompt_name = prompt_name
        self.environment = environment


class ApprovalExpired(ApprovalRequired):
    """Raised when an approval has expired."""
    pass


class ApprovalRejected(ApprovalRequired):
    """Raised when an approval is explicitly rejected."""
    
    def __init__(self, message: str, reason: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        details["rejection_reason"] = reason
        kwargs["details"] = details
        super().__init__(message, **kwargs)
        self.rejection_reason = reason


# Budget-related exceptions
class BudgetExceeded(PromptOpsError):
    """Raised when budget limits are exceeded."""
    
    def __init__(
        self,
        message: str,
        current_cost: Optional[float] = None,
        max_cost: Optional[float] = None,
        budget_name: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["current_cost"] = current_cost
        details["max_cost"] = max_cost
        details["budget_name"] = budget_name
        super().__init__(message, details, kwargs.get("cause"))
        self.current_cost = current_cost
        self.max_cost = max_cost
        self.budget_name = budget_name


class InsufficientBudget(BudgetExceeded):
    """Raised when there's not enough budget for an operation."""
    pass


# Testing-related exceptions
class TestFailureError(PromptOpsError):
    """Raised when prompt tests fail."""
    
    def __init__(
        self,
        message: str,
        test_name: Optional[str] = None,
        expected: Optional[Any] = None,
        actual: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["test_name"] = test_name
        details["expected"] = str(expected) if expected is not None else None
        details["actual"] = str(actual) if actual is not None else None
        super().__init__(message, details, kwargs.get("cause"))
        self.test_name = test_name
        self.expected = expected
        self.actual = actual


# Rollback-related exceptions
class RollbackError(PromptOpsError):
    """Raised when rollback operations fail."""
    
    def __init__(
        self,
        message: str,
        prompt_name: Optional[str] = None,
        failure_count: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["prompt_name"] = prompt_name
        details["failure_count"] = failure_count
        super().__init__(message, details, kwargs.get("cause"))
        self.prompt_name = prompt_name
        self.failure_count = failure_count


class CircuitBreakerOpen(RollbackError):
    """Raised when circuit breaker is open."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["retry_after_seconds"] = retry_after
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


# Provider-related exceptions
class ProviderError(PromptOpsError):
    """Base exception for provider errors."""
    pass


class RateLimitError(ProviderError):
    """Raised when rate limits are hit."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["retry_after_seconds"] = retry_after
        super().__init__(message, details, kwargs.get("cause"))
        self.retry_after = retry_after


class AuthenticationError(ProviderError):
    """Raised when authentication fails."""
    pass


class ModelNotFoundError(ProviderError):
    """Raised when a model is not found or unavailable."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        details["model_name"] = model_name
        super().__init__(message, details, kwargs.get("cause"))
        self.model_name = model_name


# Configuration exceptions
class ConfigurationError(PromptOpsError):
    """Raised when configuration is invalid."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["config_key"] = config_key
        details["invalid_value"] = str(invalid_value) if invalid_value is not None else None
        super().__init__(message, details, kwargs.get("cause"))
        self.config_key = config_key
        self.invalid_value = invalid_value


class ValidationError(PromptOpsError):
    """Raised when validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        details["field"] = field
        details["value"] = str(value) if value is not None else None
        super().__init__(message, details, kwargs.get("cause"))
        self.field = field
        self.value = value
