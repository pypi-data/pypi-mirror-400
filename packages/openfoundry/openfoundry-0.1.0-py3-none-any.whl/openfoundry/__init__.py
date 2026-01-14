"""
OpenFoundry - Multi-Agent Orchestration Framework for the Full AI Lifecycle.

OpenFoundry provides an extensible framework for building, deploying, and managing
AI applications through specialized agent modules:

- **Forge**: Development & SDLC (Architect, Engineer, Quality agents)
- **Conveyor**: CI/CD & Deployment (DevOps, Release agents)
- **Shield**: Responsible AI & Safety (Guardrails, PII detection)
- **Watchtower**: Monitoring & Self-Healing (OpenTelemetry, Prometheus)
"""

__version__ = "0.1.0"
__author__ = "OpenFoundry Team"

from openfoundry.core.protocols import (
    AgentId,
    AgentProtocol,
    ExecutionContext,
    TaskId,
    TaskProtocol,
    TaskStatus,
)
from openfoundry.core.base_agent import BaseAgent
from openfoundry.core.task import Task, TaskResult

__all__ = [
    # Version
    "__version__",
    # Core Protocols
    "AgentId",
    "AgentProtocol",
    "ExecutionContext",
    "TaskId",
    "TaskProtocol",
    "TaskStatus",
    # Core Classes
    "BaseAgent",
    "Task",
    "TaskResult",
]

