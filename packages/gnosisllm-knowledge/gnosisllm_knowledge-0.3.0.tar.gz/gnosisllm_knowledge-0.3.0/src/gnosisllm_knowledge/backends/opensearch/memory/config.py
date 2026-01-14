"""Memory-specific configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from gnosisllm_knowledge.core.domain.memory import MemoryStrategy


@dataclass(frozen=True)
class MemoryConfig:
    """Configuration for Agentic Memory.

    Example:
        ```python
        # From environment
        config = MemoryConfig.from_env()

        # Explicit configuration
        config = MemoryConfig(
            host="localhost",
            port=9200,
            llm_model_id="model-123",
            embedding_model_id="model-456",
        )
        ```
    """

    # === OpenSearch Connection ===
    host: str = "localhost"
    port: int = 9200
    username: str | None = None
    password: str | None = None
    use_ssl: bool = False
    verify_certs: bool = True

    # === Model IDs (Required for inference) ===
    llm_model_id: str | None = None
    embedding_model_id: str | None = None

    # === LLM Response Parsing ===
    # OpenAI: $.choices[0].message.content
    # Bedrock Claude: $.output.message.content[0].text
    llm_result_path: str = "$.choices[0].message.content"

    # === Connector Configuration ===
    # For setup: OpenAI API key
    openai_api_key: str | None = None
    llm_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # === Timeouts ===
    connect_timeout: float = 5.0
    inference_timeout: float = 60.0

    # === Default Strategies ===
    default_strategies: tuple[MemoryStrategy, ...] = (
        MemoryStrategy.SEMANTIC,
        MemoryStrategy.USER_PREFERENCE,
    )

    @property
    def url(self) -> str:
        """Get the full OpenSearch URL."""
        scheme = "https" if self.use_ssl else "http"
        return f"{scheme}://{self.host}:{self.port}"

    @property
    def auth(self) -> tuple[str, str] | None:
        """Get auth tuple if credentials are configured."""
        if self.username and self.password:
            return (self.username, self.password)
        return None

    @property
    def is_configured(self) -> bool:
        """Check if memory is properly configured for inference."""
        return bool(self.llm_model_id and self.embedding_model_id)

    @classmethod
    def from_env(cls) -> MemoryConfig:
        """Create config from environment variables.

        Environment Variables:
            OPENSEARCH_HOST: OpenSearch host (default: localhost)
            OPENSEARCH_PORT: OpenSearch port (default: 9200)
            OPENSEARCH_USERNAME: Username
            OPENSEARCH_PASSWORD: Password
            OPENSEARCH_USE_SSL: Use SSL (default: false)
            OPENSEARCH_VERIFY_CERTS: Verify certs (default: true)
            OPENSEARCH_LLM_MODEL_ID: LLM model ID for inference
            OPENSEARCH_EMBEDDING_MODEL_ID: Embedding model ID
            OPENSEARCH_LLM_RESULT_PATH: JSONPath for LLM response
            OPENAI_API_KEY: OpenAI API key (for setup)
            MEMORY_LLM_MODEL: LLM model name (default: gpt-4o)
            MEMORY_EMBEDDING_MODEL: Embedding model (default: text-embedding-3-small)
            MEMORY_EMBEDDING_DIMENSION: Embedding dimension (default: 1536)
            MEMORY_INFERENCE_TIMEOUT: Inference timeout (default: 60)
            OPENSEARCH_CONNECT_TIMEOUT: Connect timeout (default: 5)
        """
        return cls(
            # Connection
            host=os.getenv("OPENSEARCH_HOST", "localhost"),
            port=int(os.getenv("OPENSEARCH_PORT", "9200")),
            username=os.getenv("OPENSEARCH_USERNAME"),
            password=os.getenv("OPENSEARCH_PASSWORD"),
            use_ssl=os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true",
            verify_certs=os.getenv("OPENSEARCH_VERIFY_CERTS", "true").lower() == "true",
            # Model IDs
            llm_model_id=os.getenv("OPENSEARCH_LLM_MODEL_ID"),
            embedding_model_id=os.getenv("OPENSEARCH_EMBEDDING_MODEL_ID"),
            # LLM parsing
            llm_result_path=os.getenv(
                "OPENSEARCH_LLM_RESULT_PATH",
                "$.choices[0].message.content",
            ),
            # Connector setup
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            llm_model=os.getenv("MEMORY_LLM_MODEL", "gpt-4o"),
            embedding_model=os.getenv("MEMORY_EMBEDDING_MODEL", "text-embedding-3-small"),
            embedding_dimension=int(os.getenv("MEMORY_EMBEDDING_DIMENSION", "1536")),
            # Timeouts
            connect_timeout=float(os.getenv("OPENSEARCH_CONNECT_TIMEOUT", "5.0")),
            inference_timeout=float(os.getenv("MEMORY_INFERENCE_TIMEOUT", "60.0")),
        )
