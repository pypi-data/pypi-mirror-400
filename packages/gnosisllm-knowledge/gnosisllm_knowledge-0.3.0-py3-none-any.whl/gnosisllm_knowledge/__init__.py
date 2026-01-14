"""GnosisLLM Knowledge - Enterprise-grade knowledge loading, indexing, and search.

This library provides a comprehensive solution for building knowledge-powered
applications with semantic search capabilities.

Quick Start:
    ```python
    from gnosisllm_knowledge import Knowledge

    # Create instance with OpenSearch backend
    knowledge = Knowledge.from_opensearch(
        host="localhost",
        port=9200,
    )

    # Setup backend (creates indices)
    await knowledge.setup()

    # Load and index a sitemap
    await knowledge.load(
        "https://docs.example.com/sitemap.xml",
        collection_id="docs",
    )

    # Search
    results = await knowledge.search("how to configure")
    for item in results.items:
        print(f"{item.title}: {item.score}")
    ```

Features:
    - Semantic, keyword, and hybrid search
    - Multiple content loaders (website, sitemap, files)
    - Intelligent text chunking
    - OpenSearch backend with k-NN vectors
    - Multi-tenancy support
    - Event-driven architecture
    - SOLID principles throughout
"""

from gnosisllm_knowledge.api import Knowledge, Memory
from gnosisllm_knowledge.backends import (
    AgenticSearchFallback,
    MemoryIndexer,
    MemorySearcher,
    OpenSearchAgenticSearcher,
    OpenSearchConfig,
    OpenSearchIndexer,
    OpenSearchKnowledgeSearcher,
    OpenSearchSetupAdapter,
)
from gnosisllm_knowledge.chunking import FixedSizeChunker, SentenceChunker
from gnosisllm_knowledge.core.domain.document import Document, DocumentStatus, TextChunk
from gnosisllm_knowledge.core.domain.memory import (
    ContainerConfig,
    ContainerInfo,
    HistoryEntry,
    MemoryEntry,
    MemoryStats,
    MemoryStrategy,
    MemoryType,
    Message,
    Namespace,
    RecallResult,
    SessionInfo,
    StrategyConfig,
)
from gnosisllm_knowledge.core.domain.result import (
    BatchResult,
    IndexResult,
    LoadResult,
    ValidationResult,
)
from gnosisllm_knowledge.core.domain.search import (
    AgenticSearchQuery,
    AgenticSearchResult,
    AgentType,
    ReasoningStep,
    SearchMode,
    SearchQuery,
    SearchResult,
    SearchResultItem,
)
from gnosisllm_knowledge.core.events import Event, EventEmitter, EventType
from gnosisllm_knowledge.core.exceptions import (
    AgenticSearchError,
    ConfigurationError,
    ConnectionError,
    ContainerExistsError,
    ContainerNotFoundError,
    IndexError,
    InferenceError,
    InferenceTimeoutError,
    KnowledgeError,
    LoadError,
    MemoryConfigurationError,
    MemoryError,
    SearchError,
    SessionNotFoundError,
)
from gnosisllm_knowledge.core.streaming import (
    BatchCollector,
    BoundedQueue,
    PipelineConfig,
)
from gnosisllm_knowledge.fetchers import (
    HTTPContentFetcher,
    NeoreaderConfig,
    NeoreaderContentFetcher,
)
from gnosisllm_knowledge.loaders import (
    LoaderFactory,
    SitemapLoader,
    WebsiteLoader,
)
from gnosisllm_knowledge.services import (
    KnowledgeIndexingService,
    KnowledgeSearchService,
)

__version__ = "0.2.0"

__all__ = [
    "AgentType",
    "AgenticSearchError",
    "AgenticSearchFallback",
    "AgenticSearchQuery",
    "AgenticSearchResult",
    "BatchCollector",
    "BatchResult",
    "BoundedQueue",
    "ConfigurationError",
    "ConnectionError",
    "ContainerConfig",
    "ContainerExistsError",
    "ContainerInfo",
    "ContainerNotFoundError",
    # Domain Models
    "Document",
    "DocumentStatus",
    # Events
    "Event",
    "EventEmitter",
    "EventType",
    "FixedSizeChunker",
    # Fetchers
    "HTTPContentFetcher",
    "HistoryEntry",
    "IndexError",
    "IndexResult",
    "InferenceError",
    "InferenceTimeoutError",
    # Main API
    "Knowledge",
    # Exceptions
    "KnowledgeError",
    # Services
    "KnowledgeIndexingService",
    "KnowledgeSearchService",
    "LoadError",
    "LoadResult",
    # Loaders
    "LoaderFactory",
    "Memory",
    "MemoryConfigurationError",
    "MemoryEntry",
    # Memory Exceptions
    "MemoryError",
    # Memory Backend (for testing)
    "MemoryIndexer",
    "MemorySearcher",
    "MemoryStats",
    # Memory Domain Models
    "MemoryStrategy",
    "MemoryType",
    "Message",
    "Namespace",
    "NeoreaderConfig",
    "NeoreaderContentFetcher",
    "OpenSearchAgenticSearcher",
    # OpenSearch Backend
    "OpenSearchConfig",
    "OpenSearchIndexer",
    "OpenSearchKnowledgeSearcher",
    "OpenSearchSetupAdapter",
    # Streaming Pipeline
    "PipelineConfig",
    "ReasoningStep",
    "RecallResult",
    "SearchError",
    "SearchMode",
    "SearchQuery",
    "SearchResult",
    "SearchResultItem",
    # Chunkers
    "SentenceChunker",
    "SessionInfo",
    "SessionNotFoundError",
    "SitemapLoader",
    "StrategyConfig",
    "TextChunk",
    "ValidationResult",
    "WebsiteLoader",
]
