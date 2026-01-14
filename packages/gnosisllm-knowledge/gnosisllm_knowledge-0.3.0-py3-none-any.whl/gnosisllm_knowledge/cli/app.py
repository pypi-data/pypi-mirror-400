"""GnosisLLM Knowledge CLI Application.

Main entry point assembling all CLI commands with enterprise-grade UX.
"""

from __future__ import annotations

import asyncio
from typing import Annotated, Optional

import typer
from rich.console import Console

from gnosisllm_knowledge.cli.display import RichDisplayService
from gnosisllm_knowledge.cli.utils import CliConfig

# Main application
app = typer.Typer(
    name="gnosisllm-knowledge",
    help="Enterprise-grade knowledge loading, indexing, and semantic search.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# Shared console and display service
console = Console()
display = RichDisplayService(console)


def version_callback(value: bool) -> None:
    """Display version and exit."""
    if value:
        from gnosisllm_knowledge import __version__

        console.print(f"gnosisllm-knowledge [cyan]{__version__}[/cyan]")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """GnosisLLM Knowledge - Enterprise knowledge management CLI."""
    pass


# ============================================================================
# SETUP COMMAND
# ============================================================================


@app.command()
def setup(
    host: Annotated[
        Optional[str],
        typer.Option("--host", "-h", help="OpenSearch host (default: from OPENSEARCH_HOST env)."),
    ] = None,
    port: Annotated[
        Optional[int],
        typer.Option("--port", "-p", help="OpenSearch port (default: from OPENSEARCH_PORT env)."),
    ] = None,
    username: Annotated[
        Optional[str],
        typer.Option("--username", "-u", help="OpenSearch username."),
    ] = None,
    password: Annotated[
        Optional[str],
        typer.Option("--password", help="OpenSearch password."),
    ] = None,
    use_ssl: Annotated[
        Optional[bool],
        typer.Option("--use-ssl/--no-ssl", help="Enable/disable SSL (default: from OPENSEARCH_USE_SSL env)."),
    ] = None,
    verify_certs: Annotated[
        Optional[bool],
        typer.Option("--verify-certs/--no-verify-certs", help="Verify SSL certificates."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Clean up existing resources first."),
    ] = False,
    no_sample_data: Annotated[
        bool,
        typer.Option("--no-sample-data", help="Skip sample data ingestion."),
    ] = False,
    no_hybrid: Annotated[
        bool,
        typer.Option("--no-hybrid", help="Skip hybrid search pipeline."),
    ] = False,
) -> None:
    """Configure OpenSearch with ML model for neural search.

    Sets up the complete neural search infrastructure:
    - OpenAI connector for embeddings
    - Model group and deployed ML model
    - Ingest pipeline for automatic embedding generation
    - Search pipeline for hybrid scoring
    - Knowledge index with k-NN vector mapping

    [bold]Example:[/bold]
        $ gnosisllm-knowledge setup
        $ gnosisllm-knowledge setup --host opensearch.example.com --port 443 --use-ssl
        $ gnosisllm-knowledge setup --force  # Clean and recreate
    """
    from gnosisllm_knowledge.cli.commands.setup import setup_command

    asyncio.run(
        setup_command(
            display=display,
            host=host,
            port=port,
            username=username,
            password=password,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            force=force,
            no_sample_data=no_sample_data,
            no_hybrid=no_hybrid,
        )
    )


# ============================================================================
# LOAD COMMAND
# ============================================================================


@app.command()
def load(
    source: Annotated[
        str,
        typer.Argument(help="URL or sitemap to load content from."),
    ],
    source_type: Annotated[
        Optional[str],
        typer.Option(
            "--type",
            "-t",
            help="Source type: website, sitemap (auto-detects if not specified).",
        ),
    ] = None,
    index: Annotated[
        str,
        typer.Option("--index", "-i", help="Target index name."),
    ] = "knowledge",
    account_id: Annotated[
        Optional[str],
        typer.Option("--account-id", "-a", help="Multi-tenant account ID."),
    ] = None,
    collection_id: Annotated[
        Optional[str],
        typer.Option("--collection-id", "-c", help="Collection grouping ID."),
    ] = None,
    source_id: Annotated[
        Optional[str],
        typer.Option("--source-id", "-s", help="Source identifier (defaults to URL)."),
    ] = None,
    batch_size: Annotated[
        int,
        typer.Option("--batch-size", "-b", help="Documents per indexing batch."),
    ] = 100,
    max_urls: Annotated[
        int,
        typer.Option("--max-urls", "-m", help="Maximum URLs to process from sitemap."),
    ] = 1000,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Delete existing source documents first."),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview without indexing."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-V", help="Show per-document progress."),
    ] = False,
) -> None:
    """Load and index content from URLs or sitemaps.

    Fetches content, chunks it for optimal embedding, and indexes
    into OpenSearch with automatic embedding generation.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge load https://docs.example.com/intro
        $ gnosisllm-knowledge load https://example.com/sitemap.xml --type sitemap
        $ gnosisllm-knowledge load https://docs.example.com/sitemap.xml --max-urls 500
    """
    from gnosisllm_knowledge.cli.commands.load import load_command

    asyncio.run(
        load_command(
            display=display,
            source=source,
            source_type=source_type,
            index_name=index,
            account_id=account_id,
            collection_id=collection_id,
            source_id=source_id,
            batch_size=batch_size,
            max_urls=max_urls,
            force=force,
            dry_run=dry_run,
            verbose=verbose,
        )
    )


# ============================================================================
# SEARCH COMMAND
# ============================================================================


@app.command()
def search(
    query: Annotated[
        Optional[str],
        typer.Argument(help="Search query text."),
    ] = None,
    mode: Annotated[
        str,
        typer.Option(
            "--mode",
            "-m",
            help="Search mode: semantic, keyword, hybrid (default), agentic.",
        ),
    ] = "hybrid",
    index: Annotated[
        str,
        typer.Option("--index", "-i", help="Index to search."),
    ] = "knowledge",
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum results to return."),
    ] = 5,
    offset: Annotated[
        int,
        typer.Option("--offset", "-o", help="Pagination offset."),
    ] = 0,
    account_id: Annotated[
        Optional[str],
        typer.Option("--account-id", "-a", help="Filter by account ID."),
    ] = None,
    collection_ids: Annotated[
        Optional[str],
        typer.Option("--collection-ids", "-c", help="Filter by collection IDs (comma-separated)."),
    ] = None,
    source_ids: Annotated[
        Optional[str],
        typer.Option("--source-ids", "-s", help="Filter by source IDs (comma-separated)."),
    ] = None,
    min_score: Annotated[
        float,
        typer.Option("--min-score", help="Minimum score threshold (0.0-1.0)."),
    ] = 0.0,
    explain: Annotated[
        bool,
        typer.Option("--explain", "-e", help="Show score explanation."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON for scripting."),
    ] = False,
    interactive: Annotated[
        bool,
        typer.Option("--interactive", "-I", help="Interactive search session."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-V", help="Show full content (not truncated)."),
    ] = False,
) -> None:
    """Search indexed content with semantic, keyword, or hybrid modes.

    Supports multiple search strategies:
    - [cyan]semantic[/cyan]: Meaning-based vector search using embeddings
    - [cyan]keyword[/cyan]: Traditional BM25 text matching
    - [cyan]hybrid[/cyan]: Combined semantic + keyword (default, best results)
    - [cyan]agentic[/cyan]: AI-powered search with reasoning

    [bold]Example:[/bold]
        $ gnosisllm-knowledge search "how to configure auth"
        $ gnosisllm-knowledge search "API reference" --mode semantic --limit 10
        $ gnosisllm-knowledge search --interactive
    """
    from gnosisllm_knowledge.cli.commands.search import search_command

    asyncio.run(
        search_command(
            display=display,
            query=query,
            mode=mode,
            index_name=index,
            limit=limit,
            offset=offset,
            account_id=account_id,
            collection_ids=collection_ids,
            source_ids=source_ids,
            min_score=min_score,
            explain=explain,
            json_output=json_output,
            interactive=interactive,
            verbose=verbose,
        )
    )


# ============================================================================
# INFO COMMAND
# ============================================================================


@app.command()
def info() -> None:
    """Display configuration and environment information.

    Shows current settings from environment variables and
    validates connectivity to required services.
    """
    config = CliConfig.from_env()

    display.header("GnosisLLM Knowledge", "Configuration and Environment Info")

    display.table(
        "OpenSearch Configuration",
        [
            ("Host", f"{config.opensearch_host}:{config.opensearch_port}"),
            ("SSL", "Enabled" if config.opensearch_use_ssl else "Disabled"),
            ("Auth", "Configured" if config.opensearch_username else "None"),
            ("Model ID", config.opensearch_model_id or "[dim]Not set[/dim]"),
            ("Index", config.opensearch_index_name),
        ],
    )

    display.newline()

    display.table(
        "Embedding Configuration",
        [
            ("OpenAI Key", "✓ Set" if config.openai_api_key else "✗ Not set"),
            ("Model", config.openai_embedding_model),
            ("Dimension", str(config.openai_embedding_dimension)),
        ],
    )

    display.newline()

    display.table(
        "Agentic Search Configuration",
        [
            ("Flow Agent", config.opensearch_flow_agent_id or "[dim]Not set[/dim]"),
            ("Conversational Agent", config.opensearch_conversational_agent_id or "[dim]Not set[/dim]"),
            ("LLM Model", config.agentic_llm_model),
        ],
    )

    display.newline()

    display.table(
        "Agentic Memory Configuration",
        [
            ("LLM Model ID", config.memory_llm_model_id or "[dim]Not set[/dim]"),
            ("Embedding Model ID", config.memory_embedding_model_id or "[dim]Not set[/dim]"),
            ("LLM Model", config.memory_llm_model),
            ("Embedding Model", config.memory_embedding_model),
        ],
    )

    display.newline()

    display.table(
        "Content Fetching",
        [
            ("Neoreader", config.neoreader_host),
        ],
    )

    # Validation
    setup_errors = config.validate_for_setup()
    search_errors = config.validate_for_search()

    if setup_errors or search_errors:
        display.newline()
        display.warning("Configuration Issues:")
        for error in setup_errors + search_errors:
            display.error(f"  {error}")


# ============================================================================
# AGENTIC SUBCOMMAND GROUP
# ============================================================================

agentic_app = typer.Typer(
    name="agentic",
    help="AI-powered agentic search commands.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
app.add_typer(agentic_app, name="agentic")


@agentic_app.command("setup")
def agentic_setup(
    agent_type: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Agent type to setup: flow, conversational, or all (default).",
        ),
    ] = "all",
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force recreate existing agents."),
    ] = False,
) -> None:
    """Setup agentic search agents in OpenSearch.

    Creates and deploys AI agents for intelligent search:
    - [cyan]flow[/cyan]: Fast RAG for single-turn queries
    - [cyan]conversational[/cyan]: Multi-turn with memory support

    [bold]Example:[/bold]
        $ gnosisllm-knowledge agentic setup
        $ gnosisllm-knowledge agentic setup --type flow
        $ gnosisllm-knowledge agentic setup --force
    """
    from gnosisllm_knowledge.cli.commands.agentic import agentic_setup_command

    asyncio.run(
        agentic_setup_command(
            display=display,
            agent_type=agent_type,
            force=force,
        )
    )


