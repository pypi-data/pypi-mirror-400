"""
Safety scanning module for detecting sensitive content and potential risks.

This module provides comprehensive content scanning with support for:
- PII detection (SSN, credit cards, emails, phone numbers, etc.)
- Credential detection (API keys, passwords, tokens)
- Prompt injection detection
- Custom pattern matching
- Content redaction
- Risk scoring and severity levels
"""

from .scanner import (
    # Core classes
    SafetyScanner,
    SafetyReport,
    Finding,
    ScanRule,
    # Enums
    Severity,
    Category,
    # Convenience functions
    run_safety_scan,
    create_scanner_from_config,
    get_default_scanner,
    quick_scan,
    # Built-in patterns
    PII_PATTERNS,
    CREDENTIAL_PATTERNS,
    INJECTION_PATTERNS,
)

__all__ = [
    # Core classes
    "SafetyScanner",
    "SafetyReport",
    "Finding",
    "ScanRule",
    # Enums
    "Severity",
    "Category",
    # Functions
    "run_safety_scan",
    "create_scanner_from_config",
    "get_default_scanner",
    "quick_scan",
    # Patterns
    "PII_PATTERNS",
    "CREDENTIAL_PATTERNS",
    "INJECTION_PATTERNS",
]
