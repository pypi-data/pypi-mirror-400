"""Search domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SearchMode(str, Enum):
    """Search mode options.

    Attributes:
        SEMANTIC: Vector similarity search only (KNN).
        KEYWORD: BM25 text search only.
        HYBRID: Combined semantic + keyword search (default).
        AGENTIC: AI-powered search with reasoning and answer generation.
    """

    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    AGENTIC = "agentic"


class AgentType(str, Enum):
    """Agent types for agentic search.

    Attributes:
        FLOW: Fast RAG - single query/response with no conversation memory.
        CONVERSATIONAL: Multi-turn conversations with memory support.
    """

    FLOW = "flow"
    CONVERSATIONAL = "conversational"


@dataclass
class SearchQuery:
    """Search query with filters and options.

    Attributes:
        text: The search query text.
        mode: Search mode to use.
        limit: Maximum number of results to return.
        offset: Number of results to skip (for pagination).
        min_score: Minimum score threshold for results.

        Filters:
            collection_ids: Filter by collection IDs.
            source_ids: Filter by source IDs.
            account_id: Multi-tenant account filter.
            metadata_filters: Custom metadata filters.

        Advanced options:
            field_boosts: Field boosting weights.
            include_highlights: Whether to include highlights.
            include_fields: Fields to include in results.
            exclude_fields: Fields to exclude from results.
            explain: Whether to include score explanation.
    """

    text: str
    mode: SearchMode = SearchMode.HYBRID
    limit: int = 10
    offset: int = 0
    min_score: float | None = None

    # Filters
    collection_ids: list[str] | None = None
    source_ids: list[str] | None = None
    account_id: str | None = None
    metadata_filters: dict[str, Any] = field(default_factory=dict)

    # Advanced options
    field_boosts: dict[str, float] | None = None
    include_highlights: bool = True
    include_fields: list[str] | None = None
    exclude_fields: list[str] | None = None
    explain: bool = False

    def with_mode(self, mode: SearchMode) -> SearchQuery:
        """Create a copy with a different search mode."""
        return SearchQuery(
            text=self.text,
            mode=mode,
            limit=self.limit,
            offset=self.offset,
            min_score=self.min_score,
            collection_ids=self.collection_ids,
            source_ids=self.source_ids,
            account_id=self.account_id,
            metadata_filters=self.metadata_filters.copy(),
            field_boosts=self.field_boosts.copy() if self.field_boosts else None,
            include_highlights=self.include_highlights,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields,
            explain=self.explain,
        )

    def with_tenant(self, account_id: str) -> SearchQuery:
        """Create a copy with tenant information."""
        return SearchQuery(
            text=self.text,
            mode=self.mode,
            limit=self.limit,
            offset=self.offset,
            min_score=self.min_score,
            collection_ids=self.collection_ids,
            source_ids=self.source_ids,
            account_id=account_id,
            metadata_filters=self.metadata_filters.copy(),
            field_boosts=self.field_boosts.copy() if self.field_boosts else None,
            include_highlights=self.include_highlights,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields,
            explain=self.explain,
        )


@dataclass
class SearchResultItem:
    """A single search result.

    Attributes:
        doc_id: Document identifier.
        content: Document content.
        score: Relevance score.
        title: Document title.
        url: Document URL.
        source: Source identifier.
        collection_id: Collection identifier.
        source_id: Source identifier within collection.
        chunk_index: Chunk index if document is chunked.
        total_chunks: Total chunks in parent document.
        metadata: Document metadata.
        highlights: Highlighted snippets from matching content.
        explanation: Score explanation (when explain=True).
    """

    doc_id: str
    content: str
    score: float
    title: str | None = None
    url: str | None = None
    source: str | None = None
    collection_id: str | None = None
    source_id: str | None = None
    chunk_index: int | None = None
    total_chunks: int | None = None
    metadata: dict[str, Any] | None = None
    highlights: list[str] | None = None
    highlighted_title: str | None = None
    explanation: dict[str, Any] | None = None


@dataclass
class SearchResult:
    """Complete search result with metadata.

    Attributes:
        query: The original search query text.
        mode: Search mode that was used.
        items: List of search result items.
        total_hits: Total number of matching documents.
        duration_ms: Search duration in milliseconds.
        max_score: Maximum score among results.
        from_cache: Whether results came from cache.
        cache_key: Cache key if results are cacheable.
    """

    query: str
    mode: SearchMode
    items: list[SearchResultItem]
    total_hits: int
    duration_ms: float
    max_score: float | None = None
    from_cache: bool = False
    cache_key: str | None = None
    search_after_token: Any | None = None  # For cursor-based pagination
    has_more: bool = False

    @property
    def has_results(self) -> bool:
        """Check if there are any results."""
        return len(self.items) > 0

    @property
    def count(self) -> int:
        """Return the number of results in this page."""
        return len(self.items)


@dataclass
class ReasoningStep:
    """A single step in the agent's reasoning process.

    Attributes:
        tool: The tool that was used (e.g., "VectorDBTool", "MLModelTool").
        action: The action performed.
        input: Input provided to the tool.
        output: Output from the tool.
        duration_ms: Duration of this step in milliseconds.
        tokens_used: Number of tokens consumed by this step.
    """

    tool: str
    action: str
    input: str | None = None
    output: str | None = None
    duration_ms: float = 0.0
    tokens_used: int = 0


@dataclass
class AgenticSearchQuery:
    """Query for agentic search with conversation support.

    Attributes:
        text: The search query text.
        agent_type: Type of agent to use.
        conversation_id: ID for continuing a conversation.
        collection_ids: Filter by collection IDs.
        source_ids: Filter by source IDs.
        account_id: Multi-tenant account filter.
        limit: Maximum number of source documents to retrieve.
        include_reasoning: Whether to include reasoning steps.
        metadata_filters: Custom metadata filters.
        temperature: LLM temperature (0.0 to 1.0).
        max_iterations: Maximum agent iterations.
    """

    text: str
    agent_type: AgentType = AgentType.FLOW
    conversation_id: str | None = None
    collection_ids: list[str] | None = None
    source_ids: list[str] | None = None
    account_id: str | None = None
    limit: int = 10
    include_reasoning: bool = True
    metadata_filters: dict[str, Any] = field(default_factory=dict)
    temperature: float = 0.0
    max_iterations: int = 5

    def to_search_query(self) -> SearchQuery:
        """Convert to a standard SearchQuery for fallback."""
        return SearchQuery(
            text=self.text,
            mode=SearchMode.HYBRID,
            limit=self.limit,
            collection_ids=self.collection_ids,
            source_ids=self.source_ids,
            account_id=self.account_id,
            metadata_filters=self.metadata_filters.copy(),
        )


@dataclass
class AgenticSearchResult:
    """Search result with agentic enhancements.

    Extends SearchResult with AI-generated answer and reasoning.

    Attributes:
        query: The original search query text.
        mode: Search mode (always AGENTIC).
        items: Retrieved source documents.
        total_hits: Total number of matching documents.
        duration_ms: Total search duration in milliseconds.
        max_score: Maximum score among results.
        answer: AI-generated answer to the query.
        reasoning_steps: List of reasoning steps taken by the agent.
        conversation_id: Conversation ID for multi-turn searches.
        agent_type: Type of agent that was used.
        citations: References to source documents used in answer.
        total_tokens: Total tokens consumed.
        prompt_tokens: Tokens used in prompts.
        completion_tokens: Tokens used in completions.
        generated_query: The DSL query generated by QueryPlanningTool (if applicable).
    """

    query: str
    mode: SearchMode
    items: list[SearchResultItem]
    total_hits: int
    duration_ms: float
    max_score: float | None = None
    answer: str | None = None
    reasoning_steps: list[ReasoningStep] = field(default_factory=list)
    conversation_id: str | None = None
    agent_type: AgentType = AgentType.FLOW
    citations: list[str] = field(default_factory=list)
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    generated_query: str | None = None  # DSL generated by QueryPlanningTool

    @property
    def has_answer(self) -> bool:
        """Check if an answer was generated."""
        return self.answer is not None and len(self.answer) > 0

    @property
    def has_reasoning(self) -> bool:
        """Check if reasoning steps are available."""
        return len(self.reasoning_steps) > 0

    @classmethod
    def from_search_result(
        cls,
        result: SearchResult,
        answer: str | None = None,
        reasoning_steps: list[ReasoningStep] | None = None,
        agent_type: AgentType = AgentType.FLOW,
        conversation_id: str | None = None,
    ) -> AgenticSearchResult:
        """Create AgenticSearchResult from a SearchResult."""
        return cls(
            query=result.query,
            mode=SearchMode.AGENTIC,
            items=result.items,
            total_hits=result.total_hits,
            duration_ms=result.duration_ms,
            max_score=result.max_score,
            answer=answer,
            reasoning_steps=reasoning_steps or [],
            conversation_id=conversation_id,
            agent_type=agent_type,
        )
