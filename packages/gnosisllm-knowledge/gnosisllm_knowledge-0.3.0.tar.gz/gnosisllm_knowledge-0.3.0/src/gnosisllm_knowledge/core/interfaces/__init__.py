"""Interface definitions (protocols) for dependency injection."""

from gnosisllm_knowledge.core.interfaces.agentic import IAgenticSearcher
from gnosisllm_knowledge.core.interfaces.chunker import ITextChunker
from gnosisllm_knowledge.core.interfaces.fetcher import FetchResult, IContentFetcher
from gnosisllm_knowledge.core.interfaces.indexer import IDocumentIndexer
from gnosisllm_knowledge.core.interfaces.loader import IContentLoader
from gnosisllm_knowledge.core.interfaces.memory import (
    IHistoryRetriever,
    IMemoryContainerManager,
    IMemoryRetriever,
    IMemoryStats,
    IMemoryStore,
    ISessionManager,
)
from gnosisllm_knowledge.core.interfaces.searcher import IKnowledgeSearcher
from gnosisllm_knowledge.core.interfaces.setup import ISetupAdapter

__all__ = [
    # Content loading
    "IContentLoader",
    "IContentFetcher",
    "FetchResult",
    "ITextChunker",
    # Indexing and search
    "IDocumentIndexer",
    "IKnowledgeSearcher",
    "IAgenticSearcher",
    "ISetupAdapter",
    # Memory
    "IMemoryContainerManager",
    "IMemoryStore",
    "IMemoryRetriever",
    "IHistoryRetriever",
    "ISessionManager",
    "IMemoryStats",
]
