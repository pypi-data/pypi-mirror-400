"""Tests for promptops.policies module."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from promptops.policies import PolicyManager, load_policies
from promptops.exceptions import ConfigurationError


class TestPolicyManager:
    """Tests for PolicyManager class."""

    @pytest.fixture
    def policy_file(self, temp_dir):
        """Create a temporary policy file."""
        policy_path = temp_dir / "promptops.yaml"
        policies = {
            "policies": {
                "approval": {
                    "require_production": True,
                    "timeout_hours": 24,
                },
                "safety": {
                    "strict_mode": True,
                    "block_pii": True,
                },
            }
        }
        policy_path.write_text(yaml.safe_dump(policies))
        return policy_path

    @pytest.fixture
    def manager(self, policy_file):
        """Create a PolicyManager with test policies."""
        return PolicyManager(policy_file=policy_file)

    def test_load_policies(self, manager):
        """Test loading policies from file."""
        approval = manager.get("approval")
        assert approval is not None
        assert approval.get("require_production") is True

    def test_get_specific_policy(self, manager):
        """Test getting a specific policy by name."""
        timeout = manager.get("approval", "timeout_hours")
        assert timeout == 24

    def test_get_nonexistent_policy(self, manager):
        """Test getting a non-existent policy returns empty dict."""
        result = manager.get("nonexistent")
        assert result == {}

    def test_get_nonexistent_policy_name(self, manager):
        """Test getting a non-existent policy name returns None."""
        result = manager.get("approval", "nonexistent")
        assert result is None

    def test_set_policy(self, manager, policy_file):
        """Test setting a policy value."""
        manager.set("approval", "new_key", "new_value")
        assert manager.get("approval", "new_key") == "new_value"
        
        # Verify it's saved to file
        data = yaml.safe_load(policy_file.read_text())
        assert data["policies"]["approval"]["new_key"] == "new_value"

    def test_set_new_policy_type(self, manager):
        """Test setting a new policy type."""
        manager.set("custom", "setting", True)
        assert manager.get("custom", "setting") is True

    def test_evaluate_simple_policy(self, manager):
        """Test evaluating a simple policy."""
        # Simple boolean policy
        manager.set("test", "allowed", True)
        result = manager.evaluate("test", "allowed", {})
        assert result is True

    def test_evaluate_rule_policy(self, manager):
        """Test evaluating a policy with a rule."""
        manager.set("access", "admin_only", {"rule": "role == 'admin'"})
        
        result_admin = manager.evaluate("access", "admin_only", {"role": "admin"})
        assert result_admin is True
        
        result_user = manager.evaluate("access", "admin_only", {"role": "user"})
        assert result_user is False

    def test_evaluate_nonexistent_policy(self, manager):
        """Test evaluating a non-existent policy returns True (default allow)."""
        result = manager.evaluate("nonexistent", "policy", {})
        assert result is True

    def test_load_missing_file(self, temp_dir):
        """Test loading from missing file sets empty policies."""
        missing_path = temp_dir / "nonexistent.yaml"
        manager = PolicyManager(policy_file=missing_path)
        assert manager.get("any") == {}

    def test_load_invalid_yaml(self, temp_dir):
        """Test loading invalid YAML raises ConfigurationError."""
        invalid_path = temp_dir / "invalid.yaml"
        invalid_path.write_text("{ invalid: yaml: content }")
        
        with pytest.raises(ConfigurationError):
            PolicyManager(policy_file=invalid_path)

    def test_callback_on_set(self, manager):
        """Test callback is called when policy is set."""
        callback = Mock()
        manager.add_callback(callback)
        manager.set("test", "key", "value")
        callback.assert_called_once_with("test", "key", "value")


class TestLoadPolicies:
    """Tests for load_policies function."""

    def test_load_policies_returns_dict(self):
        """Test load_policies returns a dictionary."""
        with patch.object(Path, 'exists', return_value=False):
            result = load_policies()
            assert isinstance(result, dict)
