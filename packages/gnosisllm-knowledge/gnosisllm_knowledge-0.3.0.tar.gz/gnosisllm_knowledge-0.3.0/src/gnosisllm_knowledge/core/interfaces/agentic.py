"""Agentic searcher protocol - Interface for AI-powered search operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.domain.search import (
        AgenticSearchQuery,
        AgenticSearchResult,
    )


@runtime_checkable
class IAgenticSearcher(Protocol):
    """Protocol for agentic search operations using AI agents.

    Agentic searchers are responsible for:
    - Understanding natural language queries
    - Automatically constructing optimal search strategies
    - Generating context-aware answers from retrieved documents
    - Supporting multi-turn conversations with memory

    Implementations should provide AI-powered search capabilities
    that go beyond traditional search by understanding user intent
    and generating comprehensive answers.
    """

    @property
    def is_configured(self) -> bool:
        """Check if agentic search is properly configured.

        Returns:
            True if all required agents and models are configured.
        """
        ...

    @property
    def flow_agent_available(self) -> bool:
        """Check if flow agent is available.

        Returns:
            True if flow agent can be used.
        """
        ...

    @property
    def conversational_agent_available(self) -> bool:
        """Check if conversational agent is available.

        Returns:
            True if conversational agent can be used.
        """
        ...

    async def agentic_search(
        self,
        query: AgenticSearchQuery,
        index_name: str,
        **options: Any,
    ) -> AgenticSearchResult:
        """Execute agentic search with agent orchestration.

        The agent will:
        1. Analyze the query to understand user intent
        2. Search for relevant documents
        3. Generate a comprehensive answer with citations
        4. (Optional) Maintain conversation memory

        Args:
            query: Agentic search query with agent type and context.
            index_name: Target index name.
            **options: Additional agent options.

        Returns:
            AgenticSearchResult with answer, reasoning, and sources.
        """
        ...

    async def get_conversation(
        self,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        """Get conversation history for multi-turn searches.

        Args:
            conversation_id: Conversation identifier.

        Returns:
            List of conversation messages with role, content, and metadata.
        """
        ...

    async def clear_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        """Clear conversation history.

        Args:
            conversation_id: Conversation to clear.

        Returns:
            True if cleared successfully, False if not found.
        """
        ...

    async def list_conversations(
        self,
        account_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List active conversations.

        Args:
            account_id: Filter by account (multi-tenant).
            limit: Maximum number of conversations.

        Returns:
            List of conversation metadata dicts.
        """
        ...

    async def get_agent_status(
        self,
        agent_id: str,
    ) -> dict[str, Any] | None:
        """Get status of an agent.

        Args:
            agent_id: Agent identifier.

        Returns:
            Agent status info or None if not found.
        """
        ...