@agentic_app.command("chat")
def agentic_chat(
    index: Annotated[
        str,
        typer.Option("--index", "-i", help="Index to search."),
    ] = "knowledge",
    agent_type: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Agent type: flow or conversational (default).",
        ),
    ] = "conversational",
    account_id: Annotated[
        Optional[str],
        typer.Option("--account-id", "-a", help="Filter by account ID."),
    ] = None,
    collection_ids: Annotated[
        Optional[str],
        typer.Option("--collection-ids", "-c", help="Filter by collection IDs (comma-separated)."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-V", help="Show reasoning steps."),
    ] = False,
) -> None:
    """Interactive agentic chat session.

    Start a conversation with the AI-powered knowledge assistant.
    The agent remembers context for multi-turn dialogue.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge agentic chat
        $ gnosisllm-knowledge agentic chat --type flow
        $ gnosisllm-knowledge agentic chat --verbose
    """
    from gnosisllm_knowledge.cli.commands.agentic import agentic_chat_command

    asyncio.run(
        agentic_chat_command(
            display=display,
            index_name=index,
            agent_type=agent_type,
            account_id=account_id,
            collection_ids=collection_ids,
            verbose=verbose,
        )
    )


@agentic_app.command("status")
def agentic_status() -> None:
    """Show agentic search configuration status.

    Displays configured agents and their health status.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge agentic status
    """
    from gnosisllm_knowledge.cli.commands.agentic import agentic_status_command

    asyncio.run(agentic_status_command(display=display))


