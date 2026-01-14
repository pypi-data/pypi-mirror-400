"""Content fetcher protocol - Single Responsibility Principle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class FetchResult:
    """Result of a fetch operation.

    Attributes:
        content: The fetched content (usually text or markdown).
        status_code: HTTP status code or equivalent.
        content_type: MIME type of the content.
        url: The final URL after redirects.
        title: Extracted document title.
        metadata: Additional metadata from the fetch.
        encoding: Content encoding.
        headers: Response headers.
    """

    content: str
    status_code: int
    content_type: str
    url: str
    title: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    encoding: str | None = None
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Check if the fetch was successful."""
        return 200 <= self.status_code < 300

    @property
    def is_html(self) -> bool:
        """Check if the content is HTML."""
        return "html" in self.content_type.lower()

    @property
    def is_text(self) -> bool:
        """Check if the content is text."""
        return "text" in self.content_type.lower()

    @property
    def content_length(self) -> int:
        """Return the length of the content."""
        return len(self.content)


@runtime_checkable
class IContentFetcher(Protocol):
    """Protocol for fetching raw content from URLs.

    Content fetchers are responsible for:
    - Making HTTP requests to URLs
    - Converting content to a standard format (e.g., markdown)
    - Handling authentication and headers
    - Extracting metadata like titles

    Implementations should follow the Single Responsibility Principle
    and handle only content fetching, not parsing or chunking.
    """

    async def fetch(self, url: str, **options: Any) -> FetchResult:
        """Fetch content from a URL.

        Args:
            url: The URL to fetch.
            **options: Fetcher-specific options like:
                - target_selector: CSS selector for content extraction
                - remove_selector: CSS selector for elements to remove
                - timeout: Request timeout in seconds
                - headers: Additional HTTP headers

        Returns:
            FetchResult with content and metadata.

        Raises:
            ConnectionError: If the URL cannot be reached.
            TimeoutError: If the request times out.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the fetcher service is available.

        Returns:
            True if the service is healthy, False otherwise.
        """
        ...

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
        ...
