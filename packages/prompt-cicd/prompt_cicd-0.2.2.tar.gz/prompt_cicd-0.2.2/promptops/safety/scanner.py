"""
Safety scanning module for detecting sensitive content and potential risks.

Provides comprehensive content scanning with support for:
- PII detection (SSN, credit cards, emails, phone numbers, etc.)
- Prompt injection detection
- Sensitive keyword filtering
- Custom pattern matching
- Content classification
- Severity levels and risk scoring
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Tuple, Union

from ..exceptions import SafetyViolation

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Severity levels for safety findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Category(Enum):
    """Categories of safety issues."""
    PII = "pii"
    CREDENTIALS = "credentials"
    INJECTION = "injection"
    HARMFUL_CONTENT = "harmful_content"
    BANNED_TERM = "banned_term"
    CUSTOM = "custom"


@dataclass
class Finding:
    """Represents a single safety finding."""
    message: str
    severity: Severity = Severity.MEDIUM
    category: Category = Category.BANNED_TERM
    matched_text: Optional[str] = None
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "matched_text": self.matched_text,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "rule_id": self.rule_id,
            "metadata": self.metadata,
        }


@dataclass
class SafetyReport:
    """Report from a safety scan."""
    safe: bool
    findings: List[Finding]
    scanned_text_length: int = 0
    scan_duration_ms: float = 0.0
    risk_score: float = 0.0
    blocked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def critical_findings(self) -> List[Finding]:
        """Get critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]
    
    @property
    def high_findings(self) -> List[Finding]:
        """Get high severity findings."""
        return [f for f in self.findings if f.severity == Severity.HIGH]
    
    @property
    def findings_by_category(self) -> Dict[Category, List[Finding]]:
        """Group findings by category."""
        result: Dict[Category, List[Finding]] = {}
        for finding in self.findings:
            if finding.category not in result:
                result[finding.category] = []
            result[finding.category].append(finding)
        return result
    
    @property
    def findings_by_severity(self) -> Dict[Severity, List[Finding]]:
        """Group findings by severity."""
        result: Dict[Severity, List[Finding]] = {}
        for finding in self.findings:
            if finding.severity not in result:
                result[finding.severity] = []
            result[finding.severity].append(finding)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "safe": self.safe,
            "findings": [f.to_dict() for f in self.findings],
            "scanned_text_length": self.scanned_text_length,
            "scan_duration_ms": self.scan_duration_ms,
            "risk_score": self.risk_score,
            "blocked": self.blocked,
            "finding_count": len(self.findings),
            "critical_count": len(self.critical_findings),
            "high_count": len(self.high_findings),
            "metadata": self.metadata,
        }
    
    def raise_if_unsafe(self, min_severity: Severity = Severity.HIGH) -> None:
        """
        Raise SafetyViolation if findings meet minimum severity.
        
        Args:
            min_severity: Minimum severity to trigger exception.
        
        Raises:
            SafetyViolation: If unsafe findings exist at or above min_severity.
        """
        severity_order = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        min_index = severity_order.index(min_severity)
        
        for finding in self.findings:
            if severity_order.index(finding.severity) >= min_index:
                raise SafetyViolation(
                    f"Safety violation: {finding.message} "
                    f"(severity: {finding.severity.value})"
                )


@dataclass
class ScanRule:
    """A rule for the safety scanner."""
    id: str
    name: str
    pattern: Union[str, Pattern]
    category: Category
    severity: Severity
    message_template: str = "Matched rule: {name}"
    enabled: bool = True
    case_sensitive: bool = False
    
    def __post_init__(self):
        """Compile pattern if it's a string."""
        if isinstance(self.pattern, str):
            flags = 0 if self.case_sensitive else re.IGNORECASE
            self.pattern = re.compile(self.pattern, flags)


# Built-in PII patterns
PII_PATTERNS: Dict[str, Tuple[str, str]] = {
    "ssn": (
        r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        "Social Security Number detected",
    ),
    "credit_card": (
        r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "Credit card number detected",
    ),
    "email": (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Email address detected",
    ),
    "phone_us": (
        r"\b(?:\+1[-\s]?)?(?:\(?\d{3}\)?[-\s]?)?\d{3}[-\s]?\d{4}\b",
        "US phone number detected",
    ),
    "ip_address": (
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "IP address detected",
    ),
    "date_of_birth": (
        r"\b(?:0[1-9]|1[0-2])[/\-](?:0[1-9]|[12]\d|3[01])[/\-](?:19|20)\d{2}\b",
        "Date of birth pattern detected",
    ),
    "passport": (
        r"\b[A-Z]{1,2}\d{6,9}\b",
        "Passport number pattern detected",
    ),
    "drivers_license": (
        r"\b[A-Z]\d{7,8}\b",
        "Driver's license pattern detected",
    ),
}

