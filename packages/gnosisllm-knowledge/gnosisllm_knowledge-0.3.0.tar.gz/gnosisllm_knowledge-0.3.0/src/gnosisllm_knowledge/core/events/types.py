"""Event type definitions for the knowledge module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Types of events in the knowledge system.

    Events are organized by category:
    - Loading events: Document and content loading
    - Indexing events: Document indexing operations
    - Streaming events: Streaming pipeline progress
    - Search events: Search and retrieval operations
    - Agentic events: AI-powered operations
    - Setup events: Backend setup operations
    - Resilience events: Fault tolerance events
    - Health events: Health check events
    """

    # Loading events
    LOAD_STARTED = "load_started"
    LOAD_PROGRESS = "load_progress"
    DOCUMENT_FETCHED = "document_fetched"
    DOCUMENT_CHUNKED = "document_chunked"
    DOCUMENT_LOADED = "document_loaded"
    DOCUMENT_VALIDATED = "document_validated"
    DOCUMENT_REJECTED = "document_rejected"
    LOAD_COMPLETED = "load_completed"
    LOAD_FAILED = "load_failed"
    SITEMAP_DISCOVERED = "sitemap_discovered"

    # Streaming events
    STREAMING_PROGRESS = "streaming_progress"
    URL_BATCH_PROCESSED = "url_batch_processed"
    STREAMING_COMPLETED = "streaming_completed"

    # Indexing events
    INDEX_STARTED = "index_started"
    DOCUMENT_INDEXED = "document_indexed"
    DOCUMENT_INDEX_FAILED = "document_index_failed"
    BATCH_STARTED = "batch_started"
    BATCH_COMPLETED = "batch_completed"
    INDEX_COMPLETED = "index_completed"
    INDEX_FAILED = "index_failed"

    # Search events
    SEARCH_STARTED = "search_started"
    SEARCH_CACHE_HIT = "search_cache_hit"
    SEARCH_CACHE_MISS = "search_cache_miss"
    EMBEDDING_GENERATED = "embedding_generated"
    EMBEDDING_CACHE_HIT = "embedding_cache_hit"
    SEARCH_COMPLETED = "search_completed"
    SEARCH_FAILED = "search_failed"

    # Agentic events
    AGENT_STARTED = "agent_started"
    AGENT_STEP = "agent_step"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"

    # Setup events
    SETUP_STARTED = "setup_started"
    SETUP_STEP_STARTED = "setup_step_started"
    SETUP_STEP_COMPLETED = "setup_step_completed"
    SETUP_STEP_FAILED = "setup_step_failed"
    SETUP_COMPLETED = "setup_completed"

    # Resilience events
    RETRY_ATTEMPT = "retry_attempt"
    CIRCUIT_BREAKER_OPENED = "circuit_breaker_opened"
    CIRCUIT_BREAKER_CLOSED = "circuit_breaker_closed"
    CIRCUIT_BREAKER_HALF_OPEN = "circuit_breaker_half_open"
    FALLBACK_TRIGGERED = "fallback_triggered"

    # Health events
    HEALTH_CHECK_STARTED = "health_check_started"
    HEALTH_CHECK_COMPLETED = "health_check_completed"
    HEALTH_DEGRADED = "health_degraded"
    HEALTH_RECOVERED = "health_recovered"

    # Error events
    ERROR = "error"


@dataclass
class Event:
    """Base event class.

    Attributes:
        event_type: The type of event.
        timestamp: When the event occurred.
        data: Additional event data.
        account_id: Account ID for multi-tenant context.
        user_id: User ID if applicable.
        request_id: Request ID for tracing.
        trace_id: Distributed trace ID.
        span_id: Distributed trace span ID.
    """

    event_type: EventType = EventType.ERROR  # Default, usually overridden
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] = field(default_factory=dict)

    # Context
    account_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None

    # Tracing
    trace_id: str | None = None
    span_id: str | None = None

    def with_context(
        self,
        account_id: str | None = None,
        user_id: str | None = None,
        request_id: str | None = None,
    ) -> Event:
        """Create a copy with context information."""
        return Event(
            event_type=self.event_type,
            timestamp=self.timestamp,
            data=self.data.copy(),
            account_id=account_id or self.account_id,
            user_id=user_id or self.user_id,
            request_id=request_id or self.request_id,
            trace_id=self.trace_id,
            span_id=self.span_id,
        )


