"""OpenSearch backend configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class OpenSearchConfig:
    """OpenSearch backend configuration.

    Example:
        ```python
        # From environment variables
        config = OpenSearchConfig.from_env()

        # Explicit configuration
        config = OpenSearchConfig(
            host="localhost",
            port=9200,
            embedding_model="text-embedding-3-small",
        )

        # AWS OpenSearch Service
        config = OpenSearchConfig(
            host="search-domain.us-east-1.es.amazonaws.com",
            port=443,
            use_ssl=True,
            use_aws_sigv4=True,
            aws_region="us-east-1",
        )
        ```
    """

    # === Connection ===
    host: str = "localhost"
    port: int = 9200
    use_ssl: bool = False
    verify_certs: bool = True
    ca_certs: str | None = None

    # Authentication
    username: str | None = None
    password: str | None = None

    # AWS OpenSearch Service
    use_aws_sigv4: bool = False
    aws_region: str | None = None
    aws_service: str = "es"  # "es" for OpenSearch, "aoss" for Serverless

    # === Cluster (High Availability) ===
    nodes: tuple[str, ...] | None = None  # Multiple nodes for HA
    sniff_on_start: bool = False
    sniff_on_node_failure: bool = True
    sniff_timeout: float = 10.0
    sniffer_timeout: float = 60.0

    # === Embedding ===
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    openai_api_key: str | None = None
    embedding_batch_size: int = 100

    # === Index Settings ===
    index_prefix: str = "gnosisllm"
    number_of_shards: int = 5
    number_of_replicas: int = 1
    refresh_interval: str = "1s"

    # Pipeline names (auto-generated if not set)
    ingest_pipeline_name: str | None = None
    search_pipeline_name: str | None = None

    # === k-NN Settings ===
    knn_engine: str = "lucene"  # lucene (recommended for OpenSearch 2.9+), faiss
    knn_space_type: str = "cosinesimil"  # cosinesimil (recommended), l2, innerproduct
    knn_algo_param_ef_search: int = 512
    knn_algo_param_ef_construction: int = 512
    knn_algo_param_m: int = 16

    # === Neural Search (OpenSearch 2.9+) ===
    # model_id is the deployed ML model in OpenSearch for embeddings
    model_id: str | None = None
    model_group_id: str | None = None
    embedding_field: str = "content_embedding"  # Field name for embeddings

    # === Agentic Search (OpenSearch 3.2+) ===
    # Uses QueryPlanningTool for LLM-generated DSL queries
    # Agent IDs from 'gnosisllm-knowledge agentic setup'
    flow_agent_id: str | None = None
    conversational_agent_id: str | None = None
    # Agentic search pipeline (created during agentic setup)
    agentic_pipeline_name: str | None = None
    # LLM for agent reasoning (OpenAI model ID)
    agentic_llm_model: str = "gpt-4o"
    # Agent execution limits
    agentic_max_iterations: int = 5
    agentic_timeout_seconds: int = 60
    # Conversation memory settings
    memory_window_size: int = 10  # Messages to keep in context

    # === Timeouts ===
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    bulk_timeout: float = 120.0

    # === Bulk Indexing ===
    bulk_batch_size: int = 500
    bulk_max_concurrent: int = 3

    @property
    def url(self) -> str:
        """Get the full OpenSearch URL."""
        scheme = "https" if self.use_ssl else "http"
        return f"{scheme}://{self.host}:{self.port}"

    @property
    def knowledge_index_name(self) -> str:
        """Get the default knowledge index name."""
        return f"{self.index_prefix}-knowledge"

    @property
    def agentic_memory_index_name(self) -> str:
        """Get the agentic memory index name."""
        return f"{self.index_prefix}-memory"

    def get_index_name(self, collection_id: str | None = None) -> str:
        """Get index name for a collection.

        Args:
            collection_id: Optional collection ID for multi-tenant indexing.

        Returns:
            Index name pattern.
        """
        if collection_id:
            return f"{self.index_prefix}-{collection_id}"
        return self.knowledge_index_name

    @classmethod
    def from_env(cls) -> OpenSearchConfig:
        """Create config from environment variables.

        All configuration options can be set via environment variables.
        See .env.example for a complete list with descriptions.

        Returns:
            Configuration from environment.
        """
        # Parse nodes list
        nodes_str = os.getenv("OPENSEARCH_NODES", "")
        nodes = tuple(n.strip() for n in nodes_str.split(",") if n.strip()) or None

        return cls(
            # === Connection ===
            host=os.getenv("OPENSEARCH_HOST", "localhost"),
            port=int(os.getenv("OPENSEARCH_PORT", "9200")),
            use_ssl=os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true",
            verify_certs=os.getenv("OPENSEARCH_VERIFY_CERTS", "true").lower() == "true",
            ca_certs=os.getenv("OPENSEARCH_CA_CERTS"),
            # Authentication
            username=os.getenv("OPENSEARCH_USERNAME"),
            password=os.getenv("OPENSEARCH_PASSWORD"),
            # AWS OpenSearch Service
            use_aws_sigv4=os.getenv("OPENSEARCH_USE_AWS_SIGV4", "false").lower() == "true",
            aws_region=os.getenv("AWS_REGION"),
            aws_service=os.getenv("OPENSEARCH_AWS_SERVICE", "es"),
            # === Cluster (High Availability) ===
            nodes=nodes,
            sniff_on_start=os.getenv("OPENSEARCH_SNIFF_ON_START", "false").lower() == "true",
            sniff_on_node_failure=os.getenv("OPENSEARCH_SNIFF_ON_NODE_FAILURE", "true").lower()
            == "true",
            sniff_timeout=float(os.getenv("OPENSEARCH_SNIFF_TIMEOUT", "10.0")),
            sniffer_timeout=float(os.getenv("OPENSEARCH_SNIFFER_TIMEOUT", "60.0")),
            # === Embedding ===
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "1536")),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "100")),
            # === Index Settings ===
            index_prefix=os.getenv("OPENSEARCH_INDEX_PREFIX", "gnosisllm"),
            number_of_shards=int(os.getenv("OPENSEARCH_SHARDS", "5")),
            number_of_replicas=int(os.getenv("OPENSEARCH_REPLICAS", "1")),
            refresh_interval=os.getenv("OPENSEARCH_REFRESH_INTERVAL", "1s"),
            # Pipeline names
            ingest_pipeline_name=os.getenv("OPENSEARCH_INGEST_PIPELINE"),
            search_pipeline_name=os.getenv("OPENSEARCH_SEARCH_PIPELINE"),
            # === k-NN Settings ===
            knn_engine=os.getenv("OPENSEARCH_KNN_ENGINE", "lucene"),
            knn_space_type=os.getenv("OPENSEARCH_KNN_SPACE_TYPE", "cosinesimil"),
            knn_algo_param_ef_search=int(os.getenv("OPENSEARCH_KNN_EF_SEARCH", "512")),
            knn_algo_param_ef_construction=int(
                os.getenv("OPENSEARCH_KNN_EF_CONSTRUCTION", "512")
            ),
            knn_algo_param_m=int(os.getenv("OPENSEARCH_KNN_M", "16")),
            # === Neural Search ===
            model_id=os.getenv("OPENSEARCH_MODEL_ID"),
            model_group_id=os.getenv("OPENSEARCH_MODEL_GROUP_ID"),
            embedding_field=os.getenv("OPENSEARCH_EMBEDDING_FIELD", "content_embedding"),
            # === Agentic Search ===
            flow_agent_id=os.getenv("OPENSEARCH_FLOW_AGENT_ID"),
            conversational_agent_id=os.getenv("OPENSEARCH_CONVERSATIONAL_AGENT_ID"),
            agentic_pipeline_name=os.getenv("OPENSEARCH_AGENTIC_PIPELINE"),
            agentic_llm_model=os.getenv("AGENTIC_LLM_MODEL", "gpt-4o"),
            agentic_max_iterations=int(os.getenv("AGENTIC_MAX_ITERATIONS", "5")),
            agentic_timeout_seconds=int(os.getenv("AGENTIC_TIMEOUT_SECONDS", "60")),
            memory_window_size=int(os.getenv("AGENTIC_MEMORY_WINDOW_SIZE", "10")),
            # === Timeouts ===
            connect_timeout=float(os.getenv("OPENSEARCH_CONNECT_TIMEOUT", "5.0")),
            read_timeout=float(os.getenv("OPENSEARCH_READ_TIMEOUT", "30.0")),
            bulk_timeout=float(os.getenv("OPENSEARCH_BULK_TIMEOUT", "120.0")),
            # === Bulk Indexing ===
            bulk_batch_size=int(os.getenv("OPENSEARCH_BULK_BATCH_SIZE", "500")),
            bulk_max_concurrent=int(os.getenv("OPENSEARCH_BULK_MAX_CONCURRENT", "3")),
        )
