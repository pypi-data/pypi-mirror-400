"""
Quality Agent for testing and quality assurance.

Responsibilities:
- Generate unit, integration, and e2e tests
- Analyze code coverage
- Perform static analysis
- Generate test data and mocks
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from openfoundry.core.base_agent import BaseAgent
from openfoundry.core.context import Context
from openfoundry.core.protocols import TaskProtocol
from openfoundry.core.task import TaskResult


class TestGenerationResult(BaseModel):
    """Structured test generation output."""

    test_files: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of test files with 'path' and 'content'",
    )
    test_count: int = Field(default=0, description="Number of test cases generated")
    coverage_areas: list[str] = Field(
        default_factory=list,
        description="Areas of code covered by tests",
    )
    fixtures: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Test fixtures and mock data",
    )
    setup_instructions: str = Field(
        default="",
        description="Instructions for running the tests",
    )


class TestAnalysisResult(BaseModel):
    """Structured test analysis output."""

    coverage_percentage: float = Field(description="Estimated test coverage")
    uncovered_areas: list[str] = Field(default_factory=list)
    test_quality_score: int = Field(ge=1, le=10)
    recommendations: list[str] = Field(default_factory=list)
    critical_gaps: list[str] = Field(default_factory=list)


class QualityAgent(BaseAgent):
    """
    Agent for testing and quality assurance tasks.

    Capabilities:
    - test_generation: Generate tests for code
    - test_analysis: Analyze existing test coverage
    - test_data_generation: Create test data and fixtures
    - static_analysis: Perform code quality analysis
    """

    MODULE: ClassVar[str] = "forge"

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.2,
    ):
        """
        Initialize the Quality agent.

        Args:
            model: LLM model for test generation
            temperature: Sampling temperature
        """
        super().__init__(
            name="quality",
            description="Testing and quality assurance specialist",
            capabilities={
                "test_generation",
                "test_analysis",
                "test_data_generation",
                "static_analysis",
            },
        )
        self._model = model
        self._temperature = temperature

    async def _execute_internal(
        self,
        task: TaskProtocol,
        context: Context,
    ) -> TaskResult:
        """Execute quality assurance tasks."""
        task_type = task.task_type
        payload = task.payload

        if task_type == "test_generation":
            return await self._generate_tests(task, context, payload)
        elif task_type == "test_analysis":
            return await self._analyze_tests(task, context, payload)
        elif task_type == "test_data_generation":
            return await self._generate_test_data(task, context, payload)
        elif task_type == "static_analysis":
            return await self._static_analysis(task, context, payload)
        else:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Unknown task type: {task_type}",
                agent_id=self.agent_id,
            )

    async def _generate_tests(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate comprehensive tests for code."""
        code = payload.get("code", "")
        language = payload.get("language", "python")
        test_framework = payload.get("test_framework", "pytest")
        test_types = payload.get("test_types", ["unit"])
        coverage_target = payload.get("coverage_target", 80)

        system_prompt = f"""You are a testing expert. Generate comprehensive {test_framework} tests for the provided {language} code.

Requirements:
- Target {coverage_target}% code coverage
- Test types to generate: {', '.join(test_types)}
- Include edge cases and error scenarios
- Use proper test naming conventions
- Add clear assertions with descriptive messages
- Include necessary fixtures and mocks

For each test:
- Test the happy path
- Test edge cases (null, empty, boundary values)
- Test error handling
- Test any state changes

Respond with JSON matching TestGenerationResult schema."""

        user_message = f"""Code to test:
```{language}
{code}
```

Generate {test_framework} tests covering:
{chr(10).join(f'- {t} tests' for t in test_types)}"""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=TestGenerationResult,
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
                error=f"Test generation failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _analyze_tests(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Analyze existing test coverage and quality."""
        source_code = payload.get("source_code", "")
        test_code = payload.get("test_code", "")
        language = payload.get("language", "python")

        system_prompt = """You are a test quality analyst. Analyze the test coverage and quality.

Evaluate:
1. Code coverage estimation (based on code paths tested)
2. Test quality and completeness
3. Missing test scenarios
4. Test maintainability
5. Mock and fixture quality

Identify:
- Critical untested code paths
- Edge cases not covered
- Potential false positives/negatives
- Recommendations for improvement

Respond with JSON matching TestAnalysisResult schema."""

        user_message = f"""Source Code:
```{language}
{source_code}
```

Test Code:
```{language}
{test_code}
```"""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=TestAnalysisResult,
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
                error=f"Test analysis failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _generate_test_data(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate test data and fixtures."""
        schema = payload.get("schema", {})
        count = payload.get("count", 10)
        constraints = payload.get("constraints", [])
        data_type = payload.get("data_type", "json")

        system_prompt = f"""You are a test data generation expert. Generate realistic test data.

Requirements:
- Generate {count} records
- Output format: {data_type}
- Follow the provided schema
- Include edge cases in the data
- Make data realistic and varied

Constraints:
{chr(10).join(f'- {c}' for c in constraints) if constraints else 'None'}

Provide:
1. Generated test data
2. Edge case records
3. Invalid data examples for negative testing"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Schema:\n{schema}"},
        ]

        response = await context.llm.complete(
            messages=messages,
            model=self._model,
            temperature=0.5,  # Higher temperature for variety
            response_format={"type": "json_object"},
        )

        import json

        return TaskResult.success(
            task_id=task.task_id,
            output=json.loads(response.content),
            agent_id=self.agent_id,
            token_usage=response.usage,
        )

    async def _static_analysis(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Perform static code analysis."""
        code = payload.get("code", "")
        language = payload.get("language", "python")
        checks = payload.get("checks", [
            "complexity",
            "security",
            "style",
            "bugs",
            "performance",
        ])

        system_prompt = f"""You are a static code analysis expert. Analyze the {language} code.

Perform the following checks:
{chr(10).join(f'- {c}' for c in checks)}

For each issue found, provide:
1. Severity (critical, high, medium, low, info)
2. Location (line number if possible)
3. Description
4. Suggested fix

Also provide:
- Overall code quality score (1-10)
- Summary statistics
- Priority recommendations"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"```{language}\n{code}\n```"},
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
