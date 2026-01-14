"""CLI configuration provider."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


@dataclass
class CliConfig:
    """CLI configuration loaded from environment.

    Provides a unified interface for accessing configuration
    with sensible defaults for CLI operations.
    """

    # OpenSearch
    opensearch_host: str = "localhost"
    opensearch_port: int = 9200
    opensearch_username: str | None = None
    opensearch_password: str | None = None
    opensearch_use_ssl: bool = False
    opensearch_verify_certs: bool = False
    opensearch_model_id: str | None = None
    opensearch_index_name: str = "knowledge"
    opensearch_pipeline_name: str = "gnosisllm-ingest-pipeline"
    opensearch_search_pipeline_name: str = "gnosisllm-search-pipeline"

    # OpenAI
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_embedding_dimension: int = 1536

    # Agentic Search
    opensearch_flow_agent_id: str | None = None
    opensearch_conversational_agent_id: str | None = None
    agentic_llm_model: str = "gpt-4o"
    agentic_max_iterations: int = 5
    agentic_timeout_seconds: int = 60

    # Agentic Memory
    memory_llm_model_id: str | None = None
    memory_embedding_model_id: str | None = None
    memory_llm_model: str = "gpt-4o"
    memory_embedding_model: str = "text-embedding-3-small"
    memory_embedding_dimension: int = 1536

    # Neoreader
    neoreader_host: str = "https://api.neoreader.dev"

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> CliConfig:
        """Load configuration from environment.

        Args:
            env_file: Optional path to .env file.

        Returns:
            Configured CliConfig instance.
        """
        # Load .env file if exists
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls(
            opensearch_host=os.getenv("OPENSEARCH_HOST", "localhost"),
            opensearch_port=int(os.getenv("OPENSEARCH_PORT", "9200")),
            opensearch_username=os.getenv("OPENSEARCH_USERNAME"),
            opensearch_password=os.getenv("OPENSEARCH_PASSWORD"),
            opensearch_use_ssl=os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true",
            opensearch_verify_certs=os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower()
            == "true",
            opensearch_model_id=os.getenv("OPENSEARCH_MODEL_ID"),
            opensearch_index_name=os.getenv("OPENSEARCH_INDEX_NAME", "knowledge"),
            opensearch_pipeline_name=os.getenv(
                "OPENSEARCH_PIPELINE_NAME", "gnosisllm-ingest-pipeline"
            ),
            opensearch_search_pipeline_name=os.getenv(
                "OPENSEARCH_SEARCH_PIPELINE_NAME", "gnosisllm-search-pipeline"
            ),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
            openai_embedding_dimension=int(os.getenv("OPENAI_EMBEDDING_DIMENSION", "1536")),
            # Agentic search configuration
            opensearch_flow_agent_id=os.getenv("OPENSEARCH_FLOW_AGENT_ID"),
            opensearch_conversational_agent_id=os.getenv("OPENSEARCH_CONVERSATIONAL_AGENT_ID"),
            agentic_llm_model=os.getenv("AGENTIC_LLM_MODEL", "gpt-4o"),
            agentic_max_iterations=int(os.getenv("AGENTIC_MAX_ITERATIONS", "5")),
            agentic_timeout_seconds=int(os.getenv("AGENTIC_TIMEOUT_SECONDS", "60")),
            # Agentic Memory configuration
            memory_llm_model_id=os.getenv("OPENSEARCH_MEMORY_LLM_MODEL_ID"),
            memory_embedding_model_id=os.getenv("OPENSEARCH_MEMORY_EMBEDDING_MODEL_ID"),
            memory_llm_model=os.getenv("MEMORY_LLM_MODEL", "gpt-4o"),
            memory_embedding_model=os.getenv("MEMORY_EMBEDDING_MODEL", "text-embedding-3-small"),
            memory_embedding_dimension=int(os.getenv("MEMORY_EMBEDDING_DIMENSION", "1536")),
            neoreader_host=os.getenv("NEOREADER_HOST", "https://api.neoreader.dev"),
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key (e.g., "OPENSEARCH_HOST").
            default: Default value if not found.

        Returns:
            Configuration value or default.
        """
        # Convert env-style key to attribute name
        attr_name = key.lower()
        return getattr(self, attr_name, default)

    def require(self, key: str) -> str:
        """Get required configuration value.

        Args:
            key: Configuration key.

        Returns:
            Configuration value.

        Raises:
            ValueError: If value is not set.
        """
        value = self.get(key)
        if not value:
            raise ValueError(f"{key} is required but not set")
        return str(value)

    @property
    def opensearch_url(self) -> str:
        """Get OpenSearch URL."""
        protocol = "https" if self.opensearch_use_ssl else "http"
        return f"{protocol}://{self.opensearch_host}:{self.opensearch_port}"

    def validate_for_setup(self) -> list[str]:
        """Validate configuration for setup command.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required for setup")
        return errors

    def validate_for_search(self) -> list[str]:
        """Validate configuration for search command.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        if not self.opensearch_model_id:
            errors.append(
                "OPENSEARCH_MODEL_ID is required for semantic/hybrid search. "
                "Run 'gnosisllm-knowledge setup' first."
            )
        return errors

    def validate_for_agentic_search(self, agent_type: str = "flow") -> list[str]:
        """Validate configuration for agentic search.

        Args:
            agent_type: Type of agent ('flow' or 'conversational').

        Returns:
            List of validation errors (empty if valid).
        """
        errors = self.validate_for_search()

        if agent_type == "flow" and not self.opensearch_flow_agent_id:
            errors.append(
                "OPENSEARCH_FLOW_AGENT_ID is required for flow agent search. "
                "Run 'gnosisllm-knowledge agentic setup' first."
            )
        elif agent_type == "conversational" and not self.opensearch_conversational_agent_id:
            errors.append(
                "OPENSEARCH_CONVERSATIONAL_AGENT_ID is required for conversational agent search. "
                "Run 'gnosisllm-knowledge agentic setup' first."
            )

        return errors

    def validate_for_agentic_setup(self) -> list[str]:
        """Validate configuration for agentic setup command.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = self.validate_for_setup()

        if not self.opensearch_model_id:
            errors.append(
                "OPENSEARCH_MODEL_ID is required for agentic setup. "
                "Run 'gnosisllm-knowledge setup' first to deploy the embedding model."
            )

        return errors

    @property
    def has_agentic_agents(self) -> bool:
        """Check if any agentic agent is configured."""
        return bool(self.opensearch_flow_agent_id or self.opensearch_conversational_agent_id)

    @property
    def has_flow_agent(self) -> bool:
        """Check if flow agent is configured."""
        return bool(self.opensearch_flow_agent_id)

    @property
    def has_conversational_agent(self) -> bool:
        """Check if conversational agent is configured."""
        return bool(self.opensearch_conversational_agent_id)

    # === Memory Configuration ===

    def validate_for_memory(self) -> list[str]:
        """Validate configuration for memory commands.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        if not self.memory_llm_model_id:
            errors.append(
                "OPENSEARCH_MEMORY_LLM_MODEL_ID is required for memory operations. "
                "Run 'gnosisllm-knowledge memory setup' first."
            )
        if not self.memory_embedding_model_id:
            errors.append(
                "OPENSEARCH_MEMORY_EMBEDDING_MODEL_ID is required for memory operations. "
                "Run 'gnosisllm-knowledge memory setup' first."
            )
        return errors

    def validate_for_memory_setup(self) -> list[str]:
        """Validate configuration for memory setup command.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        if not self.openai_api_key:
            errors.append(
                "OPENAI_API_KEY is required for memory setup. "
                "Use --openai-key or set the environment variable."
            )
        return errors

    @property
    def has_memory_models(self) -> bool:
        """Check if memory models are configured."""
        return bool(self.memory_llm_model_id and self.memory_embedding_model_id)

    @property
    def memory_is_configured(self) -> bool:
        """Check if memory is fully configured for operations."""
        return self.has_memory_models
