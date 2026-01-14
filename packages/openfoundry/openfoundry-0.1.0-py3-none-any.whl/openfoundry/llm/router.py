"""
Model router for intelligent model selection.

Supports:
- Condition-based routing
- A/B testing
- Fallback chains
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable

import structlog


@dataclass
class RoutingCondition:
    name: str
    model: str
    condition: Callable[[dict[str, Any]], bool]
    priority: int = 0


@dataclass
class ABTest:
    name: str
    model_a: str
    model_b: str
    percentage_a: float = 0.5


class ModelRouter:
    """Routes requests to appropriate models."""

    def __init__(self, default_model: str = "gpt-4o"):
        self.default_model = default_model
        self._conditions: list[RoutingCondition] = []
        self._ab_tests: dict[str, ABTest] = {}
        self._logger = structlog.get_logger().bind(component="model_router")

    def add_condition(
        self,
        name: str,
        model: str,
        condition: Callable[[dict[str, Any]], bool],
        priority: int = 0,
    ) -> None:
        """Add a routing condition."""
        self._conditions.append(
            RoutingCondition(name=name, model=model, condition=condition, priority=priority)
        )
        self._conditions.sort(key=lambda c: c.priority, reverse=True)

    def add_ab_test(
        self,
        name: str,
        model_a: str,
        model_b: str,
        percentage_a: float = 0.5,
    ) -> None:
        """Add an A/B test."""
        self._ab_tests[name] = ABTest(
            name=name,
            model_a=model_a,
            model_b=model_b,
            percentage_a=percentage_a,
        )

    def route(self, context: dict[str, Any]) -> str:
        """Determine which model to use."""
        # Check conditions first
        for cond in self._conditions:
            try:
                if cond.condition(context):
                    return cond.model
            except Exception:
                pass

        # Check A/B tests
        ab_test_name = context.get("ab_test")
        if ab_test_name and ab_test_name in self._ab_tests:
            test = self._ab_tests[ab_test_name]
            if random.random() < test.percentage_a:
                return test.model_a
            return test.model_b

        return self.default_model