# Built-in credential patterns
CREDENTIAL_PATTERNS: Dict[str, Tuple[str, str]] = {
    "api_key": (
        r"\b(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w-]{20,}['\"]?\b",
        "API key detected",
    ),
    "password": (
        r"\b(?:password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]{4,}['\"]?\b",
        "Password in text detected",
    ),
    "bearer_token": (
        r"\bBearer\s+[\w-]+\.[\w-]+\.[\w-]+\b",
        "Bearer token detected",
    ),
    "aws_key": (
        r"\bAKIA[0-9A-Z]{16}\b",
        "AWS access key detected",
    ),
    "github_token": (
        r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b",
        "GitHub token detected",
    ),
    "private_key": (
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "Private key detected",
    ),
    "connection_string": (
        r"\b(?:mongodb|mysql|postgresql|redis|amqp)://[^\s]+\b",
        "Database connection string detected",
    ),
}

# Prompt injection patterns
INJECTION_PATTERNS: Dict[str, Tuple[str, str]] = {
    "ignore_instructions": (
        r"\bignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions?\b",
        "Potential prompt injection: ignore instructions",
    ),
    "new_instructions": (
        r"\b(?:new|override|forget)\s+instructions?\b",
        "Potential prompt injection: override instructions",
    ),
    "roleplay_jailbreak": (
        r"\b(?:pretend|act\s+as\s+if|imagine)\s+you\s+(?:are|have|can)\b",
        "Potential jailbreak attempt: roleplay",
    ),
    "developer_mode": (
        r"\b(?:developer|debug|admin|root)\s+mode\b",
        "Potential jailbreak attempt: developer mode",
    ),
    "do_anything": (
        r"\bdo\s+anything\s+now\b",
        "Potential jailbreak attempt: DAN",
    ),
    "system_prompt_leak": (
        r"\b(?:show|reveal|display|print|output)\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions)\b",
        "Potential prompt leak attempt",
    ),
}


