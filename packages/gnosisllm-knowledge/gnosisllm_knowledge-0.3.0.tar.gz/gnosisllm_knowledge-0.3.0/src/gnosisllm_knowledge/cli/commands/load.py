"""Load command for indexing content from URLs or sitemaps.

Fetches content, chunks it for optimal embedding, and indexes
into OpenSearch with automatic embedding generation via ingest pipeline.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from opensearchpy import AsyncOpenSearch
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.backends.opensearch.indexer import OpenSearchIndexer
from gnosisllm_knowledge.chunking.sentence import SentenceChunker
from gnosisllm_knowledge.cli.display.service import RichDisplayService
from gnosisllm_knowledge.cli.utils.config import CliConfig
from gnosisllm_knowledge.core.domain.document import Document, DocumentStatus
from gnosisllm_knowledge.fetchers.config import NeoreaderConfig
from gnosisllm_knowledge.fetchers.neoreader import NeoreaderContentFetcher
from gnosisllm_knowledge.loaders.factory import LoaderFactory

if TYPE_CHECKING:
    pass


async def load_command(
    display: RichDisplayService,
    source: str,
    source_type: str | None = None,
    index_name: str = "knowledge",
    account_id: str | None = None,
    collection_id: str | None = None,
    source_id: str | None = None,
    batch_size: int = 100,
    max_urls: int = 1000,
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """Execute the load command.

    Args:
        display: Display service for output.
        source: URL or sitemap to load content from.
        source_type: Source type (website, sitemap) or auto-detect.
        index_name: Target index name.
        account_id: Multi-tenant account ID.
        collection_id: Collection grouping ID.
        source_id: Source identifier (defaults to URL).
        batch_size: Documents per indexing batch.
        max_urls: Maximum URLs to process from sitemap.
        force: Delete existing source documents first.
        dry_run: Preview without indexing.
        verbose: Show per-document progress.
    """
    # Load configuration
    cli_config = CliConfig.from_env()

    # Auto-detect source type
    detected_type = source_type
    if not detected_type:
        if "sitemap" in source.lower() or source.endswith(".xml"):
            detected_type = "sitemap"
        else:
            detected_type = "website"

    # Default source_id to URL
    final_source_id = source_id or source

    # Display header
    display.header(
        "GnosisLLM Knowledge Loader",
        f"Loading from: {source[:60]}{'...' if len(source) > 60 else ''}",
    )

    # Show configuration
    config_rows = [
        ("Source", source[:50] + "..." if len(source) > 50 else source),
        ("Type", f"{detected_type} {'(auto-detected)' if not source_type else ''}"),
        ("Target Index", index_name),
        ("Batch Size", str(batch_size)),
        ("Max URLs", str(max_urls) if detected_type == "sitemap" else "N/A"),
        ("Neoreader", cli_config.neoreader_host),
        ("OpenSearch", f"{cli_config.opensearch_host}:{cli_config.opensearch_port}"),
    ]

    if account_id:
        config_rows.append(("Account ID", account_id))
    if collection_id:
        config_rows.append(("Collection ID", collection_id))
    if force:
        config_rows.append(("Force Reload", "Yes"))
    if dry_run:
        config_rows.append(("Dry Run", "Yes (no indexing)"))

    display.table("Configuration", config_rows)
    display.newline()

    # Create fetcher
    neoreader_config = NeoreaderConfig(host=cli_config.neoreader_host)
    fetcher = NeoreaderContentFetcher(neoreader_config)

    # Check Neoreader health
    display.info("Checking Neoreader connection...")
    if await fetcher.health_check():
        display.success("Neoreader connected")
    else:
        display.warning(f"Cannot connect to Neoreader at {cli_config.neoreader_host}")
        display.info("Continuing with fallback HTTP fetcher...")

    # Create loader
    chunker = SentenceChunker()
    loader_factory = LoaderFactory(fetcher=fetcher, chunker=chunker)

    try:
        loader = loader_factory.create(detected_type)
    except ValueError as e:
        display.format_error_with_suggestion(
            error=f"Invalid source: {e}",
            suggestion="Check the URL format or specify --type explicitly.",
            command="gnosisllm-knowledge load <url> --type sitemap",
        )
        sys.exit(1)

    # Configure sitemap loader if applicable
    if detected_type == "sitemap":
        loader.max_urls = max_urls

    display.newline()

    # Discover URLs
    display.info("Discovering URLs...")
    with display.loading_spinner("Discovering..."):
        validation = await loader.validate_source(source)

    if not validation.valid:
        display.format_error_with_suggestion(
            error=f"Source validation failed: {validation.message}",
            suggestion="Check that the URL is accessible.",
        )
        sys.exit(1)

    # Load documents
    documents: list[Document] = []
    url_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=display.console,
    ) as progress:
        load_task = progress.add_task("Loading content...", total=None)

        async for doc in loader.load_streaming(source):
            documents.append(doc)
            url_count += 1
            progress.update(load_task, advance=1, description=f"Loading... ({url_count} docs)")

            if url_count >= max_urls and detected_type == "sitemap":
                break

        progress.update(load_task, completed=url_count)

    display.success(f"Loaded {len(documents)} documents")

    if not documents:
        display.warning("No documents found. Check the source URL.")
        sys.exit(0)

    # Dry run - stop here
    if dry_run:
        display.newline()
        display.panel(
            f"Documents found: {len(documents)}\n\n"
            "Sample URLs:\n"
            + "\n".join(f"  • {d.url}" for d in documents[:5])
            + (f"\n  ... and {len(documents) - 5} more" if len(documents) > 5 else ""),
            title="Dry Run Complete",
            style="info",
        )
        return

    # Chunk documents
    display.newline()
    display.info("Chunking documents for optimal embedding...")

    chunker = SentenceChunker()
    chunked_documents: list[Document] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=display.console,
    ) as progress:
        chunk_task = progress.add_task("Chunking...", total=len(documents))

        for doc in documents:
            chunks = chunker.chunk(doc.content)

            if len(chunks) == 1:
                # Single chunk - use original document
                chunked_doc = Document(
                    content=doc.content,
                    url=doc.url,
                    title=doc.title,
                    source=final_source_id,
                    account_id=account_id,
                    collection_id=collection_id,
                    source_id=final_source_id,
                    metadata=doc.metadata,
                    status=DocumentStatus.PENDING,
                )
                chunked_documents.append(chunked_doc)
            else:
                # Multiple chunks - create chunk documents
                for i, chunk in enumerate(chunks):
                    chunk_doc = Document(
                        content=chunk.content,
                        url=doc.url,
                        title=doc.title,
                        source=final_source_id,
                        account_id=account_id,
                        collection_id=collection_id,
                        source_id=final_source_id,
                        chunk_index=i,
                        total_chunks=len(chunks),
                        parent_doc_id=doc.doc_id,
                        metadata={**(doc.metadata or {}), "chunk_start": chunk.start_position},
                        status=DocumentStatus.PENDING,
                    )
                    chunked_documents.append(chunk_doc)

            progress.update(chunk_task, advance=1)

    display.success(f"Created {len(chunked_documents)} chunks from {len(documents)} documents")

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
        # Create indexer config
        opensearch_config = OpenSearchConfig(
            host=cli_config.opensearch_host,
            port=cli_config.opensearch_port,
            username=cli_config.opensearch_username,
            password=cli_config.opensearch_password,
            use_ssl=cli_config.opensearch_use_ssl,
            verify_certs=cli_config.opensearch_verify_certs,
            model_id=cli_config.opensearch_model_id,
            ingest_pipeline_name=cli_config.opensearch_pipeline_name,
        )

        indexer = OpenSearchIndexer(client, opensearch_config)

        # Ensure index exists
        display.newline()
        display.info(f"Ensuring index '{index_name}' exists...")

        try:
            created = await indexer.ensure_index(index_name)
            if created:
                display.success(f"Created index: {index_name}")
            else:
                display.info(f"Index already exists: {index_name}")
        except Exception as e:
            display.format_error_with_suggestion(
                error=f"Failed to ensure index: {e}",
                suggestion="Run 'gnosisllm-knowledge setup' first to configure OpenSearch.",
            )
            sys.exit(1)

        # Force delete existing if requested
        if force:
            display.info(f"Deleting existing documents from source: {final_source_id}")
            deleted = await indexer.delete_by_query(
                {"query": {"term": {"source_id": final_source_id}}},
                index_name,
            )
            if deleted > 0:
                display.info(f"Deleted {deleted} existing documents")

        # Index documents
        display.newline()
        display.info("Indexing documents...")

        indexed_count = 0
        failed_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=display.console,
        ) as progress:
            index_task = progress.add_task("Indexing...", total=len(chunked_documents))

            # Index in batches
            for i in range(0, len(chunked_documents), batch_size):
                batch = chunked_documents[i : i + batch_size]

                result = await indexer.bulk_index(batch, index_name, batch_size=batch_size)
                indexed_count += result.indexed_count
                failed_count += result.failed_count

                progress.update(index_task, advance=len(batch))

        # Refresh index to make documents searchable
        await indexer.refresh_index(index_name)

        display.newline()

        # Display results
        if failed_count == 0:
            display.panel(
                f"Documents Loaded:     [cyan]{len(documents)}[/cyan]\n"
                f"Chunks Created:       [cyan]{len(chunked_documents)}[/cyan]\n"
                f"Documents Indexed:    [green]{indexed_count}[/green]\n"
                f"Index:                [cyan]{index_name}[/cyan]\n\n"
                f"Verify with:\n"
                f'  [dim]gnosisllm-knowledge search "your query" --index {index_name}[/dim]',
                title="Loading Complete",
                style="success",
            )
        else:
            display.panel(
                f"Documents Loaded:     [cyan]{len(documents)}[/cyan]\n"
                f"Chunks Created:       [cyan]{len(chunked_documents)}[/cyan]\n"
                f"Documents Indexed:    [green]{indexed_count}[/green]\n"
                f"Documents Failed:     [red]{failed_count}[/red]\n"
                f"Index:                [cyan]{index_name}[/cyan]",
                title="Loading Complete (with errors)",
                style="warning",
            )
            sys.exit(1)

    finally:
        await client.close()
