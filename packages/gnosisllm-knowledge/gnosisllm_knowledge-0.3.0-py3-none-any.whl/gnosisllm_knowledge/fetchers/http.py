"""Generic HTTP content fetcher."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import httpx

from gnosisllm_knowledge.core.exceptions import FetchError, TimeoutError
from gnosisllm_knowledge.core.interfaces.fetcher import FetchResult
from gnosisllm_knowledge.fetchers.config import FetcherConfig


class HTTPContentFetcher:
    """Generic HTTP content fetcher.

    Fetches raw content from URLs using HTTP requests. For better
    content extraction (converting HTML to markdown), use
    NeoreaderContentFetcher instead.

    Example:
        ```python
        fetcher = HTTPContentFetcher()
        result = await fetcher.fetch("https://example.com/page")
        print(result.content)
        ```
    """

    def __init__(self, config: FetcherConfig | None = None) -> None:
        """Initialize the fetcher.

        Args:
            config: Optional fetcher configuration.
        """
        self._config = config or FetcherConfig()
        self._logger = logging.getLogger(__name__)

    async def fetch(self, url: str, **options: Any) -> FetchResult:
        """Fetch content from a URL.

        Args:
            url: The URL to fetch.
            **options: Additional options:
                - timeout: Override default timeout
                - headers: Additional headers

        Returns:
            FetchResult with content and metadata.

        Raises:
            FetchError: If the fetch fails.
            TimeoutError: If the request times out.
        """
        timeout = options.get("timeout", self._config.timeout)
        extra_headers = options.get("headers", {})

        headers = {
            "User-Agent": self._config.user_agent,
            **self._config.headers,
            **extra_headers,
        }

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                content = response.text
                content_type = response.headers.get("content-type", "text/html")
                title = self._extract_title(content, content_type)

                return FetchResult(
                    content=content,
                    status_code=response.status_code,
                    content_type=content_type,
                    url=str(response.url),  # Final URL after redirects
                    title=title,
                    encoding=response.encoding,
                    headers=dict(response.headers),
                )

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request timed out after {timeout}s",
                timeout=timeout,
                operation="fetch",
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
        """Check if HTTP requests can be made.

        Returns:
            True (HTTP fetcher is always "healthy").
        """
        return True

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

    def _extract_title(self, content: str, content_type: str) -> str | None:
        """Extract title from content.

        Args:
            content: The fetched content.
            content_type: Content MIME type.

        Returns:
            Extracted title or None.
        """
        if "html" not in content_type.lower():
            return None

        # Try to extract from <title> tag
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()

        # Try to extract from <h1> tag
        h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()

        return None
