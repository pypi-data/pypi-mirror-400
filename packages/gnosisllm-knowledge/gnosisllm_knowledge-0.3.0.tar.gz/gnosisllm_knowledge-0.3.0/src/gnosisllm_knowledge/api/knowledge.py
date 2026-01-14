"""High-level Knowledge API facade."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from gnosisllm_knowledge.backends.opensearch import (
    OpenSearchConfig,
    OpenSearchIndexer,
    OpenSearchKnowledgeSearcher,
    OpenSearchSetupAdapter,
)
from gnosisllm_knowledge.backends.opensearch.agentic import OpenSearchAgenticSearcher
from gnosisllm_knowledge.chunking import SentenceChunker
from gnosisllm_knowledge.core.domain.result import IndexResult
from gnosisllm_knowledge.core.domain.search import (
    AgentType,
    AgenticSearchQuery,
    AgenticSearchResult,
    SearchMode,
    SearchResult,
)
from gnosisllm_knowledge.core.events.emitter import EventEmitter
from gnosisllm_knowledge.core.interfaces.setup import DiagnosticReport, HealthReport
from gnosisllm_knowledge.core.streaming.pipeline import PipelineConfig
from gnosisllm_knowledge.fetchers import NeoreaderContentFetcher
from gnosisllm_knowledge.fetchers.config import NeoreaderConfig
from gnosisllm_knowledge.loaders import LoaderFactory
from gnosisllm_knowledge.services import KnowledgeIndexingService, KnowledgeSearchService
from gnosisllm_knowledge.services.streaming_pipeline import StreamingIndexingPipeline

if TYPE_CHECKING:
    from opensearchpy import AsyncOpenSearch

    from gnosisllm_knowledge.core.interfaces.chunker import ITextChunker
    from gnosisllm_knowledge.core.interfaces.fetcher import IContentFetcher
    from gnosisllm_knowledge.core.interfaces.indexer import IDocumentIndexer
    from gnosisllm_knowledge.core.interfaces.searcher import IKnowledgeSearcher
    from gnosisllm_knowledge.core.interfaces.setup import ISetupAdapter

logger = logging.getLogger(__name__)


class Knowledge:
    """High-level facade for knowledge operations.

    Provides a simple, unified interface for loading, indexing, and
    searching knowledge documents.

    Example:
        ```python
        # Quick start with OpenSearch
        knowledge = Knowledge.from_opensearch(
            host="localhost",
            port=9200,
        )

        # Setup the backend
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
    """

    def __init__(
        self,
        *,
        indexer: IDocumentIndexer,
        searcher: IKnowledgeSearcher,
        setup: ISetupAdapter | None = None,
        fetcher: IContentFetcher | None = None,
        chunker: ITextChunker | None = None,
        loader_factory: LoaderFactory | None = None,
        default_index: str | None = None,
        events: EventEmitter | None = None,
    ) -> None:
        """Initialize Knowledge with components.

        Args:
            indexer: Document indexer.
            searcher: Knowledge searcher.
            setup: Optional setup adapter.
            fetcher: Optional content fetcher.
            chunker: Optional text chunker.
            loader_factory: Optional loader factory.
            default_index: Default index name.
            events: Optional event emitter.

        Note:
            Embeddings are generated automatically by OpenSearch ingest pipeline.
            No Python-side embedding function is needed.
        """
        self._indexer = indexer
        self._searcher = searcher
        self._setup = setup
        self._fetcher = fetcher
        self._chunker = chunker or SentenceChunker()
        self._loader_factory = loader_factory
        self._default_index = default_index
        self._events = events or EventEmitter()

        # Initialize services lazily
        self._indexing_service: KnowledgeIndexingService | None = None
        self._search_service: KnowledgeSearchService | None = None

    @classmethod
    def from_opensearch(
        cls,
        host: str = "localhost",
        port: int = 9200,
        *,
        username: str | None = None,
        password: str | None = None,
        use_ssl: bool = False,
        verify_certs: bool = True,
        neoreader_url: str | None = None,
        config: OpenSearchConfig | None = None,
        **kwargs: Any,
    ) -> Knowledge:
        """Create Knowledge instance with OpenSearch backend.

        Args:
            host: OpenSearch host.
            port: OpenSearch port.
            username: Optional username.
            password: Optional password.
            use_ssl: Use SSL connection.
            verify_certs: Verify SSL certificates.
            neoreader_url: Optional Neoreader URL for content fetching.
            config: Optional OpenSearchConfig (overrides other params).
            **kwargs: Additional config options.

        Returns:
            Configured Knowledge instance.

        Note:
            Embeddings are generated automatically by OpenSearch ingest pipeline.
            Run 'gnosisllm-knowledge setup' to configure the ML model.
        """
        # Import OpenSearch client
        try:
            from opensearchpy import AsyncOpenSearch
        except ImportError as e:
            raise ImportError(
                "opensearch-py is required for OpenSearch backend. "
                "Install with: pip install gnosisllm-knowledge[opensearch]"
            ) from e

        # Build config
        if config is None:
            config = OpenSearchConfig(
                host=host,
                port=port,
                username=username,
                password=password,
                use_ssl=use_ssl,
                verify_certs=verify_certs,
                **kwargs,
            )

        # Create client with proper timeout settings
        client_kwargs: dict[str, Any] = {
            "hosts": [{"host": config.host, "port": config.port}],
            "use_ssl": config.use_ssl,
            "verify_certs": config.verify_certs,
            "timeout": max(config.read_timeout, config.agentic_timeout_seconds),
        }

        if config.username and config.password:
            client_kwargs["http_auth"] = (config.username, config.password)

        client = AsyncOpenSearch(**client_kwargs)

        # Create components
        # Embeddings are generated automatically by OpenSearch ingest pipeline.
        # No Python-side embedding function needed.
        indexer = OpenSearchIndexer(client, config)
        searcher = OpenSearchKnowledgeSearcher(client, config)
        setup = OpenSearchSetupAdapter(client, config)

        # Create fetcher
        fetcher = None
        if neoreader_url:
            neoreader_config = NeoreaderConfig(host=neoreader_url)
            fetcher = NeoreaderContentFetcher(neoreader_config)

        # Create chunker
        chunker = SentenceChunker()

        # Create loader factory (fetcher is optional, defaults will be used if None)
        loader_factory = None
        if fetcher:
            loader_factory = LoaderFactory(fetcher=fetcher, chunker=chunker)

        return cls(
            indexer=indexer,
            searcher=searcher,
            setup=setup,
            fetcher=fetcher,
            loader_factory=loader_factory,
            default_index=config.knowledge_index_name,
        )

    @classmethod
    def from_env(cls) -> Knowledge:
        """Create Knowledge instance from environment variables.

        Returns:
            Configured Knowledge instance.
        """
        config = OpenSearchConfig.from_env()
        neoreader_config = NeoreaderConfig.from_env()

        return cls.from_opensearch(
            config=config,
            neoreader_url=neoreader_config.base_url if neoreader_config.base_url else None,
        )

    @property
    def events(self) -> EventEmitter:
        """Get the event emitter."""
        return self._events

    @property
    def indexing(self) -> KnowledgeIndexingService:
        """Get the indexing service."""
        if self._indexing_service is None:
            if self._loader_factory is None:
                raise ValueError("Loader factory not configured")

            # Get a default loader
            loader = self._loader_factory.create("sitemap")

            self._indexing_service = KnowledgeIndexingService(
                loader=loader,
                chunker=self._chunker,
                indexer=self._indexer,
                events=self._events,
            )

        return self._indexing_service

    @property
    def search_service(self) -> KnowledgeSearchService:
        """Get the search service."""
        if self._search_service is None:
            self._search_service = KnowledgeSearchService(
                searcher=self._searcher,
                default_index=self._default_index,
                events=self._events,
            )

        return self._search_service

    # === Setup Methods ===

    async def setup(self, **options: Any) -> bool:
        """Set up the backend (create indices, pipelines, etc.).

        Args:
            **options: Setup options.

        Returns:
            True if setup succeeded.
        """
        if not self._setup:
            logger.warning("No setup adapter configured")
            return False

        result = await self._setup.setup(**options)
        return result.success

    async def health_check(self) -> bool:
        """Quick health check.

        Returns:
            True if backend is healthy.
        """
        if not self._setup:
            return False
        return await self._setup.health_check()

    async def deep_health_check(self) -> HealthReport:
        """Comprehensive health check.

        Returns:
            Detailed health report.
        """
        if not self._setup:
            raise ValueError("No setup adapter configured")
        return await self._setup.deep_health_check()

    async def diagnose(self) -> DiagnosticReport:
        """Run diagnostics.

        Returns:
            Diagnostic report with recommendations.
        """
        if not self._setup:
            raise ValueError("No setup adapter configured")
        return await self._setup.diagnose()

    # === Loading Methods ===

    async def load(
        self,
        source: str,
        *,
        index_name: str | None = None,
        account_id: str | None = None,
        collection_id: str | None = None,
        source_id: str | None = None,
        source_type: str | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        **options: Any,
    ) -> IndexResult:
        """Load and index content from a source.

        Automatically detects source type (sitemap, website, etc.).

        Args:
            source: Source URL or path.
            index_name: Target index (uses default if not provided).
            account_id: Account ID for multi-tenancy.
            collection_id: Collection ID.
            source_id: Source ID (auto-generated if not provided).
            source_type: Explicit source type (auto-detected if not provided).
            on_progress: Optional progress callback (current, total).
            **options: Additional loading options.

        Returns:
            Index result with counts.
        """
        if self._loader_factory is None:
            raise ValueError("Loader factory not configured")

        index = index_name or self._default_index
        if not index:
            raise ValueError("No index specified and no default index configured")

        # Auto-detect or use explicit source type
        if source_type:
            loader = self._loader_factory.create(source_type)
        else:
            loader = self._loader_factory.create_for_source(source)

        # Create service for this load operation
        service = KnowledgeIndexingService(
            loader=loader,
            chunker=self._chunker,
            indexer=self._indexer,
            events=self._events,
        )

        return await service.load_and_index(
            source=source,
            index_name=index,
            account_id=account_id,
            collection_id=collection_id,
            source_id=source_id,
            **options,
        )

    async def load_streaming(
        self,
        source: str,
        *,
        index_name: str | None = None,
        account_id: str | None = None,
        collection_id: str | None = None,
        collection_name: str | None = None,
        source_id: str | None = None,
        url_batch_size: int = 50,
        fetch_concurrency: int = 10,
        index_batch_size: int = 100,
        on_progress: Callable[[int, int], None] | None = None,
        **options: Any,
    ) -> IndexResult:
        """Load and index content using streaming pipeline with bounded memory.

        This method is optimized for large sitemaps (10,000+ URLs) that would
        otherwise exhaust memory. It processes URLs in batches, indexing
        documents immediately rather than loading all content first.

        Memory usage is bounded and independent of sitemap size:
        - URL storage: O(url_batch_size)
        - Document storage: O(index_batch_size)
        - In-flight fetches: O(fetch_concurrency * avg_page_size)

        Args:
            source: Sitemap URL.
            index_name: Target index (uses default if not provided).
            account_id: Account ID for multi-tenancy.
            collection_id: Collection ID.
            collection_name: Collection name for display.
            source_id: Source ID (auto-generated if not provided).
            url_batch_size: URLs to discover per batch (default 50).
            fetch_concurrency: Parallel URL fetches (default 10).
            index_batch_size: Documents per index batch (default 100).
            on_progress: Optional progress callback (urls_processed, docs_indexed).
            **options: Additional loading options (max_urls, patterns, etc.).

        Returns:
            Index result with counts.

        Example:
            ```python
            # Efficiently load 100k+ URL sitemap
            result = await knowledge.load_streaming(
                "https://large-site.com/sitemap.xml",
                url_batch_size=100,
                fetch_concurrency=20,
                max_urls=50000,
            )
            print(f"Indexed {result.indexed_count} documents")
            ```
        """
        if self._loader_factory is None:
            raise ValueError("Loader factory not configured")

        index = index_name or self._default_index
        if not index:
            raise ValueError("No index specified and no default index configured")

        # Create sitemap loader specifically for streaming
        loader = self._loader_factory.create("sitemap")

        # Configure pipeline
        config = PipelineConfig(
            url_batch_size=url_batch_size,
            fetch_concurrency=fetch_concurrency,
            index_batch_size=index_batch_size,
        )

        # Create streaming pipeline
        pipeline = StreamingIndexingPipeline(
            loader=loader,
            indexer=self._indexer,
            config=config,
            events=self._events,
        )

        return await pipeline.execute(
            source=source,
            index_name=index,
            account_id=account_id,
            collection_id=collection_id,
            collection_name=collection_name,
            source_id=source_id,
            **options,
        )

    # === Search Methods ===

    async def search(
        self,
        query: str,
        *,
        index_name: str | None = None,
        mode: SearchMode = SearchMode.HYBRID,
        limit: int = 10,
        offset: int = 0,
        account_id: str | None = None,
        collection_ids: list[str] | None = None,
        source_ids: list[str] | None = None,
        min_score: float | None = None,
        **options: Any,
    ) -> SearchResult:
        """Search for knowledge documents.

        Args:
            query: Search query text.
            index_name: Index to search (uses default if not provided).
            mode: Search mode (semantic, keyword, hybrid).
            limit: Maximum results.
            offset: Result offset for pagination.
            account_id: Account ID for multi-tenancy.
            collection_ids: Filter by collection IDs.
            source_ids: Filter by source IDs.
            min_score: Minimum score threshold.
            **options: Additional search options.

        Returns:
            Search results.
        """
        return await self.search_service.search(
            query=query,
            index_name=index_name,
            mode=mode,
            limit=limit,
            offset=offset,
            account_id=account_id,
            collection_ids=collection_ids,
            source_ids=source_ids,
            min_score=min_score,
            **options,
        )

    async def semantic_search(
        self,
        query: str,
        *,
        limit: int = 10,
        **options: Any,
    ) -> SearchResult:
        """Execute semantic (vector) search.

        Args:
            query: Search query.
            limit: Maximum results.
            **options: Additional options.

        Returns:
            Search results.
        """
        return await self.search_service.semantic_search(
            query=query,
            limit=limit,
            **options,
        )

    async def keyword_search(
        self,
        query: str,
        *,
        limit: int = 10,
        **options: Any,
    ) -> SearchResult:
        """Execute keyword (BM25) search.

        Args:
            query: Search query.
            limit: Maximum results.
            **options: Additional options.

        Returns:
            Search results.
        """
        return await self.search_service.keyword_search(
            query=query,
            limit=limit,
            **options,
        )

    async def find_similar(
        self,
        doc_id: str,
        *,
        limit: int = 10,
        **options: Any,
    ) -> SearchResult:
        """Find documents similar to a given document.

        Args:
            doc_id: Document ID.
            limit: Maximum results.
            **options: Additional options.

        Returns:
            Search results.
        """
        return await self.search_service.find_similar(
            doc_id=doc_id,
            limit=limit,
            **options,
        )

    # === Management Methods ===

    async def delete_source(
        self,
        source_id: str,
        *,
        index_name: str | None = None,
        account_id: str | None = None,
    ) -> int:
        """Delete all documents from a source.

        Args:
            source_id: Source ID to delete.
            index_name: Index name.
            account_id: Account ID for multi-tenancy.

        Returns:
            Count of deleted documents.
        """
        index = index_name or self._default_index
        if not index:
            raise ValueError("No index specified")

        return await self.indexing.delete_source(source_id, index, account_id)

    async def delete_collection(
        self,
        collection_id: str,
        *,
        index_name: str | None = None,
        account_id: str | None = None,
    ) -> int:
        """Delete all documents from a collection.

        Args:
            collection_id: Collection ID to delete.
            index_name: Index name.
            account_id: Account ID for multi-tenancy.

        Returns:
            Count of deleted documents.
        """
        index = index_name or self._default_index
        if not index:
            raise ValueError("No index specified")

        return await self.indexing.delete_collection(collection_id, index, account_id)

    async def count(
        self,
        *,
        index_name: str | None = None,
        account_id: str | None = None,
        collection_id: str | None = None,
    ) -> int:
        """Count documents.

        Args:
            index_name: Index to count.
            account_id: Filter by account.
            collection_id: Filter by collection.

        Returns:
            Document count.
        """
        return await self.search_service.count(
            index_name=index_name,
            account_id=account_id,
            collection_id=collection_id,
        )

    # === Collection and Stats Methods ===

    async def get_collections(self) -> list[dict[str, Any]]:
        """Get all collections with document counts.

        Aggregates unique collection_ids from indexed documents.

        Returns:
            List of collection dictionaries with id, name, and document_count.
        """
        return await self.search_service.get_collections()

    async def get_stats(self) -> dict[str, Any]:
        """Get index statistics.

        Returns:
            Dictionary with document_count, index_name, and other stats.
        """
        return await self.search_service.get_stats()

    async def list_documents(
        self,
        *,
        source_id: str | None = None,
        collection_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List documents with optional filters.

        Args:
            source_id: Optional source ID filter.
            collection_id: Optional collection ID filter.
            limit: Maximum documents to return (max 100).
            offset: Number of documents to skip.

        Returns:
            Dictionary with documents, total, limit, offset.
        """
        index = self._default_index
        if not index:
            raise ValueError("No default index configured")

        # Clamp limit to reasonable bounds
        limit = min(max(1, limit), 100)
        offset = max(0, offset)

        return await self._searcher.list_documents(
            index_name=index,
            source_id=source_id,
            collection_id=collection_id,
            limit=limit,
            offset=offset,
        )

    # === Agentic Search Status ===

    @property
    def is_agentic_configured(self) -> bool:
        """Check if agentic search is configured.

        Returns:
            True if at least one agent type is configured.
        """
        if not hasattr(self, '_searcher') or not hasattr(self._searcher, '_config'):
            return False
        config = self._searcher._config
        return bool(config.flow_agent_id or config.conversational_agent_id)

    async def get_agentic_status(self) -> dict[str, Any]:
        """Get status of agentic search configuration.

        Returns:
            Dictionary with agent availability status:
            - available: True if any agent is configured
            - flow_agent: True if flow agent is configured
            - conversational_agent: True if conversational agent is configured
        """
        if not hasattr(self, '_searcher') or not hasattr(self._searcher, '_config'):
            return {
                "available": False,
                "flow_agent": False,
                "conversational_agent": False,
            }

        config = self._searcher._config
        return {
            "available": bool(config.flow_agent_id or config.conversational_agent_id),
            "flow_agent": bool(config.flow_agent_id),
            "conversational_agent": bool(config.conversational_agent_id),
        }

    async def agentic_search(
        self,
        query: str,
        *,
        agent_type: AgentType = AgentType.FLOW,
        index_name: str | None = None,
        collection_ids: list[str] | None = None,
        source_ids: list[str] | None = None,
        conversation_id: str | None = None,
        include_reasoning: bool = True,
        limit: int = 10,
        **options: Any,
    ) -> AgenticSearchResult:
        """Execute agentic search with AI-powered reasoning.

        Uses OpenSearch ML agents to understand queries, retrieve relevant
        documents, and generate natural language answers.

        Args:
            query: Search query text.
            agent_type: Type of agent (FLOW for fast RAG, CONVERSATIONAL for multi-turn).
            index_name: Index to search (uses default if not provided).
            collection_ids: Filter by collection IDs.
            source_ids: Filter by source IDs.
            conversation_id: Conversation ID for multi-turn (conversational agent).
            include_reasoning: Include reasoning steps in response.
            limit: Maximum source documents to retrieve.
            **options: Additional agent options.

        Returns:
            AgenticSearchResult with answer, reasoning steps, and sources.

        Raises:
            AgenticSearchError: If agent execution fails.
            ValueError: If agentic search is not configured.

        Example:
            ```python
            result = await knowledge.agentic_search(
                "How does authentication work?",
                agent_type=AgentType.FLOW,
            )
            print(result.answer)
            for source in result.items:
                print(f"- {source.title}")
            ```
        """
        # Check if agentic search is configured
        if not self.is_agentic_configured:
            raise ValueError(
                "Agentic search is not configured. "
                "Run 'gnosisllm-knowledge agentic setup' and set agent IDs in environment."
            )

        # Get client and config from the searcher
        if not hasattr(self._searcher, '_client') or not hasattr(self._searcher, '_config'):
            raise ValueError("Searcher does not have OpenSearch client/config")

        client = self._searcher._client
        config = self._searcher._config

        # Create agentic searcher
        agentic_searcher = OpenSearchAgenticSearcher(client, config)

        # Build agentic query
        agentic_query = AgenticSearchQuery(
            text=query,
            agent_type=agent_type,
            collection_ids=collection_ids,
            source_ids=source_ids,
            conversation_id=conversation_id,
            include_reasoning=include_reasoning,
            limit=limit,
        )

        # Determine index name
        index = index_name or self._default_index
        if not index:
            raise ValueError("No index specified and no default index configured")

        # Execute agentic search
        return await agentic_searcher.agentic_search(agentic_query, index, **options)

    async def close(self) -> None:
        """Close connections and clean up resources."""
        # Subclasses or future implementations can override this
        pass
