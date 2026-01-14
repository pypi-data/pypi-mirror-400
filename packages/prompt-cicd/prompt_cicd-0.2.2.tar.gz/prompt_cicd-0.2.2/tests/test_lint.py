"""Tests for the lint module."""

import pytest
from pathlib import Path

from promptops.lint.linter import (
    PromptLinter,
    lint_prompt,
    lint_all_prompts,
    LintResult,
    LintReport,
    LintIssue,
    LintSeverity,
)
from promptops.lint.rules import (
    LintRule,
    TemplateRequiredRule,
    TestsRequiredRule,
    ApprovalStatusRule,
    ProviderConfigRule,
    SecurityPatternsRule,
    PromptLengthRule,
    CacheConfigRule,
)


class TestLintRules:
    """Test individual lint rules."""
    
    def test_template_required_rule(self):
        """Test TemplateRequiredRule."""
        rule = TemplateRequiredRule()
        
        # Valid: has template
        config = {"template": "Hello {name}"}
        issues = rule.check(config)
        assert len(issues) == 0
        
        # Invalid: no template
        config = {"name": "test"}
        issues = rule.check(config)
        assert len(issues) == 1
        assert issues[0].severity == LintSeverity.ERROR
    
    def test_tests_required_rule(self):
        """Test TestsRequiredRule."""
        rule = TestsRequiredRule()
        
        # Valid: has tests
        config = {"tests": [{"name": "test1"}]}
        issues = rule.check(config)
        assert len(issues) == 0
        
        # Warning: no tests
        config = {}
        issues = rule.check(config)
        assert len(issues) == 1
        assert issues[0].severity == LintSeverity.WARNING
    
    def test_approval_status_rule_approved(self):
        """Test ApprovalStatusRule when approved."""
        rule = ApprovalStatusRule()
        
        # Valid: approved
        config = {"approved": True}
        issues = rule.check(config)
        assert len(issues) == 0
        
        # Info: not approved
        config = {"approved": False}
        issues = rule.check(config)
        assert len(issues) == 1
        assert issues[0].severity == LintSeverity.INFO
    
    def test_approval_status_rule_not_approved(self):
        """Test ApprovalStatusRule when not approved."""
        rule = ApprovalStatusRule()
        
        # Not approved - should return info
        config = {}
        issues = rule.check(config)
        assert len(issues) == 1
        assert issues[0].severity == LintSeverity.INFO
    
    def test_provider_config_rule(self):
        """Test ProviderConfigRule."""
        rule = ProviderConfigRule()
        
        # Valid: proper temperature and max_tokens
        config = {"temperature": 0.7, "max_tokens": 100}
        issues = rule.check(config)
        assert len(issues) == 0
        
        # Warning: temperature out of range
        config = {"temperature": 5.0}
        issues = rule.check(config)
        assert len(issues) == 1
        assert issues[0].severity == LintSeverity.WARNING
    
    def test_security_patterns_rule(self):
        """Test SecurityPatternsRule."""
        rule = SecurityPatternsRule()
        
        # Warning: contains API key pattern
        config = {"template": "Use this api_key: sk-abc123"}
        issues = rule.check(config)
        assert len(issues) >= 1
        assert any("Sensitive" in issue.message for issue in issues)
    
    def test_prompt_length_rule(self):
        """Test PromptLengthRule."""
        rule = PromptLengthRule()
        
        # Valid: normal length
        config = {"template": "Short prompt"}
        issues = rule.check(config)
        assert len(issues) == 0
        
        # Warning: very long prompt
        config = {"template": "x" * 10000}
        issues = rule.check(config)
        assert len(issues) >= 1
    
    def test_cache_config_rule(self):
        """Test CacheConfigRule."""
        rule = CacheConfigRule()
        
        # Valid: proper cache config
        config = {"cache": {"ttl": 3600, "enabled": True}}
        issues = rule.check(config)
        assert len(issues) == 0
        
        # Info: cache not enabled
        config = {"cache": {"enabled": False}}
        issues = rule.check(config)
        assert len(issues) >= 1


