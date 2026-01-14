"""Tests for promptops.guard module."""

import pytest
from unittest.mock import Mock, patch

from promptops.guard import Guard, enforce_safety
from promptops.exceptions import SafetyViolation


class TestGuard:
    """Tests for Guard class."""

    @pytest.fixture
    def guard(self):
        """Create a fresh Guard instance for each test."""
        return Guard()

    def test_enforce_safe_text(self, guard):
        """Test enforce passes with safe text."""
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_report.findings = []
            mock_scan.return_value = mock_report
            
            # Should not raise
            guard.enforce("Hello, world!", env="dev")

    def test_enforce_unsafe_text_raises(self, guard):
        """Test enforce raises SafetyViolation for unsafe text."""
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_finding = Mock()
            mock_finding.message = "PII detected"
            mock_report = Mock()
            mock_report.safe = False
            mock_report.findings = [mock_finding]
            mock_report.risk = 0.9
            mock_scan.return_value = mock_report
            
            with pytest.raises(SafetyViolation):
                guard.enforce("SSN: 123-45-6789", env="prod")

    def test_add_custom_rule(self, guard):
        """Test adding a custom guard rule."""
        def custom_rule(text, env, context):
            if "forbidden" in text.lower():
                return SafetyViolation("Forbidden word detected")
            return None
        
        guard.add_rule(custom_rule)
        
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            with pytest.raises(SafetyViolation, match="Forbidden word"):
                guard.enforce("This contains forbidden content", env="dev")

    def test_custom_rule_passes(self, guard):
        """Test custom rule that passes."""
        def custom_rule(text, env, context):
            return None  # Always pass
        
        guard.add_rule(custom_rule)
        
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            # Should not raise
            guard.enforce("Safe content", env="dev")

    def test_callback_called_on_pass(self, guard):
        """Test callback is called when guard passes."""
        callback = Mock()
        guard.add_callback(callback)
        
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            guard.enforce("Safe text", env="dev", context={"key": "value"})
            
            callback.assert_called_once()
            args = callback.call_args[0]
            assert args[0] == "Safe text"
            assert args[1] == "dev"
            assert args[3] is None  # No exception

    def test_callback_called_on_failure(self, guard):
        """Test callback is called when guard fails."""
        callback = Mock()
        guard.add_callback(callback)
        
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_finding = Mock()
            mock_finding.message = "Unsafe"
            mock_report = Mock()
            mock_report.safe = False
            mock_report.findings = [mock_finding]
            mock_report.risk = 0.8
            mock_scan.return_value = mock_report
            
            with pytest.raises(SafetyViolation):
                guard.enforce("Unsafe text", env="prod")
            
            callback.assert_called_once()
            args = callback.call_args[0]
            assert isinstance(args[3], SafetyViolation)

    def test_callback_exception_handled(self, guard):
        """Test that callback exceptions are handled gracefully."""
        def bad_callback(text, env, context, exc):
            raise RuntimeError("Callback error")
        
        guard.add_callback(bad_callback)
        
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            # Should not raise despite callback error
            guard.enforce("Safe text", env="dev")

    def test_context_passed_to_rules(self, guard):
        """Test that context is passed to custom rules."""
        received_context = {}
        
        def context_capturing_rule(text, env, context):
            received_context.update(context)
            return None
        
        guard.add_rule(context_capturing_rule)
        
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            guard.enforce("text", env="dev", context={"prompt": "test"})
            
            assert received_context.get("prompt") == "test"


class TestEnforceSafety:
    """Tests for enforce_safety legacy function."""

    def test_safe_text_passes(self):
        """Test safe text does not raise."""
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            # Should not raise
            enforce_safety("Safe content", "dev")

    def test_unsafe_text_raises(self):
        """Test unsafe text raises SafetyViolation."""
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_finding = Mock()
            mock_finding.message = "Dangerous content"
            mock_report = Mock()
            mock_report.safe = False
            mock_report.findings = [mock_finding]
            mock_report.risk = 0.95
            mock_scan.return_value = mock_report
            
            with pytest.raises(SafetyViolation):
                enforce_safety("Dangerous content", "prod")

    def test_strict_mode_in_prod(self):
        """Test that prod environment uses strict mode."""
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            enforce_safety("text", "prod")
            
            # Verify strict=True was passed
            mock_scan.assert_called_once_with("text", True)

    def test_non_strict_mode_in_dev(self):
        """Test that dev environment uses non-strict mode."""
        with patch("promptops.guard.run_safety_scan") as mock_scan:
            mock_report = Mock()
            mock_report.safe = True
            mock_scan.return_value = mock_report
            
            enforce_safety("text", "dev")
            
            # Verify strict=False was passed
            mock_scan.assert_called_once_with("text", False)