@dataclass
class DocumentLoadedEvent(Event):
    """Event emitted when a document is loaded."""

    url: str = ""
    source: str = ""
    chunks_count: int = 0
    content_length: int = 0

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.DOCUMENT_LOADED
        self.data = {
            "url": self.url,
            "source": self.source,
            "chunks_count": self.chunks_count,
            "content_length": self.content_length,
        }


@dataclass
class DocumentIndexedEvent(Event):
    """Event emitted when a document is indexed."""

    doc_id: str = ""
    index_name: str = ""
    success: bool = True
    error_message: str | None = None

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.DOCUMENT_INDEXED
        self.data = {
            "doc_id": self.doc_id,
            "index_name": self.index_name,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class SitemapDiscoveryEvent(Event):
    """Event emitted when URLs are discovered from a sitemap."""

    sitemap_url: str = ""
    urls_discovered: int = 0
    depth: int = 0
    total_urls: int = 0

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.SITEMAP_DISCOVERED
        self.data = {
            "sitemap_url": self.sitemap_url,
            "urls_discovered": self.urls_discovered,
            "depth": self.depth,
            "total_urls": self.total_urls,
        }


@dataclass
class BatchStartedEvent(Event):
    """Event emitted when a batch operation starts."""

    batch_index: int = 0
    batch_size: int = 0
    total_batches: int = 0

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.BATCH_STARTED
        self.data = {
            "batch_index": self.batch_index,
            "batch_size": self.batch_size,
            "total_batches": self.total_batches,
        }


@dataclass
class BatchCompletedEvent(Event):
    """Event emitted when a batch operation completes."""

    batch_index: int = 0
    success_count: int = 0
    failure_count: int = 0
    duration_ms: float = 0.0

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.BATCH_COMPLETED
        self.data = {
            "batch_index": self.batch_index,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "duration_ms": self.duration_ms,
        }


@dataclass
class StreamingProgressEvent(Event):
    """Progress event for streaming operations.

    Emitted periodically during streaming pipeline execution to
    provide visibility into progress.
    """

    urls_discovered: int = 0
    urls_processed: int = 0
    documents_indexed: int = 0
    documents_failed: int = 0
    phase: str = "unknown"
    memory_mb: float | None = None

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.STREAMING_PROGRESS
        self.data = {
            "urls_discovered": self.urls_discovered,
            "urls_processed": self.urls_processed,
            "documents_indexed": self.documents_indexed,
            "documents_failed": self.documents_failed,
            "phase": self.phase,
            "memory_mb": self.memory_mb,
        }


@dataclass
class UrlBatchProcessedEvent(Event):
    """Event emitted when a batch of URLs is processed."""

    batch_index: int = 0
    urls_in_batch: int = 0
    documents_created: int = 0
    total_urls_processed: int = 0

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.URL_BATCH_PROCESSED
        self.data = {
            "batch_index": self.batch_index,
            "urls_in_batch": self.urls_in_batch,
            "documents_created": self.documents_created,
            "total_urls_processed": self.total_urls_processed,
        }


@dataclass
class StreamingCompletedEvent(Event):
    """Event emitted when streaming pipeline completes."""

    total_urls: int = 0
    total_documents: int = 0
    indexed_count: int = 0
    failed_count: int = 0
    duration_ms: float = 0.0

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = EventType.STREAMING_COMPLETED
        self.data = {
            "total_urls": self.total_urls,
            "total_documents": self.total_documents,
            "indexed_count": self.indexed_count,
            "failed_count": self.failed_count,
            "duration_ms": self.duration_ms,
        }
