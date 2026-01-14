"""
Configuration management using Pydantic Settings.

Supports YAML files, environment variables, and .env files.
Priority: env vars > .env > yaml > defaults
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENFOUNDRY__LLM__", extra="ignore")

    default_model: str = "gpt-4o"
    fallback_models: list[str] = Field(default_factory=lambda: ["claude-3-5-sonnet"])
    max_retries: int = 3
    timeout_seconds: int = 120
    max_tokens: int = 4096
    temperature: float = 0.7

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    google_api_key: SecretStr | None = None


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENFOUNDRY__API__", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    enable_docs: bool = True
    api_prefix: str = "/api/v1"


class TelemetrySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENFOUNDRY__TELEMETRY__", extra="ignore")

    enabled: bool = True
    service_name: str = "openfoundry"
    otlp_endpoint: str = "http://localhost:4317"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


class ShieldSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENFOUNDRY__SHIELD__", extra="ignore")

    enabled: bool = True
    prompt_injection_detection: bool = True
    pii_detection: bool = True


class StateSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENFOUNDRY__STATE__", extra="ignore")

    backend: Literal["memory", "redis"] = "memory"
    redis_url: str = "redis://localhost:6379/0"
    ttl_seconds: int = 3600


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="OPENFOUNDRY__",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    project_name: str = "openfoundry"

    llm: LLMSettings = Field(default_factory=LLMSettings)
    api: APISettings = Field(default_factory=APISettings)
    telemetry: TelemetrySettings = Field(default_factory=TelemetrySettings)
    shield: ShieldSettings = Field(default_factory=ShieldSettings)
    state: StateSettings = Field(default_factory=StateSettings)

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        valid = {"development", "staging", "production"}
        if v.lower() not in valid:
            raise ValueError(f"environment must be one of {valid}")
        return v.lower()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def load_settings(config_path: Path | str | None = None) -> Settings:
    """Load settings from optional YAML file plus environment."""
    import yaml

    base_settings: dict = {}

    if config_path:
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                base_settings = yaml.safe_load(f) or {}

    return Settings(**base_settings)


def clear_settings_cache() -> None:
    """Clear the cached settings."""
    get_settings.cache_clear()
