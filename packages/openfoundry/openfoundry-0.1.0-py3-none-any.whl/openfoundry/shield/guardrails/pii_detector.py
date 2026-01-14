"""
PII (Personally Identifiable Information) detection guardrail.

Detects and optionally masks sensitive personal information.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from openfoundry.core.protocols import ExecutionContext, GuardrailResult
from openfoundry.shield.guardrails.base import BaseGuardrail


class PIIAction(Enum):
    """Action to take when PII is detected."""

    BLOCK = auto()  # Block the content entirely
    MASK = auto()   # Mask the PII and continue
    WARN = auto()   # Log warning but allow


@dataclass
class PIIPattern:
    """Definition of a PII pattern."""

    name: str
    pattern: str
    mask: str = "[REDACTED]"
    description: str = ""


class PIIDetector(BaseGuardrail):
    """
    Guardrail for detecting and handling PII.

    Supports detection of:
    - Email addresses
    - Phone numbers
    - Social Security Numbers
    - Credit card numbers
    - IP addresses
    - Custom patterns

    Can block, mask, or warn on detection.
    """

    DEFAULT_PATTERNS = [
        PIIPattern(
            name="EMAIL_ADDRESS",
            pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            mask="[EMAIL]",
            description="Email addresses",
        ),
        PIIPattern(
            name="PHONE_NUMBER",
            pattern=r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
            mask="[PHONE]",
            description="US phone numbers",
        ),
        PIIPattern(
            name="US_SSN",
            pattern=r"\b[0-9]{3}[-\s]?[0-9]{2}[-\s]?[0-9]{4}\b",
            mask="[SSN]",
            description="US Social Security Numbers",
        ),
        PIIPattern(
            name="CREDIT_CARD",
            pattern=r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
            mask="[CREDIT_CARD]",
            description="Credit card numbers",
        ),
        PIIPattern(
            name="IP_ADDRESS",
            pattern=r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            mask="[IP]",
            description="IPv4 addresses",
        ),
        PIIPattern(
            name="DATE_OF_BIRTH",
            pattern=r"\b(?:0?[1-9]|1[0-2])[/\-](?:0?[1-9]|[12][0-9]|3[01])[/\-](?:19|20)?[0-9]{2}\b",
            mask="[DOB]",
            description="Dates that may be birth dates",
        ),
    ]

    def __init__(
        self,
        action: PIIAction | str = PIIAction.MASK,
        patterns: list[str] | None = None,
        custom_patterns: list[PIIPattern] | None = None,
    ):
        """
        Initialize the PII detector.

        Args:
            action: Action to take on PII detection (block, mask, warn)
            patterns: List of pattern names to enable (None = all)
            custom_patterns: Additional custom patterns
        """
        super().__init__(
            name="pii_detector",
            description="Detects and handles personally identifiable information",
        )

        if isinstance(action, str):
            action = PIIAction[action.upper()]
        self.action = action

        # Build pattern list
        if patterns:
            self.patterns = [
                p for p in self.DEFAULT_PATTERNS if p.name in patterns
            ]
        else:
            self.patterns = list(self.DEFAULT_PATTERNS)

        if custom_patterns:
            self.patterns.extend(custom_patterns)

        # Compile patterns
        self._compiled = [
            (p, re.compile(p.pattern, re.IGNORECASE))
            for p in self.patterns
        ]

    async def validate(
        self,
        content: str,
        context: ExecutionContext | None = None,
    ) -> GuardrailResult:
        """
        Check content for PII.

        Args:
            content: Content to check
            context: Optional execution context

        Returns:
            GuardrailResult with detection results and optionally masked content
        """
        violations: list[str] = []
        detected_pii: dict[str, list[str]] = {}
        sanitized = content

        for pii_pattern, compiled in self._compiled:
            matches = compiled.findall(content)
            if matches:
                detected_pii[pii_pattern.name] = matches
                violations.append(
                    f"{pii_pattern.name}: {len(matches)} instance(s) detected"
                )

                # Mask if action is MASK
                if self.action == PIIAction.MASK:
                    sanitized = compiled.sub(pii_pattern.mask, sanitized)

        if not violations:
            return GuardrailResult.allow("No PII detected")

        self._logger.warning(
            "pii_detected",
            pii_types=list(detected_pii.keys()),
            action=self.action.name,
        )

        if self.action == PIIAction.BLOCK:
            return GuardrailResult(
                passed=False,
                message="PII detected in content",
                violations=violations,
            )
        elif self.action == PIIAction.MASK:
            return GuardrailResult(
                passed=True,
                message="PII masked in content",
                violations=violations,
                sanitized_content=sanitized,
            )
        else:  # WARN
            return GuardrailResult(
                passed=True,
                message="PII detected (warning only)",
                violations=violations,
            )

    def add_pattern(self, pattern: PIIPattern) -> None:
        """Add a custom PII pattern."""
        self.patterns.append(pattern)
        self._compiled.append((pattern, re.compile(pattern.pattern, re.IGNORECASE)))
