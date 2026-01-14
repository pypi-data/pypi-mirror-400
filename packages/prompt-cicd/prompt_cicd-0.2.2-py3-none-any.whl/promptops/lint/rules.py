"""
Lint Rules for PromptOps.

Provides the rule system for prompt linting with:
- Built-in rules for common issues
- Custom rule registration
- Severity levels
- Configurable rule sets
"""

import re
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class LintSeverity(Enum):
    """Severity levels for lint issues."""
    ERROR = "error"      # Must be fixed
    WARNING = "warning"  # Should be fixed
    INFO = "info"        # Suggestion


@dataclass
class LintIssue:
    """Represents a single lint issue."""
    rule_id: str
    message: str
    severity: LintSeverity = LintSeverity.WARNING
    line: Optional[int] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "line": self.line,
            "suggestion": self.suggestion,
        }


class LintRule(ABC):
    """Base class for lint rules."""
    
    id: str = "base-rule"
    name: str = "Base Rule"
    description: str = ""
    severity: LintSeverity = LintSeverity.WARNING
    
    @abstractmethod
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        """
        Check the prompt data and return any issues found.
        
        Args:
            prompt_data: The parsed prompt YAML data.
            file_path: Optional path to the prompt file.
            
        Returns:
            List of LintIssue objects.
        """
        pass


# Registry for lint rules
_RULES: Dict[str, LintRule] = {}


def register_rule(rule: LintRule) -> LintRule:
    """Register a lint rule."""
    _RULES[rule.id] = rule
    logger.debug(f"Registered lint rule: {rule.id}")
    return rule


def get_all_rules() -> Dict[str, LintRule]:
    """Get all registered lint rules."""
    return _RULES.copy()


def get_rule(rule_id: str) -> Optional[LintRule]:
    """Get a specific rule by ID."""
    return _RULES.get(rule_id)


# =============================================================================
# Built-in Rules
# =============================================================================


class TemplateRequiredRule(LintRule):
    """Check that a template is defined."""
    
    id = "template-required"
    name = "Template Required"
    description = "Every prompt must have a template field"
    severity = LintSeverity.ERROR
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        if "template" not in prompt_data:
            return [LintIssue(
                rule_id=self.id,
                message="Missing 'template' field - every prompt must have a template",
                severity=self.severity,
                suggestion="Add a 'template' field with your prompt text",
            )]
        
        template = prompt_data.get("template", "")
        if not template or not template.strip():
            return [LintIssue(
                rule_id=self.id,
                message="Template is empty",
                severity=self.severity,
                suggestion="Add content to your template",
            )]
        
        return []


class TemplateVariablesRule(LintRule):
    """Check for undefined or unused template variables."""
    
    id = "template-variables"
    name = "Template Variables"
    description = "Check template variable usage"
    severity = LintSeverity.WARNING
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        issues = []
        template = prompt_data.get("template", "")
        
        # Find all variables in template (both {var} and {{var}} for Jinja2)
        format_vars = set(re.findall(r'\{(\w+)\}', template))
        jinja_vars = set(re.findall(r'\{\{\s*(\w+)\s*\}\}', template))
        all_vars = format_vars | jinja_vars
        
        # Check test inputs for undefined variables
        tests = prompt_data.get("tests", [])
        for test in tests:
            test_inputs = set(test.get("input", {}).keys())
            
            # Variables in template but not in test input
            missing_in_test = all_vars - test_inputs
            if missing_in_test:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"Test '{test.get('name', 'unknown')}' missing variables: {missing_in_test}",
                    severity=LintSeverity.WARNING,
                    suggestion=f"Add these variables to the test input: {missing_in_test}",
                ))
            
            # Variables in test but not in template
            extra_in_test = test_inputs - all_vars
            if extra_in_test:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"Test '{test.get('name', 'unknown')}' has unused variables: {extra_in_test}",
                    severity=LintSeverity.INFO,
                    suggestion=f"Remove unused variables or add them to template: {extra_in_test}",
                ))
        
        return issues