class SafetyScanner:
    """
    Comprehensive safety scanner for text content.
    
    Features:
    - PII detection (SSN, credit cards, emails, etc.)
    - Credential detection (API keys, passwords, tokens)
    - Prompt injection detection
    - Custom rule support
    - Configurable severity thresholds
    - Risk scoring
    
    Example:
        >>> scanner = SafetyScanner()
        >>> scanner.enable_pii_detection()
        >>> scanner.add_banned_terms(["confidential", "secret"])
        >>> 
        >>> report = scanner.scan("My SSN is 123-45-6789")
        >>> if not report.safe:
        ...     print(f"Found {len(report.findings)} issues")
    """
    
    def __init__(
        self,
        strict: bool = False,
        block_on_critical: bool = True,
        min_block_severity: Severity = Severity.HIGH,
    ):
        """
        Initialize the safety scanner.
        
        Args:
            strict: If True, use stricter detection rules.
            block_on_critical: If True, block content with critical findings.
            min_block_severity: Minimum severity to block content.
        """
        self.strict = strict
        self.block_on_critical = block_on_critical
        self.min_block_severity = min_block_severity
        
        self._rules: List[ScanRule] = []
        self._banned_terms: Set[str] = set()
        self._allowed_terms: Set[str] = set()  # Whitelist
        self._custom_validators: List[Callable[[str], List[Finding]]] = []
        
        # Severity weights for risk scoring
        self._severity_weights = {
            Severity.INFO: 0.0,
            Severity.LOW: 0.1,
            Severity.MEDIUM: 0.3,
            Severity.HIGH: 0.6,
            Severity.CRITICAL: 1.0,
        }
        
        # Initialize with basic banned terms
        self._banned_terms.update(["ssn", "credit card", "password"])
        
        logger.debug(f"SafetyScanner initialized (strict={strict})")
    
    def enable_pii_detection(
        self,
        types: Optional[List[str]] = None,
        severity: Severity = Severity.HIGH,
    ) -> "SafetyScanner":
        """
        Enable PII detection.
        
        Args:
            types: List of PII types to detect (None for all).
            severity: Severity level for PII findings.
        
        Returns:
            Self for chaining.
        """
        patterns = PII_PATTERNS if types is None else {
            k: v for k, v in PII_PATTERNS.items() if k in types
        }
        
        for pii_type, (pattern, message) in patterns.items():
            self._rules.append(ScanRule(
                id=f"pii_{pii_type}",
                name=f"PII: {pii_type}",
                pattern=pattern,
                category=Category.PII,
                severity=severity,
                message_template=message,
            ))
        
        logger.debug(f"Enabled PII detection for {len(patterns)} types")
        return self
    
    def enable_credential_detection(
        self,
        types: Optional[List[str]] = None,
        severity: Severity = Severity.CRITICAL,
    ) -> "SafetyScanner":
        """
        Enable credential detection.
        
        Args:
            types: List of credential types to detect (None for all).
            severity: Severity level for credential findings.
        
        Returns:
            Self for chaining.
        """
        patterns = CREDENTIAL_PATTERNS if types is None else {
            k: v for k, v in CREDENTIAL_PATTERNS.items() if k in types
        }
        
        for cred_type, (pattern, message) in patterns.items():
            self._rules.append(ScanRule(
                id=f"cred_{cred_type}",
                name=f"Credential: {cred_type}",
                pattern=pattern,
                category=Category.CREDENTIALS,
                severity=severity,
                message_template=message,
            ))
        
        logger.debug(f"Enabled credential detection for {len(patterns)} types")
        return self
    
    def enable_injection_detection(
        self,
        types: Optional[List[str]] = None,
        severity: Severity = Severity.HIGH,
    ) -> "SafetyScanner":
        """
        Enable prompt injection detection.
        
        Args:
            types: List of injection types to detect (None for all).
            severity: Severity level for injection findings.
        
        Returns:
            Self for chaining.
        """
        patterns = INJECTION_PATTERNS if types is None else {
            k: v for k, v in INJECTION_PATTERNS.items() if k in types
        }
        
        for inj_type, (pattern, message) in patterns.items():
            self._rules.append(ScanRule(
                id=f"inj_{inj_type}",
                name=f"Injection: {inj_type}",
                pattern=pattern,
                category=Category.INJECTION,
                severity=severity,
                message_template=message,
            ))
        
        logger.debug(f"Enabled injection detection for {len(patterns)} types")
        return self
    
    def add_rule(self, rule: ScanRule) -> "SafetyScanner":
        """
        Add a custom scan rule.
        
        Args:
            rule: The ScanRule to add.
        
        Returns:
            Self for chaining.
        """
        self._rules.append(rule)
        logger.debug(f"Added custom rule: {rule.id}")
        return self
    
    def add_pattern(
        self,
        pattern: str,
        message: str,
        category: Category = Category.CUSTOM,
        severity: Severity = Severity.MEDIUM,
        rule_id: Optional[str] = None,
    ) -> "SafetyScanner":
        """
        Add a custom pattern to detect.
        
        Args:
            pattern: Regex pattern.
            message: Message for findings.
            category: Category for findings.
            severity: Severity for findings.
            rule_id: Optional rule ID.
        
        Returns:
            Self for chaining.
        """
        rule = ScanRule(
            id=rule_id or f"custom_{len(self._rules)}",
            name=message,
            pattern=pattern,
            category=category,
            severity=severity,
            message_template=message,
        )
        return self.add_rule(rule)
    
    def add_banned_terms(
        self,
        terms: List[str],
        severity: Severity = Severity.MEDIUM,
    ) -> "SafetyScanner":
        """
        Add banned terms to detect.
        
        Args:
            terms: List of terms to ban.
            severity: Severity for findings.
        
        Returns:
            Self for chaining.
        """
        for term in terms:
            self._banned_terms.add(term.lower())
        
        logger.debug(f"Added {len(terms)} banned terms")
        return self
    
    def add_allowed_terms(self, terms: List[str]) -> "SafetyScanner":
        """
        Add terms to whitelist (won't be flagged).
        
        Args:
            terms: List of terms to allow.
        
        Returns:
            Self for chaining.
        """
        for term in terms:
            self._allowed_terms.add(term.lower())
        return self
    
    def add_validator(
        self,
        validator: Callable[[str], List[Finding]],
    ) -> "SafetyScanner":
        """
        Add a custom validation function.
        
        Args:
            validator: Function that takes text and returns findings.
        
        Returns:
            Self for chaining.
        """
        self._custom_validators.append(validator)
        return self
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a rule by ID.
        
        Args:
            rule_id: The rule ID to remove.
        
        Returns:
            True if rule was found and removed.
        """
        for i, rule in enumerate(self._rules):
            if rule.id == rule_id:
                self._rules.pop(i)
                return True
        return False
    
    def _check_banned_terms(self, text: str) -> List[Finding]:
        """Check for banned terms in text."""
        findings = []
        text_lower = text.lower()
        
        for term in self._banned_terms:
            if term in self._allowed_terms:
                continue
            
            # Find all occurrences
            start = 0
            while True:
                pos = text_lower.find(term, start)
                if pos == -1:
                    break
                
                findings.append(Finding(
                    message=f"Blocked term detected: {term}",
                    severity=Severity.MEDIUM,
                    category=Category.BANNED_TERM,
                    matched_text=text[pos:pos + len(term)],
                    start_pos=pos,
                    end_pos=pos + len(term),
                    rule_id="banned_term",
                ))
                start = pos + 1
        
        return findings
    
    def _check_rules(self, text: str) -> List[Finding]:
        """Check all regex rules against text."""
        findings = []
        
        for rule in self._rules:
            if not rule.enabled:
                continue
            
            for match in rule.pattern.finditer(text):
                matched_text = match.group(0)
                
                # Check whitelist
                if matched_text.lower() in self._allowed_terms:
                    continue
                
                findings.append(Finding(
                    message=rule.message_template.format(
                        name=rule.name,
                        match=matched_text,
                    ),
                    severity=rule.severity,
                    category=rule.category,
                    matched_text=matched_text,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    rule_id=rule.id,
                ))
        
        return findings
    
    def _calculate_risk_score(self, findings: List[Finding]) -> float:
        """Calculate overall risk score from findings."""
        if not findings:
            return 0.0
        
        total_weight = sum(
            self._severity_weights[f.severity]
            for f in findings
        )
        
        # Normalize to 0-100 scale, cap at 100
        return min(100.0, total_weight * 20)
    
    def _should_block(self, findings: List[Finding]) -> bool:
        """Determine if content should be blocked."""
        if not findings:
            return False
        
        severity_order = [
            Severity.INFO, Severity.LOW, Severity.MEDIUM,
            Severity.HIGH, Severity.CRITICAL
        ]
        min_index = severity_order.index(self.min_block_severity)
        
        for finding in findings:
            finding_index = severity_order.index(finding.severity)
            if finding_index >= min_index:
                return True
        
        return False
    
    def scan(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SafetyReport:
        """
        Scan text for safety issues.
        
        Args:
            text: Text to scan.
            context: Optional context metadata.
        
        Returns:
            SafetyReport with findings.
        """
        import time
        start_time = time.time()
        
        findings: List[Finding] = []
        
        # Check banned terms
        findings.extend(self._check_banned_terms(text))
        
        # Check regex rules
        findings.extend(self._check_rules(text))
        
        # Run custom validators
        for validator in self._custom_validators:
            try:
                findings.extend(validator(text))
            except Exception as e:
                logger.error(f"Custom validator error: {e}")
        
        # Calculate metrics
        risk_score = self._calculate_risk_score(findings)
        should_block = self._should_block(findings)
        scan_duration = (time.time() - start_time) * 1000
        
        report = SafetyReport(
            safe=len(findings) == 0,
            findings=findings,
            scanned_text_length=len(text),
            scan_duration_ms=scan_duration,
            risk_score=risk_score,
            blocked=should_block,
            metadata=context or {},
        )
        
        if findings:
            logger.warning(
                f"Safety scan found {len(findings)} issues "
                f"(risk score: {risk_score:.1f}, blocked: {should_block})"
            )
        else:
            logger.debug(f"Safety scan passed ({scan_duration:.1f}ms)")
        
        return report
    
    def scan_and_raise(
        self,
        text: str,
        min_severity: Severity = Severity.HIGH,
    ) -> SafetyReport:
        """
        Scan text and raise exception if unsafe.
        
        Args:
            text: Text to scan.
            min_severity: Minimum severity to raise exception.
        
        Returns:
            SafetyReport if safe.
        
        Raises:
            SafetyViolation: If findings meet minimum severity.
        """
        report = self.scan(text)
        report.raise_if_unsafe(min_severity)
        return report
    
    def redact(
        self,
        text: str,
        replacement: str = "[REDACTED]",
        categories: Optional[List[Category]] = None,
    ) -> Tuple[str, SafetyReport]:
        """
        Scan and redact sensitive content.
        
        Args:
            text: Text to scan and redact.
            replacement: Replacement string for redacted content.
            categories: Categories to redact (None for all).
        
        Returns:
            Tuple of (redacted_text, report).
        """
        report = self.scan(text)
        
        if not report.findings:
            return text, report
        
        # Sort findings by position (reverse order for safe replacement)
        findings_to_redact = report.findings
        if categories:
            findings_to_redact = [
                f for f in findings_to_redact
                if f.category in categories
            ]
        
        findings_to_redact.sort(
            key=lambda f: (f.start_pos or 0),
            reverse=True
        )
        
        # Apply redactions
        redacted = text
        for finding in findings_to_redact:
            if finding.start_pos is not None and finding.end_pos is not None:
                redacted = (
                    redacted[:finding.start_pos] +
                    replacement +
                    redacted[finding.end_pos:]
                )
        
        return redacted, report
    
    def get_rules(self) -> List[ScanRule]:
        """Get all configured rules."""
        return list(self._rules)
    
    def get_banned_terms(self) -> Set[str]:
        """Get all banned terms."""
        return set(self._banned_terms)
    
    def clear_rules(self) -> None:
        """Clear all rules."""
        self._rules.clear()
    
    def clear_banned_terms(self) -> None:
        """Clear all banned terms."""
        self._banned_terms.clear()


def run_safety_scan(
    text: str,
    strict: bool = False,
    enable_pii: bool = True,
    enable_credentials: bool = True,
    enable_injection: bool = False,
    banned_terms: Optional[List[str]] = None,
) -> SafetyReport:
    """
    Convenience function for running a safety scan.
    
    Args:
        text: Text to scan.
        strict: Use strict mode.
        enable_pii: Enable PII detection.
        enable_credentials: Enable credential detection.
        enable_injection: Enable prompt injection detection.
        banned_terms: Additional banned terms.
    
    Returns:
        SafetyReport with findings.
    """
    scanner = SafetyScanner(strict=strict)
    
    if enable_pii:
        scanner.enable_pii_detection()
    
    if enable_credentials:
        scanner.enable_credential_detection()
    
    if enable_injection:
        scanner.enable_injection_detection()
    
    if banned_terms:
        scanner.add_banned_terms(banned_terms)
    
    return scanner.scan(text)


def create_scanner_from_config(config: Dict[str, Any]) -> SafetyScanner:
    """
    Create a scanner from a configuration dictionary.
    
    Args:
        config: Configuration dictionary with scanner settings.
    
    Returns:
        Configured SafetyScanner.
    """
    scanner = SafetyScanner(
        strict=config.get("strict", False),
        block_on_critical=config.get("block_on_critical", True),
        min_block_severity=Severity(config.get("min_block_severity", "high")),
    )
    
    if config.get("enable_pii", False):
        pii_types = config.get("pii_types")
        scanner.enable_pii_detection(types=pii_types)
    
    if config.get("enable_credentials", False):
        cred_types = config.get("credential_types")
        scanner.enable_credential_detection(types=cred_types)
    
    if config.get("enable_injection", False):
        inj_types = config.get("injection_types")
        scanner.enable_injection_detection(types=inj_types)
    
    if config.get("banned_terms"):
        scanner.add_banned_terms(config["banned_terms"])
    
    if config.get("allowed_terms"):
        scanner.add_allowed_terms(config["allowed_terms"])
    
    for pattern_config in config.get("custom_patterns", []):
        scanner.add_pattern(
            pattern=pattern_config["pattern"],
            message=pattern_config["message"],
            category=Category(pattern_config.get("category", "custom")),
            severity=Severity(pattern_config.get("severity", "medium")),
        )
    
    return scanner


# Singleton scanner for quick access
_default_scanner: Optional[SafetyScanner] = None


def get_default_scanner() -> SafetyScanner:
    """Get or create the default scanner instance."""
    global _default_scanner
    if _default_scanner is None:
        _default_scanner = SafetyScanner()
        _default_scanner.enable_pii_detection()
        _default_scanner.enable_credential_detection()
    return _default_scanner


def quick_scan(text: str) -> SafetyReport:
    """Quick scan using the default scanner."""
    return get_default_scanner().scan(text)
