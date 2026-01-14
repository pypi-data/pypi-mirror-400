"""High-level Memory API facade."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from gnosisllm_knowledge.backends.opensearch.memory.client import OpenSearchMemoryClient
from gnosisllm_knowledge.backends.opensearch.memory.config import MemoryConfig
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
    PayloadType,
    RecallResult,
    SessionInfo,
    StoreRequest,
    StoreResult,
    StrategyConfig,
)
from gnosisllm_knowledge.core.events.emitter import EventEmitter

logger = logging.getLogger(__name__)


class Memory:
    """High-level facade for Agentic Memory operations.

    Provides a developer-friendly interface for storing, recalling, and
    managing conversational memories using OpenSearch Agentic Memory.

    Example:
        ```python
        from gnosisllm_knowledge import Memory, MemoryStrategy, StrategyConfig, Message

        # Quick start from environment
        memory = Memory.from_env()

        # Create a container with strategy-to-namespace mapping
        container = await memory.create_container(
            name="agent-memory",
            strategies=[
                StrategyConfig(type=MemoryStrategy.SEMANTIC, namespace=["user_id"]),
                StrategyConfig(type=MemoryStrategy.USER_PREFERENCE, namespace=["user_id"]),
                StrategyConfig(type=MemoryStrategy.SUMMARY, namespace=["session_id"]),
            ],
        )

        # Store conversation
        await memory.store(
            container_id=container.id,
            messages=[
                Message(role="user", content="I'm Sarah Chen, VP of Engineering"),
                Message(role="assistant", content="Hello Sarah!"),
            ],
            user_id="sarah-123",
            infer=True,
        )

        # Recall memories
        result = await memory.recall(
            container_id=container.id,
            query="user information",
            user_id="sarah-123",
        )
        for entry in result.items:
            print(f"[{entry.strategy}] {entry.content}")
        ```
    """

    def __init__(
        self,
        *,
        client: OpenSearchMemoryClient,
        config: MemoryConfig,
        events: EventEmitter | None = None,
    ) -> None:
        """Initialize Memory facade.

        Args:
            client: OpenSearch memory client.
            config: Memory configuration.
            events: Optional event emitter.
        """
        self._client = client
        self._config = config
        self._events = events or EventEmitter()

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
        llm_model_id: str | None = None,
        embedding_model_id: str | None = None,
        llm_result_path: str = "$.choices[0].message.content",
        config: MemoryConfig | None = None,
        **kwargs: Any,
    ) -> Memory:
        """Create Memory instance with OpenSearch backend.

        Args:
            host: OpenSearch host.
            port: OpenSearch port.
            username: Optional username.
            password: Optional password.
            use_ssl: Use SSL connection.
            verify_certs: Verify SSL certificates.
            llm_model_id: LLM model ID for inference.
            embedding_model_id: Embedding model ID.
            llm_result_path: JSONPath to extract LLM response.
            config: Optional MemoryConfig (overrides other params).
            **kwargs: Additional config options.

        Returns:
            Configured Memory instance.
        """
        if config is None:
            config = MemoryConfig(
                host=host,
                port=port,
                username=username,
                password=password,
                use_ssl=use_ssl,
                verify_certs=verify_certs,
                llm_model_id=llm_model_id,
                embedding_model_id=embedding_model_id,
                llm_result_path=llm_result_path,
                **kwargs,
            )

        client = OpenSearchMemoryClient(config)
        return cls(client=client, config=config)

    @classmethod
    def from_env(cls) -> Memory:
        """Create Memory instance from environment variables.

        Environment Variables:
            OPENSEARCH_HOST: OpenSearch host (default: localhost)
            OPENSEARCH_PORT: OpenSearch port (default: 9200)
            OPENSEARCH_USERNAME: Username
            OPENSEARCH_PASSWORD: Password
            OPENSEARCH_USE_SSL: Use SSL (default: false)
            OPENSEARCH_VERIFY_CERTS: Verify certs (default: true)
            OPENSEARCH_LLM_MODEL_ID: LLM model ID for inference
            OPENSEARCH_EMBEDDING_MODEL_ID: Embedding model ID
            OPENSEARCH_LLM_RESULT_PATH: JSONPath for LLM response

        Returns:
            Configured Memory instance.
        """
        config = MemoryConfig.from_env()
        client = OpenSearchMemoryClient(config)
        return cls(client=client, config=config)

    @classmethod
    def from_config(cls, config: MemoryConfig) -> Memory:
        """Create Memory instance from configuration.

        Args:
            config: Memory configuration.

        Returns:
            Configured Memory instance.
        """
        client = OpenSearchMemoryClient(config)
        return cls(client=client, config=config)

    @property
    def events(self) -> EventEmitter:
        """Get the event emitter."""
        return self._events

    @property
    def is_configured(self) -> bool:
        """Check if memory is properly configured for inference.

        Returns:
            True if both LLM and embedding models are configured.
        """
        return self._config.is_configured

    # === Container Management ===

    async def create_container(
        self,
        name: str,
        *,
        strategies: list[StrategyConfig],
        description: str | None = None,
        llm_model_id: str | None = None,
        embedding_model_id: str | None = None,
        embedding_dimension: int = 1536,
        **options: Any,
    ) -> ContainerInfo:
        """Create a new memory container.

        Args:
            name: Container name.
            strategies: Strategy configurations with namespace scoping (REQUIRED).
            description: Optional description.
            llm_model_id: Override LLM model ID.
            embedding_model_id: Override embedding model ID.
            embedding_dimension: Embedding dimension.
            **options: Additional options.

        Returns:
            Created container info.

        Raises:
            ValueError: If strategies is empty.

        Example:
            ```python
            container = await memory.create_container(
                name="agent-memory",
                strategies=[
                    StrategyConfig(type=MemoryStrategy.SEMANTIC, namespace=["user_id"]),
                    StrategyConfig(type=MemoryStrategy.SUMMARY, namespace=["session_id"]),
                ],
            )
            ```
        """
        if not strategies:
            raise ValueError(
                "strategies is required - each strategy must be scoped to namespace fields"
            )

        container_config = ContainerConfig(
            name=name,
            description=description,
            strategies=strategies,
            llm_model_id=llm_model_id or self._config.llm_model_id,
            embedding_model_id=embedding_model_id or self._config.embedding_model_id,
            embedding_dimension=embedding_dimension,
            llm_result_path=self._config.llm_result_path,
        )

        return await self._client.create_container(container_config, **options)

    async def get_container(self, container_id: str) -> ContainerInfo | None:
        """Get container by ID.

        Args:
            container_id: Container ID.

        Returns:
            Container info or None if not found.
        """
        return await self._client.get_container(container_id)

    async def list_containers(self, limit: int = 100) -> list[ContainerInfo]:
        """List all containers.

        Args:
            limit: Maximum number of containers to return.

        Returns:
            List of container info.
        """
        return await self._client.list_containers(limit)

    async def delete_container(self, container_id: str) -> bool:
        """Delete a container.

        Args:
            container_id: Container ID.

        Returns:
            True if deleted, False if not found.
        """
        return await self._client.delete_container(container_id)

    async def update_container(
        self,
        container_id: str,
        *,
        description: str | None = None,
        strategies: list[StrategyConfig] | None = None,
        **options: Any,
    ) -> ContainerInfo:
        """Update a container.

        Args:
            container_id: Container ID.
            description: Updated description.
            strategies: Updated strategy configurations.
            **options: Additional options.

        Returns:
            Updated container info.
        """
        config = ContainerConfig(
            name="",  # Not updated
            description=description,
            strategies=strategies or [],
        )
        return await self._client.update_container(container_id, config, **options)

    # === Memory Storage ===

    async def store(
        self,
        container_id: str,
        messages: list[Message] | None = None,
        *,
        structured_data: dict[str, Any] | None = None,
        namespace: Namespace | dict[str, str] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        agent_id: str | None = None,
        infer: bool = True,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **options: Any,
    ) -> StoreResult:
        """Store conversation or data with optional LLM inference.

        Which strategies run is determined by:
        1. How the container was configured (strategy -> namespace field mapping)
        2. Which namespace fields are present in the request

        Args:
            container_id: Target container ID.
            messages: Conversation messages.
            structured_data: Structured data (alternative to messages).
            namespace: Full namespace or dict.
            user_id: Shorthand for namespace user_id.
            session_id: Shorthand for namespace session_id.
            agent_id: Shorthand for namespace agent_id.
            infer: Enable LLM inference for fact extraction.
            metadata: Custom metadata.
            tags: Custom tags.
            **options: Additional options.

        Returns:
            Store result with IDs and counts.

        Example:
            ```python
            # Store with namespace shorthand
            await memory.store(
                container_id=container.id,
                messages=[
                    Message(role="user", content="I prefer dark mode"),
                    Message(role="assistant", content="Dark mode enabled!"),
                ],
                user_id="alice-123",
                infer=True,
            )

            # Store with full namespace
            await memory.store(
                container_id=container.id,
                messages=messages,
                namespace={"user_id": "alice", "org_id": "acme"},
            )
            ```
        """
        # Build namespace
        if isinstance(namespace, dict):
            ns = Namespace(namespace)
        elif namespace is None:
            ns = Namespace()
        else:
            ns = namespace

        # Add shorthand values
        if user_id:
            ns["user_id"] = user_id
        if session_id:
            ns["session_id"] = session_id
        if agent_id:
            ns["agent_id"] = agent_id

        # Determine payload type
        payload_type = PayloadType.CONVERSATIONAL if messages else PayloadType.DATA

        request = StoreRequest(
            messages=messages,
            structured_data=structured_data,
            namespace=ns,
            payload_type=payload_type,
            infer=infer,
            metadata=metadata or {},
            tags=tags or {},
        )

        return await self._client.store(container_id, request, **options)

    # === Memory Recall ===

    async def recall(
        self,
        container_id: str,
        query: str,
        *,
        namespace: Namespace | dict[str, str] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        agent_id: str | None = None,
        strategies: list[MemoryStrategy] | None = None,
        min_score: float | None = None,
        limit: int = 10,
        after: datetime | None = None,
        before: datetime | None = None,
        **options: Any,
    ) -> RecallResult:
        """Semantic search over long-term memories.

        Args:
            container_id: Container ID.
            query: Search query text.
            namespace: Full namespace or dict.
            user_id: Shorthand for namespace user_id.
            session_id: Shorthand for namespace session_id.
            agent_id: Shorthand for namespace agent_id.
            strategies: Filter by specific strategies.
            min_score: Minimum similarity score.
            limit: Maximum results.
            after: Filter by created after timestamp.
            before: Filter by created before timestamp.
            **options: Additional options.

        Returns:
            Recall result with memory entries.

        Example:
            ```python
            result = await memory.recall(
                container_id=container.id,
                query="user preferences",
                user_id="alice-123",
                limit=5,
            )
            for entry in result.items:
                print(f"{entry.content} (score: {entry.score})")
            ```
        """
        # Build namespace
        if isinstance(namespace, dict):
            ns = Namespace(namespace)
        elif namespace is None:
            ns = Namespace()
        else:
            ns = namespace

        if user_id:
            ns["user_id"] = user_id
        if session_id:
            ns["session_id"] = session_id
        if agent_id:
            ns["agent_id"] = agent_id

        return await self._client.recall(
            container_id=container_id,
            query=query,
            namespace=ns if ns.values else None,
            strategies=strategies,
            min_score=min_score,
            limit=limit,
            after=after,
            before=before,
            **options,
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
            **options: Additional options.

        Returns:
            Memory entry or None if not found.
        """
        return await self._client.get_memory(
            container_id=container_id,
            memory_id=memory_id,
            memory_type=memory_type,
            **options,
        )

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
            memory_type: Memory type (WORKING or LONG_TERM).
            **options: Additional options.

        Returns:
            True if deleted, False if not found.
        """
        return await self._client.delete_memory(
            container_id=container_id,
            memory_id=memory_id,
            memory_type=memory_type,
            **options,
        )

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
        """
        return await self._client.update_memory(
            container_id=container_id,
            memory_id=memory_id,
            memory_type=memory_type,
            memory=memory,
            tags=tags,
            **options,
        )

    async def clear_working_memory(
        self,
        container_id: str,
        session_id: str | None = None,
        namespace: Namespace | dict[str, str] | None = None,
        user_id: str | None = None,
        **options: Any,
    ) -> int:
        """Clear working memory.

        Args:
            container_id: Container ID.
            session_id: Optional session filter.
            namespace: Full namespace or dict.
            user_id: Shorthand for namespace user_id.
            **options: Additional options.

        Returns:
            Number of messages deleted.
        """
        if isinstance(namespace, dict):
            ns = Namespace(namespace)
        elif namespace is None:
            ns = Namespace()
        else:
            ns = namespace

        if user_id:
            ns["user_id"] = user_id

        return await self._client.clear_working_memory(
            container_id=container_id,
            session_id=session_id,
            namespace=ns if ns.values else None,
            **options,
        )

    async def delete_memories(
        self,
        container_id: str,
        session_id: str | None = None,
        namespace: Namespace | dict[str, str] | None = None,
        user_id: str | None = None,
        before: datetime | None = None,
        memory_type: MemoryType = MemoryType.WORKING,
        **options: Any,
    ) -> int:
        """Delete memories by filter.

        Args:
            container_id: Container ID.
            session_id: Optional session filter.
            namespace: Full namespace or dict.
            user_id: Shorthand for namespace user_id.
            before: Delete memories created before this timestamp.
            memory_type: Memory type to delete (default: WORKING).
            **options: Additional options.

        Returns:
            Number of memories deleted.
        """
        if isinstance(namespace, dict):
            ns = Namespace(namespace)
        elif namespace is None:
            ns = Namespace()
        else:
            ns = namespace

        if user_id:
            ns["user_id"] = user_id

        return await self._client.delete_memories(
            container_id=container_id,
            session_id=session_id,
            namespace=ns if ns.values else None,
            before=before,
            memory_type=memory_type,
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

        Args:
            container_id: Container ID.
            memory_type: Memory type to delete from.
            query: OpenSearch Query DSL query.
            **options: Additional options.

        Returns:
            Number of documents deleted.

        Example:
            ```python
            # Delete all memories for a user older than 30 days
            await memory.delete_by_query(
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
        """
        return await self._client.delete_by_query(
            container_id=container_id,
            memory_type=memory_type,
            query=query,
            **options,
        )

    # === Working Memory ===

    async def get_working_memory(
        self,
        container_id: str,
        session_id: str | None = None,
        *,
        namespace: Namespace | dict[str, str] | None = None,
        limit: int = 50,
        offset: int = 0,
        **options: Any,
    ) -> list[Message]:
        """Get working memory messages.

        Args:
            container_id: Container ID.
            session_id: Optional session filter.
            namespace: Optional namespace filter.
            limit: Maximum messages to return.
            offset: Number of messages to skip.
            **options: Additional options.

        Returns:
            List of messages.
        """
        ns = Namespace(namespace) if isinstance(namespace, dict) else namespace

        return await self._client.get_working_memory(
            container_id=container_id,
            session_id=session_id,
            namespace=ns,
            limit=limit,
            offset=offset,
            **options,
        )

    # === Session Management ===

    async def create_session(
        self,
        container_id: str,
        *,
        session_id: str | None = None,
        summary: str | None = None,
        namespace: Namespace | dict[str, str] | None = None,
        user_id: str | None = None,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        **options: Any,
    ) -> SessionInfo:
        """Create a new session.

        Args:
            container_id: Container ID.
            session_id: Custom session ID (auto-generated if not provided).
            summary: Session summary text.
            namespace: Full namespace or dict.
            user_id: Shorthand for namespace user_id.
            agent_id: Shorthand for namespace agent_id.
            metadata: Custom metadata.
            **options: Additional options.

        Returns:
            Created session info.
        """
        if isinstance(namespace, dict):
            ns = Namespace(namespace)
        elif namespace is None:
            ns = Namespace()
        else:
            ns = namespace

        if user_id:
            ns["user_id"] = user_id
        if agent_id:
            ns["agent_id"] = agent_id

        return await self._client.create_session(
            container_id=container_id,
            session_id=session_id,
            summary=summary,
            namespace=ns if ns.values else None,
            metadata=metadata,
            **options,
        )

    async def get_session(
        self,
        container_id: str,
        session_id: str,
        *,
        include_messages: bool = False,
        message_limit: int = 50,
        **options: Any,
    ) -> SessionInfo | None:
        """Get session by ID.

        Args:
            container_id: Container ID.
            session_id: Session ID.
            include_messages: Include session messages.
            message_limit: Max messages to include.
            **options: Additional options.

        Returns:
            Session info or None if not found.
        """
        return await self._client.get_session(
            container_id=container_id,
            session_id=session_id,
            include_messages=include_messages,
            message_limit=message_limit,
            **options,
        )

    async def list_sessions(
        self,
        container_id: str,
        *,
        namespace: Namespace | dict[str, str] | None = None,
        user_id: str | None = None,
        limit: int = 100,
        **options: Any,
    ) -> list[SessionInfo]:
        """List sessions.

        Args:
            container_id: Container ID.
            namespace: Full namespace or dict.
            user_id: Shorthand for namespace user_id.
            limit: Maximum sessions to return.
            **options: Additional options.

        Returns:
            List of session info.
        """
        if isinstance(namespace, dict):
            ns = Namespace(namespace)
        elif namespace is None:
            ns = Namespace()
        else:
            ns = namespace

        if user_id:
            ns["user_id"] = user_id

        return await self._client.list_sessions(
            container_id=container_id,
            namespace=ns if ns.values else None,
            limit=limit,
            **options,
        )

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
            metadata: Updated metadata.
            **options: Additional options.

        Returns:
            Updated session info.
        """
        return await self._client.update_session(
            container_id=container_id,
            session_id=session_id,
            summary=summary,
            metadata=metadata,
            **options,
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
        return await self._client.delete_session(
            container_id=container_id,
            session_id=session_id,
            **options,
        )

    # === History (Audit Trail) ===

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
        return await self._client.get_history_entry(
            container_id=container_id,
            history_id=history_id,
            **options,
        )

    async def list_history(
        self,
        container_id: str,
        memory_id: str | None = None,
        namespace: Namespace | dict[str, str] | None = None,
        limit: int = 100,
        **options: Any,
    ) -> list[HistoryEntry]:
        """List history entries.

        Args:
            container_id: Container ID.
            memory_id: Filter by specific memory ID.
            namespace: Optional namespace filter.
            limit: Maximum entries to return.
            **options: Additional options.

        Returns:
            List of history entries (most recent first).
        """
        ns = Namespace(namespace) if isinstance(namespace, dict) else namespace

        return await self._client.list_history(
            container_id=container_id,
            memory_id=memory_id,
            namespace=ns,
            limit=limit,
            **options,
        )

    # === Statistics ===

    async def get_stats(self, container_id: str) -> MemoryStats:
        """Get container statistics.

        Args:
            container_id: Container ID.

        Returns:
            Memory statistics for the container.
        """
        return await self._client.get_stats(container_id)

    # === Cleanup ===

    async def close(self) -> None:
        """Close connections and clean up resources."""
        # Currently no resources to clean up, but method is here for future use
        pass
