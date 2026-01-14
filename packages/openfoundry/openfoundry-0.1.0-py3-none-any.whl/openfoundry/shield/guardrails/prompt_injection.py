"""
Prompt injection detection guardrail.

Detects attempts to manipulate LLM behavior through malicious prompts.
"""

from __future__ import annotations

import re
from typing import Any

from openfoundry.core.protocols import ExecutionContext, GuardrailResult
from openfoundry.shield.guardrails.base import BaseGuardrail


class PromptInjectionGuard(BaseGuardrail):
    """
    Guardrail for detecting prompt injection attempts.

    Uses pattern matching and heuristics to detect:
    - Instruction override attempts
    - Role-playing attacks
    - Delimiter injection
    - Context manipulation

    For production use, consider adding an ML-based classifier.
    """

    # Patterns that may indicate prompt injection
    SUSPICIOUS_PATTERNS = [
        # Instruction overrides
        r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|above|prior)",
        r"forget\s+(everything|all|what)\s+(you\s+)?(know|learned|were\s+told)",
        r"new\s+instructions?:",
        r"system\s*:\s*you\s+are",
        # Role-playing
        r"pretend\s+(you\s+are|to\s+be)\s+",
        r"act\s+as\s+(if\s+you\s+are|a)\s+",
        r"you\s+are\s+now\s+",
        r"roleplay\s+as",
        # Delimiter attacks
        r"```\s*(system|assistant|user)\s*```",
        r"<\|?(system|endoftext|im_start|im_end)\|?>",
        r"\[\[system\]\]",
        # Jailbreak patterns
        r"do\s+anything\s+now",
        r"DAN\s+mode",
        r"developer\s+mode\s+(enabled|on)",
        r"bypass\s+(safety|content|filter)",
        r"unlock\s+(your|hidden)\s+(potential|capabilities)",
    ]

    def __init__(
        self,
        threshold: float = 0.8,
        additional_patterns: list[str] | None = None,
    ):
        """
        Initialize the prompt injection guard.

        Args:
            threshold: Confidence threshold for blocking (0-1)
            additional_patterns: Extra regex patterns to check
        """
        super().__init__(
            name="prompt_injection",
            description="Detects prompt injection attempts",
        )
        self.threshold = threshold
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS]

        if additional_patterns:
            self.patterns.extend(
                re.compile(p, re.IGNORECASE) for p in additional_patterns
            )

    async def validate(
        self,
        content: str,
        context: ExecutionContext | None = None,
    ) -> GuardrailResult:
        """
        Check content for prompt injection patterns.

        Args:
            content: User input to validate
            context: Optional execution context

        Returns:
            GuardrailResult with detection results
        """
        violations: list[str] = []
        matched_patterns: list[str] = []

        for pattern in self.patterns:
            matches = pattern.findall(content)
            if matches:
                matched_patterns.append(pattern.pattern)
                violations.append(f"Suspicious pattern detected: {matches[0]}")

        # Calculate confidence based on number and severity of matches
        if not matched_patterns:
            return GuardrailResult.allow("No injection patterns detected")

        # More matches = higher confidence of injection
        confidence = min(1.0, 0.5 + (len(matched_patterns) * 0.15))

        if confidence >= self.threshold:
            self._logger.warning(
                "prompt_injection_detected",
                pattern_count=len(matched_patterns),
                confidence=confidence,
            )
            return GuardrailResult(
                passed=False,
                message="Potential prompt injection detected",
                violations=violations,
                confidence=confidence,
            )
        else:
            self._logger.info(
                "suspicious_patterns_below_threshold",
                pattern_count=len(matched_patterns),
                confidence=confidence,
            )
            return GuardrailResult(
                passed=True,
                message="Suspicious patterns detected but below threshold",
                violations=violations,
                confidence=confidence,
            )

    def add_pattern(self, pattern: str) -> None:
        """Add a custom detection pattern."""
        self.patterns.append(re.compile(pattern, re.IGNORECASE))
