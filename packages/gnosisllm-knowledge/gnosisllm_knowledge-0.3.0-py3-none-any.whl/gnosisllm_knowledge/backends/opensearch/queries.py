"""OpenSearch query builders for knowledge search.

Uses OpenSearch neural search - embeddings are generated automatically
via the deployed model. No Python-side embedding generation needed.
"""

from __future__ import annotations

from typing import Any

from gnosisllm_knowledge.core.domain.search import SearchQuery


class QueryBuilder:
    """Builder for OpenSearch queries.

    Uses OpenSearch neural search for semantic queries. The deployed
    model handles embedding generation automatically via ingest and
    search pipelines.

    Example:
        ```python
        query = SearchQuery(text="how to configure", account_id="acc123")
        builder = QueryBuilder(query, model_id="abc123")
        os_query = builder.build_hybrid_query()
        ```
    """

    def __init__(
        self,
        query: SearchQuery,
        model_id: str | None = None,
        embedding_field: str = "content_embedding",
    ) -> None:
        """Initialize query builder.

        Args:
            query: Search query parameters.
            model_id: OpenSearch ML model ID for neural search.
            embedding_field: Field name for the embedding vector.
        """
        self._query = query
        self._model_id = model_id
        self._embedding_field = embedding_field

    def build_semantic_query(self, k: int | None = None) -> dict[str, Any]:
        """Build neural (semantic) search query.

        OpenSearch automatically embeds the query text using the
        deployed model specified by model_id.

        Args:
            k: Number of results for k-NN (default: query.limit).

        Returns:
            OpenSearch query dictionary.
        """
        if not self._model_id:
            raise ValueError("model_id required for semantic search")

        k = k or self._query.limit

        query: dict[str, Any] = {
            "size": self._query.limit,
            "from": self._query.offset,
            "query": {
                "bool": {
                    "must": [
                        {
                            "neural": {
                                self._embedding_field: {
                                    "query_text": self._query.text,
                                    "model_id": self._model_id,
                                    "k": k,
                                }
                            }
                        }
                    ],
                    "filter": self._build_filters(),
                }
            },
        }

        if self._query.min_score:
            query["min_score"] = self._query.min_score

        self._add_highlighting(query)
        self._add_source_filtering(query)
        self._add_explain(query)
        self._add_search_after(query)

        return query

    def build_keyword_query(self) -> dict[str, Any]:
        """Build keyword (BM25) search query.

        Returns:
            OpenSearch query dictionary.
        """
        # Build match query with optional field boosting
        field_boosts = self._query.field_boosts or {"title": 2.0, "content": 1.0}

        should_clauses = []
        for field, boost in field_boosts.items():
            should_clauses.append(
                {
                    "match": {
                        field: {
                            "query": self._query.text,
                            "boost": boost,
                        }
                    }
                }
            )

        query: dict[str, Any] = {
            "size": self._query.limit,
            "from": self._query.offset,
            "query": {
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1,
                    "filter": self._build_filters(),
                }
            },
        }

        if self._query.min_score:
            query["min_score"] = self._query.min_score

        self._add_highlighting(query)
        self._add_source_filtering(query)
        self._add_explain(query)
        self._add_search_after(query)

        return query

    def build_hybrid_query(
        self,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        k: int | None = None,
    ) -> dict[str, Any]:
        """Build hybrid search query combining neural and keyword.

        Uses OpenSearch hybrid search with search pipeline for score
        normalization and combination.

        Args:
            semantic_weight: Weight for semantic score (default: 0.7).
            keyword_weight: Weight for keyword score (default: 0.3).
            k: Number of results for k-NN (default: query.limit * 2).

        Returns:
            OpenSearch query dictionary.
        """
        if not self._model_id:
            # Fall back to keyword-only if no model_id
            return self.build_keyword_query()

        k = k or (self._query.limit * 2)
        field_boosts = self._query.field_boosts or {"title": 2.0, "content": 1.0}

        # Build keyword should clauses
        keyword_should = []
        for field, boost in field_boosts.items():
            keyword_should.append(
                {
                    "match": {
                        field: {
                            "query": self._query.text,
                            "boost": boost,
                        }
                    }
                }
            )

        # OpenSearch hybrid query format
        query: dict[str, Any] = {
            "size": self._query.limit,
            "from": self._query.offset,
            "query": {
                "hybrid": {
                    "queries": [
                        # Neural (semantic) component
                        {
                            "neural": {
                                self._embedding_field: {
                                    "query_text": self._query.text,
                                    "model_id": self._model_id,
                                    "k": k,
                                }
                            }
                        },
                        # Keyword (BM25) component
                        {
                            "bool": {
                                "should": keyword_should,
                                "minimum_should_match": 1,
                            }
                        },
                    ]
                }
            },
        }

        # Apply filters at top level for hybrid
        filters = self._build_filters()
        if filters:
            query["query"] = {
                "bool": {
                    "must": [query["query"]],
                    "filter": filters,
                }
            }

        if self._query.min_score:
            query["min_score"] = self._query.min_score

        self._add_highlighting(query)
        self._add_source_filtering(query)
        self._add_explain(query)
        # Note: Don't add sort for hybrid queries - normalization processor handles it

        return query

    def build_more_like_this_query(
        self,
        doc_id: str,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build more-like-this query for similar documents.

        Args:
            doc_id: Document ID to find similar documents for.
            fields: Fields to use for similarity (default: content, title).

        Returns:
            OpenSearch query dictionary.
        """
        fields = fields or ["content", "title"]

        query: dict[str, Any] = {
            "size": self._query.limit,
            "from": self._query.offset,
            "query": {
                "bool": {
                    "must": [
                        {
                            "more_like_this": {
                                "fields": fields,
                                "like": [{"_id": doc_id}],
                                "min_term_freq": 1,
                                "max_query_terms": 25,
                                "min_doc_freq": 1,
                            }
                        }
                    ],
                    "filter": self._build_filters(),
                    "must_not": [{"ids": {"values": [doc_id]}}],
                }
            },
        }

        self._add_highlighting(query)
        self._add_source_filtering(query)

        return query

    def _build_filters(self) -> list[dict[str, Any]]:
        """Build filter clauses from query parameters.

        Returns:
            List of filter clauses.
        """
        filters: list[dict[str, Any]] = []

        # Multi-tenant filter (required for security)
        if self._query.account_id:
            filters.append({"term": {"account_id": self._query.account_id}})

        # Collection filter
        if self._query.collection_ids:
            filters.append({"terms": {"collection_id": self._query.collection_ids}})

        # Source filter
        if self._query.source_ids:
            filters.append({"terms": {"source_id": self._query.source_ids}})

        # Custom metadata filters
        if self._query.metadata_filters:
            for field, value in self._query.metadata_filters.items():
                if isinstance(value, list):
                    filters.append({"terms": {field: value}})
                else:
                    filters.append({"term": {field: value}})

        return filters

    def _add_highlighting(self, query: dict[str, Any]) -> None:
        """Add highlighting configuration to query.

        Args:
            query: Query dictionary to modify.
        """
        if not self._query.include_highlights:
            return

        query["highlight"] = {
            "fields": {
                "content": {
                    "fragment_size": 150,
                    "number_of_fragments": 3,
                },
                "title": {
                    "fragment_size": 150,
                    "number_of_fragments": 1,
                },
            },
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"],
        }

    def _add_source_filtering(self, query: dict[str, Any]) -> None:
        """Add source field filtering to query.

        Args:
            query: Query dictionary to modify.
        """
        if self._query.include_fields or self._query.exclude_fields:
            source: dict[str, Any] = {}
            if self._query.include_fields:
                source["includes"] = self._query.include_fields
            if self._query.exclude_fields:
                source["excludes"] = self._query.exclude_fields
            query["_source"] = source

    def _add_explain(self, query: dict[str, Any]) -> None:
        """Add explain flag to query for debugging.

        Args:
            query: Query dictionary to modify.
        """
        if self._query.explain:
            query["explain"] = True

    def _add_search_after(self, query: dict[str, Any]) -> None:
        """Add cursor-based pagination to query.

        Args:
            query: Query dictionary to modify.
        """
        # Add sort for consistent pagination
        query["sort"] = [
            {"_score": "desc"},
            {"_id": "asc"},  # Tiebreaker
        ]


def build_delete_by_source_query(
    source_id: str,
    account_id: str | None = None,
) -> dict[str, Any]:
    """Build query to delete documents by source.

    Args:
        source_id: Source ID to delete.
        account_id: Optional account filter for multi-tenancy.

    Returns:
        Delete-by-query dictionary.
    """
    filters = [{"term": {"source_id": source_id}}]
    if account_id:
        filters.append({"term": {"account_id": account_id}})

    return {
        "query": {
            "bool": {
                "filter": filters,
            }
        }
    }


def build_delete_by_collection_query(
    collection_id: str,
    account_id: str | None = None,
) -> dict[str, Any]:
    """Build query to delete documents by collection.

    Args:
        collection_id: Collection ID to delete.
        account_id: Optional account filter for multi-tenancy.

    Returns:
        Delete-by-query dictionary.
    """
    filters = [{"term": {"collection_id": collection_id}}]
    if account_id:
        filters.append({"term": {"account_id": account_id}})

    return {
        "query": {
            "bool": {
                "filter": filters,
            }
        }
    }


def build_count_query(
    account_id: str | None = None,
    collection_id: str | None = None,
    source_id: str | None = None,
) -> dict[str, Any]:
    """Build query to count documents.

    Args:
        account_id: Optional account filter.
        collection_id: Optional collection filter.
        source_id: Optional source filter.

    Returns:
        Count query dictionary.
    """
    filters: list[dict[str, Any]] = []

    if account_id:
        filters.append({"term": {"account_id": account_id}})
    if collection_id:
        filters.append({"term": {"collection_id": collection_id}})
    if source_id:
        filters.append({"term": {"source_id": source_id}})

    if not filters:
        return {"query": {"match_all": {}}}

    return {
        "query": {
            "bool": {
                "filter": filters,
            }
        }
    }
