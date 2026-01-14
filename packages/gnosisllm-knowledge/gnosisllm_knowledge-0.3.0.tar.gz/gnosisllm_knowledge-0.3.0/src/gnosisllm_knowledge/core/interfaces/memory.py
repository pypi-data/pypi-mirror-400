"""Memory protocols - Interface Segregation Principle."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from datetime import datetime

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
        StoreRequest,
        StoreResult,
    )


@runtime_checkable
class IMemoryContainerManager(Protocol):
    """Protocol for memory container management.

    Responsible for CRUD operations on memory containers.
    """

    async def create_container(
        self,
        config: ContainerConfig,
        **options: Any,
    ) -> ContainerInfo:
        """Create a new memory container.

        Args:
            config: Container configuration.
            **options: Backend-specific options.

        Returns:
            Created container info.
        """
        ...

    async def get_container(
        self,
        container_id: str,
        **options: Any,
    ) -> ContainerInfo | None:
        """Get container by ID.

        Args:
            container_id: Container ID.
            **options: Backend-specific options.

        Returns:
            Container info or None if not found.
        """
        ...

    async def list_containers(
        self,
        limit: int = 100,
        **options: Any,
    ) -> list[ContainerInfo]:
        """List all containers.

        Args:
            limit: Maximum number to return.
            **options: Backend-specific options.

        Returns:
            List of container info.
        """
        ...

    async def update_container(
        self,
        container_id: str,
        config: ContainerConfig,
        **options: Any,
    ) -> ContainerInfo:
        """Update container configuration.

        Args:
            container_id: Container ID.
            config: Updated configuration.
            **options: Backend-specific options.

        Returns:
            Updated container info.
        """
        ...

    async def delete_container(
        self,
        container_id: str,
        **options: Any,
    ) -> bool:
        """Delete a container.

        Args:
            container_id: Container ID.
            **options: Backend-specific options.

        Returns:
            True if deleted.
        """
        ...


@runtime_checkable
class IMemoryStore(Protocol):
    """Protocol for storing memories.

    Responsible for adding memories to containers.
    """

    async def store(
        self,
        container_id: str,
        request: StoreRequest,
        **options: Any,
    ) -> StoreResult:
        """Store memory in container.

        Args:
            container_id: Target container ID.
            request: Store request with messages/data.
            **options: Backend-specific options.

        Returns:
            Store result with IDs and counts.
        """
        ...

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
            limit: Maximum messages.
            offset: Skip count.
            **options: Backend-specific options.

        Returns:
            List of messages.
        """
        ...

    async def clear_working_memory(
        self,
        container_id: str,
        session_id: str | None = None,
        namespace: Namespace | None = None,
        **options: Any,
    ) -> int:
        """Clear working memory.

        Args:
            container_id: Container ID.
            session_id: Optional session filter.
            namespace: Optional namespace filter.
            **options: Backend-specific options.

        Returns:
            Number of messages deleted.
        """
        ...


@runtime_checkable
class IMemoryRetriever(Protocol):
    """Protocol for retrieving/searching memories.

    Responsible for semantic search over long-term memory.
    """

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
        """Semantic search over long-term memories.

        Args:
            container_id: Container ID.
            query: Search query.
            namespace: Optional namespace filter.
            strategies: Filter by strategies.
            min_score: Minimum similarity score.
            limit: Maximum results.
            after: Filter by created after.
            before: Filter by created before.
            **options: Backend-specific options.

        Returns:
            Recall result with memory entries.
        """
        ...

    async def get_memory(
        self,
        container_id: str,
        memory_id: str,
        memory_type: MemoryType,
        **options: Any,
    ) -> MemoryEntry | None:
        """Get specific memory by ID.

        For sessions, use ISessionManager.get_session().
        For history, use IHistoryRetriever.get_history_entry().

        Args:
            container_id: Container ID.
            memory_id: Memory document ID.
            memory_type: Memory type (WORKING or LONG_TERM).
            **options: Backend-specific options.

        Returns:
            Memory entry or None.
        """
        ...

    async def delete_memory(
        self,
        container_id: str,
        memory_id: str,
        memory_type: MemoryType,
        **options: Any,
    ) -> bool:
        """Delete specific memory.

        Args:
            container_id: Container ID.
            memory_id: Memory document ID.
            memory_type: Memory type (WORKING or LONG_TERM).
            **options: Backend-specific options.

        Returns:
            True if deleted.
        """
        ...

    async def delete_memories(
        self,
        container_id: str,
        session_id: str | None = None,
        namespace: Namespace | None = None,
        before: datetime | None = None,
        **options: Any,
    ) -> int:
        """Delete memories by filter.

        Args:
            container_id: Container ID.
            session_id: Filter by session.
            namespace: Filter by namespace.
            before: Delete before timestamp.
            **options: Backend-specific options.

        Returns:
            Number deleted.
        """
        ...

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
            **options: Backend-specific options.

        Returns:
            Updated memory entry.
        """
        ...

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
            **options: Backend-specific options.

        Returns:
            Number of documents deleted.
        """
        ...


@runtime_checkable
class IHistoryRetriever(Protocol):
    """Protocol for retrieving memory history (audit trail). READ-ONLY.

    History is READ-ONLY. Updates and deletes are NOT supported.
    """

    async def get_history_entry(
        self,
        container_id: str,
        history_id: str,
        **options: Any,
    ) -> HistoryEntry | None:
        """Get a specific history entry by ID.

        Args:
            container_id: Container ID.
            history_id: History entry ID.
            **options: Backend-specific options.

        Returns:
            History entry or None.
        """
        ...

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
            **options: Backend-specific options.

        Returns:
            List of history entries.
        """
        ...


@runtime_checkable
class ISessionManager(Protocol):
    """Protocol for session management.

    Responsible for session lifecycle operations.
    """

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
            **options: Backend-specific options.

        Returns:
            Created session info.
        """
        ...

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
            include_messages: Include session messages.
            message_limit: Max messages to include.
            **options: Backend-specific options.

        Returns:
            Session info or None.
        """
        ...

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
            namespace: Filter by namespace.
            limit: Maximum to return.
            **options: Backend-specific options.

        Returns:
            List of session info.
        """
        ...

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

        Use this to update session summary or metadata.
        Note: There is no explicit "end session" API in OpenSearch.

        Args:
            container_id: Container ID.
            session_id: Session ID.
            summary: Updated summary text.
            metadata: Updated metadata (additional_info).
            **options: Backend-specific options.

        Returns:
            Updated session info.
        """
        ...

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
            **options: Backend-specific options.

        Returns:
            True if deleted.
        """
        ...


@runtime_checkable
class IMemoryStats(Protocol):
    """Protocol for memory statistics."""

    async def get_stats(
        self,
        container_id: str,
        **options: Any,
    ) -> MemoryStats:
        """Get container statistics.

        Args:
            container_id: Container ID.
            **options: Backend-specific options.

        Returns:
            Memory statistics.
        """
        ...
