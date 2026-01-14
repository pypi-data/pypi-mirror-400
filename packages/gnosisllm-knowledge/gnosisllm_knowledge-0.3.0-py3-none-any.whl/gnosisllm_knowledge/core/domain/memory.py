"""Memory domain models for Agentic Memory."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class MemoryStrategy(str, Enum):
    """Memory extraction strategies.

    Attributes:
        SEMANTIC: General facts and knowledge extraction.
        USER_PREFERENCE: User preferences and choices.
        SUMMARY: Conversation summaries.
    """

    SEMANTIC = "SEMANTIC"
    USER_PREFERENCE = "USER_PREFERENCE"
    SUMMARY = "SUMMARY"


class MemoryType(str, Enum):
    """Memory storage types.

    Attributes:
        WORKING: Raw conversation messages (short-term).
        LONG_TERM: Extracted facts with embeddings.
        SESSIONS: Session metadata.
        HISTORY: Audit trail of operations.
    """

    WORKING = "working"
    LONG_TERM = "long-term"
    SESSIONS = "sessions"
    HISTORY = "history"


class PayloadType(str, Enum):
    """Memory payload types.

    Attributes:
        CONVERSATIONAL: Conversation messages.
        DATA: Structured data (agent state, traces).
    """

    CONVERSATIONAL = "conversational"
    DATA = "data"


class EmbeddingModelType(str, Enum):
    """Embedding model types supported by OpenSearch.

    Attributes:
        TEXT_EMBEDDING: Dense vector embeddings (default).
        SPARSE_ENCODING: Sparse vector encoding.
    """

    TEXT_EMBEDDING = "TEXT_EMBEDDING"
    SPARSE_ENCODING = "SPARSE_ENCODING"


class HistoryAction(str, Enum):
    """History audit trail action types.

    Attributes:
        ADD: Memory was added.
        UPDATE: Memory was updated.
        DELETE: Memory was deleted.
    """

    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass
class StrategyConfig:
    """Configuration for a memory extraction strategy.

    Each strategy MUST be scoped to namespace fields.
    When storing memory, only strategies whose namespace fields are
    present in the request will run.

    Attributes:
        type: Strategy type (SEMANTIC, USER_PREFERENCE, SUMMARY).
        namespace: Fields used to scope this strategy (REQUIRED).
        llm_result_path: JSONPath to extract LLM response.
        system_prompt: Optional custom system prompt.
        llm_id: Optional strategy-specific LLM override.
    """

    type: MemoryStrategy
    namespace: list[str]  # REQUIRED - no default
    llm_result_path: str | None = None
    system_prompt: str | None = None
    llm_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to OpenSearch API format."""
        config: dict[str, Any] = {}
        if self.llm_result_path:
            config["llm_result_path"] = self.llm_result_path
        if self.system_prompt:
            config["system_prompt"] = self.system_prompt
        if self.llm_id:
            config["llm_id"] = self.llm_id

        return {
            "type": self.type.value,
            "namespace": self.namespace,
            "configuration": config,
        }


@dataclass
class IndexSettings:
    """Index-level settings for memory container indexes.

    Attributes:
        number_of_shards: Number of shards for the index.
        number_of_replicas: Number of replicas for the index.
    """

    number_of_shards: int = 1
    number_of_replicas: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to OpenSearch index settings format."""
        return {
            "index": {
                "number_of_shards": str(self.number_of_shards),
                "number_of_replicas": str(self.number_of_replicas),
            }
        }


@dataclass
class ContainerIndexSettings:
    """Settings for all memory container indexes.

    Attributes:
        session_index: Settings for session index.
        short_term_memory_index: Settings for working memory index.
        long_term_memory_index: Settings for long-term memory index.
        long_term_memory_history_index: Settings for history index.
    """

    session_index: IndexSettings | None = None
    short_term_memory_index: IndexSettings | None = None
    long_term_memory_index: IndexSettings | None = None
    long_term_memory_history_index: IndexSettings | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to OpenSearch API format."""
        result: dict[str, Any] = {}
        if self.session_index:
            result["session_index"] = self.session_index.to_dict()
        if self.short_term_memory_index:
            result["short_term_memory_index"] = self.short_term_memory_index.to_dict()
        if self.long_term_memory_index:
            result["long_term_memory_index"] = self.long_term_memory_index.to_dict()
        if self.long_term_memory_history_index:
            result["long_term_memory_history_index"] = (
                self.long_term_memory_history_index.to_dict()
            )
        return result


@dataclass
class ContainerConfig:
    """Memory container configuration.

    Attributes:
        name: Container name.
        description: Optional description.
        strategies: List of extraction strategies.
        embedding_model_id: OpenSearch embedding model ID.
        embedding_model_type: Type of embedding model (TEXT_EMBEDDING or SPARSE_ENCODING).
        llm_model_id: OpenSearch LLM model ID for inference.
        llm_result_path: JSONPath to extract LLM response.
        embedding_dimension: Embedding vector dimension.
        index_prefix: Custom index prefix (optional).
        use_system_index: Whether to use system indexes (default: True).
        index_settings: Optional index-level settings (shards, replicas).
    """

    name: str
    description: str | None = None
    strategies: list[StrategyConfig] = field(default_factory=list)
    embedding_model_id: str | None = None
    embedding_model_type: EmbeddingModelType = EmbeddingModelType.TEXT_EMBEDDING
    llm_model_id: str | None = None
    llm_result_path: str = "$.choices[0].message.content"
    embedding_dimension: int = 1536
    index_prefix: str | None = None
    use_system_index: bool = True
    index_settings: ContainerIndexSettings | None = None


