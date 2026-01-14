"""
Release Agent for deployment and release management.

Responsibilities:
- Manage release versions and changelogs
- Plan deployment strategies (canary, blue-green)
- Generate rollback procedures
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from openfoundry.core.base_agent import BaseAgent
from openfoundry.core.context import Context
from openfoundry.core.protocols import TaskProtocol
from openfoundry.core.task import TaskResult


class ReleaseStrategy(BaseModel):
    """Structured release strategy output."""

    strategy_type: str = Field(description="canary, blue-green, rolling, etc.")
    phases: list[dict[str, Any]] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    rollback_triggers: list[str] = Field(default_factory=list)
    rollback_procedure: str = ""
    estimated_duration: str = ""


class ChangelogEntry(BaseModel):
    """Structured changelog entry."""

    version: str
    date: str
    sections: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Categories like Added, Changed, Fixed, etc.",
    )
    breaking_changes: list[str] = Field(default_factory=list)
    migration_notes: str = ""


class ReleaseAgent(BaseAgent):
    """
    Agent for release and deployment management.

    Capabilities:
    - release_strategy: Plan deployment strategies
    - changelog_generation: Generate changelogs from commits
    - version_bump: Determine version increments
    - rollback_plan: Create rollback procedures

    Example:
        release = ReleaseAgent()
        result = await release.execute(
            Task.create(
                task_type="release_strategy",
                payload={
                    "current_version": "1.2.3",
                    "changes": ["New API endpoint", "Bug fixes"],
                    "risk_level": "medium",
                }
            ),
            context
        )
    """

    MODULE: ClassVar[str] = "conveyor"

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.3,
    ):
        """
        Initialize the Release agent.

        Args:
            model: LLM model for generation
            temperature: Sampling temperature
        """
        super().__init__(
            name="release",
            description="Release and deployment management specialist",
            capabilities={
                "release_strategy",
                "changelog_generation",
                "version_bump",
                "rollback_plan",
            },
        )
        self._model = model
        self._temperature = temperature

    async def _execute_internal(
        self,
        task: TaskProtocol,
        context: Context,
    ) -> TaskResult:
        """Execute release tasks."""
        task_type = task.task_type
        payload = task.payload

        if task_type == "release_strategy":
            return await self._plan_release_strategy(task, context, payload)
        elif task_type == "changelog_generation":
            return await self._generate_changelog(task, context, payload)
        elif task_type == "version_bump":
            return await self._determine_version(task, context, payload)
        elif task_type == "rollback_plan":
            return await self._create_rollback_plan(task, context, payload)
        else:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Unknown task type: {task_type}",
                agent_id=self.agent_id,
            )

    async def _plan_release_strategy(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Plan a release strategy."""
        current_version = payload.get("current_version", "")
        changes = payload.get("changes", [])
        risk_level = payload.get("risk_level", "medium")
        environment = payload.get("environment", "production")

        system_prompt = """You are a release engineering expert. Plan a safe deployment strategy.

Consider:
- Risk level and blast radius
- Rollback capability
- Monitoring and success criteria
- Progressive rollout phases
- Communication plan

Choose appropriate strategy:
- Canary: Gradual rollout with traffic splitting
- Blue-Green: Full environment switch with instant rollback
- Rolling: Gradual pod replacement
- Feature flags: Controlled feature exposure

Respond with JSON matching ReleaseStrategy schema."""

        user_message = f"""Current Version: {current_version}
Changes:
{chr(10).join(f'- {c}' for c in changes)}
Risk Level: {risk_level}
Target Environment: {environment}"""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=ReleaseStrategy,
                model=self._model,
                temperature=self._temperature,
            )

            return TaskResult.success(
                task_id=task.task_id,
                output=result.model_dump(),
                agent_id=self.agent_id,
            )

        except Exception as e:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Release strategy planning failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _generate_changelog(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate changelog from commits or changes."""
        version = payload.get("version", "")
        commits = payload.get("commits", [])
        date = payload.get("date", "")

        system_prompt = """You are a technical writer. Generate a clear changelog entry.

Follow Keep a Changelog format:
- Added: New features
- Changed: Changes in existing functionality
- Deprecated: Soon-to-be removed features
- Removed: Removed features
- Fixed: Bug fixes
- Security: Vulnerability fixes

Be concise but informative. Highlight breaking changes prominently.

Respond with JSON matching ChangelogEntry schema."""

        user_message = f"""Version: {version}
Date: {date}
Commits/Changes:
{chr(10).join(f'- {c}' for c in commits)}"""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=ChangelogEntry,
                model=self._model,
                temperature=self._temperature,
            )

            return TaskResult.success(
                task_id=task.task_id,
                output=result.model_dump(),
                agent_id=self.agent_id,
            )

        except Exception as e:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Changelog generation failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _determine_version(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Determine semantic version bump."""
        current_version = payload.get("current_version", "0.0.0")
        changes = payload.get("changes", [])

        messages = [
            {
                "role": "system",
                "content": """You are a versioning expert following Semantic Versioning (semver).

Rules:
- MAJOR: Breaking changes, incompatible API changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes, backwards compatible

Analyze the changes and recommend the appropriate version bump.
Respond with JSON: {"bump_type": "major|minor|patch", "new_version": "x.y.z", "reasoning": "..."}""",
            },
            {
                "role": "user",
                "content": f"""Current Version: {current_version}
Changes:
{chr(10).join(f'- {c}' for c in changes)}""",
            },
        ]

        response = await context.llm.complete(
            messages=messages,
            model=self._model,
            temperature=self._temperature,
            response_format={"type": "json_object"},
        )

        import json

        return TaskResult.success(
            task_id=task.task_id,
            output=json.loads(response.content),
            agent_id=self.agent_id,
            token_usage=response.usage,
        )

    async def _create_rollback_plan(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Create a rollback procedure."""
        deployment_type = payload.get("deployment_type", "kubernetes")
        current_version = payload.get("current_version", "")
        previous_version = payload.get("previous_version", "")

        messages = [
            {
                "role": "system",
                "content": f"""You are a reliability engineer. Create a detailed rollback plan for {deployment_type}.

Include:
1. Trigger conditions (when to rollback)
2. Step-by-step rollback procedure
3. Verification steps
4. Communication template
5. Post-mortem checklist

Be specific and actionable.""",
            },
            {
                "role": "user",
                "content": f"""Deployment Type: {deployment_type}
Current Version: {current_version}
Rollback Target: {previous_version}""",
            },
        ]

        response = await context.llm.complete(
            messages=messages,
            model=self._model,
            temperature=self._temperature,
        )

        return TaskResult.success(
            task_id=task.task_id,
            output={"rollback_plan": response.content},
            agent_id=self.agent_id,
            token_usage=response.usage,
        )