# ============================================================================
# MEMORY SUBCOMMAND GROUP
# ============================================================================

memory_app = typer.Typer(
    name="memory",
    help="Agentic Memory management commands.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
app.add_typer(memory_app, name="memory")

# Container sub-subcommand
container_app = typer.Typer(
    name="container",
    help="Memory container management.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
memory_app.add_typer(container_app, name="container")

# Session sub-subcommand
session_app = typer.Typer(
    name="session",
    help="Session management.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
memory_app.add_typer(session_app, name="session")


@memory_app.command("setup")
def memory_setup(
    openai_key: Annotated[
        Optional[str],
        typer.Option("--openai-key", envvar="OPENAI_API_KEY", help="OpenAI API key for connector setup."),
    ] = None,
    llm_model: Annotated[
        str,
        typer.Option("--llm-model", help="LLM model for fact extraction."),
    ] = "gpt-4o",
    embedding_model: Annotated[
        str,
        typer.Option("--embedding-model", help="Embedding model name."),
    ] = "text-embedding-3-small",
) -> None:
    """Setup OpenSearch for Agentic Memory.

    Creates the required LLM and embedding connectors and models
    for Agentic Memory to work.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory setup --openai-key sk-...
        $ gnosisllm-knowledge memory setup --llm-model gpt-4o --embedding-model text-embedding-3-small
    """
    from gnosisllm_knowledge.cli.commands.memory import memory_setup_command

    asyncio.run(
        memory_setup_command(
            display=display,
            openai_key=openai_key,
            llm_model=llm_model,
            embedding_model=embedding_model,
        )
    )


@memory_app.command("status")
def memory_status() -> None:
    """Show memory configuration status.

    Displays configured models and verifies their health.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory status
    """
    from gnosisllm_knowledge.cli.commands.memory import memory_status_command

    asyncio.run(memory_status_command(display=display))


@memory_app.command("store")
def memory_store(
    container_id: Annotated[
        str,
        typer.Argument(help="Container ID to store messages in."),
    ],
    file: Annotated[
        Optional[str],
        typer.Option("--file", "-f", help="JSON file with messages."),
    ] = None,
    user_id: Annotated[
        Optional[str],
        typer.Option("--user-id", help="User ID for namespace."),
    ] = None,
    session_id: Annotated[
        Optional[str],
        typer.Option("--session-id", help="Session ID for namespace."),
    ] = None,
    infer: Annotated[
        bool,
        typer.Option("--infer/--no-infer", help="Enable/disable fact extraction."),
    ] = True,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON."),
    ] = False,
) -> None:
    """Store conversation in memory.

    Stores messages in working memory and optionally extracts facts
    to long-term memory using LLM inference.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory store <container-id> -f messages.json --user-id alice
        $ gnosisllm-knowledge memory store <container-id> -f messages.json --no-infer
    """
    from gnosisllm_knowledge.cli.commands.memory import memory_store_command

    asyncio.run(
        memory_store_command(
            display=display,
            container_id=container_id,
            file=file,
            user_id=user_id,
            session_id=session_id,
            infer=infer,
            json_output=json_output,
        )
    )


@memory_app.command("recall")
def memory_recall(
    container_id: Annotated[
        str,
        typer.Argument(help="Container ID to search."),
    ],
    query: Annotated[
        str,
        typer.Argument(help="Search query text."),
    ],
    user_id: Annotated[
        Optional[str],
        typer.Option("--user-id", help="Filter by user ID."),
    ] = None,
    session_id: Annotated[
        Optional[str],
        typer.Option("--session-id", help="Filter by session ID."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Maximum results."),
    ] = 10,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON."),
    ] = False,
) -> None:
    """Search long-term memory.

    Performs semantic search over extracted facts and memories.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory recall <container-id> "user preferences" --user-id alice
        $ gnosisllm-knowledge memory recall <container-id> "food preferences" --limit 5 --json
    """
    from gnosisllm_knowledge.cli.commands.memory import memory_recall_command

    asyncio.run(
        memory_recall_command(
            display=display,
            container_id=container_id,
            query=query,
            user_id=user_id,
            session_id=session_id,
            limit=limit,
            json_output=json_output,
        )
    )


@memory_app.command("stats")
def memory_stats(
    container_id: Annotated[
        str,
        typer.Argument(help="Container ID."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON."),
    ] = False,
) -> None:
    """Show container statistics.

    Displays memory counts, session count, and strategy breakdown.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory stats <container-id>
        $ gnosisllm-knowledge memory stats <container-id> --json
    """
    from gnosisllm_knowledge.cli.commands.memory import memory_stats_command

    asyncio.run(
        memory_stats_command(
            display=display,
            container_id=container_id,
            json_output=json_output,
        )
    )


# === Container Commands ===


@container_app.command("create")
def container_create(
    name: Annotated[
        str,
        typer.Argument(help="Container name."),
    ],
    description: Annotated[
        Optional[str],
        typer.Option("--description", "-d", help="Container description."),
    ] = None,
    config_file: Annotated[
        Optional[str],
        typer.Option("--config", "-c", help="JSON file with strategy configuration."),
    ] = None,
) -> None:
    """Create a new memory container.

    Containers hold memories with configurable extraction strategies.
    Each strategy is scoped to namespace fields for partitioning.

    [bold]Example config.json:[/bold]
        {
          "strategies": [
            {"type": "SEMANTIC", "namespace": ["user_id"]},
            {"type": "USER_PREFERENCE", "namespace": ["user_id"]},
            {"type": "SUMMARY", "namespace": ["session_id"]}
          ]
        }

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory container create my-memory
        $ gnosisllm-knowledge memory container create agent-memory -c config.json
    """
    from gnosisllm_knowledge.cli.commands.memory import container_create_command

    asyncio.run(
        container_create_command(
            display=display,
            name=name,
            description=description,
            config_file=config_file,
        )
    )


@container_app.command("list")
def container_list(
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON."),
    ] = False,
) -> None:
    """List all memory containers.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory container list
        $ gnosisllm-knowledge memory container list --json
    """
    from gnosisllm_knowledge.cli.commands.memory import container_list_command

    asyncio.run(
        container_list_command(
            display=display,
            json_output=json_output,
        )
    )


@container_app.command("delete")
def container_delete(
    container_id: Annotated[
        str,
        typer.Argument(help="Container ID to delete."),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt."),
    ] = False,
) -> None:
    """Delete a memory container.

    This permanently deletes the container and all its memories.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory container delete <container-id>
        $ gnosisllm-knowledge memory container delete <container-id> --force
    """
    from gnosisllm_knowledge.cli.commands.memory import container_delete_command

    asyncio.run(
        container_delete_command(
            display=display,
            container_id=container_id,
            force=force,
        )
    )


# === Session Commands ===


@session_app.command("list")
def session_list(
    container_id: Annotated[
        str,
        typer.Argument(help="Container ID."),
    ],
    user_id: Annotated[
        Optional[str],
        typer.Option("--user-id", help="Filter by user ID."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Maximum sessions."),
    ] = 20,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON."),
    ] = False,
) -> None:
    """List sessions in a container.

    [bold]Example:[/bold]
        $ gnosisllm-knowledge memory session list <container-id>
        $ gnosisllm-knowledge memory session list <container-id> --user-id alice
    """
    from gnosisllm_knowledge.cli.commands.memory import session_list_command

    asyncio.run(
        session_list_command(
            display=display,
            container_id=container_id,
            user_id=user_id,
            limit=limit,
            json_output=json_output,
        )
    )


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
