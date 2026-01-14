"""Streaming interfaces for memory-efficient processing.

These protocols define contracts for streaming operations that process
data in bounded batches rather than loading everything into memory.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.domain.document import Document
    from gnosisllm_knowledge.core.domain.result import IndexResult


class IStreamingUrlDiscoverer(Protocol):
    """Protocol for streaming URL discovery.

    Implementations yield URLs as they are discovered rather than
    collecting all URLs first. This enables processing to begin
    immediately and keeps memory usage bounded.

    Example:
        ```python
        discoverer: IStreamingUrlDiscoverer = StreamingSitemapDiscoverer()

        async for url_batch in discoverer.discover_urls_streaming(
            source="https://example.com/sitemap.xml",
            batch_size=50,
        ):
            for url in url_batch:
                await process(url)
        ```
    """

    async def discover_urls_streaming(
        self,
        source: str,
        batch_size: int = 100,
        **options: Any,
    ) -> AsyncIterator[list[str]]:
        """Yield batches of discovered URLs.

        Args:
            source: The sitemap or source URL.
            batch_size: Number of URLs per batch.
            **options: Discoverer-specific options (max_urls, patterns, etc.)

        Yields:
            Batches of discovered URLs as they're found.
        """
        ...


class IStreamingLoader(Protocol):
    """Protocol for streaming content loading.

    Processes URLs in bounded batches with immediate indexing,
    preventing memory accumulation.
    """

    async def load_streaming_with_indexing(
        self,
        source: str,
        index_callback: Callable[[list[Document]], Awaitable[IndexResult]],
        url_batch_size: int = 50,
        doc_batch_size: int = 100,
        **options: Any,
    ) -> IndexResult:
        """Load and index with streaming, calling callback for each batch.

        This method:
        1. Discovers URLs in batches (not all at once)
        2. Fetches content for each URL batch
        3. Indexes documents immediately after fetching
        4. Moves to next batch only after indexing completes

        Memory usage is bounded by:
        - url_batch_size * avg_url_length (URL strings)
        - doc_batch_size * avg_doc_size (document content)
        - fetch_concurrency * avg_page_size (in-flight fetches)

        Args:
            source: Source URL.
            index_callback: Called with each batch of documents to index.
            url_batch_size: URLs to process per iteration.
            doc_batch_size: Documents per index batch.
            **options: Additional options.

        Returns:
            Aggregated index result.
        """
        ...


class IStreamingPipeline(Protocol):
    """Protocol for streaming indexing pipelines.

    Orchestrates the full streaming load -> index pipeline with
    bounded memory guarantees.
    """

    async def execute(
        self,
        source: str,
        index_name: str,
        *,
        account_id: str | None = None,
        collection_id: str | None = None,
        source_id: str | None = None,
        **options: Any,
    ) -> IndexResult:
        """Execute the streaming pipeline.

        Args:
            source: Sitemap URL.
            index_name: Target OpenSearch index.
            account_id: For multi-tenancy filtering.
            collection_id: Collection within account.
            source_id: Source identifier.
            **options: Additional loader options.

        Returns:
            Aggregated index result.
        """
        ...
