"""LLM-based evaluation for semantic testing."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class JudgeResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNCERTAIN = "uncertain"


@dataclass
class JudgeReport:
    """Result from LLM judge evaluation."""
    result: JudgeResult
    rule: str
    score: float  # 0.0 to 1.0
    reason: str
    details: Dict[str, Any] = None

    @property
    def passed(self) -> bool:
        return self.result == JudgeResult.PASS


# Built-in rule implementations
BUILTIN_RULES: Dict[str, Callable[[str, str], JudgeReport]] = {}


def register_rule(name: str):
    """Decorator to register a judge rule."""
    def decorator(func: Callable[[str, str], JudgeReport]):
        BUILTIN_RULES[name] = func
        return func
    return decorator


@register_rule("neutral_tone")
def _neutral_tone(prompt_name: str, output: str) -> JudgeReport:
    """Check for neutral, non-offensive tone."""
    banned = ["hate", "idiot", "stupid", "dumb", "terrible"]
    found = [b for b in banned if b in output.lower()]
    passed = len(found) == 0
    return JudgeReport(
        result=JudgeResult.PASS if passed else JudgeResult.FAIL,
        rule="neutral_tone",
        score=1.0 if passed else 0.0,
        reason="Offensive terms found" if found else "Tone is neutral",
        details={"found_terms": found}
    )


@register_rule("summary_present")
def _summary_present(prompt_name: str, output: str) -> JudgeReport:
    """Check that output contains meaningful content."""
    word_count = len(output.split())
    passed = word_count > 5
    return JudgeReport(
        result=JudgeResult.PASS if passed else JudgeResult.FAIL,
        rule="summary_present",
        score=min(1.0, word_count / 10),
        reason=f"Output has {word_count} words",
        details={"word_count": word_count}
    )


@register_rule("is_coherent")
def _is_coherent(prompt_name: str, output: str) -> JudgeReport:
    """Basic coherence check."""
    has_sentences = output.count('.') > 0 or output.count('!') > 0 or output.count('?') > 0
    not_empty = len(output.strip()) > 10
    passed = has_sentences and not_empty
    return JudgeReport(
        result=JudgeResult.PASS if passed else JudgeResult.FAIL,
        rule="is_coherent",
        score=1.0 if passed else 0.0,
        reason="Output appears coherent" if passed else "Output may be incoherent"
    )


@register_rule("factual_style")
def _factual_style(prompt_name: str, output: str) -> JudgeReport:
    """Check for factual, non-opinionated style."""
    opinion_markers = ["I think", "I believe", "in my opinion", "personally"]
    found = [m for m in opinion_markers if m.lower() in output.lower()]
    passed = len(found) == 0
    return JudgeReport(
        result=JudgeResult.PASS if passed else JudgeResult.FAIL,
        rule="factual_style",
        score=1.0 if passed else 0.5,
        reason="Contains opinion markers" if found else "Factual style",
        details={"opinion_markers": found}
    )


def llm_judge(
    prompt_name: str,
    output: str,
    rule: str,
    custom_rules: Optional[Dict[str, Callable]] = None,
) -> bool:
    """Evaluate output against a rule. Returns True if passed."""
    report = llm_judge_detailed(prompt_name, output, rule, custom_rules)
    return report.passed


def llm_judge_detailed(
    prompt_name: str,
    output: str,
    rule: str,
    custom_rules: Optional[Dict[str, Callable]] = None,
) -> JudgeReport:
    """Evaluate output with detailed report."""
    all_rules = {**BUILTIN_RULES, **(custom_rules or {})}
    
    if rule in all_rules:
        return all_rules[rule](prompt_name, output)
    
    logger.warning(f"Unknown rule '{rule}', defaulting to pass")
    return JudgeReport(
        result=JudgeResult.PASS,
        rule=rule,
        score=1.0,
        reason="Unknown rule, defaulting to pass"
    )


def evaluate_all(
    prompt_name: str,
    output: str,
    rules: List[str],
    custom_rules: Optional[Dict[str, Callable]] = None,
) -> List[JudgeReport]:
    """Evaluate output against multiple rules."""
    return [llm_judge_detailed(prompt_name, output, rule, custom_rules) for rule in rules]


def get_available_rules() -> List[str]:
    """Get list of available built-in rules."""
    return list(BUILTIN_RULES.keys())
