"""
Metrics collection using Prometheus.

Provides metrics for:
- Task execution
- Agent performance
- LLM usage
- System health
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    pass


class MetricsCollector:
    """
    Collector for Prometheus metrics.

    Tracks:
    - Task counts and latencies
    - Agent health and performance
    - LLM token usage and costs
    - Error rates

    Example:
        collector = MetricsCollector()
        collector.record_task_execution(
            agent="forge.engineer",
            task_type="code_generation",
            duration_ms=1500,
            success=True,
        )
    """

    def __init__(self, prefix: str = "openfoundry"):
        """
        Initialize the metrics collector.

        Args:
            prefix: Metric name prefix
        """
        self.prefix = prefix
        self._logger = structlog.get_logger().bind(component="metrics")

        try:
            from prometheus_client import Counter, Histogram, Gauge

            # Task metrics
            self.task_total = Counter(
                f"{prefix}_tasks_total",
                "Total number of tasks processed",
                ["agent", "task_type", "status"],
            )

            self.task_duration = Histogram(
                f"{prefix}_task_duration_seconds",
                "Task execution duration in seconds",
                ["agent", "task_type"],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            )

            # LLM metrics
            self.llm_tokens = Counter(
                f"{prefix}_llm_tokens_total",
                "Total LLM tokens used",
                ["model", "type"],  # type: prompt or completion
            )

            self.llm_cost = Counter(
                f"{prefix}_llm_cost_usd_total",
                "Total LLM cost in USD",
                ["model"],
            )

            self.llm_requests = Counter(
                f"{prefix}_llm_requests_total",
                "Total LLM API requests",
                ["model", "status"],
            )

            # Agent metrics
            self.active_agents = Gauge(
                f"{prefix}_active_agents",
                "Number of active agents",
                ["module"],
            )

            self.agent_health = Gauge(
                f"{prefix}_agent_health",
                "Agent health status (1=healthy, 0=unhealthy)",
                ["agent"],
            )

            # Guardrail metrics
            self.guardrail_checks = Counter(
                f"{prefix}_guardrail_checks_total",
                "Total guardrail checks",
                ["guardrail", "result"],
            )

            self._enabled = True

        except ImportError:
            self._logger.warning(
                "prometheus_client_not_installed",
                message="Install prometheus-client for metrics",
            )
            self._enabled = False

    def record_task_execution(
        self,
        agent: str,
        task_type: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        """
        Record task execution metrics.

        Args:
            agent: Agent ID that executed the task
            task_type: Type of task
            duration_ms: Execution duration in milliseconds
            success: Whether task succeeded
        """
        if not self._enabled:
            return

        status = "success" if success else "failure"
        self.task_total.labels(agent=agent, task_type=task_type, status=status).inc()
        self.task_duration.labels(agent=agent, task_type=task_type).observe(
            duration_ms / 1000
        )

    def record_llm_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        success: bool = True,
    ) -> None:
        """
        Record LLM usage metrics.

        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost_usd: Cost in USD
            success: Whether request succeeded
        """
        if not self._enabled:
            return

        self.llm_tokens.labels(model=model, type="prompt").inc(prompt_tokens)
        self.llm_tokens.labels(model=model, type="completion").inc(completion_tokens)
        self.llm_cost.labels(model=model).inc(cost_usd)

        status = "success" if success else "failure"
        self.llm_requests.labels(model=model, status=status).inc()

    def record_guardrail_check(
        self,
        guardrail: str,
        passed: bool,
    ) -> None:
        """
        Record guardrail check metrics.

        Args:
            guardrail: Guardrail name
            passed: Whether check passed
        """
        if not self._enabled:
            return

        result = "passed" if passed else "blocked"
        self.guardrail_checks.labels(guardrail=guardrail, result=result).inc()

    def set_agent_health(self, agent: str, healthy: bool) -> None:
        """
        Set agent health status.

        Args:
            agent: Agent ID
            healthy: Whether agent is healthy
        """
        if not self._enabled:
            return

        self.agent_health.labels(agent=agent).set(1 if healthy else 0)

    def set_active_agents(self, module: str, count: int) -> None:
        """
        Set active agent count.

        Args:
            module: Module name
            count: Number of active agents
        """
        if not self._enabled:
            return

        self.active_agents.labels(module=module).set(count)


# Global metrics collector instance
_metrics: MetricsCollector | None = None


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics
