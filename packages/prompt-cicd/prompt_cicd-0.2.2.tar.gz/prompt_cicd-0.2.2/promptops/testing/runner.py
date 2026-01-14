"""Test runner for executing prompt tests."""

import logging
import time
from typing import Any, Callable, Dict, List, Optional, Protocol

from . import assertions
from .llm_judge import llm_judge
from .results import TestFailure, TestReport, TestResult, TestStatus

logger = logging.getLogger(__name__)


class PromptProtocol(Protocol):
    """Protocol for prompt objects."""
    name: str
    def render(self, inputs: Dict[str, Any]) -> str: ...


class ProviderProtocol(Protocol):
    """Protocol for provider objects."""
    def run(self, prompt: str) -> str: ...


ASSERTION_MAP: Dict[str, Callable] = {
    "max_words": assertions.max_words,
    "min_words": assertions.min_words,
    "must_include": assertions.must_include,
    "must_exclude": assertions.must_exclude,
    "matches_pattern": assertions.matches_pattern,
    "is_json": assertions.is_json,
    "max_chars": assertions.max_chars,
    "min_chars": assertions.min_chars,
    "starts_with": assertions.starts_with,
    "ends_with": assertions.ends_with,
    "no_profanity": assertions.no_profanity,
}


def run_single_test(
    prompt: PromptProtocol,
    provider: ProviderProtocol,
    test: Dict[str, Any],
) -> TestResult:
    """Run a single test case."""
    name = test.get("name", "unnamed")
    start_time = time.time()
    
    try:
        # Skip if marked
        if test.get("skip", False):
            return TestResult(
                name=name,
                status=TestStatus.SKIPPED,
                duration_ms=0,
            )
        
        # Render and run
        rendered = prompt.render(test.get("input", {}))
        output = provider.run(rendered)
        asserts = test.get("assert", {})
        
        # Run assertions
        for assert_type, value in asserts.items():
            if assert_type == "semantic":
                rules = value if isinstance(value, list) else [value]
                for rule in rules:
                    if not llm_judge(prompt.name, output, rule):
                        raise AssertionError(f"Semantic test failed: {rule}")
            elif assert_type in ASSERTION_MAP:
                ASSERTION_MAP[assert_type](output, value)
        
        duration = (time.time() - start_time) * 1000
        return TestResult(
            name=name,
            status=TestStatus.PASSED,
            duration_ms=duration,
            output=output,
            input_data=test.get("input"),
        )
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.warning(f"Test '{name}' failed: {e}")
        return TestResult(
            name=name,
            status=TestStatus.FAILED,
            duration_ms=duration,
            error=str(e),
            input_data=test.get("input"),
        )


def run_tests(
    prompt: PromptProtocol,
    provider: ProviderProtocol,
    tests: List[Dict[str, Any]],
    stop_on_failure: bool = False,
    on_result: Optional[Callable[[TestResult], None]] = None,
) -> TestReport:
    """Run multiple test cases."""
    start_time = time.time()
    results: List[TestResult] = []
    failures: List[TestFailure] = []
    
    for test in tests:
        result = run_single_test(prompt, provider, test)
        results.append(result)
        
        if on_result:
            on_result(result)
        
        if result.status == TestStatus.FAILED:
            failures.append(TestFailure(
                name=result.name,
                error=result.error or "",
                duration_ms=result.duration_ms,
            ))
            if stop_on_failure:
                break
    
    total_duration = (time.time() - start_time) * 1000
    passed_count = sum(1 for r in results if r.status == TestStatus.PASSED)
    
    logger.info(f"Tests complete: {passed_count}/{len(results)} passed")
    
    return TestReport(
        passed=len(failures) == 0,
        failures=failures,
        total_tests=len(results),
        passed_count=passed_count,
        failed_count=len(failures),
        skipped_count=sum(1 for r in results if r.status == TestStatus.SKIPPED),
        duration_ms=total_duration,
        results=results,
    )
