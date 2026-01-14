"""
DevOps Agent for infrastructure and deployment tasks.

Responsibilities:
- Generate Infrastructure as Code (Terraform, CloudFormation)
- Create Docker configurations
- Generate Kubernetes manifests
- CI/CD pipeline configuration
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from openfoundry.core.base_agent import BaseAgent
from openfoundry.core.context import Context
from openfoundry.core.protocols import TaskProtocol
from openfoundry.core.task import TaskResult


class DockerConfig(BaseModel):
    """Structured Docker configuration output."""

    dockerfile: str = Field(description="Dockerfile content")
    docker_compose: str | None = Field(default=None, description="docker-compose.yml if applicable")
    build_args: dict[str, str] = Field(default_factory=dict)
    env_vars: list[str] = Field(default_factory=list, description="Required environment variables")
    ports: list[str] = Field(default_factory=list)
    volumes: list[str] = Field(default_factory=list)


class KubernetesManifest(BaseModel):
    """Structured Kubernetes manifest output."""

    manifests: list[dict[str, Any]] = Field(default_factory=list)
    namespace: str = "default"
    resources: list[str] = Field(default_factory=list, description="Resource types created")
    notes: str = ""


class DevOpsAgent(BaseAgent):
    """
    Agent for DevOps and infrastructure tasks.

    Capabilities:
    - docker_config: Generate Dockerfile and docker-compose
    - kubernetes_manifest: Generate K8s manifests
    - terraform_config: Generate Terraform configurations
    - ci_pipeline: Generate CI/CD pipeline configurations

    Example:
        devops = DevOpsAgent()
        result = await devops.execute(
            Task.create(
                task_type="docker_config",
                payload={
                    "application": "Python FastAPI web service",
                    "language": "python",
                    "framework": "fastapi",
                }
            ),
            context
        )
    """

    MODULE: ClassVar[str] = "conveyor"

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.2,
    ):
        """
        Initialize the DevOps agent.

        Args:
            model: LLM model for generation
            temperature: Sampling temperature
        """
        super().__init__(
            name="devops",
            description="DevOps and infrastructure specialist",
            capabilities={
                "docker_config",
                "kubernetes_manifest",
                "terraform_config",
                "ci_pipeline",
            },
        )
        self._model = model
        self._temperature = temperature

    async def _execute_internal(
        self,
        task: TaskProtocol,
        context: Context,
    ) -> TaskResult:
        """Execute DevOps tasks."""
        task_type = task.task_type
        payload = task.payload

        if task_type == "docker_config":
            return await self._generate_docker_config(task, context, payload)
        elif task_type == "kubernetes_manifest":
            return await self._generate_k8s_manifest(task, context, payload)
        elif task_type == "terraform_config":
            return await self._generate_terraform(task, context, payload)
        elif task_type == "ci_pipeline":
            return await self._generate_ci_pipeline(task, context, payload)
        else:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Unknown task type: {task_type}",
                agent_id=self.agent_id,
            )

    async def _generate_docker_config(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate Docker configuration with multistage builds."""
        application = payload.get("application", "")
        language = payload.get("language", "python")
        framework = payload.get("framework", "")
        requirements = payload.get("requirements", [])
        multistage = payload.get("multistage", True)

        system_prompt = f"""You are a Docker expert. Generate production-ready Docker configurations.

Guidelines:
- {"Use multi-stage builds for smaller images" if multistage else "Use single stage build"}
- Follow security best practices (non-root user, minimal base image)
- Optimize layer caching by ordering commands properly
- Include health checks where applicable
- Use appropriate base images for {language}
- Pin versions for reproducibility
- Add .dockerignore recommendations

Respond with JSON matching DockerConfig schema."""

        user_message = f"""Application: {application}
Language: {language}
Framework: {framework}
Requirements: {', '.join(requirements) if requirements else 'Standard dependencies'}
Multi-stage: {multistage}"""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=DockerConfig,
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
                error=f"Docker config generation failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _generate_k8s_manifest(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate Kubernetes manifests."""
        application = payload.get("application", "")
        replicas = payload.get("replicas", 2)
        resources = payload.get("resources", {})
        expose = payload.get("expose", True)
        namespace = payload.get("namespace", "default")

        system_prompt = """You are a Kubernetes expert. Generate production-ready K8s manifests.

Include:
- Deployment with proper resource limits and requests
- Service for internal communication
- Ingress if external exposure needed
- ConfigMaps/Secrets for configuration
- HorizontalPodAutoscaler for scaling
- PodDisruptionBudget for availability

Follow best practices:
- Use specific image tags
- Define resource limits
- Include liveness/readiness probes
- Use labels consistently

Respond with JSON matching KubernetesManifest schema."""

        user_message = f"""Application: {application}
Replicas: {replicas}
Namespace: {namespace}
Resource Requirements: {resources}
Expose Externally: {expose}"""

        try:
            result = await context.llm.complete_structured(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                output_schema=KubernetesManifest,
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
                error=f"K8s manifest generation failed: {str(e)}",
                agent_id=self.agent_id,
            )

    async def _generate_terraform(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate Terraform configuration."""
        cloud = payload.get("cloud", "aws")
        infrastructure = payload.get("infrastructure", "")
        region = payload.get("region", "us-east-1")

        messages = [
            {
                "role": "system",
                "content": f"""You are a Terraform expert for {cloud.upper()}. Generate production-ready IaC.

Guidelines:
- Use modules for reusability
- Include proper variable definitions
- Add outputs for important values
- Follow {cloud} best practices
- Include proper tagging

Provide complete, deployable Terraform code.""",
            },
            {
                "role": "user",
                "content": f"""Infrastructure needed: {infrastructure}
Cloud Provider: {cloud}
Region: {region}""",
            },
        ]

        response = await context.llm.complete(
            messages=messages,
            model=self._model,
            temperature=self._temperature,
        )

        return TaskResult.success(
            task_id=task.task_id,
            output={"terraform": response.content},
            agent_id=self.agent_id,
            token_usage=response.usage,
        )

    async def _generate_ci_pipeline(
        self,
        task: TaskProtocol,
        context: Context,
        payload: dict[str, Any],
    ) -> TaskResult:
        """Generate CI/CD pipeline configuration."""
        platform = payload.get("platform", "github_actions")
        language = payload.get("language", "python")
        steps = payload.get("steps", ["lint", "test", "build", "deploy"])

        messages = [
            {
                "role": "system",
                "content": f"""You are a CI/CD expert. Generate a production-ready pipeline for {platform}.

Include stages for:
{chr(10).join(f'- {step}' for step in steps)}

Best practices:
- Cache dependencies
- Run tests in parallel where possible
- Use matrix builds for multiple versions
- Include proper secrets management
- Add status badges""",
            },
            {
                "role": "user",
                "content": f"""Platform: {platform}
Language: {language}
Steps: {', '.join(steps)}""",
            },
        ]

        response = await context.llm.complete(
            messages=messages,
            model=self._model,
            temperature=self._temperature,
        )

        return TaskResult.success(
            task_id=task.task_id,
            output={"pipeline": response.content},
            agent_id=self.agent_id,
            token_usage=response.usage,
        )
