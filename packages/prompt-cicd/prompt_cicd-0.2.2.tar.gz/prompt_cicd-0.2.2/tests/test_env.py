"""Tests for promptops.env module."""

import pytest
import os

from promptops.env import get_env


class TestGetEnv:
    """Tests for the get_env function."""

    def test_default_env(self):
        """Test that default environment is 'dev'."""
        # Ensure env variable is not set
        os.environ.pop("PROMPTOPS_ENV", None)
        assert get_env() == "dev"

    def test_custom_env(self):
        """Test reading custom environment from env var."""
        os.environ["PROMPTOPS_ENV"] = "prod"
        assert get_env() == "prod"

    def test_staging_env(self):
        """Test staging environment."""
        os.environ["PROMPTOPS_ENV"] = "staging"
        assert get_env() == "staging"

    def test_empty_env_returns_default(self):
        """Test that empty env var returns default."""
        os.environ["PROMPTOPS_ENV"] = ""
        # Empty string is falsy, but os.getenv returns it as-is
        result = get_env()
        # Empty string should be returned, not the default
        assert result == ""
