"""Test result classes for reporting."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestFailure:
    """Represents a single test failure."""
    name: str
    error: str
    assertion_type: Optional[str] = None
    expected: Any = None
    actual: Any = None
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "error": self.error,
            "assertion_type": self.assertion_type,
            "expected": self.expected,
            "actual": self.actual,
            "duration_ms": self.duration_ms,
        }


@dataclass
class TestResult:
    """Result of a single test case."""
    name: str
    status: TestStatus
    duration_ms: float = 0.0
    error: Optional[str] = None
    output: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def passed(self) -> bool:
        return self.status == TestStatus.PASSED


@dataclass
class TestReport:
    """Report from a test run."""
    passed: bool
    failures: List[TestFailure]
    total_tests: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    duration_ms: float = 0.0
    results: List[TestResult] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed_count / self.total_tests
    
    def summary(self) -> str:
        return (
            f"Tests: {self.passed_count}/{self.total_tests} passed "
            f"({self.success_rate:.1%}) in {self.duration_ms:.0f}ms"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "total_tests": self.total_tests,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "success_rate": self.success_rate,
            "duration_ms": self.duration_ms,
            "failures": [f.to_dict() for f in self.failures],
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_results(cls, results: List[TestResult]) -> "TestReport":
        """Create report from list of test results."""
        failures = [
            TestFailure(name=r.name, error=r.error or "", duration_ms=r.duration_ms)
            for r in results if r.status == TestStatus.FAILED
        ]
        passed_count = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed_count = sum(1 for r in results if r.status == TestStatus.FAILED)
        skipped_count = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        total_duration = sum(r.duration_ms for r in results)
        
        return cls(
            passed=failed_count == 0,
            failures=failures,
            total_tests=len(results),
            passed_count=passed_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            duration_ms=total_duration,
            results=results,
        )