class TestPromptLinter:
    """Test PromptLinter class."""
    
    def test_lint_valid_prompt(self):
        """Test linting a valid prompt."""
        linter = PromptLinter()
        config = {
            "template": "Hello {name}",
            "provider": "openai",
            "tests": [{"name": "test1"}],
            "approved": True,
        }
        
        result = linter.lint(config, "test_prompt", "v1")
        assert isinstance(result, LintResult)
        assert result.passed  # Should pass with no errors
    
    def test_lint_invalid_prompt(self):
        """Test linting an invalid prompt."""
        linter = PromptLinter()
        config = {}  # Missing template
        
        result = linter.lint(config, "test_prompt", "v1")
        assert not result.passed
        assert len(result.issues) > 0
    
    def test_custom_rules(self):
        """Test adding custom rules."""
        class CustomRule(LintRule):
            id = "custom"
            def check(self, prompt_data, file_path=None):
                return [LintIssue(
                    rule_id="custom",
                    severity=LintSeverity.WARNING,
                    message="Custom rule"
                )]
        
        # Need to register the custom rule
        from promptops.lint.rules import register_rule
        register_rule(CustomRule())
        
        linter = PromptLinter(enabled_rules={"custom"})
        config = {"template": "test"}
        
        result = linter.lint(config, "test", "v1")
        assert any(issue.rule_id == "custom" for issue in result.issues)
    
    def test_min_severity_filter(self):
        """Test minimum severity filtering."""
        linter_info = PromptLinter(min_severity=LintSeverity.INFO)
        linter_warning = PromptLinter(min_severity=LintSeverity.WARNING)
        linter_error = PromptLinter(min_severity=LintSeverity.ERROR)
        
        config = {}  # Will have warnings and errors
        
        # Get all issues
        result_all = linter_info.lint(config, "test", "v1")
        
        # Get only warnings and errors
        result_warning = linter_warning.lint(config, "test", "v1")
        
        # Get only errors
        result_error = linter_error.lint(config, "test", "v1")
        
        assert len(result_all.issues) >= len(result_warning.issues)
        assert len(result_warning.issues) >= len(result_error.issues)


class TestLintResult:
    """Test LintResult class."""
    
    def test_to_dict(self):
        """Test converting result to dictionary."""
        issue = LintIssue(
            rule_id="test_rule",
            severity=LintSeverity.ERROR,
            message="Test message"
        )
        result = LintResult(
            prompt_name="test",
            version="v1",
            issues=[issue],
            file_path="test.yaml"
        )
        
        data = result.to_dict()
        assert data["prompt_name"] == "test"
        assert data["version"] == "v1"
        assert len(data["issues"]) == 1
        assert data["passed"] is False
    
    def test_passed_property(self):
        """Test passed property."""
        # No errors = passed
        result = LintResult("test", "v1", issues=[])
        assert result.passed is True
        
        # Has error = not passed
        issue = LintIssue("rule", "msg", LintSeverity.ERROR)
        result = LintResult("test", "v1", issues=[issue])
        assert result.passed is False
        
        # Only warnings = passed
        issue = LintIssue("rule", "msg", LintSeverity.WARNING)
        result = LintResult("test", "v1", issues=[issue])
        assert result.passed is True


class TestLintReport:
    """Test LintReport class."""
    
    def test_summary(self):
        """Test summary generation."""
        result1 = LintResult("prompt1", "v1", issues=[])
        result2 = LintResult("prompt2", "v1", issues=[
            LintIssue("rule", "error", LintSeverity.ERROR)
        ])
        
        report = LintReport([result1, result2])
        summary = report.summary()
        
        assert "2 prompt" in summary
        assert "1" in summary  # Should show 1 error
    
    def test_passed_property(self):
        """Test overall passed property."""
        result1 = LintResult("prompt1", "v1", issues=[])
        result2 = LintResult("prompt2", "v1", issues=[])
        report = LintReport([result1, result2])
        assert report.passed is True
        
        result3 = LintResult("prompt3", "v1", issues=[
            LintIssue("rule", "error", LintSeverity.ERROR)
        ])
        report2 = LintReport([result1, result3])
        assert report2.passed is False


class TestLintFunctions:
    """Test module-level lint functions."""
    
    def test_lint_prompt_dict(self, tmp_path):
        """Test linting a prompt configuration."""
        # Create a temporary prompt file
        prompts_dir = tmp_path / "prompts" / "test"
        prompts_dir.mkdir(parents=True)
        config_file = prompts_dir / "v1.yaml"
        config_file.write_text("template: 'Hello {name}'\nprovider: openai\n")
        
        # Change to tmp_path to make relative path work
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = lint_prompt("test", "v1", source="local")
            assert isinstance(result, LintResult)
            assert result.prompt_name == "test"
            assert result.version == "v1"
        finally:
            os.chdir(old_cwd)
    
    def test_lint_all_prompts_empty_dir(self, tmp_path):
        """Test linting empty directory."""
        report = lint_all_prompts(str(tmp_path))
        assert isinstance(report, LintReport)
        assert len(report.results) == 0
    
    def test_lint_all_prompts_with_files(self, tmp_path):
        """Test linting directory with prompt files."""
        # Create test prompt files
        prompt_dir = tmp_path / "prompts" / "test_prompt"
        prompt_dir.mkdir(parents=True)
        
        prompt_file = prompt_dir / "v1.yaml"
        prompt_file.write_text("""
template: "Hello {name}"
provider: openai
tests:
  - name: test1
""")
        
        report = lint_all_prompts(str(tmp_path / "prompts"))
        assert len(report.results) >= 1
