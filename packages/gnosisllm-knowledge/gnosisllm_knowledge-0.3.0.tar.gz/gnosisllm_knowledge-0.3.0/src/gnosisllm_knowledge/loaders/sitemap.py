"""Sitemap loader with recursive discovery and URL filtering."""

from __future__ import annotations

import asyncio
import fnmatch
import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any
from xml.etree import ElementTree

import httpx

from gnosisllm_knowledge.core.domain.document import Document
from gnosisllm_knowledge.core.domain.result import IndexResult
from gnosisllm_knowledge.core.events.types import SitemapDiscoveryEvent, UrlBatchProcessedEvent
from gnosisllm_knowledge.core.streaming.pipeline import PipelineConfig
from gnosisllm_knowledge.loaders.base import BaseLoader
from gnosisllm_knowledge.loaders.sitemap_streaming import StreamingSitemapDiscoverer

# XML namespace for sitemaps
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Default limits
DEFAULT_MAX_URLS = 1000
DEFAULT_MAX_DEPTH = 3


class SitemapLoader(BaseLoader):
    """Loader for sitemap XML files with recursive discovery.

    Features:
    - Recursive sitemap discovery (sitemap index files)
    - URL filtering with allow/block patterns
    - Configurable max URLs and depth limits
    - Parallel processing of nested sitemaps
    - Deduplication of discovered URLs

    Example:
        ```python
        loader = SitemapLoader(
            fetcher, chunker,
            config={
                "max_urls": 500,
                "max_depth": 2,
                "allowed_patterns": ["*/docs/*", "*/blog/*"],
                "blocked_patterns": ["*/admin/*"],
            }
        )
        result = await loader.load("https://example.com/sitemap.xml")
        ```
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the sitemap loader."""
        super().__init__(*args, **kwargs)
        self._sitemap_logger = logging.getLogger(f"{__name__}.SitemapLoader")

    @property
    def name(self) -> str:
        """Return the loader name."""
        return "sitemap"

    def supports(self, source: str) -> bool:
        """Check if this loader supports the given source.

        Supports URLs that look like sitemaps (contain 'sitemap' or end with .xml).

        Args:
            source: The source URL.

        Returns:
            True if this looks like a sitemap URL.
        """
        source_lower = source.lower()
        is_http = source_lower.startswith(("http://", "https://"))
        is_sitemap = "sitemap" in source_lower or source_lower.endswith(".xml")
        return is_http and is_sitemap

    async def _get_urls(self, source: str, **options: Any) -> list[str]:
        """Get list of URLs to process from the sitemap.

        Recursively discovers URLs from sitemap and sitemap index files.

        Args:
            source: The sitemap URL.
            **options: Loader-specific options:
                - max_urls: Maximum URLs to return
                - max_depth: Maximum recursion depth
                - allowed_patterns: URL patterns to include
                - blocked_patterns: URL patterns to exclude

        Returns:
            List of discovered and filtered URLs.
        """
        max_urls = options.get("max_urls", self._config.get("max_urls", DEFAULT_MAX_URLS))
        max_depth = options.get("max_depth", self._config.get("max_depth", DEFAULT_MAX_DEPTH))
        allowed_patterns = options.get(
            "allowed_patterns", self._config.get("allowed_patterns", [])
        )
        blocked_patterns = options.get(
            "blocked_patterns", self._config.get("blocked_patterns", [])
        )

        discovered_urls: set[str] = set()

        await self._discover_urls(
            sitemap_url=source,
            depth=0,
            max_depth=max_depth,
            max_urls=max_urls,
            discovered=discovered_urls,
            allowed_patterns=allowed_patterns,
            blocked_patterns=blocked_patterns,
        )

        # Convert to list and limit
        urls = list(discovered_urls)[:max_urls]
        self._sitemap_logger.info(f"Discovered {len(urls)} URLs from sitemap")

        return urls

    async def _discover_urls(
        self,
        sitemap_url: str,
        depth: int,
        max_depth: int,
        max_urls: int,
        discovered: set[str],
        allowed_patterns: list[str],
        blocked_patterns: list[str],
    ) -> None:
        """Recursively discover URLs from a sitemap.

        Args:
            sitemap_url: The sitemap URL to process.
            depth: Current recursion depth.
            max_depth: Maximum recursion depth.
            max_urls: Maximum URLs to discover.
            discovered: Set of already discovered URLs (modified in place).
            allowed_patterns: URL patterns to include.
            blocked_patterns: URL patterns to exclude.
        """
        if depth > max_depth:
            self._sitemap_logger.debug(f"Max depth {max_depth} reached, skipping {sitemap_url}")
            return

        if len(discovered) >= max_urls:
            self._sitemap_logger.debug(f"Max URLs {max_urls} reached")
            return

        try:
            content = await self._fetch_sitemap(sitemap_url)
            if not content:
                return

            root = ElementTree.fromstring(content)

            # Check if this is a sitemap index
            sitemap_refs = root.findall(".//sm:sitemap/sm:loc", SITEMAP_NS)
            if sitemap_refs:
                # This is a sitemap index - recursively process each sitemap
                self._sitemap_logger.info(
                    f"Found sitemap index with {len(sitemap_refs)} sitemaps at depth {depth}"
                )

                # Process nested sitemaps in parallel
                tasks = []
                for sitemap_ref in sitemap_refs:
                    if sitemap_ref.text and len(discovered) < max_urls:
                        tasks.append(
                            self._discover_urls(
                                sitemap_url=sitemap_ref.text.strip(),
                                depth=depth + 1,
                                max_depth=max_depth,
                                max_urls=max_urls,
                                discovered=discovered,
                                allowed_patterns=allowed_patterns,
                                blocked_patterns=blocked_patterns,
                            )
                        )

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                return

            # Process regular sitemap URLs
            url_elements = root.findall(".//sm:url/sm:loc", SITEMAP_NS)
            urls_added = 0

            for url_elem in url_elements:
                if url_elem.text and len(discovered) < max_urls:
                    url = url_elem.text.strip()

                    # Apply filters
                    if self._should_include_url(url, allowed_patterns, blocked_patterns):
                        if url not in discovered:
                            discovered.add(url)
                            urls_added += 1

            # Emit discovery event
            self._events.emit(
                SitemapDiscoveryEvent(
                    sitemap_url=sitemap_url,
                    urls_discovered=urls_added,
                    depth=depth,
                    total_urls=len(discovered),
                )
            )

            self._sitemap_logger.debug(
                f"Discovered {urls_added} URLs from {sitemap_url} at depth {depth}"
            )

        except Exception as e:
            self._sitemap_logger.error(f"Failed to process sitemap {sitemap_url}: {e}")

    async def _fetch_sitemap(self, url: str) -> str | None:
        """Fetch sitemap XML content.

        Args:
            url: The sitemap URL to fetch.

        Returns:
            Sitemap XML content or None if fetch failed.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers={"Accept": "application/xml, text/xml, */*"},
                    follow_redirects=True,
                )
                response.raise_for_status()
                return response.text
        except Exception as e:
            self._sitemap_logger.error(f"Failed to fetch sitemap {url}: {e}")
            return None

    def _should_include_url(
        self,
        url: str,
        allowed_patterns: list[str],
        blocked_patterns: list[str],
    ) -> bool:
        """Check if a URL should be included based on patterns.

        Args:
            url: The URL to check.
            allowed_patterns: Patterns that must match (if any).
            blocked_patterns: Patterns that must not match.

        Returns:
            True if URL should be included.
        """
        # Check blocked patterns first
        for pattern in blocked_patterns:
            if self._matches_pattern(url, pattern):
                return False

        # If allowed patterns specified, at least one must match
        if allowed_patterns:
            return any(self._matches_pattern(url, p) for p in allowed_patterns)

        return True

    def _matches_pattern(self, url: str, pattern: str) -> bool:
        """Check if URL matches a pattern.

        Supports both glob patterns (with *) and regex patterns.

        Args:
            url: The URL to check.
            pattern: The pattern to match against.

        Returns:
            True if URL matches the pattern.
        """
        # Try fnmatch for glob patterns
        if "*" in pattern or "?" in pattern:
            return fnmatch.fnmatch(url, pattern)

        # Try regex
        try:
            return bool(re.search(pattern, url))
        except re.error:
            # Invalid regex, try substring match
            return pattern in url

    async def load_streaming_with_indexing(
        self,
        source: str,
        index_callback: Callable[[list[Document]], Awaitable[IndexResult]],
        url_batch_size: int = 50,
        doc_batch_size: int = 100,
        config: PipelineConfig | None = None,
        **options: Any,
    ) -> IndexResult:
        """Load sitemap with streaming URL discovery and progressive indexing.

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
            source: Sitemap URL.
            index_callback: Called with each batch of documents to index.
            url_batch_size: URLs to process per iteration.
            doc_batch_size: Documents per index batch.
            config: Pipeline configuration.
            **options: Additional loader options.

        Returns:
            Aggregated IndexResult.
        """
        config = config or PipelineConfig(url_batch_size=url_batch_size)
        discoverer = StreamingSitemapDiscoverer(config=config)

        total_indexed = 0
        total_failed = 0
        all_errors: list[dict[str, Any]] = []
        batch_index = 0
        total_urls_processed = 0

        async for url_batch in discoverer.discover_urls_streaming(
            sitemap_url=source,
            batch_size=url_batch_size,
            max_urls=options.get("max_urls", 10000),
            max_depth=options.get("max_depth", 3),
            allowed_patterns=options.get("allowed_patterns", []),
            blocked_patterns=options.get("blocked_patterns", []),
        ):
            # Fetch content for this batch of URLs
            documents = await self._fetch_url_batch(url_batch, source, **options)
            total_urls_processed += len(url_batch)

            # Emit URL batch processed event
            self._events.emit(
                UrlBatchProcessedEvent(
                    batch_index=batch_index,
                    urls_in_batch=len(url_batch),
                    documents_created=len(documents),
                    total_urls_processed=total_urls_processed,
                )
            )

            # Index in sub-batches
            for i in range(0, len(documents), doc_batch_size):
                doc_batch = documents[i : i + doc_batch_size]
                result = await index_callback(doc_batch)
                total_indexed += result.indexed_count
                total_failed += result.failed_count
                if result.errors:
                    all_errors.extend(result.errors)

            # Memory freed: url_batch and documents go out of scope
            self._sitemap_logger.info(
                f"Processed URL batch {batch_index}: {len(url_batch)} URLs, "
                f"{len(documents)} docs, {total_indexed} total indexed"
            )
            batch_index += 1

        return IndexResult(
            success=total_failed == 0,
            indexed_count=total_indexed,
            failed_count=total_failed,
            errors=all_errors,
        )

    async def _fetch_url_batch(
        self,
        urls: list[str],
        source: str,
        **options: Any,
    ) -> list[Document]:
        """Fetch and chunk content for a batch of URLs.

        Args:
            urls: List of URLs to fetch.
            source: Original source identifier.
            **options: Loader options.

        Returns:
            List of Document objects from all URLs.
        """
        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def fetch_one(url: str) -> list[Document]:
            async with semaphore:
                return await self._load_url(url, source, **options)

        results = await asyncio.gather(
            *[fetch_one(url) for url in urls],
            return_exceptions=True,
        )

        documents: list[Document] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self._sitemap_logger.error(f"Failed to fetch {urls[i]}: {result}")
            elif isinstance(result, list):
                documents.extend(result)

        return documents
