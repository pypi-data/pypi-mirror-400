"""
Command-line interface for OpenFoundry.

Provides commands for:
- Starting the server
- Managing agents
- Executing tasks and workflows
- Configuration management
"""

from openfoundry.cli.main import app

__all__ = ["app"]
