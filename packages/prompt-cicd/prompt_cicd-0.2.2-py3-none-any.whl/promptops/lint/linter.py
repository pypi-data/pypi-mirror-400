"""
Prompt Linter for PromptOps.

Provides static analysis and validation for prompts with:
- Configurable rule sets
- Multiple severity levels
- Detailed issue reporting
- Batch linting support
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from .rules import (
    LintRule,
    LintIssue,
    LintSeverity,
    get_all_rules,
    get_rule,
)

logger = logging.getLogger(__name__)


@dataclass
class LintResult:
    """Result of linting a single prompt."""
    prompt_name: str
    version: str
    file_path: Optional[str] = None
    issues: List[LintIssue] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Check if linting passed (no errors)."""
        return not any(issue.severity == LintSeverity.ERROR for issue in self.issues)
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == LintSeverity.ERROR)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == LintSeverity.WARNING)
    
    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == LintSeverity.INFO)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_name": self.prompt_name,
            "version": self.version,
            "file_path": self.file_path,
            "passed": self.passed,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues": [i.to_dict() for i in self.issues],
        }
    
    def summary(self) -> str:
        """Get a summary string."""
        if self.passed and not self.issues:
            return f"✅ {self.prompt_name} v{self.version}: No issues"
        
        parts = []
        if self.error_count:
            parts.append(f"{self.error_count} error(s)")
        if self.warning_count:
            parts.append(f"{self.warning_count} warning(s)")
        if self.info_count:
            parts.append(f"{self.info_count} info(s)")
        
        status = "❌" if not self.passed else "⚠️"
        return f"{status} {self.prompt_name} v{self.version}: {', '.join(parts)}"


@dataclass
class LintReport:
    """Report for linting multiple prompts."""
    results: List[LintResult] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)
    
    @property
    def total_errors(self) -> int:
        return sum(r.error_count for r in self.results)
    
    @property
    def total_warnings(self) -> int:
        return sum(r.warning_count for r in self.results)
    
    @property
    def total_info(self) -> int:
        return sum(r.info_count for r in self.results)
    
    def summary(self) -> str:
        lines = [
            f"Linted {len(self.results)} prompt(s)",
            f"  Errors: {self.total_errors}",
            f"  Warnings: {self.total_warnings}",
            f"  Info: {self.total_info}",
        ]
        return "\n".join(lines)


