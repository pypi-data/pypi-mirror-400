"""Tests for promptops.renderer module."""

import pytest

from promptops.renderer import (
    render_template,
    validate_template,
    preview_template,
    _safe_format,
)


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_simple_format(self):
        """Test simple format string rendering."""
        template = "Hello, {name}!"
        result = render_template(template, {"name": "World"}, engine="format")
        assert result == "Hello, World!"

    def test_multiple_variables(self):
        """Test template with multiple variables."""
        template = "{greeting}, {name}! Welcome to {place}."
        inputs = {"greeting": "Hello", "name": "Alice", "place": "Wonderland"}
        result = render_template(template, inputs, engine="format")
        assert result == "Hello, Alice! Welcome to Wonderland."

    def test_jinja2_template(self):
        """Test Jinja2 template rendering."""
        template = "Hello, {{ name }}!"
        result = render_template(template, {"name": "World"}, engine="jinja2")
        assert result == "Hello, World!"

    def test_jinja2_with_logic(self):
        """Test Jinja2 template with conditional logic."""
        template = "{% if formal %}Dear {{ name }}{% else %}Hi {{ name }}{% endif %}"
        
        result_formal = render_template(template, {"name": "Smith", "formal": True}, engine="jinja2")
        assert result_formal == "Dear Smith"
        
        result_casual = render_template(template, {"name": "Bob", "formal": False}, engine="jinja2")
        assert result_casual == "Hi Bob"

    def test_auto_engine_detection(self):
        """Test auto engine detection prefers jinja2 if available."""
        template = "Hello, {{ name }}!"
        result = render_template(template, {"name": "Test"}, engine="auto")
        assert result == "Hello, Test!"

    def test_safe_format_missing_key(self):
        """Test safe format replaces missing keys with empty string."""
        template = "Hello, {name}! Your score is {score}."
        result = render_template(template, {"name": "Alice"}, engine="format", safe=True)
        assert result == "Hello, Alice! Your score is ."

    def test_defaults_are_applied(self):
        """Test that defaults are used for missing inputs."""
        template = "Hello, {name}! Score: {score}"
        defaults = {"score": "N/A"}
        result = render_template(template, {"name": "Bob"}, engine="format", defaults=defaults)
        assert result == "Hello, Bob! Score: N/A"

    def test_inputs_override_defaults(self):
        """Test that inputs override defaults."""
        template = "{greeting}, {name}!"
        defaults = {"greeting": "Hello", "name": "Default"}
        result = render_template(template, {"name": "Override"}, engine="format", defaults=defaults)
        assert result == "Hello, Override!"

    def test_unknown_engine_raises(self):
        """Test that unknown engine raises ValueError."""
        with pytest.raises(ValueError, match="Unknown template engine"):
            render_template("test", {}, engine="unknown")


class TestSafeFormat:
    """Tests for _safe_format function."""

    def test_all_keys_present(self):
        """Test formatting when all keys are present."""
        result = _safe_format("{a} {b}", {"a": "1", "b": "2"})
        assert result == "1 2"

    def test_missing_key_returns_empty(self):
        """Test missing keys are replaced with empty string."""
        result = _safe_format("{a} {b}", {"a": "1"})
        assert result == "1 "

    def test_all_keys_missing(self):
        """Test all missing keys."""
        result = _safe_format("{a} {b}", {})
        assert result == " "


class TestValidateTemplate:
    """Tests for validate_template function."""

    def test_valid_format_template(self):
        """Test valid format template."""
        assert validate_template("Hello, {name}!", engine="format") is True

    def test_valid_jinja2_template(self):
        """Test valid Jinja2 template."""
        assert validate_template("Hello, {{ name }}!", engine="jinja2") is True

    def test_invalid_jinja2_template(self):
        """Test invalid Jinja2 template returns False."""
        # Unclosed block
        result = validate_template("{% if x %}", engine="jinja2")
        assert result is False


class TestPreviewTemplate:
    """Tests for preview_template function."""

    def test_preview_renders_template(self):
        """Test preview renders with sample inputs."""
        template = "Hello, {name}!"
        result = preview_template(template, {"name": "Preview"})
        assert result == "Hello, Preview!"

    def test_preview_with_jinja2(self):
        """Test preview with Jinja2 engine."""
        template = "{{ greeting }}, {{ name }}!"
        result = preview_template(template, {"greeting": "Hi", "name": "Test"}, engine="jinja2")
        assert result == "Hi, Test!"
