"""Neoreader content fetcher for clean markdown extraction."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import httpx

from gnosisllm_knowledge.core.exceptions import (
    ConnectionError,
    FetchError,
    TimeoutError,
)
from gnosisllm_knowledge.core.interfaces.fetcher import FetchResult
from gnosisllm_knowledge.fetchers.config import NeoreaderConfig


class NeoreaderContentFetcher:
    """Content fetcher using Neoreader for clean markdown extraction.

    Neoreader converts web pages to clean markdown, removing navigation,
    ads, and other noise. This produces much better content for RAG
    systems compared to raw HTML.

    Example:
        ```python
        config = NeoreaderConfig.from_env()
        fetcher = NeoreaderContentFetcher(config)
        result = await fetcher.fetch("https://example.com/page")
        print(result.content)  # Clean markdown
        ```
    """

    def __init__(self, config: NeoreaderConfig | None = None) -> None:
        """Initialize the fetcher.

        Args:
            config: Neoreader configuration. Uses environment variables if not provided.
        """
        self._config = config or NeoreaderConfig.from_env()
        self._logger = logging.getLogger(__name__)

    async def fetch(self, url: str, **options: Any) -> FetchResult:
        """Fetch content from a URL using Neoreader.

        Args:
            url: The URL to fetch.
            **options: Additional options:
                - target_selector: CSS selector for content
                - remove_selector: CSS selector for removal
                - timeout: Override default timeout

        Returns:
            FetchResult with markdown content.

        Raises:
            FetchError: If the fetch fails.
            TimeoutError: If the request times out.
            ConnectionError: If Neoreader is not available.
        """
        timeout = options.get("timeout", self._config.timeout)
        target_selector = options.get("target_selector", self._config.target_selector)
        remove_selector = options.get("remove_selector", self._config.remove_selector)

        headers = {
            "Accept": "text/markdown",
            "X-Respond-With": "markdown",
        }

        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"

        if target_selector:
            headers["X-Target-Selector"] = target_selector
        if remove_selector:
            headers["X-Remove-Selector"] = remove_selector
        if timeout:
            headers["X-Timeout"] = str(int(timeout * 1000))

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    f"{self._config.host}/{url}",
                    headers=headers,
                )
                response.raise_for_status()

                content = response.text
                title = self._extract_title(content)

                return FetchResult(
                    content=content,
                    status_code=response.status_code,
                    content_type="text/markdown",
                    url=url,
                    title=title,
                    encoding="utf-8",
                    headers=dict(response.headers),
                )

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request timed out after {timeout}s",
                timeout=timeout,
                operation="fetch",
                cause=e,
            ) from e
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Cannot connect to Neoreader at {self._config.host}",
                host=self._config.host,
                cause=e,
            ) from e
        except httpx.HTTPStatusError as e:
            raise FetchError(
                f"HTTP {e.response.status_code}",
                source=url,
                status_code=e.response.status_code,
                cause=e,
            ) from e
        except Exception as e:
            raise FetchError(str(e), source=url, cause=e) from e

    async def health_check(self) -> bool:
        """Check if Neoreader service is available.

        Returns:
            True if Neoreader is responding, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try to reach the Neoreader health endpoint or root
                response = await client.get(f"{self._config.host}/health")
                return response.status_code < 500
        except Exception:
            try:
                # Fallback to root endpoint
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(self._config.host)
                    return response.status_code < 500
            except Exception:
                return False

    async def fetch_batch(
        self,
        urls: list[str],
        max_concurrent: int = 10,
        **options: Any,
    ) -> list[FetchResult | Exception]:
        """Fetch multiple URLs concurrently.

        Args:
            urls: List of URLs to fetch.
            max_concurrent: Maximum concurrent requests.
            **options: Options passed to each fetch call.

        Returns:
            List of FetchResult objects or Exception for failed fetches.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_limit(url: str) -> FetchResult | Exception:
            async with semaphore:
                try:
                    return await self.fetch(url, **options)
                except Exception as e:
                    return e

        results = await asyncio.gather(
            *[fetch_with_limit(url) for url in urls],
        )

        return list(results)

    def _extract_title(self, content: str) -> str | None:
        """Extract title from markdown content.

        Looks for the first H1 heading in the markdown.

        Args:
            content: Markdown content.

        Returns:
            Title string or None.
        """
        # Look for first H1 heading
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()

        # Try regex for H1
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        return None
