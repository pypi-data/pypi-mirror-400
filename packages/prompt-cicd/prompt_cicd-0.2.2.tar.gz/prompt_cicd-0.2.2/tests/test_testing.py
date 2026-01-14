"""Tests for testing module."""

import pytest
from promptops.testing.assertions import (
    AssertionError as PromptOpsAssertionError,
    max_words,
    min_words,
    max_chars,
    must_include,
    must_exclude,
    matches_pattern,
    is_json,
)
from promptops.testing.results import (
    TestResult,
    TestReport,
    TestStatus,
)
from promptops.testing.llm_judge import (
    llm_judge,
    JudgeResult,
    get_available_rules,
)


class TestAssertions:
    """Test assertion functions."""
    
    def test_max_words(self):
        """Test max words assertion."""
        max_words("Hello world", 5)
        with pytest.raises(PromptOpsAssertionError):
            max_words("One two three four five six", 5)
    
    def test_min_words(self):
        """Test min words assertion."""
        min_words("Hello world test", 3)
        with pytest.raises(PromptOpsAssertionError):
            min_words("Hello", 3)
    
    def test_max_chars(self):
        """Test max chars assertion."""
        max_chars("Hello", 10)
        with pytest.raises(PromptOpsAssertionError):
            max_chars("Hello world", 5)
    
    def test_must_include(self):
        """Test contains assertion."""
        must_include("Hello world", "world")
        with pytest.raises(PromptOpsAssertionError):
            must_include("Hello world", "goodbye")
    
    def test_must_exclude(self):
        """Test not contains assertion."""
        must_exclude("Hello world", "goodbye")
        with pytest.raises(PromptOpsAssertionError):
            must_exclude("Hello world", "world")
    
    def test_matches_pattern(self):
        """Test pattern matching assertion."""
        matches_pattern("test123", r"test\d+")
        with pytest.raises(PromptOpsAssertionError):
            matches_pattern("test", r"test\d+")
    
    def test_is_json(self):
        """Test JSON validation assertion."""
        is_json('{"key": "value"}')
        with pytest.raises(PromptOpsAssertionError):
            is_json("not json")


class TestTestResult:
    """Test TestResult class."""
    
    def test_passed_result(self):
        """Test creating passed result."""
        result = TestResult(
            name="test1",
            status=TestStatus.PASSED,
        )
        assert result.name == "test1"
        assert result.status == TestStatus.PASSED
        assert result.passed is True
    
    def test_failed_result(self):
        """Test creating failed result."""
        result = TestResult(
            name="test1",
            status=TestStatus.FAILED,
            error="Assertion failed",
        )
        assert result.status == TestStatus.FAILED
        assert result.error == "Assertion failed"
        assert result.passed is False


class TestTestReport:
    """Test TestReport class."""
    
    def test_all_passed(self):
        """Test report with all tests passed."""
        results = [
            TestResult(name="test1", status=TestStatus.PASSED),
            TestResult(name="test2", status=TestStatus.PASSED),
        ]
        report = TestReport.from_results(results)
        assert report.passed is True
        assert report.total_tests == 2
        assert report.passed_count == 2
    
    def test_some_failed(self):
        """Test report with failed tests."""
        results = [
            TestResult(name="test1", status=TestStatus.PASSED),
            TestResult(name="test2", status=TestStatus.FAILED, error="Failed"),
        ]
        report = TestReport.from_results(results)
        assert report.passed is False
        assert report.total_tests == 2


class TestLLMJudge:
    """Test LLM judge functionality."""
    
    def test_available_rules(self):
        """Test getting available rules."""
        rules = get_available_rules()
        assert "neutral_tone" in rules
        assert "summary_present" in rules
        assert "is_coherent" in rules
    
    def test_neutral_tone_pass(self):
        """Test neutral tone passing."""
        result = llm_judge("test", "This is a nice response.", "neutral_tone")
        assert result is True
    
    def test_neutral_tone_fail(self):
        """Test neutral tone failing."""
        result = llm_judge("test", "This is stupid and terrible.", "neutral_tone")
        assert result is False
    
    def test_summary_present_pass(self):
        """Test summary present passing."""
        result = llm_judge("test", "Here is a detailed summary of the topic.", "summary_present")
        assert result is True
    
    def test_summary_present_fail(self):
        """Test summary present failing."""
        result = llm_judge("test", "Yes", "summary_present")
        assert result is False
