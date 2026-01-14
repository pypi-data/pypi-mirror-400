# OpenFoundry

Multi-agent orchestration framework for AI applications.

## Overview

OpenFoundry is a framework for building and orchestrating AI agents across the full AI lifecycle:

- **The Forge** - Development & SDLC agents (Architect, Engineer, Quality)
- **The Conveyor** - CI/CD & deployment agents (DevOps, Release)
- **The Shield** - Responsible AI & safety (Guardrails, PII detection)
- **The Watchtower** - Monitoring & observability (OpenTelemetry, Prometheus)

## Features

- Protocol-based agent interfaces (PEP 544)
- Multi-provider LLM support via LiteLLM (OpenAI, Anthropic, Google, Mistral, etc.)
- Async-first architecture for high concurrency
- Structured outputs with Pydantic validation
- DAG-based workflow engine
- Comprehensive guardrails for safe AI usage
- Full observability with OpenTelemetry and Prometheus

## Quick Start

```bash
# Install
pip install openfoundry

# Initialize a new project
openfoundry init

# Start the server
openfoundry serve

# List available agents
openfoundry agent list
```

## Requirements

- Python 3.12+
- API keys for LLM providers (OpenAI, Anthropic, etc.)

## Documentation

See the [docs](./docs) directory for detailed documentation.

## License

MIT
