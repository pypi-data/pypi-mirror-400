"""Knowledge search service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from gnosisllm_knowledge.core.domain.search import (
    SearchMode,
    SearchQuery,
    SearchResult,
)
from gnosisllm_knowledge.core.events.emitter import EventEmitter
from gnosisllm_knowledge.core.events.types import EventType
from gnosisllm_knowledge.core.exceptions import SearchError

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.interfaces.searcher import IKnowledgeSearcher

logger = logging.getLogger(__name__)


class KnowledgeSearchService:
    """Service for searching knowledge documents.

    Provides a high-level interface for semantic, keyword, and hybrid search.

    Example:
        ```python
        service = KnowledgeSearchService(
            searcher=OpenSearchKnowledgeSearcher(client, config, get_embedding),
        )

        # Semantic search
        results = await service.search(
            query="how to configure authentication",
            mode=SearchMode.HYBRID,
            collection_ids=["docs"],
        )
        ```
    """

    def __init__(
        self,
        searcher: IKnowledgeSearcher,
        default_index: str | None = None,
        events: EventEmitter | None = None,
    ) -> None:
        """Initialize the search service.

        Args:
            searcher: Knowledge searcher implementation.
            default_index: Default index name for searches.
            events: Optional event emitter for tracking.
        """
        self._searcher = searcher
        self._default_index = default_index
        self._events = events or EventEmitter()

    @property
    def events(self) -> EventEmitter:
        """Get the event emitter."""
        return self._events

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

        Raises:
            SearchError: If search fails.
        """
        index = index_name or self._default_index
        if not index:
            raise SearchError(message="No index specified and no default index configured")

        search_query = SearchQuery(
            text=query,
            mode=mode,
            limit=limit,
            offset=offset,
            account_id=account_id,
            collection_ids=collection_ids,
            source_ids=source_ids,
            min_score=min_score,
        )

        try:
            result = await self._searcher.search(search_query, index, **options)

            # TODO: Emit search event when SearchCompletedEvent is defined
            # await self._events.emit_async(SearchCompletedEvent(...))

            return result

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(
                message=f"Search failed: {e}",
                details={"query": query[:100]},
                cause=e,
            ) from e

    async def semantic_search(
        self,
        query: str,
        *,
        index_name: str | None = None,
        limit: int = 10,
        account_id: str | None = None,
        collection_ids: list[str] | None = None,
        **options: Any,
    ) -> SearchResult:
        """Execute semantic (vector) search.

        Args:
            query: Search query text.
            index_name: Index to search.
            limit: Maximum results.
            account_id: Account ID for multi-tenancy.
            collection_ids: Filter by collection IDs.
            **options: Additional options.

        Returns:
            Search results.
        """
        return await self.search(
            query=query,
            index_name=index_name,
            mode=SearchMode.SEMANTIC,
            limit=limit,
            account_id=account_id,
            collection_ids=collection_ids,
            **options,
        )

    async def keyword_search(
        self,
        query: str,
        *,
        index_name: str | None = None,
        limit: int = 10,
        account_id: str | None = None,
        collection_ids: list[str] | None = None,
        **options: Any,
    ) -> SearchResult:
        """Execute keyword (BM25) search.

        Args:
            query: Search query text.
            index_name: Index to search.
            limit: Maximum results.
            account_id: Account ID for multi-tenancy.
            collection_ids: Filter by collection IDs.
            **options: Additional options.

        Returns:
            Search results.
        """
        return await self.search(
            query=query,
            index_name=index_name,
            mode=SearchMode.KEYWORD,
            limit=limit,
            account_id=account_id,
            collection_ids=collection_ids,
            **options,
        )

    async def hybrid_search(
        self,
        query: str,
        *,
        index_name: str | None = None,
        limit: int = 10,
        account_id: str | None = None,
        collection_ids: list[str] | None = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        **options: Any,
    ) -> SearchResult:
        """Execute hybrid search (semantic + keyword).

        Args:
            query: Search query text.
            index_name: Index to search.
            limit: Maximum results.
            account_id: Account ID for multi-tenancy.
            collection_ids: Filter by collection IDs.
            semantic_weight: Weight for semantic score.
            keyword_weight: Weight for keyword score.
            **options: Additional options.

        Returns:
            Search results.
        """
        return await self.search(
            query=query,
            index_name=index_name,
            mode=SearchMode.HYBRID,
            limit=limit,
            account_id=account_id,
            collection_ids=collection_ids,
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight,
            **options,
        )

    async def find_similar(
        self,
        doc_id: str,
        *,
        index_name: str | None = None,
        limit: int = 10,
        **options: Any,
    ) -> SearchResult:
        """Find documents similar to a given document.

        Args:
            doc_id: Document ID to find similar documents for.
            index_name: Index to search.
            limit: Maximum results.
            **options: Additional options.

        Returns:
            Search results.
        """
        index = index_name or self._default_index
        if not index:
            raise SearchError(message="No index specified")

        return await self._searcher.get_similar_documents(doc_id, index, limit)

    async def multi_search(
        self,
        queries: list[str],
        *,
        index_name: str | None = None,
        mode: SearchMode = SearchMode.HYBRID,
        limit: int = 10,
        account_id: str | None = None,
        **options: Any,
    ) -> list[SearchResult]:
        """Execute multiple searches in parallel.

        Args:
            queries: List of query texts.
            index_name: Index to search.
            mode: Search mode.
            limit: Maximum results per query.
            account_id: Account ID for multi-tenancy.
            **options: Additional options.

        Returns:
            List of search results.
        """
        index = index_name or self._default_index
        if not index:
            raise SearchError(message="No index specified")

        search_queries = [
            SearchQuery(
                text=query,
                mode=mode,
                limit=limit,
                account_id=account_id,
            )
            for query in queries
        ]

        return await self._searcher.multi_search(search_queries, index)

    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector.
        """
        return await self._searcher.get_embedding(text)

    async def count(
        self,
        index_name: str | None = None,
        account_id: str | None = None,
        collection_id: str | None = None,
    ) -> int:
        """Count documents in index.

        Args:
            index_name: Index to count.
            account_id: Filter by account.
            collection_id: Filter by collection.

        Returns:
            Document count.
        """
        index = index_name or self._default_index
        if not index:
            raise SearchError(message="No index specified")

        # Build count query
        query = SearchQuery(
            text="",
            limit=0,
            account_id=account_id,
            collection_ids=[collection_id] if collection_id else None,
        )

        # Use a simple match_all to get total count
        result = await self._searcher.search(query, index)
        return result.total_hits

    async def get_collections(
        self,
        index_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all collections with document counts.

        Args:
            index_name: Index to query (uses default if not provided).

        Returns:
            List of collections with id, name, and document_count.
        """
        index = index_name or self._default_index
        if not index:
            logger.warning("No index specified for get_collections")
            return []

        try:
            return await self._searcher.get_collections(index)
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            return []

    async def get_stats(
        self,
        index_name: str | None = None,
    ) -> dict[str, Any]:
        """Get index statistics.

        Args:
            index_name: Index to query (uses default if not provided).

        Returns:
            Dictionary with document_count, index_name, and other stats.
        """
        index = index_name or self._default_index
        if not index:
            return {"document_count": 0, "index_name": "", "exists": False}

        try:
            return await self._searcher.get_stats(index)
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"document_count": 0, "index_name": index, "error": str(e)}