class PromptLinter:
    """
    Linter for PromptOps prompts.
    
    Provides configurable static analysis with:
    - Built-in and custom rules
    - Severity filtering
    - Batch processing
    """
    
    def __init__(
        self,
        enabled_rules: Optional[Set[str]] = None,
        disabled_rules: Optional[Set[str]] = None,
        min_severity: LintSeverity = LintSeverity.INFO,
    ):
        """
        Initialize the linter.
        
        Args:
            enabled_rules: If set, only use these rules. If None, use all.
            disabled_rules: Rules to skip.
            min_severity: Minimum severity to report.
        """
        self.enabled_rules = enabled_rules
        self.disabled_rules = disabled_rules or set()
        self.min_severity = min_severity
        self._rules: Dict[str, LintRule] = {}
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load and filter rules."""
        all_rules = get_all_rules()
        
        for rule_id, rule in all_rules.items():
            # Skip disabled rules
            if rule_id in self.disabled_rules:
                continue
            
            # If enabled_rules is set, only include those
            if self.enabled_rules and rule_id not in self.enabled_rules:
                continue
            
            self._rules[rule_id] = rule
        
        logger.debug(f"Loaded {len(self._rules)} lint rules")
    
    def lint(
        self,
        prompt_data: Dict[str, Any],
        prompt_name: str = "unknown",
        version: str = "unknown",
        file_path: Optional[str] = None,
    ) -> LintResult:
        """
        Lint a single prompt.
        
        Args:
            prompt_data: Parsed prompt YAML data.
            prompt_name: Name of the prompt.
            version: Version string.
            file_path: Optional file path.
            
        Returns:
            LintResult with all issues found.
        """
        result = LintResult(
            prompt_name=prompt_name,
            version=version,
            file_path=file_path,
        )
        
        severity_order = {
            LintSeverity.ERROR: 0,
            LintSeverity.WARNING: 1,
            LintSeverity.INFO: 2,
        }
        min_order = severity_order.get(self.min_severity, 2)
        
        for rule_id, rule in self._rules.items():
            try:
                issues = rule.check(prompt_data, file_path)
                
                # Filter by severity
                for issue in issues:
                    issue_order = severity_order.get(issue.severity, 2)
                    if issue_order <= min_order:
                        result.issues.append(issue)
                        
            except Exception as e:
                logger.warning(f"Rule {rule_id} failed: {e}")
                result.issues.append(LintIssue(
                    rule_id="linter-error",
                    message=f"Rule {rule_id} failed: {e}",
                    severity=LintSeverity.WARNING,
                ))
        
        # Sort issues by severity
        result.issues.sort(key=lambda i: severity_order.get(i.severity, 2))
        
        return result
    
    def lint_file(self, file_path: str) -> LintResult:
        """
        Lint a prompt file.
        
        Args:
            file_path: Path to the YAML file.
            
        Returns:
            LintResult with all issues found.
        """
        path = Path(file_path)
        
        if not path.exists():
            return LintResult(
                prompt_name="unknown",
                version="unknown",
                file_path=file_path,
                issues=[LintIssue(
                    rule_id="file-not-found",
                    message=f"File not found: {file_path}",
                    severity=LintSeverity.ERROR,
                )],
            )
        
        try:
            content = path.read_text()
            data = yaml.safe_load(content)
            
            if not isinstance(data, dict):
                return LintResult(
                    prompt_name="unknown",
                    version="unknown",
                    file_path=file_path,
                    issues=[LintIssue(
                        rule_id="invalid-yaml",
                        message="YAML must be a dictionary",
                        severity=LintSeverity.ERROR,
                    )],
                )
            
            # Extract name and version from file path
            prompt_name = data.get("name", path.parent.name)
            version = data.get("version", path.stem)
            
            return self.lint(data, prompt_name, version, file_path)
            
        except yaml.YAMLError as e:
            return LintResult(
                prompt_name="unknown",
                version="unknown",
                file_path=file_path,
                issues=[LintIssue(
                    rule_id="yaml-parse-error",
                    message=f"YAML parse error: {e}",
                    severity=LintSeverity.ERROR,
                )],
            )
    
    def lint_directory(
        self,
        directory: str = "prompts",
        recursive: bool = True,
    ) -> LintReport:
        """
        Lint all prompts in a directory.
        
        Args:
            directory: Path to prompts directory.
            recursive: Whether to search subdirectories.
            
        Returns:
            LintReport with results for all prompts.
        """
        report = LintReport()
        path = Path(directory)
        
        if not path.exists():
            logger.warning(f"Directory not found: {directory}")
            return report
        
        pattern = "**/*.yaml" if recursive else "*.yaml"
        
        for yaml_file in path.glob(pattern):
            result = self.lint_file(str(yaml_file))
            report.results.append(result)
        
        return report


def lint_prompt(
    name: str,
    version: str,
    source: str = "local",
    min_severity: str = "info",
) -> LintResult:
    """
    Convenience function to lint a single prompt.
    
    Args:
        name: Prompt name.
        version: Version string.
        source: Source type (local).
        min_severity: Minimum severity to report.
        
    Returns:
        LintResult with issues.
    """
    severity_map = {
        "error": LintSeverity.ERROR,
        "warning": LintSeverity.WARNING,
        "info": LintSeverity.INFO,
    }
    
    linter = PromptLinter(min_severity=severity_map.get(min_severity, LintSeverity.INFO))
    
    if source == "local":
        file_path = f"prompts/{name}/{version}.yaml"
        return linter.lint_file(file_path)
    
    raise ValueError(f"Unsupported source: {source}")


def lint_all_prompts(
    directory: str = "prompts",
    min_severity: str = "info",
) -> LintReport:
    """
    Lint all prompts in a directory.
    
    Args:
        directory: Path to prompts directory.
        min_severity: Minimum severity to report.
        
    Returns:
        LintReport with all results.
    """
    severity_map = {
        "error": LintSeverity.ERROR,
        "warning": LintSeverity.WARNING,
        "info": LintSeverity.INFO,
    }
    
    linter = PromptLinter(min_severity=severity_map.get(min_severity, LintSeverity.INFO))
    return linter.lint_directory(directory)


# Re-export for convenience
__all__ = [
    "PromptLinter",
    "LintResult",
    "LintIssue",
    "LintSeverity",
    "LintReport",
    "lint_prompt",
    "lint_all_prompts",
]
