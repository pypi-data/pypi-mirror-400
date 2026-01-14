"""
Architect Agent for system design and requirements analysis.

Responsibilities:
- Translate high-level requirements into system designs
- Generate API schemas and interface definitions
- Create architecture decision records
- Design database schemas
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from openfoundry.core.base_agent import BaseAgent
from openfoundry.core.context import Context
from openfoundry.core.protocols import TaskProtocol
from openfoundry.core.task import TaskResult


class SystemDesign(BaseModel):
    """Structured system design output."""

    summary: str = Field(description="Brief summary of the design")
    components: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of system components with their responsibilities",
    )
    interfaces: list[dict[str, Any]] = Field(
        default_factory=list,
        description="API interfaces and contracts",
    )
    data_models: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Data models and schemas",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="External dependencies and services",
    )
    considerations: list[str] = Field(
        default_factory=list,
        description="Architecture considerations and trade-offs",
    )


class APISchema(BaseModel):
    """Structured API schema output."""

    title: str
    description: str
    version: str = "1.0.0"
    endpoints: list[dict[str, Any]] = Field(default_factory=list)
    schemas: dict[str, Any] = Field(default_factory=dict)


class ArchitectAgent(BaseAgent):
    """
    Agent for system architecture and design tasks.

    Capabilities:
    - system_design: Create comprehensive system designs
    - api_design: Design API schemas and endpoints
    - database_design: Design database schemas
    - requirements_analysis: Analyze and refine requirements
    """

    MODULE: ClassVar[str] = "forge"

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.3,
    ):
        """
        Initialize the Architect agent.

        Args:
            model: LLM model to use for design tasks
            temperature: Sampling temperature (lower = more focused)
        """
        super().__init__(
            name="architect",
            description="System architecture and design specialist",
            capabilities={
                "system_design",
                "api_design",
                "database_design",
                "requirements_analysis",
            },
        )
        self._model = model
        self._temperature = temperature

    async def _execute_internal(
        self,
        task: TaskProtocol,
        context: Context,
    ) -> TaskResult:
        """Execute architecture tasks."""
        task_type = task.task_type
        payload = task.payload

        if task_type == "system_design":
            return await self._design_system(task, context, payload)
        elif task_type == "api_design":
            return await self._design_api(task, context, payload)
        elif task_type == "database_design":
            return await self._design_database(task, context, payload)
        elif task_type == "requirements_analysis":
            return await self._analyze_requirements(task, context, payload)
        else:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Unknown task type: {task_type}",
                agent_id=self.agent_id,
            )

    async def _design_system(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Create a system design from requirements."""
        requirements = payload.get("requirements", "")
        constraints = payload.get("constraints", [])
        existing_systems = payload.get("existing_systems", [])

        system_prompt = """You are a senior software architect. Create a detailed system design based on the requirements.

Your design should include:
1. A summary of the proposed architecture
2. Key components and their responsibilities
3. Interfaces between components (APIs, events, etc.)
4. Data models and storage considerations
5. External dependencies
6. Architecture trade-offs and considerations

Respond with a JSON object matching the SystemDesign schema."""

        user_message = f"""Requirements:
{requirements}

Constraints:
{chr(10).join(f'- {c}' for c in constraints) if constraints else 'None specified'}

Existing Systems to Integrate:
{chr(10).join(f'- {s}' for s in existing_systems) if existing_systems else 'None'}"""

        try:
            design = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=SystemDesign,
                model=self._model,
                temperature=self._temperature,
            )

            return TaskResult.success(
                task_id=task.task_id,
                output=design.model_dump(),
                agent_id=self.agent_id,
            )

        except Exception as e:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Design generation failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _design_api(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Design API schema and endpoints."""
        description = payload.get("description", "")
        resources = payload.get("resources", [])
        style = payload.get("style", "REST")

        system_prompt = f"""You are an API design expert. Design a {style} API based on the requirements.

Your design should include:
1. Clear endpoint definitions with HTTP methods
2. Request/response schemas
3. Authentication requirements
4. Error response formats
5. Pagination patterns where applicable

Respond with a JSON object matching the APISchema schema."""

        user_message = f"""API Description:
{description}

Resources to model:
{chr(10).join(f'- {r}' for r in resources) if resources else 'Determine from description'}

API Style: {style}"""

        try:
            schema = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=APISchema,
                model=self._model,
                temperature=self._temperature,
            )

            return TaskResult.success(
                task_id=task.task_id,
                output=schema.model_dump(),
                agent_id=self.agent_id,
            )

        except Exception as e:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"API design failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _design_database(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Design database schema."""
        entities = payload.get("entities", [])
        database_type = payload.get("database_type", "PostgreSQL")
        requirements = payload.get("requirements", "")

        messages = [
            {
                "role": "system",
                "content": f"""You are a database design expert. Design a {database_type} schema.

Include:
1. Table definitions with columns and types
2. Primary and foreign keys
3. Indexes for common queries
4. Constraints and validations
5. Relationships between tables""",
            },
            {
                "role": "user",
                "content": f"""Requirements:
{requirements}

Entities:
{chr(10).join(f'- {e}' for e in entities) if entities else 'Determine from requirements'}""",
            },
        ]

        response = await context.llm.complete(
            messages=messages,
            model=self._model,
            temperature=self._temperature,
        )

        return TaskResult.success(
            task_id=task.task_id,
            output={"schema": response.content},
            agent_id=self.agent_id,
            token_usage=response.usage,
        )

    async def _analyze_requirements(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Analyze and refine requirements."""
        raw_requirements = payload.get("requirements", "")

        messages = [
            {
                "role": "system",
                "content": """You are a requirements analyst. Analyze the provided requirements and:

1. Identify functional requirements
2. Identify non-functional requirements
3. Highlight ambiguities or gaps
4. Suggest clarifying questions
5. Prioritize requirements (must-have, should-have, nice-to-have)

Provide structured analysis in JSON format.""",
            },
            {"role": "user", "content": raw_requirements},
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
