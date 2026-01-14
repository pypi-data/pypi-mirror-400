"""OpenSearch backend implementation."""

from gnosisllm_knowledge.backends.opensearch.agentic import (
    AgenticSearchFallback,
    OpenSearchAgenticSearcher,
)
from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.backends.opensearch.indexer import OpenSearchIndexer
from gnosisllm_knowledge.backends.opensearch.searcher import OpenSearchKnowledgeSearcher
from gnosisllm_knowledge.backends.opensearch.setup import OpenSearchSetupAdapter

__all__ = [
    "OpenSearchConfig",
    "OpenSearchIndexer",
    "OpenSearchKnowledgeSearcher",
    "OpenSearchSetupAdapter",
    "OpenSearchAgenticSearcher",
    "AgenticSearchFallback",
]