class TestsRequiredRule(LintRule):
    """Check that at least one test is defined."""
    
    id = "tests-required"
    name = "Tests Required"
    description = "Prompts should have at least one test"
    severity = LintSeverity.WARNING
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        tests = prompt_data.get("tests", [])
        
        if not tests:
            return [LintIssue(
                rule_id=self.id,
                message="No tests defined for this prompt",
                severity=self.severity,
                suggestion="Add a 'tests' section with at least one test case",
            )]
        
        return []


class TestAssertionsRule(LintRule):
    """Check that tests have proper assertions."""
    
    id = "test-assertions"
    name = "Test Assertions"
    description = "Tests should have meaningful assertions"
    severity = LintSeverity.WARNING
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        issues = []
        tests = prompt_data.get("tests", [])
        
        for test in tests:
            test_name = test.get("name", "unknown")
            assertions = test.get("assert", {})
            
            if not assertions:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"Test '{test_name}' has no assertions",
                    severity=self.severity,
                    suggestion="Add assertions like max_words, must_include, etc.",
                ))
        
        return issues


class PromptLengthRule(LintRule):
    """Check prompt length for cost efficiency."""
    
    id = "prompt-length"
    name = "Prompt Length"
    description = "Check for overly long prompts that may be costly"
    severity = LintSeverity.INFO
    
    # Approximate tokens per character
    CHARS_PER_TOKEN = 4
    WARNING_TOKENS = 500
    ERROR_TOKENS = 2000
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        issues = []
        template = prompt_data.get("template", "")
        
        char_count = len(template)
        estimated_tokens = char_count // self.CHARS_PER_TOKEN
        
        if estimated_tokens > self.ERROR_TOKENS:
            issues.append(LintIssue(
                rule_id=self.id,
                message=f"Template is very long (~{estimated_tokens} tokens) - may be costly",
                severity=LintSeverity.WARNING,
                suggestion="Consider breaking into smaller prompts or reducing instructions",
                metadata={"estimated_tokens": estimated_tokens},
            ))
        elif estimated_tokens > self.WARNING_TOKENS:
            issues.append(LintIssue(
                rule_id=self.id,
                message=f"Template is moderately long (~{estimated_tokens} tokens)",
                severity=LintSeverity.INFO,
                suggestion="Review if all content is necessary",
                metadata={"estimated_tokens": estimated_tokens},
            ))
        
        return issues


class ApprovalStatusRule(LintRule):
    """Check approval status for production readiness."""
    
    id = "approval-status"
    name = "Approval Status"
    description = "Check if prompt is approved for production"
    severity = LintSeverity.INFO
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        approved = prompt_data.get("approved", False)
        
        if not approved:
            return [LintIssue(
                rule_id=self.id,
                message="Prompt is not approved for production",
                severity=self.severity,
                suggestion="Run 'promptops approve <name> <version>' when ready",
            )]
        
        return []


class SecurityPatternsRule(LintRule):
    """Check for security anti-patterns in prompts."""
    
    id = "security-patterns"
    name = "Security Patterns"
    description = "Check for potential security issues"
    severity = LintSeverity.ERROR
    
    # Patterns that might indicate security issues
    SUSPICIOUS_PATTERNS = [
        (r"ignore\s+(all\s+)?(previous|above)\s+instructions?", "Potential prompt injection vulnerability"),
        (r"act\s+as\s+if\s+you\s+(have\s+)?no\s+restrictions?", "Jailbreak pattern detected"),
        (r"pretend\s+(you\s+)?(are|can|have)", "Role manipulation pattern"),
        (r"api[_\-]?key|password|secret|token", "Sensitive term in prompt"),
        (r"\b(sudo|rm\s+-rf|eval|exec)\b", "Dangerous command pattern"),
    ]
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        issues = []
        template = prompt_data.get("template", "").lower()
        
        for pattern, message in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, template, re.IGNORECASE):
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=message,
                    severity=self.severity,
                    suggestion="Review and remove or sanitize this content",
                ))
        
        return issues


