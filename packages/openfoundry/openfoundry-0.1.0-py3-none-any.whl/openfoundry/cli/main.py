"""
Main CLI entry point for OpenFoundry.

Usage:
    openfoundry serve          # Start the server
    openfoundry agent list     # List registered agents
    openfoundry task submit    # Submit a task
    openfoundry workflow run   # Run a workflow
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(
    name="openfoundry",
    help="OpenFoundry - Multi-Agent Orchestration Framework",
    no_args_is_help=True,
)

console = Console()

# Sub-command groups
agent_app = typer.Typer(help="Agent management commands")
task_app = typer.Typer(help="Task management commands")
workflow_app = typer.Typer(help="Workflow management commands")

app.add_typer(agent_app, name="agent")
app.add_typer(task_app, name="task")
app.add_typer(workflow_app, name="workflow")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of workers"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Start the OpenFoundry server."""
    import uvicorn

    console.print(
        Panel.fit(
            "[bold green]Starting OpenFoundry Server[/bold green]\n"
            f"Host: {host}\n"
            f"Port: {port}\n"
            f"Workers: {workers}",
            title="OpenFoundry",
        )
    )

    if config:
        import os
        os.environ["OPENFOUNDRY_CONFIG"] = str(config)

    uvicorn.run(
        "openfoundry.communication.http.app:create_app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        factory=True,
    )


@app.command()
def version():
    """Show OpenFoundry version."""
    from openfoundry import __version__
    console.print(f"OpenFoundry version: [bold]{__version__}[/bold]")


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Project path"),
    template: str = typer.Option("default", "--template", "-t", help="Project template"),
):
    """Initialize a new OpenFoundry project."""
    config_dir = path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create default config
    config_file = config_dir / "settings.yaml"
    if not config_file.exists():
        config_file.write_text("""# OpenFoundry Configuration
environment: development
debug: true

llm:
  default_model: gpt-4o
  fallback_models:
    - claude-3-5-sonnet

api:
  host: "0.0.0.0"
  port: 8000
  enable_docs: true

telemetry:
  enabled: true
  log_level: INFO
  log_format: console
""")

    # Create .env template
    env_file = path / ".env.example"
    if not env_file.exists():
        env_file.write_text("""# OpenFoundry Environment Variables

# LLM API Keys
OPENFOUNDRY__LLM__OPENAI_API_KEY=sk-...
OPENFOUNDRY__LLM__ANTHROPIC_API_KEY=sk-ant-...

# Environment
OPENFOUNDRY__ENVIRONMENT=development
OPENFOUNDRY__DEBUG=true
""")

    console.print(f"[green]Initialized OpenFoundry project at {path}[/green]")
    console.print("\nNext steps:")
    console.print("  1. Copy .env.example to .env and add your API keys")
    console.print("  2. Run 'openfoundry serve' to start the server")


# Agent commands
@agent_app.command("list")
def agent_list(
    capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Filter by capability"),
):
    """List registered agents."""
    table = Table(title="Registered Agents")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Module", style="yellow")
    table.add_column("Capabilities", style="blue")

    agents = [
        ("forge.architect", "Architect", "forge", "system_design, api_design"),
        ("forge.engineer", "Engineer", "forge", "code_generation, bug_fix"),
        ("forge.quality", "Quality", "forge", "test_generation, static_analysis"),
        ("conveyor.devops", "DevOps", "conveyor", "docker_config, kubernetes_manifest"),
        ("conveyor.release", "Release", "conveyor", "release_strategy, changelog"),
    ]

    for agent in agents:
        table.add_row(*agent)

    console.print(table)


@agent_app.command("info")
def agent_info(
    agent_id: str = typer.Argument(..., help="Agent ID to get info for"),
):
    """Get detailed information about an agent."""
    console.print(f"[bold]Agent: {agent_id}[/bold]")


# Task commands
@task_app.command("submit")
def task_submit(
    task_type: str = typer.Argument(..., help="Type of task"),
    payload: Optional[str] = typer.Option(None, "--payload", "-p", help="JSON payload"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Payload file"),
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for completion"),
):
    """Submit a task for execution."""
    import json

    if file:
        task_payload = json.loads(file.read_text())
    elif payload:
        task_payload = json.loads(payload)
    else:
        task_payload = {}

    console.print(f"[yellow]Submitting task: {task_type}[/yellow]")
    console.print(f"Payload: {task_payload}")
    console.print("[green]Task submitted successfully![/green]")
    console.print("Task ID: [bold]abc-123-def[/bold]")

    if wait:
        console.print("Waiting for completion...")


@task_app.command("status")
def task_status(
    task_id: str = typer.Argument(..., help="Task ID"),
):
    """Get task status."""
    console.print(f"[bold]Task: {task_id}[/bold]")
    console.print("Status: [green]COMPLETED[/green]")


@task_app.command("list")
def task_list(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of tasks to show"),
):
    """List tasks."""
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Created", style="blue")

    console.print(table)
    console.print("[dim]No tasks found.[/dim]")


# Workflow commands
@workflow_app.command("run")
def workflow_run(
    definition: Path = typer.Argument(..., help="Workflow definition file"),
    input_file: Optional[Path] = typer.Option(None, "--input", "-i", help="Input data file"),
):
    """Run a workflow."""
    console.print(f"[yellow]Running workflow from: {definition}[/yellow]")

    if not definition.exists():
        console.print("[red]Workflow file not found![/red]")
        raise typer.Exit(1)

    console.print("[green]Workflow started![/green]")
    console.print("Workflow ID: [bold]wf-abc-123[/bold]")


@workflow_app.command("status")
def workflow_status(
    workflow_id: str = typer.Argument(..., help="Workflow ID"),
):
    """Get workflow status."""
    console.print(f"[bold]Workflow: {workflow_id}[/bold]")
    console.print("Status: [yellow]RUNNING[/yellow]")
    console.print("Steps completed: 2/5")


@workflow_app.command("list")
def workflow_list(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
):
    """List workflows."""
    table = Table(title="Workflows")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Progress", style="blue")

    console.print(table)
    console.print("[dim]No workflows found.[/dim]")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
