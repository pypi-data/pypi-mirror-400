"""
Engineer Agent for code generation and development.

Responsibilities:
- Generate code from designs and specifications
- Refactor and improve existing code
- Fix bugs with self-correction
- Implement features based on requirements
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from openfoundry.core.base_agent import BaseAgent
from openfoundry.core.context import Context
from openfoundry.core.protocols import TaskProtocol
from openfoundry.core.task import TaskResult


class CodeGenerationResult(BaseModel):
    """Structured code generation output."""

    files: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of files with 'path' and 'content' keys",
    )
    explanation: str = Field(
        default="",
        description="Explanation of the generated code",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Required dependencies/packages",
    )
    usage_example: str = Field(
        default="",
        description="Example of how to use the generated code",
    )


class CodeReviewResult(BaseModel):
    """Structured code review output."""

    summary: str
    issues: list[dict[str, Any]] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    security_concerns: list[str] = Field(default_factory=list)
    score: int = Field(ge=1, le=10, description="Code quality score 1-10")


class EngineerAgent(BaseAgent):
    """
    Agent for code generation and development tasks.

    Capabilities:
    - code_generation: Generate code from specifications
    - code_refactor: Refactor and improve code
    - bug_fix: Fix bugs with analysis
    - feature_implementation: Implement features
    - code_review: Review code for quality
    """

    MODULE: ClassVar[str] = "forge"

    def __init__(
        self,
        model: str = "claude-3-5-sonnet",
        max_iterations: int = 3,
        temperature: float = 0.2,
    ):
        """
        Initialize the Engineer agent.

        Args:
            model: LLM model optimized for code generation
            max_iterations: Max self-correction iterations
            temperature: Sampling temperature (lower = more deterministic)
        """
        super().__init__(
            name="engineer",
            description="Code generation and development specialist",
            capabilities={
                "code_generation",
                "code_refactor",
                "bug_fix",
                "feature_implementation",
                "code_review",
            },
            max_iterations=max_iterations,
        )
        self._model = model
        self._temperature = temperature

    async def _execute_internal(
        self,
        task: TaskProtocol,
        context: Context,
    ) -> TaskResult:
        """Execute engineering tasks."""
        task_type = task.task_type
        payload = task.payload

        if task_type == "code_generation":
            return await self._generate_code(task, context, payload)
        elif task_type == "code_refactor":
            return await self._refactor_code(task, context, payload)
        elif task_type == "bug_fix":
            return await self._fix_bug(task, context, payload)
        elif task_type == "feature_implementation":
            return await self._implement_feature(task, context, payload)
        elif task_type == "code_review":
            return await self._review_code(task, context, payload)
        else:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Unknown task type: {task_type}",
                agent_id=self.agent_id,
            )

    async def _generate_code(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate code from specification."""
        specification = payload.get("specification", "")
        language = payload.get("language", "python")
        framework = payload.get("framework", "")
        style_guide = payload.get("style_guide", "")

        system_prompt = f"""You are an expert {language} developer. Generate clean, production-ready code.

Guidelines:
- Follow {language} best practices and idioms
- Include proper error handling
- Add type hints where applicable
- Write modular, testable code
- Include inline documentation for complex logic
{f'- Use the {framework} framework' if framework else ''}
{f'- Follow style guide: {style_guide}' if style_guide else ''}

Respond with a JSON object containing:
- files: array of {{path, content}} objects
- explanation: brief explanation of the code
- dependencies: required packages
- usage_example: how to use the code"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Specification:\n{specification}"},
        ]

        try:
            result = await context.llm.complete_structured(
                messages=messages,
                output_schema=CodeGenerationResult,
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
                error=f"Code generation failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _refactor_code(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Refactor existing code."""
        code = payload.get("code", "")
        goals = payload.get("goals", ["improve readability", "reduce complexity"])
        language = payload.get("language", "python")

        system_prompt = f"""You are a {language} refactoring expert. Improve the code while maintaining functionality.

Refactoring goals:
{chr(10).join(f'- {g}' for g in goals)}

Provide:
1. Refactored code
2. List of changes made
3. Explanation of improvements"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Code to refactor:\n```{language}\n{code}\n```"},
        ]

        response = await context.llm.complete(
            messages=messages,
            model=self._model,
            temperature=self._temperature,
        )

        return TaskResult.success(
            task_id=task.task_id,
            output={"refactored_code": response.content},
            agent_id=self.agent_id,
            token_usage=response.usage,
        )

    async def _fix_bug(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Fix a bug with self-correction loop."""
        code = payload.get("code", "")
        error_message = payload.get("error", "")
        description = payload.get("description", "")
        test_cases = payload.get("test_cases", [])

        # Initial analysis and fix
        system_prompt = """You are a debugging expert. Analyze the bug and provide a fix.

Your response should include:
1. Root cause analysis
2. Fixed code
3. Explanation of the fix
4. Prevention suggestions"""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""Bug Description: {description}

Error Message:
{error_message}

Code:
```
{code}
```

Test Cases:
{chr(10).join(f'- {tc}' for tc in test_cases) if test_cases else 'None provided'}""",
            },
        ]

        # Self-correction loop
        for iteration in range(self._max_iterations):
            response = await context.llm.complete(
                messages=messages,
                model=self._model,
                temperature=self._temperature,
            )

            # In a full implementation, we would:
            # 1. Extract the fixed code
            # 2. Run tests to verify
            # 3. If tests fail, add feedback and iterate

            # For now, return the response
            return TaskResult.success(
                task_id=task.task_id,
                output={
                    "analysis": response.content,
                    "iterations": iteration + 1,
                },
                agent_id=self.agent_id,
                token_usage=response.usage,
            )

        return TaskResult.failure(
            task_id=task.task_id,
            error="Max iterations reached without successful fix",
            agent_id=self.agent_id,
        )

    async def _implement_feature(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Implement a feature based on requirements."""
        requirements = payload.get("requirements", "")
        existing_code = payload.get("existing_code", "")
        language = payload.get("language", "python")
        architecture = payload.get("architecture", "")

        system_prompt = f"""You are a senior {language} developer implementing a new feature.

Guidelines:
- Integrate seamlessly with existing code
- Follow existing patterns and conventions
- Maintain backward compatibility
- Include necessary tests
{f'- Follow architecture: {architecture}' if architecture else ''}

Provide:
1. New/modified files
2. Integration instructions
3. Test suggestions"""

        user_message = f"""Feature Requirements:
{requirements}

Existing Code Context:
```{language}
{existing_code if existing_code else 'New project - no existing code'}
```"""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=CodeGenerationResult,
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
                error=f"Feature implementation failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _review_code(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Review code for quality and issues."""
        code = payload.get("code", "")
        language = payload.get("language", "python")
        focus_areas = payload.get("focus_areas", [])

        system_prompt = f"""You are a senior code reviewer. Analyze the {language} code thoroughly.

Review focus:
{chr(10).join(f'- {area}' for area in focus_areas) if focus_areas else '- General code quality'}

Evaluate:
1. Code correctness and logic
2. Error handling
3. Security vulnerabilities
4. Performance considerations
5. Maintainability and readability
6. Best practices adherence

Respond with JSON matching the CodeReviewResult schema."""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"```{language}\n{code}\n```"},
                ],
                output_schema=CodeReviewResult,
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
                error=f"Code review failed: {str(e)}",
                agent_id=self.agent_id,
            )
