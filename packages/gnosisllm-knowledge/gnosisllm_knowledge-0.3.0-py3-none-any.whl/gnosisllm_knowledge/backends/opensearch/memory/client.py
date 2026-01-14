"""OpenSearch Agentic Memory API client."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

import httpx

from gnosisllm_knowledge.core.domain.memory import (
    ContainerConfig,
    ContainerInfo,
    HistoryAction,
    HistoryEntry,
    MemoryEntry,
    MemoryStats,
    MemoryStrategy,
    MemoryType,
    Message,
    Namespace,
    PayloadType,
    RecallResult,
    SessionInfo,
    StoreRequest,
    StoreResult,
)
from gnosisllm_knowledge.core.exceptions import ContainerNotFoundError, MemoryError

if TYPE_CHECKING:
    from gnosisllm_knowledge.backends.opensearch.memory.config import MemoryConfig

logger = logging.getLogger(__name__)


class OpenSearchMemoryClient:
    """Client for OpenSearch Agentic Memory APIs.

    Implements memory operations using the OpenSearch ML Memory plugin.

    Example:
        ```python
        client = OpenSearchMemoryClient(config)

        # Create container
        container = await client.create_container(ContainerConfig(
            name="my-memory",
            strategies=[
                StrategyConfig(type=MemoryStrategy.SEMANTIC, namespace=["user_id"]),
            ],
        ))

        # List containers
        containers = await client.list_containers()
        ```
    """

    def __init__(self, config: MemoryConfig) -> None:
        """Initialize the client.

        Args:
            config: Memory configuration.
        """
        self._config = config
        self._base_url = config.url
        self._auth = config.auth

    # === Container Management ===

    async def create_container(
        self,
        config: ContainerConfig,
        **options: Any,
    ) -> ContainerInfo:
        """Create a memory container.

        Args:
            config: Container configuration.
            **options: Additional options.

        Returns:
            Created container info.
        """
        # Build strategies list
        strategies = [s.to_dict() for s in config.strategies]
        if not strategies:
            # Use default strategies from config
            strategies = [
                {
                    "type": s.value,
                    "namespace": ["user_id"],
                    "configuration": {
                        "llm_result_path": self._config.llm_result_path,
                    },
                }
                for s in self._config.default_strategies
            ]

        body: dict[str, Any] = {
            "name": config.name,
            "configuration": {
                "embedding_model_id": config.embedding_model_id
                or self._config.embedding_model_id,
                "embedding_model_type": config.embedding_model_type.value,
                "embedding_dimension": config.embedding_dimension,
                "llm_id": config.llm_model_id or self._config.llm_model_id,
                "strategies": strategies,
                "use_system_index": config.use_system_index,
                "parameters": {
                    "llm_result_path": config.llm_result_path,
                },
            },
        }

        if config.description:
            body["description"] = config.description
        if config.index_prefix:
            body["configuration"]["index_prefix"] = config.index_prefix
        if config.index_settings:
            body["configuration"]["index_settings"] = config.index_settings.to_dict()

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/_create",
                json=body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        container_id = result.get("memory_container_id")

        return ContainerInfo(
            id=container_id,
            name=config.name,
            description=config.description,
            strategies=[s.type for s in config.strategies] if config.strategies else [],
            embedding_model_id=config.embedding_model_id,
            llm_model_id=config.llm_model_id,
        )

    async def get_container(
        self,
        container_id: str,
        **options: Any,
    ) -> ContainerInfo | None:
        """Get container by ID.

        Args:
            container_id: Container ID.
            **options: Additional options.

        Returns:
            Container info or None if not found.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.get(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}",
                auth=self._auth,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

        return self._parse_container_info(container_id, data)

    async def list_containers(
        self,
        limit: int = 100,
        **options: Any,
    ) -> list[ContainerInfo]:
        """List all containers.

        Args:
            limit: Maximum number of containers to return.
            **options: Additional options.

        Returns:
            List of container info.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/_search",
                json={"query": {"match_all": {}}, "size": limit},
                auth=self._auth,
            )
            response.raise_for_status()
            data = response.json()

        containers = []
        for hit in data.get("hits", {}).get("hits", []):
            container = self._parse_container_info(hit["_id"], hit["_source"])
            containers.append(container)

        return containers

    async def update_container(
        self,
        container_id: str,
        config: ContainerConfig,
        **options: Any,
    ) -> ContainerInfo:
        """Update a container configuration.

        Args:
            container_id: Container ID.
            config: Updated configuration.
            **options: Additional options.

        Returns:
            Updated container info.
        """
        body: dict[str, Any] = {}

        if config.description is not None:
            body["description"] = config.description

        if config.strategies:
            body["configuration"] = {
                "strategies": [s.to_dict() for s in config.strategies],
            }

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.put(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}",
                json=body,
                auth=self._auth,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_container_info(container_id, data)

    async def delete_container(
        self,
        container_id: str,
        **options: Any,
    ) -> bool:
        """Delete a container.

        Args:
            container_id: Container ID.
            **options: Additional options.

        Returns:
            True if deleted, False if not found.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.delete(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}",
                auth=self._auth,
            )
            if response.status_code == 404:
                return False
            response.raise_for_status()

        return True

    # === Memory Storage ===

    async def store(
        self,
        container_id: str,
        request: StoreRequest,
        **options: Any,
    ) -> StoreResult:
        """Store memory with optional inference.

        Which strategies run is determined by:
        1. How the container was configured (strategy -> namespace field mapping)
        2. Which namespace fields are present in the request

        Example:
            Container has SEMANTIC scoped to "user_id", SUMMARY scoped to "session_id".
            - namespace={"user_id": "123"} -> Runs SEMANTIC only
            - namespace={"user_id": "123", "session_id": "abc"} -> Runs both

        Args:
            container_id: Target container.
            request: Store request with namespace values.
            **options: Additional options.

        Returns:
            Store result.
        """
        # Build request body
        body: dict[str, Any] = {
            "payload_type": request.payload_type.value,
            "infer": request.infer,
        }

        if request.payload_type == PayloadType.CONVERSATIONAL:
            if not request.messages:
                raise MemoryError("Messages required for conversational payload")
            body["messages"] = [m.to_dict() for m in request.messages]
        else:
            if not request.structured_data:
                raise MemoryError("Structured data required for data payload")
            body["structured_data"] = request.structured_data

        # Namespace determines which strategies run based on container config
        body["namespace"] = request.namespace.to_dict()

        if request.metadata:
            body["metadata"] = request.metadata
        if request.tags:
            body["tags"] = request.tags

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.inference_timeout
            if request.infer
            else self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories",
                json=body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        return StoreResult(
            session_id=result.get("session_id"),
            working_memory_id=result.get("working_memory_id"),
        )

    # === Working Memory ===

    async def get_working_memory(
        self,
        container_id: str,
        session_id: str | None = None,
        namespace: Namespace | None = None,
        limit: int = 50,
        offset: int = 0,
        **options: Any,
    ) -> list[Message]:
        """Get working memory messages.

        Args:
            container_id: Container ID.
            session_id: Optional session filter.
            namespace: Optional namespace filter.
            limit: Maximum number of messages to return.
            offset: Number of messages to skip.
            **options: Additional options.

        Returns:
            List of messages.
        """
        search_body: dict[str, Any] = {
            "query": {"match_all": {}},
            "size": limit,
            "from": offset,
            "sort": [{"created_time": "asc"}],
        }

        filters = []
        if session_id:
            filters.append({"term": {"session_id": session_id}})
        if namespace:
            for key, value in namespace.values.items():
                filters.append({"term": {f"namespace.{key}": value}})

        if filters:
            search_body["query"] = {"bool": {"filter": filters}}

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/working/_search",
                json=search_body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        messages = []
        for hit in result.get("hits", {}).get("hits", []):
            source = hit["_source"]
            content_parts = source.get("content", [])
            content = content_parts[0].get("text", "") if content_parts else ""
            messages.append(
                Message(
                    role=source.get("role", "user"),
                    content=content,
                    timestamp=datetime.fromtimestamp(source["created_time"] / 1000)
                    if source.get("created_time")
                    else None,
                )
            )

        return messages

    async def clear_working_memory(
        self,
        container_id: str,
        session_id: str | None = None,
        namespace: Namespace | None = None,
        **options: Any,
    ) -> int:
        """Clear working memory.

        Deletes working memory messages matching the filter criteria.
        Uses delete-by-query internally.

        Args:
            container_id: Container ID.
            session_id: Optional session filter.
            namespace: Optional namespace filter.
            **options: Backend-specific options.

        Returns:
            Number of messages deleted.
        """
        # Build query for delete-by-query
        filters = []
        if session_id:
            filters.append({"term": {"session_id": session_id}})
        if namespace:
            for key, value in namespace.values.items():
                filters.append({"term": {f"namespace.{key}": value}})

        if filters:
            query: dict[str, Any] = {"bool": {"filter": filters}}
        else:
            query = {"match_all": {}}

        return await self.delete_by_query(
            container_id=container_id,
            memory_type=MemoryType.WORKING,
            query=query,
            **options,
        )

    async def delete_by_query(
        self,
        container_id: str,
        memory_type: MemoryType,
        query: dict[str, Any],
        **options: Any,
    ) -> int:
        """Delete memories matching an OpenSearch Query DSL query.

        Provides full flexibility for complex deletion criteria.

        Example:
            ```python
            # Delete all memories for a user older than 30 days
            await client.delete_by_query(
                container_id=container_id,
                memory_type=MemoryType.WORKING,
                query={
                    "bool": {
                        "must": [
                            {"term": {"namespace.user_id": "user123"}},
                            {"range": {"created_time": {"lt": "now-30d"}}}
                        ]
                    }
                }
            )
            ```

        Args:
            container_id: Container ID.
            memory_type: Memory type to delete from.
            query: OpenSearch Query DSL query.
            **options: Backend-specific options.

        Returns:
            Number of documents deleted.
        """
        body = {"query": query}

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.inference_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/{memory_type.value}/_delete_by_query",
                json=body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        return result.get("deleted", 0)

    # === Memory Recall (Phase 5) ===

    async def recall(
        self,
        container_id: str,
        query: str,
        namespace: Namespace | None = None,
        strategies: list[MemoryStrategy] | None = None,
        min_score: float | None = None,
        limit: int = 10,
        after: datetime | None = None,
        before: datetime | None = None,
        **options: Any,
    ) -> RecallResult:
        """Semantic search over long-term memory.

        Uses the ML API endpoint (NOT direct index access).
        CRITICAL: Memory content is in the 'memory' field, not 'content'.

        Example:
            ```python
            result = await client.recall(
                container_id="container-123",
                query="user preferences",
                namespace=Namespace({"user_id": "alice-123"}),
                strategies=[MemoryStrategy.SEMANTIC],
                limit=5,
            )
            for item in result.items:
                print(f"{item.content} (score: {item.score})")
            ```

        Args:
            container_id: Container ID.
            query: Search query text.
            namespace: Optional namespace filter.
            strategies: Filter by specific strategies.
            min_score: Minimum similarity score.
            limit: Maximum results to return.
            after: Filter by created after timestamp.
            before: Filter by created before timestamp.
            **options: Additional options.

        Returns:
            RecallResult with matching memory entries.
        """
        # Build neural query
        search_body: dict[str, Any] = {
            "query": {
                "neural": {
                    "memory_embedding": {
                        "query_text": query,
                        "model_id": self._config.embedding_model_id,
                        "k": limit,
                    },
                },
            },
            "size": limit,
            "_source": ["memory", "strategy_type", "namespace", "created_time"],
        }

        # Add filters
        filters = []
        if namespace:
            for key, value in namespace.values.items():
                filters.append({"term": {f"namespace.{key}": value}})
        if strategies:
            filters.append({"terms": {"strategy_type": [s.value for s in strategies]}})
        if after:
            filters.append(
                {"range": {"created_time": {"gte": int(after.timestamp() * 1000)}}}
            )
        if before:
            filters.append(
                {"range": {"created_time": {"lte": int(before.timestamp() * 1000)}}}
            )

        if filters:
            search_body["query"] = {
                "bool": {
                    "must": [search_body["query"]],
                    "filter": filters,
                },
            }

        if min_score:
            search_body["min_score"] = min_score

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/long-term/_search",
                json=search_body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        items = []
        for hit in result.get("hits", {}).get("hits", []):
            source = hit["_source"]
            items.append(
                MemoryEntry(
                    id=hit["_id"],
                    content=source.get("memory", ""),  # CRITICAL: field is "memory"
                    strategy=MemoryStrategy(source["strategy_type"])
                    if source.get("strategy_type")
                    else None,
                    score=hit.get("_score", 0.0),
                    namespace=source.get("namespace", {}),
                    created_at=datetime.fromtimestamp(source["created_time"] / 1000)
                    if source.get("created_time")
                    else None,
                )
            )

        return RecallResult(
            items=items,
            total=result.get("hits", {}).get("total", {}).get("value", len(items)),
            query=query,
            took_ms=result.get("took", 0),
        )

    async def get_memory(
        self,
        container_id: str,
        memory_id: str,
        memory_type: MemoryType,
        **options: Any,
    ) -> MemoryEntry | None:
        """Get a specific memory by ID.

        Args:
            container_id: Container ID.
            memory_id: Memory document ID.
            memory_type: Memory type (WORKING or LONG_TERM).
            **options: Backend-specific options.

        Returns:
            Memory entry or None if not found.

        Raises:
            ValueError: If memory_type is SESSIONS or HISTORY.
        """
        if memory_type == MemoryType.SESSIONS:
            raise ValueError("Use get_session() for session retrieval")
        if memory_type == MemoryType.HISTORY:
            raise ValueError("Use get_history_entry() for history retrieval")

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.get(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/{memory_type.value}/{memory_id}",
                auth=self._auth,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

        return self._parse_memory_entry(memory_id, data, memory_type)

    async def delete_memory(
        self,
        container_id: str,
        memory_id: str,
        memory_type: MemoryType,
        **options: Any,
    ) -> bool:
        """Delete a specific memory by ID.

        Args:
            container_id: Container ID.
            memory_id: Memory document ID.
            memory_type: Memory type (WORKING, LONG_TERM).
            **options: Backend-specific options.

        Returns:
            True if deleted, False if not found.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.delete(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/{memory_type.value}/{memory_id}",
                auth=self._auth,
            )
            if response.status_code == 404:
                return False
            response.raise_for_status()

        return True

    async def update_memory(
        self,
        container_id: str,
        memory_id: str,
        memory_type: MemoryType,
        *,
        memory: str | None = None,
        tags: dict[str, str] | None = None,
        **options: Any,
    ) -> MemoryEntry:
        """Update a specific memory.

        Note: History memory type does NOT support updates.

        Args:
            container_id: Container ID.
            memory_id: Memory document ID.
            memory_type: Memory type (working, long-term, sessions).
            memory: Updated memory content (for long-term).
            tags: Updated tags.
            **options: Additional options.

        Returns:
            Updated memory entry.

        Raises:
            MemoryError: If trying to update history.
        """
        if memory_type == MemoryType.HISTORY:
            raise MemoryError("History memory does not support updates")

        body: dict[str, Any] = {}
        if memory is not None:
            body["memory"] = memory
        if tags is not None:
            body["tags"] = tags

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.put(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/{memory_type.value}/{memory_id}",
                json=body,
                auth=self._auth,
            )
            response.raise_for_status()
            data = response.json()

        return MemoryEntry(
            id=memory_id,
            content=data.get("memory", ""),
            strategy=MemoryStrategy(data["strategy_type"])
            if data.get("strategy_type")
            else None,
            namespace=data.get("namespace", {}),
            metadata=data.get("tags", {}),
        )

    async def delete_memories(
        self,
        container_id: str,
        session_id: str | None = None,
        namespace: Namespace | None = None,
        before: datetime | None = None,
        **options: Any,
    ) -> int:
        """Delete memories by filter.

        This is a convenience wrapper around delete_by_query.

        Args:
            container_id: Container ID.
            session_id: Filter by session.
            namespace: Filter by namespace.
            before: Delete memories created before this timestamp.
            **options: Additional options (memory_type defaults to WORKING).

        Returns:
            Number of memories deleted.
        """
        # Build query from filters
        filters = []

        if session_id:
            filters.append({"term": {"session_id": session_id}})
        if namespace:
            for key, value in namespace.values.items():
                filters.append({"term": {f"namespace.{key}": value}})
        if before:
            filters.append(
                {"range": {"created_time": {"lt": int(before.timestamp() * 1000)}}}
            )

        if filters:
            query: dict[str, Any] = {"bool": {"filter": filters}}
        else:
            query = {"match_all": {}}

        # Default to working memory if not specified
        memory_type = options.pop("memory_type", MemoryType.WORKING)

        return await self.delete_by_query(
            container_id=container_id,
            memory_type=memory_type,
            query=query,
            **options,
        )

    # === Session Management (Phase 6) ===

    async def create_session(
        self,
        container_id: str,
        *,
        session_id: str | None = None,
        summary: str | None = None,
        namespace: Namespace | None = None,
        metadata: dict[str, Any] | None = None,
        **options: Any,
    ) -> SessionInfo:
        """Create a new session.

        Args:
            container_id: Container ID.
            session_id: Custom session ID (auto-generated if not provided).
            summary: Session summary text.
            namespace: Session namespace.
            metadata: Custom metadata (stored as additional_info).
            **options: Additional options.

        Returns:
            Created session info.
        """
        body: dict[str, Any] = {}
        if session_id:
            body["session_id"] = session_id
        if summary:
            body["summary"] = summary
        if namespace:
            body["namespace"] = namespace.values
        if metadata:
            body["additional_info"] = metadata

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/sessions",
                json=body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        return SessionInfo(
            id=result.get("session_id"),
            container_id=container_id,
            summary=summary,
            namespace=namespace.values if namespace else {},
            metadata=metadata or {},
        )

    async def get_session(
        self,
        container_id: str,
        session_id: str,
        include_messages: bool = False,
        message_limit: int = 50,
        **options: Any,
    ) -> SessionInfo | None:
        """Get session by ID.

        Args:
            container_id: Container ID.
            session_id: Session ID.
            include_messages: Whether to include session messages.
            message_limit: Max messages to include.
            **options: Additional options.

        Returns:
            Session info or None if not found.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.get(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/sessions/{session_id}",
                auth=self._auth,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

        session = SessionInfo(
            id=session_id,
            container_id=container_id,
            summary=data.get("summary"),
            namespace=data.get("namespace", {}),
            metadata=data.get("additional_info", {}),
            started_at=datetime.fromtimestamp(data["created_time"] / 1000)
            if data.get("created_time")
            else None,
        )

        if include_messages:
            session.messages = await self.get_working_memory(
                container_id=container_id,
                session_id=session_id,
                limit=message_limit,
            )

        return session

    async def list_sessions(
        self,
        container_id: str,
        namespace: Namespace | None = None,
        limit: int = 100,
        **options: Any,
    ) -> list[SessionInfo]:
        """List sessions.

        Args:
            container_id: Container ID.
            namespace: Optional namespace filter.
            limit: Maximum sessions to return.
            **options: Additional options.

        Returns:
            List of session info.
        """
        search_body: dict[str, Any] = {
            "query": {"match_all": {}},
            "size": limit,
        }

        if namespace:
            filters = [
                {"term": {f"namespace.{k}": v}} for k, v in namespace.values.items()
            ]
            search_body["query"] = {"bool": {"filter": filters}}

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/sessions/_search",
                json=search_body,
                auth=self._auth,
            )
            # Handle 500 error when sessions index doesn't exist yet
            # OpenSearch returns "index must not be null" when no sessions have been created
            if response.status_code == 500:
                try:
                    error_body = response.json()
                    error_reason = error_body.get("error", {}).get("reason", "")
                    if "index must not be null" in error_reason:
                        return []
                except Exception:
                    pass
            response.raise_for_status()
            result = response.json()

        sessions = []
        for hit in result.get("hits", {}).get("hits", []):
            source = hit["_source"]
            sessions.append(
                SessionInfo(
                    id=hit["_id"],
                    container_id=container_id,
                    summary=source.get("summary"),
                    namespace=source.get("namespace", {}),
                    metadata=source.get("additional_info", {}),
                    started_at=datetime.fromtimestamp(source["created_time"] / 1000)
                    if source.get("created_time")
                    else None,
                )
            )

        return sessions

    async def update_session(
        self,
        container_id: str,
        session_id: str,
        *,
        summary: str | None = None,
        metadata: dict[str, Any] | None = None,
        **options: Any,
    ) -> SessionInfo:
        """Update a session.

        Args:
            container_id: Container ID.
            session_id: Session ID.
            summary: Updated summary text.
            metadata: Updated metadata (additional_info).
            **options: Additional options.

        Returns:
            Updated session info.
        """
        body: dict[str, Any] = {}
        if summary is not None:
            body["summary"] = summary
        if metadata is not None:
            body["additional_info"] = metadata

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.put(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/sessions/{session_id}",
                json=body,
                auth=self._auth,
            )
            response.raise_for_status()
            data = response.json()

        return SessionInfo(
            id=session_id,
            container_id=container_id,
            summary=data.get("summary"),
            namespace=data.get("namespace", {}),
            metadata=data.get("additional_info", {}),
        )

    async def delete_session(
        self,
        container_id: str,
        session_id: str,
        **options: Any,
    ) -> bool:
        """Delete a session.

        Args:
            container_id: Container ID.
            session_id: Session ID.
            **options: Additional options.

        Returns:
            True if deleted, False if not found.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.delete(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/sessions/{session_id}",
                auth=self._auth,
            )
            if response.status_code == 404:
                return False
            response.raise_for_status()

        return True

    # === History (Audit Trail - Phase 6) ===

    async def get_history_entry(
        self,
        container_id: str,
        history_id: str,
        **options: Any,
    ) -> HistoryEntry | None:
        """Get a specific history entry by ID.

        History entries are READ-ONLY audit trail records.

        Args:
            container_id: Container ID.
            history_id: History entry ID.
            **options: Additional options.

        Returns:
            History entry or None if not found.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.get(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/history/{history_id}",
                auth=self._auth,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

        return self._parse_history_entry(history_id, container_id, data)

    async def list_history(
        self,
        container_id: str,
        memory_id: str | None = None,
        namespace: Namespace | None = None,
        limit: int = 100,
        **options: Any,
    ) -> list[HistoryEntry]:
        """List history entries.

        Args:
            container_id: Container ID.
            memory_id: Filter by specific memory ID.
            namespace: Filter by namespace.
            limit: Maximum entries to return.
            **options: Additional options.

        Returns:
            List of history entries (most recent first).
        """
        search_body: dict[str, Any] = {
            "query": {"match_all": {}},
            "size": limit,
            "sort": [{"created_time": "desc"}],
        }

        filters = []
        if memory_id:
            filters.append({"term": {"memory_id": memory_id}})
        if namespace:
            for key, value in namespace.values.items():
                filters.append({"term": {f"namespace.{key}": value}})

        if filters:
            search_body["query"] = {"bool": {"filter": filters}}

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/history/_search",
                json=search_body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        entries = []
        for hit in result.get("hits", {}).get("hits", []):
            entry = self._parse_history_entry(hit["_id"], container_id, hit["_source"])
            entries.append(entry)

        return entries

    # === Statistics (Phase 6) ===

    async def get_stats(
        self,
        container_id: str,
        **options: Any,
    ) -> MemoryStats:
        """Get container statistics.

        Args:
            container_id: Container ID.
            **options: Additional options.

        Returns:
            Memory statistics for the container.

        Raises:
            ContainerNotFoundError: If container doesn't exist.
        """
        container = await self.get_container(container_id)
        if not container:
            raise ContainerNotFoundError(container_id=container_id)

        # Count working memory
        working_count = await self._count_memories(container_id, MemoryType.WORKING)

        # Count long-term memory
        long_term_count = await self._count_memories(container_id, MemoryType.LONG_TERM)

        # Count sessions
        session_count = await self._count_memories(container_id, MemoryType.SESSIONS)

        # Get strategy breakdown
        breakdown: dict[MemoryStrategy, int] = {}
        for strategy in MemoryStrategy:
            count = await self._count_memories(
                container_id,
                MemoryType.LONG_TERM,
                strategy=strategy,
            )
            if count > 0:
                breakdown[strategy] = count

        return MemoryStats(
            container_id=container_id,
            container_name=container.name,
            working_memory_count=working_count,
            long_term_memory_count=long_term_count,
            session_count=session_count,
            strategies_breakdown=breakdown,
        )

    async def _count_memories(
        self,
        container_id: str,
        memory_type: MemoryType,
        strategy: MemoryStrategy | None = None,
    ) -> int:
        """Count memories by type and optional strategy.

        Args:
            container_id: Container ID.
            memory_type: Memory type to count.
            strategy: Optional strategy filter.

        Returns:
            Number of memories matching criteria.
        """
        search_body: dict[str, Any] = {
            "query": {"match_all": {}},
            "size": 0,
        }

        if strategy:
            search_body["query"] = {"term": {"strategy_type": strategy.value}}

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/memory_containers/{container_id}/memories/{memory_type.value}/_search",
                json=search_body,
                auth=self._auth,
            )
            if response.status_code == 404:
                return 0
            # Handle 500 error when sessions index doesn't exist yet
            # OpenSearch returns "index must not be null" when no sessions have been created
            if response.status_code == 500:
                try:
                    error_body = response.json()
                    error_reason = error_body.get("error", {}).get("reason", "")
                    if "index must not be null" in error_reason:
                        return 0
                except Exception:
                    pass
            response.raise_for_status()
            result = response.json()

        return result.get("hits", {}).get("total", {}).get("value", 0)

    # === Helpers ===

    def _parse_container_info(
        self, container_id: str, data: dict[str, Any]
    ) -> ContainerInfo:
        """Parse container info from API response.

        Args:
            container_id: Container ID.
            data: Raw API response data.

        Returns:
            Parsed ContainerInfo object.
        """
        config = data.get("configuration", {})
        strategies = [
            MemoryStrategy(s["type"]) for s in config.get("strategies", [])
        ]

        return ContainerInfo(
            id=container_id,
            name=data.get("name", ""),
            description=data.get("description"),
            strategies=strategies,
            embedding_model_id=config.get("embedding_model_id"),
            llm_model_id=config.get("llm_id"),
            created_at=datetime.fromtimestamp(data["created_time"] / 1000)
            if data.get("created_time")
            else None,
            updated_at=datetime.fromtimestamp(data["last_updated_time"] / 1000)
            if data.get("last_updated_time")
            else None,
        )

    def _parse_memory_entry(
        self,
        memory_id: str,
        data: dict[str, Any],
        memory_type: MemoryType,
    ) -> MemoryEntry:
        """Parse memory entry from API response.

        Handles both working memory and long-term memory formats.
        CRITICAL: Long-term memory content is in 'memory' field, not 'content'.

        Args:
            memory_id: Memory document ID.
            data: Raw API response data.
            memory_type: Type of memory being parsed.

        Returns:
            Parsed MemoryEntry object.
        """
        # Long-term memory has 'memory' field with extracted content
        # Working memory has 'messages' array with conversation
        if memory_type == MemoryType.LONG_TERM:
            content = data.get("memory", "")
            strategy = (
                MemoryStrategy(data["strategy_type"])
                if data.get("strategy_type")
                else None
            )
        else:
            # Working memory: extract text from messages
            messages = data.get("messages", [])
            content_parts = []
            for msg in messages:
                msg_content = msg.get("content", [])
                for part in msg_content:
                    if part.get("type") == "text":
                        content_parts.append(
                            f"[{msg.get('role', 'unknown')}]: {part.get('text', '')}"
                        )
            content = "\n".join(content_parts)
            strategy = None

        return MemoryEntry(
            id=memory_id,
            content=content,
            strategy=strategy,
            score=0.0,
            namespace=data.get("namespace", {}),
            created_at=datetime.fromtimestamp(data["created_time"] / 1000)
            if data.get("created_time")
            else None,
            metadata=data.get("tags", {}),
        )

    def _parse_history_entry(
        self,
        history_id: str,
        container_id: str,
        data: dict[str, Any],
    ) -> HistoryEntry:
        """Parse history entry from API response.

        Args:
            history_id: History entry ID.
            container_id: Parent container ID.
            data: Raw API response data.

        Returns:
            Parsed HistoryEntry object.
        """
        return HistoryEntry(
            id=history_id,
            memory_id=data.get("memory_id", ""),
            container_id=container_id,
            action=HistoryAction(data["action"])
            if data.get("action")
            else HistoryAction.ADD,
            owner_id=data.get("owner_id"),
            before=data.get("before"),
            after=data.get("after"),
            namespace=data.get("namespace", {}),
            tags=data.get("tags", {}),
            created_at=datetime.fromtimestamp(data["created_time"] / 1000)
            if data.get("created_time")
            else None,
        )
