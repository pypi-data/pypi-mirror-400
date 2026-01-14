"""OpenSearch knowledge searcher implementation.

Uses OpenSearch neural search - embeddings are generated automatically
by the deployed ML model. No Python-side embedding generation needed.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.backends.opensearch.queries import QueryBuilder
from gnosisllm_knowledge.core.domain.search import (
    SearchMode,
    SearchQuery,
    SearchResult,
    SearchResultItem,
)
from gnosisllm_knowledge.core.exceptions import SearchError

if TYPE_CHECKING:
    from opensearchpy import AsyncOpenSearch

logger = logging.getLogger(__name__)


class OpenSearchKnowledgeSearcher:
    """OpenSearch knowledge searcher.

    Implements the IKnowledgeSearcher protocol for semantic, keyword,
    and hybrid search over knowledge documents.

    Uses OpenSearch neural search for semantic queries - the deployed
    ML model handles embedding generation automatically.

    Example:
        ```python
        config = OpenSearchConfig.from_env()
        client = AsyncOpenSearch(hosts=[config.url])
        searcher = OpenSearchKnowledgeSearcher(client, config)

        query = SearchQuery(text="how to configure", mode=SearchMode.HYBRID)
        results = await searcher.search(query, "my-index")
        ```
    """

    def __init__(
        self,
        client: AsyncOpenSearch,
        config: OpenSearchConfig,
    ) -> None:
        """Initialize the searcher.

        Args:
            client: OpenSearch async client.
            config: OpenSearch configuration (includes model_id).
        """
        self._client = client
        self._config = config

    async def search(
        self,
        query: SearchQuery,
        index_name: str,
        **options: Any,
    ) -> SearchResult:
        """Execute search query using the specified mode.

        Args:
            query: Search query with mode and parameters.
            index_name: Index to search.
            **options: Additional search options.

        Returns:
            Search results.
        """
        mode = query.mode

        if mode == SearchMode.SEMANTIC:
            return await self.semantic_search(query, index_name, **options)
        elif mode == SearchMode.KEYWORD:
            return await self.keyword_search(query, index_name, **options)
        elif mode == SearchMode.HYBRID:
            return await self.hybrid_search(query, index_name, **options)
        else:
            # Default to hybrid
            return await self.hybrid_search(query, index_name, **options)

    async def semantic_search(
        self,
        query: SearchQuery,
        index_name: str,
        **options: Any,
    ) -> SearchResult:
        """Execute semantic (neural) search.

        OpenSearch handles embedding generation via the deployed model.

        Args:
            query: Search query.
            index_name: Index to search.
            **options: Additional options.

        Returns:
            Search results.
        """
        start_time = time.perf_counter()

        model_id = options.get("model_id", self._config.model_id)
        if not model_id:
            raise SearchError(
                message="model_id required for semantic search",
                details={"query": query.text[:100]},
            )

        # Build and execute query
        builder = QueryBuilder(
            query,
            model_id=model_id,
            embedding_field=self._config.embedding_field,
        )
        os_query = builder.build_semantic_query()

        result = await self._execute_search(
            query, os_query, index_name, start_time
        )
        return result

    async def keyword_search(
        self,
        query: SearchQuery,
        index_name: str,
        **options: Any,
    ) -> SearchResult:
        """Execute keyword (BM25) search.

        Args:
            query: Search query.
            index_name: Index to search.
            **options: Additional options.

        Returns:
            Search results.
        """
        start_time = time.perf_counter()

        builder = QueryBuilder(query)
        os_query = builder.build_keyword_query()

        result = await self._execute_search(
            query, os_query, index_name, start_time
        )
        return result

    async def hybrid_search(
        self,
        query: SearchQuery,
        index_name: str,
        **options: Any,
    ) -> SearchResult:
        """Execute hybrid search (semantic + keyword).

        Uses OpenSearch hybrid query with search pipeline for
        score normalization.

        Args:
            query: Search query.
            index_name: Index to search.
            **options: semantic_weight, keyword_weight, model_id.

        Returns:
            Search results.
        """
        start_time = time.perf_counter()

        model_id = options.get("model_id", self._config.model_id)

        # Build hybrid query
        semantic_weight = options.get("semantic_weight", 0.7)
        keyword_weight = options.get("keyword_weight", 0.3)

        builder = QueryBuilder(
            query,
            model_id=model_id,
            embedding_field=self._config.embedding_field,
        )
        os_query = builder.build_hybrid_query(
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight,
        )

        # Use search pipeline for hybrid if configured
        search_params = {}
        if self._config.search_pipeline_name:
            search_params["search_pipeline"] = self._config.search_pipeline_name

        result = await self._execute_search(
            query, os_query, index_name, start_time, **search_params
        )
        return result

    async def get_similar_documents(
        self,
        doc_id: str,
        index_name: str,
        limit: int = 10,
    ) -> SearchResult:
        """Find documents similar to a given document.

        Args:
            doc_id: Document ID to find similar documents for.
            index_name: Index to search.
            limit: Maximum results.

        Returns:
            Search results with similar documents.
        """
        start_time = time.perf_counter()

        query = SearchQuery(text="", limit=limit)
        builder = QueryBuilder(query)
        os_query = builder.build_more_like_this_query(doc_id)

        result = await self._execute_search(
            query, os_query, index_name, start_time
        )
        return result

    async def multi_search(
        self,
        queries: list[SearchQuery],
        index_name: str,
    ) -> list[SearchResult]:
        """Execute multiple searches in a single request.

        Args:
            queries: List of search queries.
            index_name: Index to search.

        Returns:
            List of search results.
        """
        if not queries:
            return []

        start_time = time.perf_counter()
        msearch_body = []

        for query in queries:
            builder = QueryBuilder(
                query,
                model_id=self._config.model_id,
                embedding_field=self._config.embedding_field,
            )

            if query.mode == SearchMode.SEMANTIC:
                os_query = builder.build_semantic_query()
            elif query.mode == SearchMode.KEYWORD:
                os_query = builder.build_keyword_query()
            else:
                os_query = builder.build_hybrid_query()

            msearch_body.append({"index": index_name})
            msearch_body.append(os_query)

        response = await self._client.msearch(body=msearch_body)

        results = []
        for i, resp in enumerate(response.get("responses", [])):
            duration_ms = (time.perf_counter() - start_time) * 1000
            result = self._parse_response(queries[i], resp, duration_ms)
            results.append(result)

        return results

    async def _execute_search(
        self,
        query: SearchQuery,
        os_query: dict[str, Any],
        index_name: str,
        start_time: float,
        **params: Any,
    ) -> SearchResult:
        """Execute search and parse results.

        Args:
            query: Original search query.
            os_query: OpenSearch query dictionary.
            index_name: Index to search.
            start_time: Search start time.
            **params: Additional search parameters.

        Returns:
            Parsed search results.
        """
        try:
            logger.debug(f"OpenSearch query: {os_query}")
            logger.debug(f"Query include_highlights: {query.include_highlights}")

            response = await self._client.search(
                index=index_name,
                body=os_query,
                **params,
            )

            # Debug: Log first hit to see if highlights are present
            hits = response.get("hits", {}).get("hits", [])
            if hits:
                first_hit = hits[0]
                logger.debug(f"First hit keys: {first_hit.keys()}")
                if "highlight" in first_hit:
                    logger.debug(f"Highlight data: {first_hit['highlight']}")
                else:
                    logger.debug("No 'highlight' key in response hit")

            duration_ms = (time.perf_counter() - start_time) * 1000
            return self._parse_response(query, response, duration_ms)

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(
                message=f"Search failed: {e}",
                details={"query": query.text[:100], "index": index_name},
                cause=e,
            ) from e

    def _parse_response(
        self,
        query: SearchQuery,
        response: dict[str, Any],
        duration_ms: float,
    ) -> SearchResult:
        """Parse OpenSearch response into SearchResult.

        Args:
            query: Original query.
            response: OpenSearch response.
            duration_ms: Search duration in milliseconds.

        Returns:
            Parsed search result.
        """
        hits = response.get("hits", {})
        total = hits.get("total", {})
        total_hits = total.get("value", 0) if isinstance(total, dict) else total
        max_score = hits.get("max_score")

        items = []
        search_after_token = None

        for hit in hits.get("hits", []):
            source = hit.get("_source", {})

            # Extract highlights
            highlights = None
            highlighted_title = None
            if "highlight" in hit:
                highlight_data = hit["highlight"]
                highlights = highlight_data.get("content", [])
                title_highlights = highlight_data.get("title", [])
                if title_highlights:
                    highlighted_title = title_highlights[0]

            item = SearchResultItem(
                doc_id=hit.get("_id", ""),
                content=source.get("content", ""),
                score=hit.get("_score", 0.0),
                title=source.get("title"),
                url=source.get("url"),
                source=source.get("source"),
                collection_id=source.get("collection_id"),
                highlights=highlights,
                highlighted_title=highlighted_title,
                metadata=source.get("metadata"),
                chunk_index=source.get("chunk_index"),
                total_chunks=source.get("total_chunks"),
                explanation=hit.get("_explanation") if query.explain else None,
            )
            items.append(item)

            # Track search_after for cursor pagination
            if "sort" in hit:
                search_after_token = hit["sort"]

        return SearchResult(
            query=query.text,
            mode=query.mode,
            items=items,
            total_hits=total_hits,
            duration_ms=duration_ms,
            max_score=max_score,
            search_after_token=search_after_token,
            has_more=len(items) == query.limit and total_hits > query.offset + len(items),
        )

    async def get_collections(self, index_name: str) -> list[dict[str, Any]]:
        """Get unique collections with document counts via aggregation.

        Args:
            index_name: Index to query.

        Returns:
            List of collections with id, name, and document_count.
        """
        try:
            # Check if index exists
            exists = await self._client.indices.exists(index=index_name)
            if not exists:
                logger.debug(f"Index {index_name} does not exist")
                return []

            # Aggregation query for unique collection_ids with counts
            # Also aggregate collection_name for display
            query = {
                "size": 0,
                "aggs": {
                    "collections": {
                        "terms": {
                            "field": "collection_id",
                            "size": 1000,  # Max collections to return
                        },
                        "aggs": {
                            "collection_name": {
                                "terms": {
                                    "field": "collection_name",
                                    "size": 1,
                                }
                            }
                        }
                    }
                }
            }

            response = await self._client.search(index=index_name, body=query)

            collections = []
            buckets = response.get("aggregations", {}).get("collections", {}).get("buckets", [])

            for bucket in buckets:
                collection_id = bucket.get("key")
                if not collection_id:
                    continue

                doc_count = bucket.get("doc_count", 0)

                # Get collection name from nested agg or use ID as fallback
                name_buckets = bucket.get("collection_name", {}).get("buckets", [])
                collection_name = name_buckets[0].get("key") if name_buckets else collection_id

                collections.append({
                    "id": collection_id,
                    "name": collection_name or collection_id,
                    "document_count": doc_count,
                })

            logger.debug(f"Found {len(collections)} collections in {index_name}")
            return collections

        except Exception as e:
            logger.error(f"Failed to get collections from {index_name}: {e}")
            return []

    async def get_stats(self, index_name: str) -> dict[str, Any]:
        """Get index statistics.

        Args:
            index_name: Index to query.

        Returns:
            Dictionary with document_count and index info.
        """
        try:
            # Check if index exists
            exists = await self._client.indices.exists(index=index_name)
            if not exists:
                return {
                    "document_count": 0,
                    "index_name": index_name,
                    "exists": False,
                }

            # Get index stats
            stats = await self._client.indices.stats(index=index_name)
            index_stats = stats.get("indices", {}).get(index_name, {})
            primaries = index_stats.get("primaries", {})
            docs = primaries.get("docs", {})

            return {
                "document_count": docs.get("count", 0),
                "index_name": index_name,
                "exists": True,
                "size_bytes": primaries.get("store", {}).get("size_in_bytes", 0),
            }

        except Exception as e:
            logger.error(f"Failed to get stats for {index_name}: {e}")
            return {
                "document_count": 0,
                "index_name": index_name,
                "error": str(e),
            }

    async def list_documents(
        self,
        index_name: str,
        *,
        account_id: str | None = None,
        source_id: str | None = None,
        collection_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List documents with optional filters.

        Args:
            index_name: Index to query.
            account_id: Optional account ID filter.
            source_id: Optional source ID filter.
            collection_id: Optional collection ID filter.
            limit: Maximum documents to return.
            offset: Number of documents to skip.

        Returns:
            Dictionary with documents, total, limit, offset.
        """
        try:
            # Check if index exists
            exists = await self._client.indices.exists(index=index_name)
            if not exists:
                logger.debug(f"Index {index_name} does not exist")
                return {
                    "documents": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                }

            # Build filter clauses
            filters: list[dict[str, Any]] = []

            if account_id:
                filters.append({"term": {"account_id": account_id}})

            if source_id:
                filters.append({"term": {"source_id": source_id}})

            if collection_id:
                filters.append({"term": {"collection_id": collection_id}})

            # Build query with match_all and filters
            query: dict[str, Any] = {
                "size": limit,
                "from": offset,
                "sort": [
                    {"created_at": {"order": "desc", "unmapped_type": "date"}},
                    {"_id": {"order": "asc"}},
                ],
                "_source": {
                    "excludes": ["content_embedding"],
                },
            }

            if filters:
                query["query"] = {
                    "bool": {
                        "must": [{"match_all": {}}],
                        "filter": filters,
                    }
                }
            else:
                query["query"] = {"match_all": {}}

            response = await self._client.search(index=index_name, body=query)

            hits = response.get("hits", {})
            total = hits.get("total", {})
            total_hits = total.get("value", 0) if isinstance(total, dict) else total

            documents = []
            for hit in hits.get("hits", []):
                source = hit.get("_source", {})
                doc = {
                    "id": hit.get("_id", ""),
                    "title": source.get("title"),
                    "url": source.get("url"),
                    "content_preview": (source.get("content", ""))[:200],
                    "content": source.get("content"),
                    "chunk_index": source.get("chunk_index"),
                    "total_chunks": source.get("total_chunks"),
                    "source_id": source.get("source_id"),
                    "collection_id": source.get("collection_id"),
                    "created_at": source.get("created_at"),
                    "metadata": source.get("metadata"),
                }
                documents.append(doc)

            logger.debug(
                f"Listed {len(documents)} documents from {index_name} "
                f"(total: {total_hits}, source_id: {source_id})"
            )

            return {
                "documents": documents,
                "total": total_hits,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            logger.error(f"Failed to list documents from {index_name}: {e}")
            return {
                "documents": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
            }
