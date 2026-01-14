"""Agentic search commands for AI-powered knowledge retrieval.

Commands:
- setup: Configure agents in OpenSearch
- chat: Interactive agentic chat session
- status: Show agent configuration status
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Any

from opensearchpy import AsyncOpenSearch
from rich.prompt import Prompt

from gnosisllm_knowledge.backends.opensearch.agentic import OpenSearchAgenticSearcher
from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.backends.opensearch.setup import OpenSearchSetupAdapter
from gnosisllm_knowledge.cli.display.service import RichDisplayService, StepProgress
from gnosisllm_knowledge.cli.utils.config import CliConfig
from gnosisllm_knowledge.core.domain.search import AgentType, AgenticSearchQuery

if TYPE_CHECKING:
    pass


async def _create_client(cli_config: CliConfig) -> AsyncOpenSearch:
    """Create async OpenSearch client from CLI config."""
    http_auth = None
    if cli_config.opensearch_username and cli_config.opensearch_password:
        http_auth = (cli_config.opensearch_username, cli_config.opensearch_password)

    return AsyncOpenSearch(
        hosts=[{"host": cli_config.opensearch_host, "port": cli_config.opensearch_port}],
        http_auth=http_auth,
        use_ssl=cli_config.opensearch_use_ssl,
        verify_certs=cli_config.opensearch_verify_certs,
        ssl_show_warn=False,
    )


def _create_opensearch_config(cli_config: CliConfig) -> OpenSearchConfig:
    """Create OpenSearchConfig from CLI config."""
    return OpenSearchConfig(
        host=cli_config.opensearch_host,
        port=cli_config.opensearch_port,
        username=cli_config.opensearch_username,
        password=cli_config.opensearch_password,
        use_ssl=cli_config.opensearch_use_ssl,
        verify_certs=cli_config.opensearch_verify_certs,
        model_id=cli_config.opensearch_model_id,
        openai_api_key=cli_config.openai_api_key,
        flow_agent_id=cli_config.opensearch_flow_agent_id,
        conversational_agent_id=cli_config.opensearch_conversational_agent_id,
        agentic_llm_model=cli_config.agentic_llm_model,
        agentic_max_iterations=cli_config.agentic_max_iterations,
        agentic_timeout_seconds=cli_config.agentic_timeout_seconds,
    )


async def agentic_setup_command(
    display: RichDisplayService,
    agent_type: str = "all",
    force: bool = False,
) -> None:
    """Setup agentic search agents.

    Args:
        display: Display service for output.
        agent_type: Agent type to setup ('flow', 'conversational', 'all').
        force: Force recreate existing agents.
    """
    cli_config = CliConfig.from_env()

    display.header(
        "GnosisLLM Agentic Search Setup",
        "Configuring AI agents for intelligent search",
    )

    # Validate configuration
    errors = cli_config.validate_for_agentic_setup()
    if errors:
        for error in errors:
            display.error(error)
        display.newline()
        display.format_error_with_suggestion(
            error="Configuration validation failed.",
            suggestion="Ensure all required environment variables are set.",
            command="gnosisllm-knowledge setup",
        )
        sys.exit(1)

    # Create client and adapter
    client = await _create_client(cli_config)
    config = _create_opensearch_config(cli_config)
    adapter = OpenSearchSetupAdapter(client, config)

    try:
        # Determine which agents to setup
        agent_types_to_setup: list[str] = []
        if agent_type in ("flow", "all"):
            agent_types_to_setup.append("flow")
        if agent_type in ("conversational", "all"):
            agent_types_to_setup.append("conversational")

        # If force, cleanup existing agents first
        if force:
            display.info("Force mode: cleaning up existing agents...")
            try:
                cleanup_result = await adapter.cleanup_agents()
                for step in cleanup_result.steps_completed:
                    display.success(step)
            except Exception as e:
                display.warning(f"Cleanup warning (continuing): {e}")
            display.newline()

        # Build step list
        steps = []
        if "flow" in agent_types_to_setup:
            steps.append(StepProgress("llm_connector", "Create LLM connector for reasoning"))
            steps.append(StepProgress("llm_model", "Deploy LLM model"))
            steps.append(StepProgress("flow_agent", "Create flow agent for fast RAG"))
        if "conversational" in agent_types_to_setup:
            if "flow" not in agent_types_to_setup:
                steps.append(StepProgress("llm_connector", "Create LLM connector for reasoning"))
                steps.append(StepProgress("llm_model", "Deploy LLM model"))
            steps.append(StepProgress("conversational_agent", "Create conversational agent with memory"))

        progress = display.progress(steps)
        results: dict[str, str] = {}
        step_idx = 0

        try:
            if "flow" in agent_types_to_setup:
                # LLM connector
                progress.update(step_idx, "running")
                # Connector is created as part of setup_flow_agent
                progress.complete(step_idx)
                step_idx += 1

                # LLM model
                progress.update(step_idx, "running")
                progress.complete(step_idx)
                step_idx += 1

                # Flow agent
                progress.update(step_idx, "running")
                flow_agent_id = await adapter.setup_flow_agent()
                results["flow_agent_id"] = flow_agent_id
                progress.complete(step_idx)
                step_idx += 1

            if "conversational" in agent_types_to_setup:
                if "flow" not in agent_types_to_setup:
                    # LLM connector (if not already done)
                    progress.update(step_idx, "running")
                    progress.complete(step_idx)
                    step_idx += 1

                    # LLM model
                    progress.update(step_idx, "running")
                    progress.complete(step_idx)
                    step_idx += 1

                # Conversational agent
                progress.update(step_idx, "running")
                conv_agent_id = await adapter.setup_conversational_agent()
                results["conversational_agent_id"] = conv_agent_id
                progress.complete(step_idx)
                step_idx += 1

        except Exception as e:
            progress.fail(step_idx, str(e))
            progress.stop()
            display.newline()
            display.error(f"Setup failed: {e}")
            sys.exit(1)

        progress.stop()
        display.newline()

        # Show environment variable instructions
        content = "[bold]Add to your .env file:[/bold]\n\n"
        if "flow_agent_id" in results:
            content += f"  [green]OPENSEARCH_FLOW_AGENT_ID={results['flow_agent_id']}[/green]\n"
        if "conversational_agent_id" in results:
            content += f"  [green]OPENSEARCH_CONVERSATIONAL_AGENT_ID={results['conversational_agent_id']}[/green]\n"

        content += "\n[bold]Test with:[/bold]\n"
        content += '  [dim]gnosisllm-knowledge search --mode agentic "your question"[/dim]\n'
        content += "  [dim]gnosisllm-knowledge agentic chat[/dim]"

        display.panel(content, title="Agentic Setup Complete", style="success")

    finally:
        await client.close()


async def agentic_chat_command(
    display: RichDisplayService,
    index_name: str = "knowledge",
    agent_type: str = "conversational",
    account_id: str | None = None,
    collection_ids: str | None = None,
    verbose: bool = False,
) -> None:
    """Interactive agentic chat session.

    Args:
        display: Display service for output.
        index_name: Index to search.
        agent_type: Agent type ('flow' or 'conversational').
        account_id: Filter by account ID.
        collection_ids: Filter by collection IDs (comma-separated).
        verbose: Show reasoning steps.
    """
    cli_config = CliConfig.from_env()

    # Validate configuration
    errors = cli_config.validate_for_agentic_search(agent_type)
    if errors:
        for error in errors:
            display.error(error)
        sys.exit(1)

    display.header(
        "GnosisLLM Agentic Chat",
        f"Agent: {agent_type} | Index: {index_name} | Press Ctrl+C to exit",
    )

    client = await _create_client(cli_config)
    config = _create_opensearch_config(cli_config)
    searcher = OpenSearchAgenticSearcher(client, config)

    conversation_id: str | None = None
    collection_list = collection_ids.split(",") if collection_ids else None

    async def start_new_conversation() -> str | None:
        """Create a new conversation memory for multi-turn chat."""
        if agent_type == "conversational":
            return await searcher.create_conversation(
                name="CLI Chat Session",
                account_id=account_id,
            )
        return None

    try:
        # Show help
        display.info("[dim]Commands: /new (new conversation), /quit (exit), /help (show help)[/dim]")

        # Create initial conversation memory for conversational agent
        if agent_type == "conversational":
            conversation_id = await start_new_conversation()
            if conversation_id:
                display.info(f"[dim]Conversation started (memory_id: {conversation_id[:8]}...)[/dim]")
            else:
                display.info("[dim]Conversation mode (memory will be created automatically)[/dim]")

        while True:
            try:
                display.newline()
                user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ("/new", "/clear"):
                    if conversation_id:
                        await searcher.clear_conversation(conversation_id)
                    # Create a fresh conversation memory
                    conversation_id = await start_new_conversation()
                    if conversation_id:
                        display.info(f"Started new conversation (memory_id: {conversation_id[:8]}...)")
                    else:
                        display.info("Started new conversation.")
                    continue

                if user_input.lower() in ("/quit", "/exit", "/q"):
                    break

                if user_input.lower() == "/help":
                    _show_chat_help(display)
                    continue

                # Build agentic query
                query = AgenticSearchQuery(
                    text=user_input,
                    agent_type=AgentType.CONVERSATIONAL if agent_type == "conversational" else AgentType.FLOW,
                    conversation_id=conversation_id,
                    collection_ids=collection_list,
                    account_id=account_id,
                    include_reasoning=verbose,
                )

                # Execute search with loading indicator
                with display.loading_spinner("Thinking..."):
                    result = await searcher.agentic_search(query, index_name)

                # Update conversation ID if agent returns one (prefer agent's memory_id)
                if result.conversation_id:
                    conversation_id = result.conversation_id

                # Display answer
                display.newline()
                if result.answer:
                    display.console.print(f"[bold green]Assistant[/bold green]: {result.answer}")
                else:
                    display.warning("No answer generated.")

                # Show reasoning steps if verbose
                if verbose and result.reasoning_steps:
                    display.newline()
                    display.console.print("[dim]Reasoning:[/dim]")
                    for step in result.reasoning_steps:
                        display.console.print(f"  [dim]→ {step.tool}: {step.action}[/dim]")

                # Show sources if available
                if result.items:
                    display.newline()
                    display.info(f"[dim]Sources: {len(result.items)} documents ({result.duration_ms:.0f}ms)[/dim]")
                    for i, item in enumerate(result.items[:3], 1):
                        display.console.print(f"  [dim]{i}. {item.title or 'Untitled'}[/dim]")
                        if item.url:
                            display.console.print(f"     [blue]{item.url[:60]}[/blue]")

                # Show conversation ID in verbose mode
                if verbose and conversation_id:
                    display.console.print(f"  [dim]Memory ID: {conversation_id}[/dim]")

            except KeyboardInterrupt:
                display.newline()
                display.info("Goodbye!")
                break
            except Exception as e:
                display.error(f"Error: {e}")

    finally:
        await client.close()


async def agentic_status_command(
    display: RichDisplayService,
) -> None:
    """Show agentic search configuration status."""
    cli_config = CliConfig.from_env()

    display.header(
        "GnosisLLM Agentic Status",
        "Agent configuration and health",
    )

    display.agentic_status(
        flow_agent_id=cli_config.opensearch_flow_agent_id,
        conversational_agent_id=cli_config.opensearch_conversational_agent_id,
        embedding_model_id=cli_config.opensearch_model_id,
        llm_model=cli_config.agentic_llm_model,
    )

    # If any agent is configured, try to get status from OpenSearch
    if cli_config.has_agentic_agents and cli_config.opensearch_model_id:
        display.newline()

        client = await _create_client(cli_config)
        config = _create_opensearch_config(cli_config)
        searcher = OpenSearchAgenticSearcher(client, config)

        try:
            # Check flow agent
            if cli_config.opensearch_flow_agent_id:
                status = await searcher.get_agent_status(cli_config.opensearch_flow_agent_id)
                if status:
                    display.success(f"Flow agent '{status.get('name')}' is active")
                else:
                    display.warning("Flow agent not found in OpenSearch")

            # Check conversational agent
            if cli_config.opensearch_conversational_agent_id:
                status = await searcher.get_agent_status(cli_config.opensearch_conversational_agent_id)
                if status:
                    display.success(f"Conversational agent '{status.get('name')}' is active")
                else:
                    display.warning("Conversational agent not found in OpenSearch")

        except Exception as e:
            display.warning(f"Could not verify agent status: {e}")
        finally:
            await client.close()


async def agentic_search_command(
    display: RichDisplayService,
    query: str,
    index_name: str = "knowledge",
    agent_type: str = "flow",
    account_id: str | None = None,
    collection_ids: str | None = None,
    source_ids: str | None = None,
    limit: int = 5,
    json_output: bool = False,
    verbose: bool = False,
) -> dict[str, Any] | None:
    """Execute agentic search.

    Args:
        display: Display service for output.
        query: Search query text.
        index_name: Index to search.
        agent_type: Agent type ('flow' or 'conversational').
        account_id: Filter by account ID.
        collection_ids: Filter by collection IDs (comma-separated).
        source_ids: Filter by source IDs (comma-separated).
        limit: Maximum source documents to retrieve.
        json_output: Output as JSON for scripting.
        verbose: Show reasoning steps.

    Returns:
        Search result dict or None if failed.
    """
    cli_config = CliConfig.from_env()

    # Validate configuration
    errors = cli_config.validate_for_agentic_search(agent_type)
    if errors:
        if json_output:
            print(json.dumps({"error": errors[0]}))
        else:
            for error in errors:
                display.error(error)
        return None

    # Parse filter lists
    collection_list = collection_ids.split(",") if collection_ids else None
    source_list = source_ids.split(",") if source_ids else None

    client = await _create_client(cli_config)
    config = _create_opensearch_config(cli_config)
    searcher = OpenSearchAgenticSearcher(client, config)

    try:
        if not json_output:
            display.header(
                "GnosisLLM Agentic Search",
                f"Query: {query[:50]}{'...' if len(query) > 50 else ''}",
            )

        # Build query
        agentic_query = AgenticSearchQuery(
            text=query,
            agent_type=AgentType.CONVERSATIONAL if agent_type == "conversational" else AgentType.FLOW,
            collection_ids=collection_list,
            source_ids=source_list,
            account_id=account_id,
            limit=limit,
            include_reasoning=verbose,
        )

        # Execute with loading spinner
        if not json_output:
            with display.loading_spinner("Agent thinking..."):
                result = await searcher.agentic_search(agentic_query, index_name)
        else:
            result = await searcher.agentic_search(agentic_query, index_name)

        # JSON output
        if json_output:
            output = {
                "query": result.query,
                "mode": "agentic",
                "agent_type": result.agent_type.value,
                "answer": result.answer,
                "total_hits": result.total_hits,
                "duration_ms": result.duration_ms,
                "conversation_id": result.conversation_id,
                "reasoning_steps": [
                    {
                        "tool": step.tool,
                        "action": step.action,
                        "input": step.input,
                        "output": step.output[:200] if step.output else None,
                    }
                    for step in result.reasoning_steps
                ] if verbose else [],
                "sources": [
                    {
                        "title": item.title,
                        "url": item.url,
                        "score": item.score,
                        "content": item.content[:300] if not verbose else item.content,
                    }
                    for item in result.items
                ],
            }
            print(json.dumps(output, indent=2, default=str))
            return output

        # Human-readable output
        display.agentic_result(
            answer=result.answer,
            sources=result.items,
            reasoning_steps=result.reasoning_steps if verbose else None,
            duration_ms=result.duration_ms,
            query=result.query,
            conversation_id=result.conversation_id,
            verbose=verbose,
        )

        return {"answer": result.answer, "sources": len(result.items)}

    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            display.format_error_with_suggestion(
                error=f"Agentic search failed: {e}",
                suggestion="Check that agents are configured and OpenSearch ML plugin is enabled.",
                command="gnosisllm-knowledge agentic status",
            )
        return None

    finally:
        await client.close()


def _show_chat_help(display: RichDisplayService) -> None:
    """Show chat help message."""
    help_content = """[bold]Available Commands:[/bold]

  [cyan]/new[/cyan], [cyan]/clear[/cyan]  - Start a new conversation
  [cyan]/quit[/cyan], [cyan]/exit[/cyan]  - Exit chat
  [cyan]/help[/cyan]           - Show this help message

[bold]Tips:[/bold]
  - Ask follow-up questions to continue the conversation
  - The agent remembers context from previous messages
  - Use specific questions for better answers"""

    display.panel(help_content, title="Chat Help", style="info")