@dataclass
class ContainerInfo:
    """Memory container information.

    Attributes:
        id: Container ID.
        name: Container name.
        description: Container description.
        strategies: Configured strategies.
        embedding_model_id: Embedding model ID.
        llm_model_id: LLM model ID.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: str
    name: str
    description: str | None = None
    strategies: list[MemoryStrategy] = field(default_factory=list)
    embedding_model_id: str | None = None
    llm_model_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Message:
    """A conversation message.

    Attributes:
        role: Message role (user, assistant, system).
        content: Message content.
        timestamp: Optional timestamp.
    """

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to OpenSearch API format."""
        return {
            "role": self.role,
            "content": [{"text": self.content, "type": "text"}],
        }


@dataclass
class Namespace:
    """Memory namespace for partitioning and strategy scoping.

    Completely configurable key-value pairs for memory isolation.
    Common fields: user_id, session_id, agent_id, org_id.

    When creating a container, strategies are scoped to namespace fields.
    When adding memory with `infer=True`, OpenSearch automatically runs
    strategies based on which namespace fields are present.

    Attributes:
        values: Namespace key-value pairs.
    """

    values: dict[str, str] = field(default_factory=dict)

    def __getitem__(self, key: str) -> str | None:
        """Get namespace value by key."""
        return self.values.get(key)

    def __setitem__(self, key: str, value: str) -> None:
        """Set namespace value by key."""
        self.values[key] = value

    def to_dict(self) -> dict[str, str]:
        """Get namespace as dictionary for API calls."""
        return dict(self.values)


@dataclass
class StoreRequest:
    """Request to store memory.

    Attributes:
        messages: Conversation messages (for conversational payload).
        structured_data: Structured data (for data payload).
        namespace: Namespace for partitioning and strategy scoping.
        payload_type: Type of payload.
        infer: Whether to apply LLM inference for fact extraction.
        metadata: Optional custom metadata.
        tags: Optional custom tags.
    """

    messages: list[Message] | None = None
    structured_data: dict[str, Any] | None = None
    namespace: Namespace = field(default_factory=Namespace)
    payload_type: PayloadType = PayloadType.CONVERSATIONAL
    infer: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class StoreResult:
    """Result of a store operation.

    Attributes:
        session_id: Session ID (for conversational).
        working_memory_id: Working memory document ID.
        long_term_count: Number of facts extracted (if infer=True).
        extraction_time_ms: Time taken for extraction.
    """

    session_id: str | None = None
    working_memory_id: str | None = None
    long_term_count: int = 0
    extraction_time_ms: int | None = None


@dataclass
class MemoryEntry:
    """A memory entry from long-term storage.

    Attributes:
        id: Memory document ID.
        content: The memory content (extracted fact).
        strategy: Which strategy extracted this.
        score: Similarity score (for search results).
        namespace: Namespace values.
        created_at: Creation timestamp.
        metadata: Custom metadata.
    """

    id: str
    content: str
    strategy: MemoryStrategy | None = None
    score: float = 0.0
    namespace: dict[str, str] = field(default_factory=dict)
    created_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecallResult:
    """Result of a recall (search) operation.

    Attributes:
        items: List of memory entries.
        total: Total number of matches.
        query: The search query.
        took_ms: Time taken in milliseconds.
    """

    items: list[MemoryEntry]
    total: int
    query: str
    took_ms: int = 0


@dataclass
class SessionInfo:
    """Session information.

    Attributes:
        id: Session ID.
        container_id: Parent container ID.
        summary: Session summary text.
        namespace: Session namespace.
        started_at: Session start time.
        ended_at: Session end time (if ended).
        message_count: Number of messages in session.
        messages: Session messages (if requested).
        metadata: Custom session metadata.
    """

    id: str
    container_id: str
    summary: str | None = None
    namespace: dict[str, str] = field(default_factory=dict)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    message_count: int = 0
    messages: list[Message] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HistoryEntry:
    """Audit trail entry for memory operations. READ-ONLY.

    History is READ-ONLY and cannot be updated or deleted.

    Attributes:
        id: History entry ID.
        memory_id: ID of the affected memory.
        container_id: Parent container ID.
        action: Operation type (ADD, UPDATE, DELETE).
        owner_id: User who performed the action.
        before: State before change (for UPDATE/DELETE).
        after: State after change.
        namespace: Namespace at time of operation.
        tags: Tags at time of operation.
        created_at: Operation timestamp.
    """

    id: str
    memory_id: str
    container_id: str
    action: HistoryAction
    owner_id: str | None = None
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    namespace: dict[str, str] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    created_at: datetime | None = None


@dataclass
class MemoryStats:
    """Memory usage statistics.

    Attributes:
        container_id: Container ID.
        container_name: Container name.
        working_memory_count: Messages in working memory.
        long_term_memory_count: Facts in long-term memory.
        session_count: Number of sessions.
        strategies_breakdown: Count per strategy.
        storage_size_bytes: Estimated storage size.
        last_updated: Last update timestamp.
    """

    container_id: str
    container_name: str
    working_memory_count: int = 0
    long_term_memory_count: int = 0
    session_count: int = 0
    strategies_breakdown: dict[MemoryStrategy, int] = field(default_factory=dict)
    storage_size_bytes: int = 0
    last_updated: datetime | None = None
