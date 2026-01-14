"""Search backend implementations."""

from gnosisllm_knowledge.backends.memory import MemoryIndexer, MemorySearcher
from gnosisllm_knowledge.backends.opensearch import (
    AgenticSearchFallback,
    OpenSearchAgenticSearcher,
    OpenSearchConfig,
    OpenSearchIndexer,
    OpenSearchKnowledgeSearcher,
    OpenSearchSetupAdapter,
)
from gnosisllm_knowledge.backends.opensearch.memory import (
    MemoryConfig,
    MemorySetup,
    OpenSearchMemoryClient,
)
from gnosisllm_knowledge.backends.opensearch.queries import QueryBuilder

__all__ = [
    "AgenticSearchFallback",
    # OpenSearch Memory
    "MemoryConfig",
    # Memory (for testing)
    "MemoryIndexer",
    "MemorySearcher",
    "MemorySetup",
    "OpenSearchAgenticSearcher",
    # OpenSearch
    "OpenSearchConfig",
    "OpenSearchIndexer",
    "OpenSearchKnowledgeSearcher",
    "OpenSearchMemoryClient",
    "OpenSearchSetupAdapter",
    "QueryBuilder",
]
