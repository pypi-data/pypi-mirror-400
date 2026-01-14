"""
Testing module for prompt evaluation and validation.

Provides tools for testing LLM prompt outputs including:
- Assertion functions for output validation
- LLM-based semantic evaluation
- Test runner with detailed reporting
"""

from .assertions import (
    max_words,
    min_words,
    must_include,
    must_exclude,
    matches_pattern,
    is_json,
    max_chars,
    min_chars,
    starts_with,
    ends_with,
    contains_number,
    no_profanity,
    sentiment_positive,
)
from .llm_judge import (
    llm_judge,
    llm_judge_detailed,
    evaluate_all,
    register_rule,
    get_available_rules,
    JudgeResult,
    JudgeReport,
)
from .results import (
    TestFailure,
    TestReport,
    TestResult,
    TestStatus,
)
from .runner import (
    run_tests,
    run_single_test,
    ASSERTION_MAP,
)

__all__ = [
    # Assertions
    "max_words",
    "min_words",
    "must_include",
    "must_exclude",
    "matches_pattern",
    "is_json",
    "max_chars",
    "min_chars",
    "starts_with",
    "ends_with",
    "contains_number",
    "no_profanity",
    "sentiment_positive",
    # LLM Judge
    "llm_judge",
    "llm_judge_detailed",
    "evaluate_all",
    "register_rule",
    "get_available_rules",
    "JudgeResult",
    "JudgeReport",
    # Results
    "TestFailure",
    "TestReport",
    "TestResult",
    "TestStatus",
    # Runner
    "run_tests",
    "run_single_test",
    "ASSERTION_MAP",
]
