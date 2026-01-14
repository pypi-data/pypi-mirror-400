"""Search command for querying indexed knowledge.

Supports multiple search modes:
- semantic: Meaning-based vector search using embeddings
- keyword: Traditional BM25 text matching
- hybrid: Combined semantic + keyword (default, best results)
- agentic: AI-powered search with reasoning and answer generation
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Any

from opensearchpy import AsyncOpenSearch
from rich.prompt import Prompt

from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.backends.opensearch.searcher import OpenSearchKnowledgeSearcher
from gnosisllm_knowledge.cli.display.service import RichDisplayService, SearchResultDisplay
from gnosisllm_knowledge.cli.utils.config import CliConfig
from gnosisllm_knowledge.core.domain.search import SearchMode, SearchQuery

if TYPE_CHECKING:
    pass


def _get_search_mode(mode: str) -> SearchMode:
    """Convert mode string to SearchMode enum."""
    mode_map = {
        "semantic": SearchMode.SEMANTIC,
        "keyword": SearchMode.KEYWORD,
        "hybrid": SearchMode.HYBRID,
        "agentic": SearchMode.AGENTIC,
    }
    return mode_map.get(mode.lower(), SearchMode.HYBRID)


async def search_command(
    display: RichDisplayService,
    query: str | None = None,
    mode: str = "hybrid",
    index_name: str = "knowledge",
    limit: int = 5,
    offset: int = 0,
    account_id: str | None = None,
    collection_ids: str | None = None,
    source_ids: str | None = None,
    min_score: float = 0.0,
    explain: bool = False,
    json_output: bool = False,
    interactive: bool = False,
    verbose: bool = False,
) -> None:
    """Execute the search command.

    Args:
        display: Display service for output.
        query: Search query text.
        mode: Search mode (semantic, keyword, hybrid, agentic).
        index_name: Index to search.
        limit: Maximum results to return.
        offset: Pagination offset.
        account_id: Filter by account ID.
        collection_ids: Filter by collection IDs (comma-separated).
        source_ids: Filter by source IDs (comma-separated).
        min_score: Minimum score threshold.
        explain: Show score explanation.
        json_output: Output as JSON for scripting.
        interactive: Interactive search session.
        verbose: Show full content (not truncated).
    """
    # Load configuration
    cli_config = CliConfig.from_env()

    # Validate configuration for semantic/hybrid search
    search_mode = _get_search_mode(mode)

    # Handle agentic mode - redirect to agentic search
    if search_mode == SearchMode.AGENTIC:
        from gnosisllm_knowledge.cli.commands.agentic import agentic_search_command

        result = await agentic_search_command(
            display=display,
            query=query or "",
            index_name=index_name,
            agent_type="flow",  # Default to flow for single queries
            account_id=account_id,
            collection_ids=collection_ids,
            source_ids=source_ids,
            limit=limit,
            json_output=json_output,
            verbose=verbose,
        )
        if not result and not json_output:
            sys.exit(1)
        return

    if search_mode in (SearchMode.SEMANTIC, SearchMode.HYBRID):
        if not cli_config.opensearch_model_id:
            if not json_output:
                display.format_error_with_suggestion(
                    error="OPENSEARCH_MODEL_ID is required for semantic/hybrid search.",
                    suggestion="Run setup first or use --mode keyword for basic search.",
                    command="gnosisllm-knowledge setup",
                )
            else:
                print(json.dumps({"error": "OPENSEARCH_MODEL_ID required"}))
            sys.exit(1)

    # Interactive mode
    if interactive:
        await _interactive_search(
            display=display,
            cli_config=cli_config,
            index_name=index_name,
            mode=mode,
            limit=limit,
            account_id=account_id,
            collection_ids=collection_ids,
            source_ids=source_ids,
            min_score=min_score,
            verbose=verbose,
        )
        return

    # Regular search requires query
    if not query:
        if not json_output:
            display.format_error_with_suggestion(
                error="Search query is required.",
                suggestion="Provide a query or use --interactive mode.",
                command='gnosisllm-knowledge search "your query here"',
            )
        else:
            print(json.dumps({"error": "Query required"}))
        sys.exit(1)

    # Execute single search
    result = await _execute_search(
        display=display,
        cli_config=cli_config,
        query=query,
        mode=mode,
        index_name=index_name,
        limit=limit,
        offset=offset,
        account_id=account_id,
        collection_ids=collection_ids,
        source_ids=source_ids,
        min_score=min_score,
        explain=explain,
        json_output=json_output,
        verbose=verbose,
    )

    if not result and not json_output:
        sys.exit(1)


async def _execute_search(
    display: RichDisplayService,
    cli_config: CliConfig,
    query: str,
    mode: str,
    index_name: str,
    limit: int,
    offset: int,
    account_id: str | None,
    collection_ids: str | None,
    source_ids: str | None,
    min_score: float,
    explain: bool,
    json_output: bool,
    verbose: bool,
) -> dict[str, Any] | None:
    """Execute a single search and display results."""
    # Parse filter lists
    collection_list = collection_ids.split(",") if collection_ids else None
    source_list = source_ids.split(",") if source_ids else None

    # Create OpenSearch client
    http_auth = None
    if cli_config.opensearch_username and cli_config.opensearch_password:
        http_auth = (cli_config.opensearch_username, cli_config.opensearch_password)

    client = AsyncOpenSearch(
        hosts=[{"host": cli_config.opensearch_host, "port": cli_config.opensearch_port}],
        http_auth=http_auth,
        use_ssl=cli_config.opensearch_use_ssl,
        verify_certs=cli_config.opensearch_verify_certs,
        ssl_show_warn=False,
    )

    try:
        # Create searcher config
        opensearch_config = OpenSearchConfig(
            host=cli_config.opensearch_host,
            port=cli_config.opensearch_port,
            username=cli_config.opensearch_username,
            password=cli_config.opensearch_password,
            use_ssl=cli_config.opensearch_use_ssl,
            verify_certs=cli_config.opensearch_verify_certs,
            model_id=cli_config.opensearch_model_id,
            search_pipeline_name=cli_config.opensearch_search_pipeline_name,
        )

        searcher = OpenSearchKnowledgeSearcher(client, opensearch_config)

        # Build search query
        search_query = SearchQuery(
            text=query,
            mode=_get_search_mode(mode),
            limit=limit,
            offset=offset,
            account_id=account_id,
            collection_ids=collection_list,
            source_ids=source_list,
            min_score=min_score,
            explain=explain,
            include_highlights=True,
        )

        # Execute search
        if not json_output:
            display.header(
                "GnosisLLM Knowledge Search",
                f"Query: {query[:50]}{'...' if len(query) > 50 else ''}",
            )

        try:
            result = await searcher.search(search_query, index_name)
        except Exception as e:
            if not json_output:
                display.format_error_with_suggestion(
                    error=f"Search failed: {e}",
                    suggestion="Check that OpenSearch is running and the index exists.",
                    command=f"gnosisllm-knowledge load <url> --index {index_name}",
                )
            else:
                print(json.dumps({"error": str(e)}))
            return None

        # JSON output
        if json_output:
            output = {
                "query": result.query,
                "mode": result.mode.value,
                "total_hits": result.total_hits,
                "duration_ms": result.duration_ms,
                "max_score": result.max_score,
                "results": [
                    {
                        "id": item.doc_id,
                        "title": item.title,
                        "content": item.content if verbose else item.content[:300],
                        "score": item.score,
                        "url": item.url,
                        "source": item.source,
                        "collection_id": item.collection_id,
                        "chunk_index": item.chunk_index,
                        "total_chunks": item.total_chunks,
                        "highlights": item.highlights,
                    }
                    for item in result.items
                ],
            }
            print(json.dumps(output, indent=2, default=str))
            return output

        # Human-readable output
        search_results = []
        for i, item in enumerate(result.items, 1):
            content_preview = item.content
            if not verbose and len(content_preview) > 200:
                content_preview = content_preview[:200] + "..."

            search_results.append(
                SearchResultDisplay(
                    rank=i,
                    title=item.title or "Untitled",
                    content_preview=content_preview,
                    score=item.score or 0.0,
                    url=item.url,
                    collection_id=item.collection_id,
                    highlights=item.highlights or [],
                )
            )

        display.search_results(
            results=search_results,
            query=result.query,
            total_hits=result.total_hits,
            duration_ms=result.duration_ms,
            mode=result.mode.value,
        )

        # Show tip for different modes
        if mode == "hybrid":
            display.newline()
            display.info(
                "[dim]Tip: Use --mode semantic for meaning-based, --mode keyword for exact match[/dim]"
            )

        return {"total_hits": result.total_hits, "duration_ms": result.duration_ms}

    finally:
        await client.close()


async def _interactive_search(
    display: RichDisplayService,
    cli_config: CliConfig,
    index_name: str,
    mode: str,
    limit: int,
    account_id: str | None,
    collection_ids: str | None,
    source_ids: str | None,
    min_score: float,
    verbose: bool,
) -> None:
    """Run interactive search session."""
    display.header(
        "GnosisLLM Knowledge Search (Interactive)",
        f"Index: {index_name} | Mode: {mode} | Press Ctrl+C to exit",
    )

    # Parse filter lists
    collection_list = collection_ids.split(",") if collection_ids else None
    source_list = source_ids.split(",") if source_ids else None

    # Create OpenSearch client
    http_auth = None
    if cli_config.opensearch_username and cli_config.opensearch_password:
        http_auth = (cli_config.opensearch_username, cli_config.opensearch_password)

    client = AsyncOpenSearch(
        hosts=[{"host": cli_config.opensearch_host, "port": cli_config.opensearch_port}],
        http_auth=http_auth,
        use_ssl=cli_config.opensearch_use_ssl,
        verify_certs=cli_config.opensearch_verify_certs,
        ssl_show_warn=False,
    )

    try:
        # Create searcher config
        opensearch_config = OpenSearchConfig(
            host=cli_config.opensearch_host,
            port=cli_config.opensearch_port,
            username=cli_config.opensearch_username,
            password=cli_config.opensearch_password,
            use_ssl=cli_config.opensearch_use_ssl,
            verify_certs=cli_config.opensearch_verify_certs,
            model_id=cli_config.opensearch_model_id,
            search_pipeline_name=cli_config.opensearch_search_pipeline_name,
        )

        searcher = OpenSearchKnowledgeSearcher(client, opensearch_config)

        last_results: list[Any] = []

        while True:
            try:
                display.newline()
                user_input = Prompt.ask("[bold cyan]Search[/bold cyan]")

                if not user_input:
                    continue

                # Check if user wants to view a result
                if user_input.isdigit():
                    idx = int(user_input) - 1
                    if 0 <= idx < len(last_results):
                        item = last_results[idx]
                        display.panel(
                            f"{item.content}\n\n"
                            f"[dim]URL: {item.url or 'N/A'}[/dim]\n"
                            f"[dim]Score: {item.score:.2%}[/dim]"
                            + (
                                f" | Chunk: {item.chunk_index + 1}/{item.total_chunks}"
                                if item.total_chunks
                                else ""
                            ),
                            title=item.title or "Document",
                            style="info",
                        )
                    else:
                        display.warning(f"Invalid selection. Enter 1-{len(last_results)}.")
                    continue

                # Execute search
                search_query = SearchQuery(
                    text=user_input,
                    mode=_get_search_mode(mode),
                    limit=limit,
                    offset=0,
                    account_id=account_id,
                    collection_ids=collection_list,
                    source_ids=source_list,
                    min_score=min_score,
                    highlight=True,
                )

                with display.loading_spinner("Searching..."):
                    result = await searcher.search(search_query, index_name)

                last_results = result.items

                if not result.items:
                    display.warning("No results found.")
                    continue

                # Display compact results
                display.info(f"Found {result.total_hits} results in {result.duration_ms:.1f}ms")
                display.newline()

                for i, item in enumerate(result.items, 1):
                    score_pct = (item.score or 0) * 100 if (item.score or 0) <= 1 else item.score
                    title = item.title or "Untitled"
                    display.console.print(
                        f"  [cyan]{i}.[/cyan] [bold]{title[:50]}[/bold] "
                        f"[dim]({score_pct:.1f}%)[/dim]"
                    )
                    if item.url:
                        display.console.print(f"     [blue]{item.url[:60]}[/blue]")

                display.newline()
                display.info("[dim]Enter number to view full content, or new query[/dim]")

            except KeyboardInterrupt:
                display.newline()
                display.info("Exiting interactive mode.")
                break
            except Exception as e:
                display.error(f"Search error: {e}")

    finally:
        await client.close()
