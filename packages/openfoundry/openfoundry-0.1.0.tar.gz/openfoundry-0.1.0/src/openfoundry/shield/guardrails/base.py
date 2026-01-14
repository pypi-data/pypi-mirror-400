"""
Base guardrail classes and chain implementation.

Guardrails validate and transform content before/after LLM calls.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import structlog

from openfoundry.core.protocols import ExecutionContext, GuardrailResult


class BaseGuardrail(ABC):
    """
    Abstract base class for guardrails.

    Guardrails can:
    - Block content that violates policies
    - Transform/sanitize content
    - Log violations for monitoring
    """

    def __init__(self, name: str, description: str = ""):
        self._name = name
        self._description = description
        self._logger = structlog.get_logger().bind(guardrail=name)

    @property
    def name(self) -> str:
        """Guardrail name."""
        return self._name

    @property
    def description(self) -> str:
        """Guardrail description."""
        return self._description

    @abstractmethod
    async def validate(
        self,
        content: str,
        context: ExecutionContext | None = None,
    ) -> GuardrailResult:
        """
        Validate content against this guardrail.

        Args:
            content: Content to validate
            context: Optional execution context

        Returns:
            GuardrailResult indicating pass/fail and any transformations
        """
        ...


class GuardrailChain:
    """
    Chain multiple guardrails for sequential validation.

    Supports:
    - Sequential validation with early exit on failure
    - Content transformation between guardrails
    - Aggregated results and logging

    Example:
        chain = GuardrailChain([
            PromptInjectionGuard(),
            PIIDetector(action="mask"),
            ToxicityGuard(),
        ])

        result = await chain.validate(user_input)
        if not result.passed:
            return "Content blocked: " + result.message
    """

    def __init__(
        self,
        guardrails: list[BaseGuardrail],
        fail_fast: bool = True,
    ):
        """
        Initialize the guardrail chain.

        Args:
            guardrails: List of guardrails to apply
            fail_fast: Stop on first failure if True
        """
        self.guardrails = guardrails
        self.fail_fast = fail_fast
        self._logger = structlog.get_logger().bind(component="guardrail_chain")

    async def validate(
        self,
        content: str,
        context: ExecutionContext | None = None,
    ) -> GuardrailResult:
        """
        Run content through all guardrails.

        Args:
            content: Content to validate
            context: Optional execution context

        Returns:
            Aggregated GuardrailResult
        """
        current_content = content
        all_violations: list[str] = []
        all_passed = True

        for guardrail in self.guardrails:
            result = await guardrail.validate(current_content, context)

            if not result.passed:
                all_passed = False
                all_violations.extend(result.violations)

                self._logger.warning(
                    "guardrail_failed",
                    guardrail=guardrail.name,
                    violations=result.violations,
                )

                if self.fail_fast:
                    return GuardrailResult(
                        passed=False,
                        message=f"Blocked by {guardrail.name}: {result.message}",
                        violations=all_violations,
                        confidence=result.confidence,
                    )

            # Use sanitized content for next guardrail
            if result.sanitized_content:
                current_content = result.sanitized_content

        if all_passed:
            return GuardrailResult(
                passed=True,
                message="All guardrails passed",
                sanitized_content=current_content if current_content != content else None,
            )
        else:
            return GuardrailResult(
                passed=False,
                message="Content failed guardrail validation",
                violations=all_violations,
                sanitized_content=current_content if current_content != content else None,
            )

    def add_guardrail(self, guardrail: BaseGuardrail) -> GuardrailChain:
        """Add a guardrail to the chain."""
        self.guardrails.append(guardrail)
        return self

    def remove_guardrail(self, name: str) -> bool:
        """Remove a guardrail by name."""
        for i, g in enumerate(self.guardrails):
            if g.name == name:
                self.guardrails.pop(i)
                return True
        return False
