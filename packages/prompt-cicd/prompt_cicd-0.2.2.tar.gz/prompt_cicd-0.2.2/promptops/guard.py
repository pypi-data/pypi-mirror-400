"""Extensible guard for enforcing safety, approval, budget, and custom rules."""

import logging
from typing import Callable, Optional, List, Dict, Any
from .safety.scanner import run_safety_scan
from .exceptions import SafetyViolation, ApprovalRequired, BudgetExceeded

logger = logging.getLogger("promptops.guard")

class Guard:
    """
    Extensible guard for enforcing safety, approval, budget, and custom rules.
    """
    def __init__(self):
        self._rules: List[Callable[[str, str, dict], Optional[Exception]]] = []
        self._callbacks: List[Callable[[str, str, dict, Optional[Exception]], None]] = []

    def add_rule(self, rule: Callable[[str, str, dict], Optional[Exception]]):
        """Register a custom guard rule. Rule returns Exception or None."""
        self._rules.append(rule)

    def add_callback(self, callback: Callable[[str, str, dict, Optional[Exception]], None]):
        """Register a callback for guard events."""
        self._callbacks.append(callback)

    def enforce(self, text: str, env: str = "dev", context: Optional[dict] = None):
        """Run all guard rules and raise on first failure."""
        context = context or {}
        # Built-in safety rule
        exc = self._safety_rule(text, env, context)
        if exc:
            self._notify(text, env, context, exc)
            raise exc
        # Custom rules
        for rule in self._rules:
            exc = rule(text, env, context)
            if exc:
                self._notify(text, env, context, exc)
                raise exc
        self._notify(text, env, context, None)

    def _safety_rule(self, text: str, env: str, context: dict) -> Optional[Exception]:
        strict = env == "prod"
        report = run_safety_scan(text, strict)
        if not getattr(report, "safe", True):
            logger.warning(f"Safety violation: {report.findings}")
            return SafetyViolation(
                "\n".join(getattr(f, "message", str(f)) for f in getattr(report, "findings", [])),
                findings=getattr(report, "findings", []),
                risk_score=getattr(report, "risk", None)
            )
        return None

    def _notify(self, text: str, env: str, context: dict, exc: Optional[Exception]):
        for cb in self._callbacks:
            try:
                cb(text, env, context, exc)
            except Exception as e:
                logger.error(f"Guard callback failed: {e}")


def enforce_safety(text, env):
    """
    Legacy function for backward compatibility. Raises SafetyViolation if not safe.
    """
    strict = env == "prod"
    report = run_safety_scan(text, strict)
    if not getattr(report, "safe", True):
        raise SafetyViolation(
            "\n".join(getattr(f, "message", str(f)) for f in getattr(report, "findings", [])),
            findings=getattr(report, "findings", []),
            risk_score=getattr(report, "risk", None)
        )

def enforce_safety(text, env):
    """
    Legacy function for backward compatibility. Raises SafetyViolation if not safe.
    """
    strict = env == "prod"
    report = run_safety_scan(text, strict)
    if not getattr(report, "safe", True):
        raise SafetyViolation(
            "\n".join(getattr(f, "message", str(f)) for f in getattr(report, "findings", [])),
            findings=getattr(report, "findings", []),
            risk_score=getattr(report, "risk", None)
        )
