"""Streaming sitemap discovery with bounded memory.

This module provides streaming URL discovery from sitemaps, yielding
batches of URLs as they're discovered rather than collecting all URLs
first. This enables immediate processing and keeps memory bounded.
"""

from __future__ import annotations

import asyncio
import fnmatch
import logging
import re
from collections.abc import AsyncIterator
from typing import Any
from xml.etree import ElementTree

import httpx

from gnosisllm_knowledge.core.streaming.pipeline import BoundedQueue, PipelineConfig

# XML namespace for sitemaps
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class StreamingSitemapDiscoverer:
    """Discovers sitemap URLs in a streaming fashion.

    Instead of collecting all URLs before processing, this yields
    batches of URLs as they're discovered, enabling immediate processing.

    Key differences from SitemapLoader._get_urls():
    - Yields batches instead of returning complete list
    - Uses bounded queue for backpressure
    - Memory usage is O(batch_size) not O(total_urls)

    Example:
        ```python
        discoverer = StreamingSitemapDiscoverer()

        async for url_batch in discoverer.discover_urls_streaming(
            sitemap_url="https://example.com/sitemap.xml",
            batch_size=50,
            max_urls=1000,
        ):
            # Process batch immediately
            for url in url_batch:
                await fetch_and_process(url)
        ```
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
    ) -> None:
        """Initialize the streaming sitemap discoverer.

        Args:
            config: Pipeline configuration with batch sizes and concurrency.
        """
        self._config = config or PipelineConfig()
        self._logger = logging.getLogger(__name__)

    async def discover_urls_streaming(
        self,
        sitemap_url: str,
        batch_size: int | None = None,
        max_urls: int = 10000,
        max_depth: int = 3,
        allowed_patterns: list[str] | None = None,
        blocked_patterns: list[str] | None = None,
        **options: Any,
    ) -> AsyncIterator[list[str]]:
        """Yield batches of URLs as they're discovered.

        Args:
            sitemap_url: Root sitemap URL.
            batch_size: URLs per batch (default from config).
            max_urls: Maximum total URLs to discover.
            max_depth: Maximum sitemap recursion depth.
            allowed_patterns: URL patterns to include.
            blocked_patterns: URL patterns to exclude.
            **options: Additional options (unused, for compatibility).

        Yields:
            Lists of discovered URLs, batch_size at a time.
        """
        batch_size = batch_size or self._config.url_batch_size
        allowed_patterns = allowed_patterns or []
        blocked_patterns = blocked_patterns or []

        # Use bounded queue for discovered URLs
        # Queue size is 2x batch_size to allow producer to stay ahead
        url_queue: BoundedQueue[str] = BoundedQueue(maxsize=batch_size * 2)

        # Tracking state
        discovered_count = 0
        seen_urls: set[str] = set()

        async def discover_recursive(url: str, depth: int) -> None:
            """Recursively discover URLs, pushing to queue."""
            nonlocal discovered_count

            if depth > max_depth or discovered_count >= max_urls:
                return

            content = await self._fetch_sitemap(url)
            if not content:
                return

            try:
                root = ElementTree.fromstring(content)
            except ElementTree.ParseError as e:
                self._logger.error(f"Failed to parse sitemap {url}: {e}")
                return

            # Check for sitemap index
            sitemap_refs = root.findall(".//sm:sitemap/sm:loc", SITEMAP_NS)
            if sitemap_refs:
                self._logger.info(
                    f"Found sitemap index with {len(sitemap_refs)} sitemaps at depth {depth}"
                )
                # Process nested sitemaps (limited parallelism to avoid overwhelming)
                tasks = []
                for ref in sitemap_refs[:10]:  # Limit parallel sitemap fetches
                    if ref.text and discovered_count < max_urls:
                        tasks.append(discover_recursive(ref.text.strip(), depth + 1))
                await asyncio.gather(*tasks, return_exceptions=True)
                return

            # Process URL entries
            url_elements = root.findall(".//sm:url/sm:loc", SITEMAP_NS)
            for url_elem in url_elements:
                if url_elem.text and discovered_count < max_urls:
                    page_url = url_elem.text.strip()

                    if page_url in seen_urls:
                        continue

                    if not self._should_include_url(
                        page_url, allowed_patterns, blocked_patterns
                    ):
                        continue

                    seen_urls.add(page_url)
                    await url_queue.put(page_url)  # Backpressure if queue full
                    discovered_count += 1

                    if discovered_count % 100 == 0:
                        self._logger.debug(f"Discovered {discovered_count} URLs so far")

        async def discover_and_close() -> None:
            """Run discovery and close queue when done."""
            try:
                await discover_recursive(sitemap_url, depth=0)
            except Exception as e:
                self._logger.error(f"Discovery error: {e}")
            finally:
                url_queue.close()

        # Start discovery in background task
        discovery_task = asyncio.create_task(discover_and_close())

        # Yield batches from queue
        batch: list[str] = []
        try:
            async for url in url_queue:
                batch.append(url)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []

            # Yield remaining URLs
            if batch:
                yield batch

        finally:
            # Ensure discovery task is complete or cancelled
            if not discovery_task.done():
                discovery_task.cancel()
                try:
                    await discovery_task
                except asyncio.CancelledError:
                    pass

    async def _fetch_sitemap(self, url: str) -> str | None:
        """Fetch sitemap XML content.

        Args:
            url: The sitemap URL to fetch.

        Returns:
            Sitemap XML content or None if fetch failed.
        """
        try:
            async with httpx.AsyncClient(
                timeout=self._config.fetch_timeout_seconds
            ) as client:
                response = await client.get(
                    url,
                    headers={"Accept": "application/xml, text/xml, */*"},
                    follow_redirects=True,
                )
                response.raise_for_status()
                return response.text
        except Exception as e:
            self._logger.error(f"Failed to fetch sitemap {url}: {e}")
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
