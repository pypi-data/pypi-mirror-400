"""Memory CLI commands for Agentic Memory management.

Commands:
- setup: Configure LLM and embedding models for memory
- container create/list/delete: Manage memory containers
- store: Store messages in memory
- recall: Search long-term memory
- stats: Show container statistics
- session list: List sessions in a container
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from gnosisllm_knowledge.api.memory import Memory
from gnosisllm_knowledge.backends.opensearch.memory.config import MemoryConfig
from gnosisllm_knowledge.backends.opensearch.memory.setup import MemorySetup
from gnosisllm_knowledge.cli.display.service import RichDisplayService, StepProgress
from gnosisllm_knowledge.cli.utils.config import CliConfig
from gnosisllm_knowledge.core.domain.memory import (
    MemoryStrategy,
    MemoryType,
    Message,
    StrategyConfig,
)

if TYPE_CHECKING:
    pass


def _create_memory_config(cli_config: CliConfig) -> MemoryConfig:
    """Create MemoryConfig from CLI config."""
    return MemoryConfig(
        host=cli_config.opensearch_host,
        port=cli_config.opensearch_port,
        username=cli_config.opensearch_username,
        password=cli_config.opensearch_password,
        use_ssl=cli_config.opensearch_use_ssl,
        verify_certs=cli_config.opensearch_verify_certs,
        llm_model_id=cli_config.memory_llm_model_id,
        embedding_model_id=cli_config.memory_embedding_model_id,
        openai_api_key=cli_config.openai_api_key,
        llm_model=cli_config.memory_llm_model,
        embedding_model=cli_config.memory_embedding_model,
        embedding_dimension=cli_config.memory_embedding_dimension,
    )


# === SETUP COMMAND ===


async def memory_setup_command(
    display: RichDisplayService,
    openai_key: str | None = None,
    llm_model: str = "gpt-4o",
    embedding_model: str = "text-embedding-3-small",
) -> None:
    """Setup OpenSearch for Agentic Memory.

    Creates the required LLM and embedding connectors and models
    for Agentic Memory to work.

    Args:
        display: Display service for output.
        openai_key: OpenAI API key (overrides env).
        llm_model: LLM model name for fact extraction.
        embedding_model: Embedding model name.
    """
    cli_config = CliConfig.from_env()

    # Use provided key or fall back to env
    api_key = openai_key or cli_config.openai_api_key

    if not api_key:
        display.format_error_with_suggestion(
            error="OpenAI API key is required for memory setup.",
            suggestion="Provide --openai-key or set OPENAI_API_KEY environment variable.",
            command="export OPENAI_API_KEY=sk-...",
        )
        sys.exit(1)

    display.header(
        "GnosisLLM Memory Setup",
        "Configuring Agentic Memory connectors and models",
    )

    # Show configuration
    display.table(
        "Configuration",
        [
            ("OpenSearch", f"{cli_config.opensearch_host}:{cli_config.opensearch_port}"),
            ("LLM Model", llm_model),
            ("Embedding Model", embedding_model),
        ],
    )
    display.newline()

    # Create memory config
    config = MemoryConfig(
        host=cli_config.opensearch_host,
        port=cli_config.opensearch_port,
        username=cli_config.opensearch_username,
        password=cli_config.opensearch_password,
        use_ssl=cli_config.opensearch_use_ssl,
        verify_certs=cli_config.opensearch_verify_certs,
        openai_api_key=api_key,
        llm_model=llm_model,
        embedding_model=embedding_model,
    )

    setup = MemorySetup(config)

    # Build progress steps
    steps = [
        StepProgress("llm_connector", "Create LLM connector for fact extraction"),
        StepProgress("llm_model", "Deploy LLM model"),
        StepProgress("embed_connector", "Create embedding connector"),
        StepProgress("embed_model", "Deploy embedding model"),
    ]
    progress = display.progress(steps)

    results: dict[str, str] = {}

    try:
        # LLM setup (connector + model)
        progress.update(0, "running")
        progress.update(1, "running")
        llm_model_id = await setup.setup_llm_model()
        results["llm_model_id"] = llm_model_id
        progress.complete(0)
        progress.complete(1)

        # Embedding setup (connector + model)
        progress.update(2, "running")
        progress.update(3, "running")
        embedding_model_id = await setup.setup_embedding_model()
        results["embedding_model_id"] = embedding_model_id
        progress.complete(2)
        progress.complete(3)

    except Exception as e:
        progress.stop()
        display.newline()
        display.format_error_with_suggestion(
            error=f"Memory setup failed: {e}",
            suggestion="Check OpenSearch connection and ML plugin configuration.",
        )
        sys.exit(1)

    progress.stop()
    display.newline()

    # Success panel with environment variables
    content = "[bold green]Setup complete![/bold green]\n\n"
    content += "[bold]Add to your .env file:[/bold]\n\n"
    content += f"  [green]OPENSEARCH_MEMORY_LLM_MODEL_ID={results['llm_model_id']}[/green]\n"
    content += f"  [green]OPENSEARCH_MEMORY_EMBEDDING_MODEL_ID={results['embedding_model_id']}[/green]\n"
    content += "\n[bold]Next steps:[/bold]\n"
    content += "  [dim]gnosisllm-knowledge memory container create my-memory[/dim]\n"
    content += "  [dim]gnosisllm-knowledge memory store <container-id> -f messages.json[/dim]"

    display.panel(content, title="Memory Setup Complete", style="success")


# === CONTAINER COMMANDS ===


async def container_create_command(
    display: RichDisplayService,
    name: str,
    description: str | None = None,
    config_file: str | None = None,
) -> None:
    """Create a new memory container.

    Args:
        display: Display service for output.
        name: Container name.
        description: Optional container description.
        config_file: Optional JSON config file with strategy configuration.
    """
    cli_config = CliConfig.from_env()

    # Validate configuration
    errors = cli_config.validate_for_memory()
    if errors:
        for error in errors:
            display.error(error)
        display.newline()
        display.format_error_with_suggestion(
            error="Memory is not configured.",
            suggestion="Run memory setup first.",
            command="gnosisllm-knowledge memory setup --openai-key sk-...",
        )
        sys.exit(1)

    display.header("Create Memory Container", f"Name: {name}")

    # Parse strategy config
    strategy_configs: list[StrategyConfig] = []

    if config_file:
        try:
            with open(config_file) as f:
                config_data = json.load(f)
            for s in config_data.get("strategies", []):
                strategy_configs.append(
                    StrategyConfig(
                        type=MemoryStrategy(s["type"]),
                        namespace=s["namespace"],
                    )
                )
            display.info(f"Loaded {len(strategy_configs)} strategies from {config_file}")
        except Exception as e:
            display.error(f"Failed to load config file: {e}")
            sys.exit(1)
    else:
        # Default strategy configuration
        strategy_configs = [
            StrategyConfig(type=MemoryStrategy.SEMANTIC, namespace=["user_id"]),
            StrategyConfig(type=MemoryStrategy.USER_PREFERENCE, namespace=["user_id"]),
            StrategyConfig(type=MemoryStrategy.SUMMARY, namespace=["session_id"]),
        ]
        display.info("[dim]Using default strategy configuration:[/dim]")
        display.console.print("  [cyan]SEMANTIC[/cyan], [cyan]USER_PREFERENCE[/cyan] -> scoped to user_id")
        display.console.print("  [cyan]SUMMARY[/cyan] -> scoped to session_id")
        display.newline()

    # Create container
    memory = Memory.from_config(_create_memory_config(cli_config))

    with display.loading_spinner("Creating container..."):
        try:
            container = await memory.create_container(
                name=name,
                description=description,
                strategies=strategy_configs,
            )
        except Exception as e:
            display.error(f"Failed to create container: {e}")
            sys.exit(1)

    display.newline()
    display.success(f"Container created: [cyan]{container.id}[/cyan]")
    display.console.print(f"  Name: {container.name}")
    display.console.print(f"  Strategies: {', '.join(s.value for s in container.strategies)}")
    display.newline()
    display.info(f"[dim]Use container ID for store/recall operations:[/dim]")
    display.console.print(f"  gnosisllm-knowledge memory store {container.id} -f messages.json")


async def container_list_command(
    display: RichDisplayService,
    json_output: bool = False,
) -> None:
    """List all memory containers.

    Args:
        display: Display service for output.
        json_output: Output as JSON.
    """
    cli_config = CliConfig.from_env()
    memory = Memory.from_config(_create_memory_config(cli_config))

    with display.loading_spinner("Fetching containers..."):
        try:
            containers = await memory.list_containers()
        except Exception as e:
            display.error(f"Failed to list containers: {e}")
            sys.exit(1)

    if json_output:
        output = [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "strategies": [s.value for s in c.strategies],
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in containers
        ]
        display.json_output({"containers": output, "total": len(containers)})
        return

    if not containers:
        display.warning("No containers found.")
        display.newline()
        display.info("Create a container with:")
        display.console.print("  gnosisllm-knowledge memory container create my-memory")
        return

    display.header("Memory Containers", f"{len(containers)} containers")

    rows = []
    for c in containers:
        strategies = ", ".join(s.value for s in c.strategies)
        created = c.created_at.strftime("%Y-%m-%d") if c.created_at else "-"
        rows.append((c.id[:12] + "...", c.name, strategies, created))

    display.table(
        "Containers",
        rows,
        headers=["ID", "Name", "Strategies", "Created"],
    )


async def container_delete_command(
    display: RichDisplayService,
    container_id: str,
    force: bool = False,
) -> None:
    """Delete a memory container.

    Args:
        display: Display service for output.
        container_id: Container ID to delete.
        force: Skip confirmation prompt.
    """
    cli_config = CliConfig.from_env()
    memory = Memory.from_config(_create_memory_config(cli_config))

    if not force:
        confirmed = display.confirm(
            f"[yellow]Delete container {container_id[:12]}...?[/yellow] This cannot be undone."
        )
        if not confirmed:
            display.info("Cancelled.")
            return

    with display.loading_spinner("Deleting container..."):
        try:
            deleted = await memory.delete_container(container_id)
        except Exception as e:
            display.error(f"Failed to delete container: {e}")
            sys.exit(1)

    if deleted:
        display.success(f"Container deleted: {container_id}")
    else:
        display.warning(f"Container not found: {container_id}")


# === STORE COMMAND ===


async def memory_store_command(
    display: RichDisplayService,
    container_id: str,
    file: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    infer: bool = True,
    json_output: bool = False,
) -> None:
    """Store conversation in memory.

    Args:
        display: Display service for output.
        container_id: Target container ID.
        file: JSON file with messages.
        user_id: User ID for namespace.
        session_id: Session ID for namespace.
        infer: Enable fact extraction (default: True).
        json_output: Output as JSON.
    """
    if not file:
        display.error("Provide --file with messages to store.")
        display.newline()
        display.info("Example messages.json:")
        display.console.print("""  {
    "messages": [
      {"role": "user", "content": "Hello, I'm Alice"},
      {"role": "assistant", "content": "Hello Alice!"}
    ]
  }""")
        sys.exit(1)

    cli_config = CliConfig.from_env()
    memory = Memory.from_config(_create_memory_config(cli_config))

    # Load messages from file
    try:
        with open(file) as f:
            data = json.load(f)
        messages = [Message(**m) for m in data.get("messages", [])]
    except Exception as e:
        display.error(f"Failed to load messages: {e}")
        sys.exit(1)

    if not messages:
        display.error("No messages found in file.")
        sys.exit(1)

    if not json_output:
        display.header("Store Memory", f"Container: {container_id[:12]}...")
        display.info(f"Messages: {len(messages)}")
        display.info(f"User ID: {user_id or '[dim]not set[/dim]'}")
        display.info(f"Session ID: {session_id or '[dim]not set[/dim]'}")
        display.info(f"Fact extraction: {'enabled' if infer else 'disabled'}")
        display.newline()

    with display.loading_spinner("Storing messages..."):
        try:
            result = await memory.store(
                container_id=container_id,
                messages=messages,
                user_id=user_id,
                session_id=session_id,
                infer=infer,
            )
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                display.error(f"Failed to store messages: {e}")
            sys.exit(1)

    if json_output:
        output = {
            "working_memory_id": result.working_memory_id,
            "session_id": result.session_id,
            "long_term_count": result.long_term_count,
            "infer": infer,
        }
        print(json.dumps(output, indent=2))
        return

    display.success("Messages stored!")
    display.console.print(f"  Working memory ID: [cyan]{result.working_memory_id}[/cyan]")
    if result.session_id:
        display.console.print(f"  Session ID: [cyan]{result.session_id}[/cyan]")
    if infer:
        display.newline()
        display.info("[dim]Fact extraction is running asynchronously...[/dim]")
        display.info("[dim]Use 'memory recall' to search extracted facts.[/dim]")


# === RECALL COMMAND ===


async def memory_recall_command(
    display: RichDisplayService,
    container_id: str,
    query: str,
    user_id: str | None = None,
    session_id: str | None = None,
    limit: int = 10,
    json_output: bool = False,
) -> None:
    """Search long-term memory.

    Args:
        display: Display service for output.
        container_id: Container ID to search.
        query: Search query text.
        user_id: Filter by user ID.
        session_id: Filter by session ID.
        limit: Maximum results.
        json_output: Output as JSON.
    """
    cli_config = CliConfig.from_env()
    memory = Memory.from_config(_create_memory_config(cli_config))

    if not json_output:
        display.header("Recall Memory", f"Query: {query[:50]}...")

    with display.loading_spinner("Searching memories..."):
        try:
            result = await memory.recall(
                container_id=container_id,
                query=query,
                user_id=user_id,
                session_id=session_id,
                limit=limit,
            )
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                display.error(f"Failed to search memories: {e}")
            sys.exit(1)

    if json_output:
        output = {
            "query": result.query,
            "total": result.total,
            "took_ms": result.took_ms,
            "items": [
                {
                    "id": e.id,
                    "content": e.content,
                    "strategy": e.strategy.value if e.strategy else None,
                    "score": e.score,
                    "namespace": e.namespace,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in result.items
            ],
        }
        print(json.dumps(output, indent=2, default=str))
        return

    display.console.print(f"[bold]Found {result.total} memories[/bold] ({result.took_ms}ms)")
    display.newline()

    if not result.items:
        display.warning("No memories found matching your query.")
        return

    for i, entry in enumerate(result.items, 1):
        strategy_tag = f"[cyan][{entry.strategy.value}][/cyan]" if entry.strategy else ""
        score_pct = entry.score * 100 if entry.score <= 1 else entry.score
        display.console.print(f"{i}. {strategy_tag} {entry.content}")
        display.console.print(f"   [dim]Score: {score_pct:.1f}%[/dim]")
        if entry.namespace:
            ns_str = ", ".join(f"{k}={v}" for k, v in entry.namespace.items())
            display.console.print(f"   [dim]Namespace: {ns_str}[/dim]")


# === STATS COMMAND ===


async def memory_stats_command(
    display: RichDisplayService,
    container_id: str,
    json_output: bool = False,
) -> None:
    """Show container statistics.

    Args:
        display: Display service for output.
        container_id: Container ID to get stats for.
        json_output: Output as JSON.
    """
    cli_config = CliConfig.from_env()
    memory = Memory.from_config(_create_memory_config(cli_config))

    with display.loading_spinner("Fetching statistics..."):
        try:
            stats = await memory.get_stats(container_id)
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                display.error(f"Failed to get stats: {e}")
            sys.exit(1)

    if json_output:
        output = {
            "container_id": stats.container_id,
            "container_name": stats.container_name,
            "working_memory_count": stats.working_memory_count,
            "long_term_memory_count": stats.long_term_memory_count,
            "session_count": stats.session_count,
            "strategies_breakdown": {
                k.value: v for k, v in stats.strategies_breakdown.items()
            } if stats.strategies_breakdown else {},
            "storage_size_bytes": stats.storage_size_bytes,
            "last_updated": stats.last_updated.isoformat() if stats.last_updated else None,
        }
        print(json.dumps(output, indent=2))
        return

    display.header(
        "Memory Statistics",
        f"Container: {stats.container_name} ({stats.container_id[:12]}...)",
    )

    display.table(
        "Memory Counts",
        [
            ("Working Memory", f"{stats.working_memory_count:,} messages"),
            ("Long-term Memory", f"{stats.long_term_memory_count:,} facts"),
            ("Sessions", f"{stats.session_count:,}"),
        ],
    )

    if stats.strategies_breakdown:
        display.newline()
        strategy_rows = [
            (strategy.value, f"{count:,} facts")
            for strategy, count in stats.strategies_breakdown.items()
        ]
        display.table("Strategy Breakdown", strategy_rows)


# === SESSION COMMANDS ===


async def session_list_command(
    display: RichDisplayService,
    container_id: str,
    user_id: str | None = None,
    limit: int = 20,
    json_output: bool = False,
) -> None:
    """List sessions in a container.

    Args:
        display: Display service for output.
        container_id: Container ID.
        user_id: Filter by user ID.
        limit: Maximum sessions to return.
        json_output: Output as JSON.
    """
    cli_config = CliConfig.from_env()
    memory = Memory.from_config(_create_memory_config(cli_config))

    with display.loading_spinner("Fetching sessions..."):
        try:
            sessions = await memory.list_sessions(
                container_id=container_id,
                user_id=user_id,
                limit=limit,
            )
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                display.error(f"Failed to list sessions: {e}")
            sys.exit(1)

    if json_output:
        output = {
            "sessions": [
                {
                    "id": s.id,
                    "summary": s.summary,
                    "namespace": s.namespace,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "message_count": s.message_count,
                }
                for s in sessions
            ],
            "total": len(sessions),
        }
        print(json.dumps(output, indent=2))
        return

    if not sessions:
        display.warning("No sessions found.")
        return

    display.header("Sessions", f"Container: {container_id[:12]}...")

    rows = []
    for s in sessions:
        started = s.started_at.strftime("%Y-%m-%d %H:%M") if s.started_at else "-"
        summary = (s.summary[:50] + "...") if s.summary and len(s.summary) > 50 else (s.summary or "-")
        rows.append((s.id[:12] + "...", summary, started))

    display.table("Sessions", rows, headers=["ID", "Summary", "Started"])


# === STATUS COMMAND ===


async def memory_status_command(
    display: RichDisplayService,
) -> None:
    """Show memory configuration status."""
    cli_config = CliConfig.from_env()

    display.header("GnosisLLM Memory Status", "Configuration and health")

    # Configuration status
    status_rows = []

    # LLM Model
    if cli_config.memory_llm_model_id:
        status_rows.append(("LLM Model", "[green]Configured[/green]"))
        status_rows.append(("  ID", f"[dim]{cli_config.memory_llm_model_id}[/dim]"))
    else:
        status_rows.append(("LLM Model", "[red]Not configured[/red]"))

    # Embedding Model
    if cli_config.memory_embedding_model_id:
        status_rows.append(("Embedding Model", "[green]Configured[/green]"))
        status_rows.append(("  ID", f"[dim]{cli_config.memory_embedding_model_id}[/dim]"))
    else:
        status_rows.append(("Embedding Model", "[red]Not configured[/red]"))

    # OpenSearch connection
    status_rows.append(("OpenSearch", f"{cli_config.opensearch_host}:{cli_config.opensearch_port}"))

    display.table("Memory Configuration", status_rows)

    # Check if setup is needed
    if not cli_config.memory_llm_model_id or not cli_config.memory_embedding_model_id:
        display.newline()
        display.format_error_with_suggestion(
            error="Memory is not fully configured.",
            suggestion="Run memory setup to create connectors and models.",
            command="gnosisllm-knowledge memory setup --openai-key sk-...",
        )
        return

    # Try to verify setup
    display.newline()

    config = _create_memory_config(cli_config)
    setup = MemorySetup(config)

    with display.loading_spinner("Verifying setup..."):
        try:
            status = await setup.verify_setup()
        except Exception as e:
            display.warning(f"Could not verify setup: {e}")
            return

    if status.is_ready:
        display.success("Memory is ready!")
        display.console.print("  All models are deployed and responding.")
    else:
        display.warning("Memory setup is incomplete:")
        for check, passed in status.checks.items():
            icon = "[green]ok[/green]" if passed else "[red]FAIL[/red]"
            display.console.print(f"  {check}: {icon}")
