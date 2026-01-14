"""Website loader for single URL loading."""

from __future__ import annotations

from typing import Any

from gnosisllm_knowledge.loaders.base import BaseLoader


class WebsiteLoader(BaseLoader):
    """Loader for single website URLs.

    This is the simplest loader that handles loading content from
    a single URL. For loading multiple URLs from a sitemap, use
    SitemapLoader instead.

    Example:
        ```python
        loader = WebsiteLoader(fetcher, chunker)
        result = await loader.load("https://example.com/page")
        ```
    """

    @property
    def name(self) -> str:
        """Return the loader name."""
        return "website"

    def supports(self, source: str) -> bool:
        """Check if this loader supports the given source.

        Supports HTTP and HTTPS URLs that don't look like sitemaps.

        Args:
            source: The source URL.

        Returns:
            True if this is a regular website URL.
        """
        source_lower = source.lower()
        is_http = source_lower.startswith(("http://", "https://"))
        is_sitemap = "sitemap" in source_lower or source_lower.endswith(".xml")
        return is_http and not is_sitemap

    async def _get_urls(self, source: str, **options: Any) -> list[str]:
        """Get list of URLs to process.

        For website loader, this simply returns the source URL.

        Args:
            source: The source URL.
            **options: Loader-specific options (ignored).

        Returns:
            List containing just the source URL.
        """
        return [source]