class MetadataRule(LintRule):
    """Check for recommended metadata fields."""
    
    id = "metadata"
    name = "Metadata"
    description = "Check for recommended metadata"
    severity = LintSeverity.INFO
    
    RECOMMENDED_FIELDS = ["name", "version", "description"]
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        issues = []
        
        for field in self.RECOMMENDED_FIELDS:
            if field not in prompt_data:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"Missing recommended field: '{field}'",
                    severity=self.severity,
                    suggestion=f"Add a '{field}' field for better documentation",
                ))
        
        return issues


class ProviderConfigRule(LintRule):
    """Check provider configuration."""
    
    id = "provider-config"
    name = "Provider Configuration"
    description = "Check provider settings"
    severity = LintSeverity.WARNING
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        issues = []
        
        # Check temperature
        temperature = prompt_data.get("temperature")
        if temperature is not None:
            if not isinstance(temperature, (int, float)):
                issues.append(LintIssue(
                    rule_id=self.id,
                    message="Temperature must be a number",
                    severity=LintSeverity.ERROR,
                ))
            elif temperature < 0 or temperature > 2:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"Temperature {temperature} is outside typical range (0-2)",
                    severity=LintSeverity.WARNING,
                ))
        
        # Check max_tokens
        max_tokens = prompt_data.get("max_tokens")
        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                issues.append(LintIssue(
                    rule_id=self.id,
                    message="max_tokens must be an integer",
                    severity=LintSeverity.ERROR,
                ))
            elif max_tokens > 4000:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"max_tokens={max_tokens} may be costly",
                    severity=LintSeverity.INFO,
                ))
        
        return issues


class CacheConfigRule(LintRule):
    """Check cache configuration."""
    
    id = "cache-config"
    name = "Cache Configuration"
    description = "Check caching settings"
    severity = LintSeverity.INFO
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        issues = []
        cache = prompt_data.get("cache", {})
        
        if not cache.get("enabled"):
            issues.append(LintIssue(
                rule_id=self.id,
                message="Caching is not enabled - may increase costs",
                severity=self.severity,
                suggestion="Add 'cache: enabled: true' to enable response caching",
            ))
        else:
            # Check TTL
            ttl = cache.get("ttl")
            if ttl and ttl > 86400:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"Cache TTL of {ttl}s is very long (>24h)",
                    severity=LintSeverity.WARNING,
                    suggestion="Consider a shorter TTL for freshness",
                ))
        
        return issues


class SemanticTestsRule(LintRule):
    """Check for semantic test usage."""
    
    id = "semantic-tests"
    name = "Semantic Tests"
    description = "Recommend semantic testing for quality"
    severity = LintSeverity.INFO
    
    def check(self, prompt_data: Dict[str, Any], file_path: Optional[str] = None) -> List[LintIssue]:
        tests = prompt_data.get("tests", [])
        
        has_semantic = any(
            "semantic" in test.get("assert", {})
            for test in tests
        )
        
        if tests and not has_semantic:
            return [LintIssue(
                rule_id=self.id,
                message="No semantic tests defined",
                severity=self.severity,
                suggestion="Add semantic assertions like 'is_coherent', 'neutral_tone' for quality checks",
            )]
        
        return []


# =============================================================================
# Register Built-in Rules
# =============================================================================

register_rule(TemplateRequiredRule())
register_rule(TemplateVariablesRule())
register_rule(TestsRequiredRule())
register_rule(TestAssertionsRule())
register_rule(PromptLengthRule())
register_rule(ApprovalStatusRule())
register_rule(SecurityPatternsRule())
register_rule(MetadataRule())
register_rule(ProviderConfigRule())
register_rule(CacheConfigRule())
register_rule(SemanticTestsRule())
