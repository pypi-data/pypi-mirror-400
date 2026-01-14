"""OpenSearch agentic searcher implementation.

Uses OpenSearch ML agents for AI-powered search with reasoning capabilities.
Supports flow agents (fast RAG) and conversational agents (multi-turn with memory).
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from opensearchpy import AsyncOpenSearch

from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.core.domain.search import (
    AgentType,
    AgenticSearchQuery,
    AgenticSearchResult,
    ReasoningStep,
    SearchMode,
    SearchResultItem,
)
from gnosisllm_knowledge.core.exceptions import AgenticSearchError

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.interfaces.agentic import IAgenticSearcher


class OpenSearchAgenticSearcher:
    """Executes agentic search using OpenSearch ML agents.

    Supports two agent types:
    - Flow Agent: Fast, sequential RAG with minimal reasoning
    - Conversational Agent: Multi-turn with memory and detailed reasoning

    The searcher integrates with OpenSearch's ML Commons plugin to:
    1. Execute agents via /_plugins/_ml/agents/{agent_id}/_execute
    2. Parse agent responses including reasoning traces
    3. Extract search results from VectorDBTool outputs
    4. Manage conversation memory for multi-turn interactions

    Example:
        ```python
        config = OpenSearchConfig.from_env()
        client = AsyncOpenSearch(hosts=[config.url])
        searcher = OpenSearchAgenticSearcher(client, config)

        query = AgenticSearchQuery(
            text="How do I configure OAuth2?",
            agent_type=AgentType.FLOW,
        )
        result = await searcher.agentic_search(query, "knowledge")
        print(result.answer)
        ```
    """

    def __init__(
        self,
        client: AsyncOpenSearch,
        config: OpenSearchConfig,
    ) -> None:
        """Initialize the agentic searcher.

        Args:
            client: Async OpenSearch client.
            config: OpenSearch configuration with agent IDs.
        """
        self._client = client
        self._config = config
        self._logger = logging.getLogger(__name__)

    @property
    def is_configured(self) -> bool:
        """Check if at least one agent is configured."""
        return self.flow_agent_available or self.conversational_agent_available

    @property
    def flow_agent_available(self) -> bool:
        """Check if flow agent is configured."""
        return bool(self._config.flow_agent_id)

    @property
    def conversational_agent_available(self) -> bool:
        """Check if conversational agent is configured."""
        return bool(self._config.conversational_agent_id)

    async def agentic_search(
        self,
        query: AgenticSearchQuery,
        index_name: str,
        **options: Any,
    ) -> AgenticSearchResult:
        """Execute agentic search with agent orchestration.

        The flow with RAGTool:
        1. Select agent based on query.agent_type
        2. Build execution request with query and filters
        3. Execute agent via OpenSearch ML API
        4. RAGTool searches the index and generates an AI answer
        5. Parse response for answer, reasoning, and source documents

        Args:
            query: Agentic search query with agent type and context.
            index_name: Target index name.
            **options: Additional agent options.

        Returns:
            AgenticSearchResult with answer, reasoning, and sources.

        Raises:
            AgenticSearchError: If agent execution fails.
        """
        start = datetime.now(UTC)

        # Select agent based on type
        agent_id = self._get_agent_id(query.agent_type)
        if not agent_id:
            raise AgenticSearchError(
                message=f"Agent not configured for type: {query.agent_type.value}",
                agent_type=query.agent_type.value,
                details={"hint": "Run 'gnosisllm-knowledge agentic setup --force' to configure agents."},
            )

        # Build execution request
        execute_body = self._build_execute_request(query, index_name)

        self._logger.debug(
            "Executing agentic search",
            extra={
                "agent_id": agent_id,
                "agent_type": query.agent_type.value,
                "query": query.text[:100],
                "index_name": index_name,
            },
        )

        # Execute agent - RAGTool handles search AND answer generation
        agent_response = await self._execute_agent(agent_id, execute_body)

        duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

        return self._parse_rag_response(query, agent_response, duration_ms)

    def _parse_rag_response(
        self,
        query: AgenticSearchQuery,
        response: dict[str, Any],
        duration_ms: float,
    ) -> AgenticSearchResult:
        """Parse RAGTool response into AgenticSearchResult.

        RAGTool returns both an AI-generated answer and source documents.

        Response format:
        {
            "inference_results": [
                {
                    "output": [
                        {"name": "knowledge_search", "result": "<LLM answer>"}
                    ]
                }
            ]
        }

        Args:
            query: The original query.
            response: Agent execution response.
            duration_ms: Total execution duration.

        Returns:
            Parsed AgenticSearchResult with answer and sources.
        """
        answer: str | None = None
        reasoning_steps: list[ReasoningStep] = []
        items: list[SearchResultItem] = []
        conversation_id = response.get("memory_id")

        # Parse inference results
        inference_results = response.get("inference_results", [])
        if inference_results:
            outputs = inference_results[0].get("output", [])

            for output in outputs:
                name = output.get("name", "")
                result = output.get("result", "")

                # Handle dataAsMap structure
                data_as_map = output.get("dataAsMap", {})
                if data_as_map and "response" in data_as_map:
                    result = data_as_map.get("response", result)

                if name == "memory_id":
                    conversation_id = str(result) if result else None
                elif name in ("knowledge_search", "RAGTool", "response"):
                    # RAGTool returns the LLM-generated answer
                    answer = self._extract_answer_from_result(result)

                    if query.include_reasoning:
                        reasoning_steps.append(
                            ReasoningStep(
                                tool="RAGTool",
                                action="rag_search",
                                input=query.text,
                                output=answer[:200] if answer else None,
                                duration_ms=duration_ms,
                            )
                        )

            # Extract source documents if available in the response
            for output in outputs:
                name = output.get("name", "")
                result = output.get("result", "")

                # Try to extract source documents from additional_info or similar
                additional_info = output.get("additional_info", {})
                if additional_info:
                    hits = additional_info.get("hits", {})
                    if hits:
                        items.extend(self._parse_opensearch_hits(hits))

        # If no answer from structured output, try raw response
        if not answer and "response" in response:
            answer = response.get("response")

        # Preserve the query's conversation_id if agent didn't return one
        final_conversation_id = conversation_id or query.conversation_id

        return AgenticSearchResult(
            query=query.text,
            mode=SearchMode.AGENTIC,
            items=items,
            total_hits=len(items),
            duration_ms=duration_ms,
            max_score=items[0].score if items else None,
            answer=answer,
            reasoning_steps=reasoning_steps,
            conversation_id=final_conversation_id,
            agent_type=query.agent_type,
            citations=[item.doc_id for item in items[:5]],
        )

    async def get_conversation(
        self,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        """Get conversation history for multi-turn searches.

        Args:
            conversation_id: Conversation identifier (memory_id).

        Returns:
            List of conversation messages with role and content.
        """
        try:
            response = await self._client.transport.perform_request(
                "GET",
                f"/_plugins/_ml/memory/{conversation_id}/_messages",
            )
            messages = response.get("messages", [])
            return [
                {
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("create_time"),
                }
                for msg in messages
            ]
        except Exception as e:
            self._logger.warning(f"Failed to get conversation: {e}")
            return []

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
        try:
            await self._client.transport.perform_request(
                "DELETE",
                f"/_plugins/_ml/memory/{conversation_id}",
            )
            return True
        except Exception as e:
            self._logger.warning(f"Failed to clear conversation: {e}")
            return False

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
        try:
            body: dict[str, Any] = {"size": limit}
            if account_id:
                body["query"] = {"term": {"account_id": account_id}}

            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/memory/_search",
                body=body,
            )
            hits = response.get("hits", {}).get("hits", [])
            return [
                {
                    "conversation_id": hit.get("_id"),
                    "name": hit.get("_source", {}).get("name"),
                    "created_at": hit.get("_source", {}).get("create_time"),
                    "updated_at": hit.get("_source", {}).get("update_time"),
                }
                for hit in hits
            ]
        except Exception as e:
            self._logger.warning(f"Failed to list conversations: {e}")
            return []

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
        try:
            response = await self._client.transport.perform_request(
                "GET",
                f"/_plugins/_ml/agents/{agent_id}",
            )
            return {
                "agent_id": agent_id,
                "name": response.get("name"),
                "type": response.get("type"),
                "description": response.get("description"),
                "tools": [t.get("name") for t in response.get("tools", [])],
                "created_at": response.get("created_time"),
            }
        except Exception as e:
            self._logger.warning(f"Failed to get agent status: {e}")
            return None

    async def create_conversation(
        self,
        name: str | None = None,
        account_id: str | None = None,
    ) -> str | None:
        """Create a new conversation memory.

        Uses the OpenSearch Memory API to create a conversation memory.
        The endpoint is POST /_plugins/_ml/memory (introduced in 2.12).

        Args:
            name: Optional name for the conversation.
            account_id: Optional account ID for multi-tenancy.

        Returns:
            The new conversation/memory ID, or None if creation fails.
        """
        body: dict[str, Any] = {}
        if name:
            body["name"] = name
        if account_id:
            body["account_id"] = account_id

        try:
            # POST /_plugins/_ml/memory creates a new memory (OpenSearch 2.12+)
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/memory",
                body=body if body else None,
            )
            memory_id = response.get("memory_id")
            if memory_id:
                self._logger.debug(f"Created conversation memory: {memory_id}")
            return memory_id
        except Exception as e:
            self._logger.warning(f"Failed to create conversation: {e}")
            # Return None - agent will work without pre-created memory
            # (agent may create its own memory on first use)
            return None

    def _get_agent_id(self, agent_type: AgentType) -> str | None:
        """Get agent ID for the specified type."""
        if agent_type == AgentType.FLOW:
            return self._config.flow_agent_id
        elif agent_type == AgentType.CONVERSATIONAL:
            return self._config.conversational_agent_id
        return None

    def _build_execute_request(
        self,
        query: AgenticSearchQuery,
        index_name: str,
    ) -> dict[str, Any]:
        """Build agent execution request.

        RAGTool requires:
        - question: The user's query (required)

        The index is configured at agent creation time, not at execution time.
        RAGTool searches the configured index and generates an AI answer.

        Conversational agents also support:
        - memory_id: For conversation continuity

        Args:
            query: The agentic search query.
            index_name: Target index name (for logging, not used by RAGTool).

        Returns:
            Request body for agent execution.
        """
        request: dict[str, Any] = {
            "parameters": {
                "question": query.text,
            }
        }

        # Add conversation context for conversational agents
        if query.agent_type == AgentType.CONVERSATIONAL and query.conversation_id:
            request["parameters"]["memory_id"] = query.conversation_id

        return request

    async def _execute_agent(
        self,
        agent_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute agent and return response.

        Args:
            agent_id: The agent ID to execute.
            body: Request body with parameters.

        Returns:
            Agent execution response.

        Raises:
            AgenticSearchError: If execution fails or times out.
        """
        try:
            response = await asyncio.wait_for(
                self._client.transport.perform_request(
                    "POST",
                    f"/_plugins/_ml/agents/{agent_id}/_execute",
                    body=body,
                ),
                timeout=self._config.agentic_timeout_seconds,
            )
            return response
        except asyncio.TimeoutError:
            raise AgenticSearchError(
                message="Agent execution timed out",
                agent_id=agent_id,
                details={"timeout_seconds": self._config.agentic_timeout_seconds},
            )
        except Exception as e:
            self._logger.error(f"Agent execution failed: {e}")
            raise AgenticSearchError(
                message=f"Agent execution failed: {e}",
                agent_id=agent_id,
                cause=e,
            )

    def _extract_dsl_from_agent_response(
        self,
        response: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Extract generated DSL query from agent response.

        The flow agent with QueryPlanningTool returns the DSL in the output.
        Format: {"inference_results": [{"output": [{"name": "response", "result": "<DSL JSON>"}]}]}

        Args:
            response: Agent execution response.

        Returns:
            Parsed DSL query dict, or None if not found.
        """
        try:
            inference_results = response.get("inference_results", [])
            if not inference_results:
                return None

            outputs = inference_results[0].get("output", [])
            for output in outputs:
                name = output.get("name", "")
                result = output.get("result", "")

                # QueryPlanningTool outputs come as "response" or "query_planner"
                if name in ("response", "query_planner", "QueryPlanningTool"):
                    if isinstance(result, dict):
                        return result
                    if isinstance(result, str) and result.strip():
                        # Try to parse as JSON
                        return self._parse_dsl_string(result)

            return None
        except Exception as e:
            self._logger.warning(f"Failed to extract DSL from agent response: {e}")
            return None

    def _parse_dsl_string(self, dsl_string: str) -> dict[str, Any] | None:
        """Parse a DSL query string into a dictionary.

        Handles various formats:
        - Raw JSON
        - Markdown code blocks
        - JSON with surrounding text

        Args:
            dsl_string: The DSL query as a string.

        Returns:
            Parsed DSL query dict, or None if parsing fails.
        """
        dsl_string = dsl_string.strip()

        # Remove markdown code blocks if present
        if dsl_string.startswith("```"):
            lines = dsl_string.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:] if lines else []
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            dsl_string = "\n".join(lines).strip()

        # Try to find and parse JSON
        try:
            # Find the first { and last }
            start = dsl_string.find("{")
            end = dsl_string.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = dsl_string[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            self._logger.debug(f"Failed to parse DSL JSON: {e}")

        # Try parsing the whole string
        try:
            return json.loads(dsl_string)
        except json.JSONDecodeError:
            pass

        return None

    async def _execute_dsl_query(
        self,
        index_name: str,
        dsl_query: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a DSL query against the index.

        Args:
            index_name: Target index name.
            dsl_query: OpenSearch DSL query to execute.

        Returns:
            Search response with hits.

        Raises:
            AgenticSearchError: If query execution fails.
        """
        try:
            response = await self._client.search(
                index=index_name,
                body=dsl_query,
            )
            return response
        except Exception as e:
            self._logger.error(f"DSL query execution failed: {e}")
            raise AgenticSearchError(
                message=f"Failed to execute generated DSL query: {e}",
                details={"index_name": index_name, "query": str(dsl_query)[:200]},
                cause=e,
            )

    def _parse_agentic_response(
        self,
        query: AgenticSearchQuery,
        agent_response: dict[str, Any],
        duration_ms: float,
        search_response: dict[str, Any] | None = None,
        generated_dsl: dict[str, Any] | None = None,
    ) -> AgenticSearchResult:
        """Parse agent response into AgenticSearchResult.

        Supports two response formats:

        1. QueryPlanningTool (OpenSearch 3.2+):
           The agent generates DSL queries which we then execute.
           Agent response: {"inference_results": [{"output": [{"name": "response", "result": "<DSL JSON>"}]}]}
           Search response: Standard OpenSearch search response with hits.

        2. Legacy VectorDBTool + MLModelTool:
           {
               "inference_results": [
                   {
                       "output": [
                           {"name": "knowledge_search", "result": {...}},
                           {"name": "answer_generator", "result": "..."}
                       ]
                   }
               ]
           }

        Args:
            query: The original query.
            agent_response: Agent execution response.
            duration_ms: Total execution duration.
            search_response: Search results from executing the generated DSL (optional).
            generated_dsl: The DSL query generated by the agent (optional).

        Returns:
            Parsed AgenticSearchResult.
        """
        answer: str | None = None
        reasoning_steps: list[ReasoningStep] = []
        items: list[SearchResultItem] = []
        conversation_id = agent_response.get("memory_id")
        dsl_string: str | None = None
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0

        # Parse search results from executed DSL query first (QueryPlanningTool flow)
        if search_response:
            hits_data = search_response.get("hits", {})
            items.extend(self._parse_opensearch_hits(hits_data))

            if query.include_reasoning:
                dsl_string = json.dumps(generated_dsl) if generated_dsl else None
                reasoning_steps.append(
                    ReasoningStep(
                        tool="QueryPlanningTool",
                        action="query_generation",
                        input=query.text,
                        output=dsl_string[:200] if dsl_string else None,
                        duration_ms=0,
                    )
                )
                reasoning_steps.append(
                    ReasoningStep(
                        tool="QueryPlanningTool",
                        action="search_execution",
                        input=dsl_string[:100] if dsl_string else query.text,
                        output=f"Found {len(items)} documents",
                        duration_ms=0,
                    )
                )

        # Parse inference results for additional outputs (legacy or conversational)
        inference_results = agent_response.get("inference_results", [])
        if inference_results:
            outputs = inference_results[0].get("output", [])

            for output in outputs:
                name = output.get("name", "")
                # Handle both direct result and dataAsMap structure (conversational agents)
                result = output.get("result", "")
                data_as_map = output.get("dataAsMap", {})
                if data_as_map and "response" in data_as_map:
                    result = data_as_map.get("response", result)

                if name == "memory_id":
                    # Extract conversation ID from conversational agent
                    conversation_id = str(result) if result else None
                elif name == "parent_message_id":
                    # Track parent message ID for conversation threading
                    pass  # Could store for future use
                elif name in ("answer_generator", "MLModelTool"):
                    # Parse answer from output (legacy format)
                    answer = self._extract_answer_from_result(result)

                    # Add reasoning step for answer generation
                    if query.include_reasoning:
                        reasoning_steps.append(
                            ReasoningStep(
                                tool="MLModelTool",
                                action="answer_generation",
                                input=query.text,
                                output=answer[:100] if answer else None,
                                duration_ms=0,
                            )
                        )
                elif name in ("knowledge_search", "VectorDBTool"):
                    # Parse search results from legacy VectorDBTool output
                    items.extend(self._parse_tool_search_results(result))

                    # Add reasoning step
                    if query.include_reasoning:
                        reasoning_steps.append(
                            ReasoningStep(
                                tool="VectorDBTool",
                                action="search",
                                input=query.text,
                                output=f"Found {len(items)} documents",
                                duration_ms=0,
                            )
                        )
                # Skip "response" and "query_planner" here - they're handled via generated_dsl parameter

            # Parse token usage if available
            usage = inference_results[0].get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

        # Parse agentic context for reasoning traces (if present)
        agentic_context = agent_response.get("agentic_context", {})
        traces = agentic_context.get("traces", [])
        for trace in traces:
            if query.include_reasoning:
                reasoning_steps.append(
                    ReasoningStep(
                        tool=trace.get("tool", "unknown"),
                        action=trace.get("action", ""),
                        input=trace.get("input"),
                        output=trace.get("output"),
                        duration_ms=trace.get("duration_ms", 0),
                        tokens_used=trace.get("tokens", 0),
                    )
                )

        # If no answer from structured output, try to get from raw response
        if not answer and "response" in agent_response:
            answer = agent_response.get("response")

        # Preserve the query's conversation_id if agent didn't return one
        # This allows multi-turn conversations when memory was created beforehand
        final_conversation_id = conversation_id or query.conversation_id

        return AgenticSearchResult(
            query=query.text,
            mode=SearchMode.AGENTIC,
            items=items,
            total_hits=len(items),
            duration_ms=duration_ms,
            max_score=items[0].score if items else None,
            answer=answer,
            reasoning_steps=reasoning_steps,
            conversation_id=final_conversation_id,
            agent_type=query.agent_type,
            citations=[item.doc_id for item in items[:5]],  # Top 5 as citations
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            generated_query=dsl_string,  # Include the generated DSL for debugging
        )

    def _extract_answer_from_result(
        self,
        result: str | dict[str, Any],
    ) -> str | None:
        """Extract answer text from LLM tool result.

        Handles raw OpenAI API response format:
        {
            "choices": [
                {"message": {"content": "The answer..."}}
            ]
        }

        Args:
            result: Tool output (may be string JSON or dict).

        Returns:
            Extracted answer text or None.
        """
        # If it's already plain text, return it
        if isinstance(result, str):
            if not result.strip().startswith("{"):
                return result

            # Try to parse as JSON (OpenAI response format)
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                return result  # Return as-is if not valid JSON

        if not isinstance(result, dict):
            return str(result) if result else None

        # OpenAI response format
        choices = result.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if content:
                return content.strip()

        # Fallback: look for common answer keys
        for key in ("answer", "text", "content", "output", "result"):
            if key in result:
                return str(result[key]).strip()

        return None

    def _parse_tool_search_results(
        self,
        result: str | dict[str, Any] | list[Any],
    ) -> list[SearchResultItem]:
        """Parse search results from VectorDBTool output.

        Args:
            result: Tool output (may be string JSON or dict).

        Returns:
            List of SearchResultItem.
        """
        items: list[SearchResultItem] = []

        # Parse if string
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                return items

        # Handle list of hits
        if isinstance(result, list):
            hits = result
        elif isinstance(result, dict):
            hits = result.get("hits", {}).get("hits", [])
            if not hits:
                hits = result.get("hits", [])
        else:
            return items

        for hit in hits:
            source = hit.get("_source", hit) if isinstance(hit, dict) else {}
            if not source:
                continue

            items.append(
                SearchResultItem(
                    doc_id=hit.get("_id", source.get("id", "")),
                    content=source.get("content", ""),
                    score=hit.get("_score", source.get("score", 0.0)),
                    title=source.get("title"),
                    url=source.get("url"),
                    source=source.get("source"),
                    collection_id=source.get("collection_id"),
                    source_id=source.get("source_id"),
                    chunk_index=source.get("chunk_index"),
                    metadata=source.get("metadata"),
                )
            )

        return items

    def _parse_opensearch_hits(
        self,
        hits_data: dict[str, Any],
    ) -> list[SearchResultItem]:
        """Parse OpenSearch hits structure into SearchResultItems.

        Standard OpenSearch response format:
        {
            "total": {"value": 10},
            "max_score": 1.0,
            "hits": [
                {"_id": "...", "_score": 0.9, "_source": {...}}
            ]
        }

        Args:
            hits_data: OpenSearch hits object.

        Returns:
            List of SearchResultItem.
        """
        items: list[SearchResultItem] = []

        hits = hits_data.get("hits", [])
        for hit in hits:
            if not isinstance(hit, dict):
                continue

            source = hit.get("_source", {})
            if not source:
                continue

            items.append(
                SearchResultItem(
                    doc_id=hit.get("_id", ""),
                    content=source.get("content", ""),
                    score=hit.get("_score", 0.0),
                    title=source.get("title"),
                    url=source.get("url"),
                    source=source.get("source"),
                    collection_id=source.get("collection_id"),
                    source_id=source.get("source_id"),
                    chunk_index=source.get("chunk_index"),
                    total_chunks=source.get("total_chunks"),
                    metadata=source.get("metadata"),
                )
            )

        return items


class AgenticSearchFallback:
    """Fallback handler for when agentic search fails.

    Provides graceful degradation to standard hybrid search when:
    - Agents are not configured
    - Agent execution fails
    - Timeout occurs

    This ensures users always get results, even if the AI-powered
    answer generation is unavailable.

    Example:
        ```python
        agentic_searcher = OpenSearchAgenticSearcher(client, config)
        standard_searcher = OpenSearchKnowledgeSearcher(client, config)
        fallback = AgenticSearchFallback(agentic_searcher, standard_searcher)

        # Always returns results, with or without AI answer
        result = await fallback.search_with_fallback(query, "knowledge")
        ```
    """

    def __init__(
        self,
        agentic_searcher: OpenSearchAgenticSearcher,
        standard_searcher: Any,  # OpenSearchKnowledgeSearcher
    ) -> None:
        """Initialize the fallback handler.

        Args:
            agentic_searcher: Agentic search implementation.
            standard_searcher: Standard knowledge searcher for fallback.
        """
        self._agentic = agentic_searcher
        self._standard = standard_searcher
        self._logger = logging.getLogger(__name__)

    @property
    def is_agentic_available(self) -> bool:
        """Check if agentic search is available."""
        return self._agentic.is_configured

    async def search_with_fallback(
        self,
        query: AgenticSearchQuery,
        index_name: str,
        **options: Any,
    ) -> AgenticSearchResult:
        """Execute agentic search with fallback to standard search.

        If agentic search is not configured or fails, automatically
        falls back to hybrid search and wraps the results in an
        AgenticSearchResult without an AI-generated answer.

        Args:
            query: Agentic search query.
            index_name: Target index name.
            **options: Additional options.

        Returns:
            AgenticSearchResult (may not have answer if in fallback mode).
        """
        if not self._agentic.is_configured:
            self._logger.warning("Agentic search not configured, using fallback")
            return await self._execute_fallback(query, index_name, "Agents not configured")

        try:
            return await self._agentic.agentic_search(query, index_name, **options)
        except Exception as e:
            self._logger.warning(f"Agentic search failed, falling back: {e}")
            return await self._execute_fallback(query, index_name, str(e))

    async def _execute_fallback(
        self,
        query: AgenticSearchQuery,
        index_name: str,
        reason: str,
    ) -> AgenticSearchResult:
        """Execute fallback search and convert to AgenticSearchResult.

        Args:
            query: Original agentic query.
            index_name: Target index.
            reason: Reason for fallback.

        Returns:
            AgenticSearchResult without AI answer.
        """
        # Convert to standard search query
        standard_query = query.to_search_query()

        # Execute standard hybrid search
        result = await self._standard.search(standard_query, index_name)

        # Convert to AgenticSearchResult
        return AgenticSearchResult.from_search_result(
            result,
            answer=None,  # No AI answer in fallback
            reasoning_steps=[
                ReasoningStep(
                    tool="FallbackSearch",
                    action="hybrid_search",
                    input=query.text,
                    output=f"Fallback mode: {reason}. Found {result.total_hits} results.",
                    duration_ms=result.duration_ms,
                )
            ],
            agent_type=query.agent_type,
        )


# Type alias for protocol compliance
AgenticSearcherImpl: type[IAgenticSearcher] = OpenSearchAgenticSearcher  # type: ignore[assignment]
