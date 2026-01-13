"""
IQToolkit configuration management for multi-database support.
"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml


class DatabaseConfig:
    """Database connection configuration."""

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.type = config.get("type")  # postgresql, mongodb
        self.host = config.get("host")
        self.port = config.get("port")
        self.database = config.get("database")
        self.username = config.get("username")
        self.password = config.get("password")

    def get_connection_string(self) -> str:
        """Generate connection string for the database."""
        if self.type == "postgresql" or self.type == "postgres":
            return (
                f"postgresql://{self.username}:{self.password}@"
                f"{self.host}:{self.port}/{self.database}"
            )
        elif self.type == "mongodb" or self.type == "mongo":
            return (
                f"mongodb://{self.username}:{self.password}@"
                f"{self.host}:{self.port}/{self.database}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.type}")


class LLMProviderConfig:
    """LLM provider configuration."""

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.api_key = config.get("api_key", "").replace(
            "${OPENAI_API_KEY}", os.getenv("OPENAI_API_KEY", "")
        )
        self.model = config.get("model")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)


class IQToolkitConfig:
    """Main configuration manager for IQToolkit."""

    def __init__(self, config_data: dict[str, Any]):
        self.default_provider = config_data.get("default_provider", "openai")

        # Load providers
        self.providers: dict[str, LLMProviderConfig] = {}
        providers_config = config_data.get("providers", {})
        for provider_name, provider_config in providers_config.items():
            self.providers[provider_name] = LLMProviderConfig(
                provider_name, provider_config
            )

        # Load databases
        self.databases: dict[str, DatabaseConfig] = {}
        databases_config = config_data.get("databases", {})
        for db_name, db_config in databases_config.items():
            self.databases[db_name] = DatabaseConfig(db_name, db_config)

        # Load simple config options (backward compatibility)
        self.openai_api_key = config_data.get(
            "openai_api_key", os.getenv("OPENAI_API_KEY", "")
        )
        self.llm_provider = config_data.get("llm_provider", "openai")
        self.openai_model = config_data.get("openai_model", "gpt-4o")
        self.ollama_model = config_data.get("ollama_model", "mistral")
        self.ollama_host = config_data.get("ollama_host", "http://localhost:11434")
        self.log_format = config_data.get("log_format", "plain")
        self.top_n = int(config_data.get("top_n", 5))
        self.output = config_data.get("output", "")

    @staticmethod
    def load(config_path: str = ".iqtoolkit-analyzer.yml") -> "IQToolkitConfig":
        """Load configuration from YAML file."""
        path = Path(config_path).expanduser()
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}

        return IQToolkitConfig(config_data)

    def get_database(self, name: str) -> Optional[DatabaseConfig]:
        """Get database configuration by name."""
        return self.databases.get(name)

    def get_provider(self, name: str) -> Optional[LLMProviderConfig]:
        """Get LLM provider configuration by name."""
        return self.providers.get(name)

    def list_databases(self) -> list[str]:
        """List all configured database names."""
        return list(self.databases.keys())

    def list_providers(self) -> list[str]:
        """List all configured providers."""
        return list(self.providers.keys())
