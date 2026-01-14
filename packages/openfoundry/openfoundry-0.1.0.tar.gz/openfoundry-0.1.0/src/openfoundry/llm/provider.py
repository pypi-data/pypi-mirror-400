"""
Unified LLM provider using LiteLLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, TypeVar

import litellm
import structlog
from pydantic import BaseModel

from openfoundry.core.protocols import LLMResponse, StreamChunk, TokenUsage

T = TypeVar("T", bound=BaseModel)

MODEL_ALIASES = {
    "gpt4": "gpt-4",
    "gpt4o": "gpt-4o",
    "claude": "claude-3-5-sonnet-20241022",
    "gemini": "gemini/gemini-2.0-flash",
}

# Cost per 1K tokens (input, output) in USD
MODEL_COSTS: dict[str, tuple[float, float]] = {
    "gpt-4o": (0.0025, 0.01),
    "gpt-4": (0.03, 0.06),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    "claude-3-5-sonnet-20241022": (0.003, 0.015),
    "claude-3-opus-20240229": (0.015, 0.075),
    "gemini/gemini-2.0-flash": (0.0001, 0.0004),
}


def resolve_model(model: str) -> str:
    return MODEL_ALIASES.get(model, model)


def estimate_tokens(text: str) -> int:
    """Estimate token count from text. Rough approximation: ~4 chars per token."""
    if not text:
        return 0
    return max(1, len(text) // 4)


@dataclass
class CostTracker:
    """Track costs across LLM calls."""

    total_cost: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    call_count: int = 0
    costs_by_model: dict[str, float] = field(default_factory=dict)

    def add_usage(self, model: str, usage: TokenUsage) -> float:
        """Add usage and return cost for this call."""
        input_cost, output_cost = MODEL_COSTS.get(model, (0.01, 0.03))
        cost = (usage.prompt_tokens * input_cost / 1000) + (
            usage.completion_tokens * output_cost / 1000
        )

        self.total_cost += cost
        self.total_prompt_tokens += usage.prompt_tokens
        self.total_completion_tokens += usage.completion_tokens
        self.call_count += 1
        self.costs_by_model[model] = self.costs_by_model.get(model, 0.0) + cost

        return cost


class LLMProvider:
    """Unified LLM provider using LiteLLM."""

    def __init__(
        self,
        default_model: str = "gpt-4o",
        fallback_models: list[str] | None = None,
        max_retries: int = 3,
        timeout: int = 120,
    ):
        self.default_model = resolve_model(default_model)
        self.fallback_models = [resolve_model(m) for m in (fallback_models or [])]
        self.max_retries = max_retries
        self.timeout = timeout
        self._logger = structlog.get_logger().bind(component="llm_provider")
        self._cost_tracker = CostTracker()

        litellm.set_verbose = False

    @property
    def cost_tracker(self) -> CostTracker:
        """Get the cost tracker."""
        return self._cost_tracker

    async def _try_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Any:
        """Try completion with a specific model."""
        try:
            return await litellm.acompletion(
                model=model,
                messages=messages,
                timeout=self.timeout,
                **kwargs,
            )
        except Exception as e:
            self._logger.warning(
                "model_completion_failed",
                model=model,
                error=str(e),
            )
            raise

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion with fallback support."""
        model = resolve_model(model or self.default_model)
        models_to_try = [model] + self.fallback_models

        last_error = None
        for m in models_to_try:
            try:
                response = await self._try_completion(m, messages, tools=tools, **kwargs)

                usage = TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )

                # Track cost
                cost = self._cost_tracker.add_usage(m, usage)
                self._logger.debug("completion_cost", model=m, cost=cost)

                return LLMResponse(
                    content=response.choices[0].message.content or "",
                    model=response.model,
                    usage=usage,
                    finish_reason=response.choices[0].finish_reason,
                    tool_calls=[tc.model_dump() for tc in (response.choices[0].message.tool_calls or [])],
                )
            except Exception as e:
                last_error = e
                continue

        raise last_error or RuntimeError("All models failed")

    async def stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Stream a completion."""
        model = resolve_model(model or self.default_model)

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            stream=True,
            timeout=self.timeout,
            **kwargs,
        )

        # Track tokens for streaming (estimate since we don't get usage)
        prompt_tokens = sum(estimate_tokens(m.get("content", "")) for m in messages)
        completion_tokens = 0

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                completion_tokens += estimate_tokens(content)
                yield StreamChunk(
                    content=content,
                    finish_reason=chunk.choices[0].finish_reason,
                )

        # Track estimated cost after streaming completes
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        self._cost_tracker.add_usage(model, usage)
