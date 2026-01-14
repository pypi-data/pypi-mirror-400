"""Source configuration domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceConfig:
    """Configuration for a content source.

    Attributes:
        url: The source URL or path.
        source_type: Type of source (website, sitemap, file, etc.).
        options: Additional loader-specific options.

        Sitemap-specific options:
            max_urls: Maximum number of URLs to process.
            max_depth: Maximum sitemap recursion depth.
            allowed_patterns: URL patterns to include.
            blocked_patterns: URL patterns to exclude.

        Fetcher options:
            target_selector: CSS selector for content extraction.
            remove_selector: CSS selector for elements to remove.
            timeout: Request timeout in seconds.

        Multi-tenancy:
            account_id: Account/tenant identifier.
            collection_id: Collection identifier.
            source_id: Source identifier within collection.
    """

    url: str
    source_type: str = "website"
    options: dict[str, Any] = field(default_factory=dict)

    # Sitemap-specific options
    max_urls: int | None = None
    max_depth: int | None = None
    allowed_patterns: list[str] = field(default_factory=list)
    blocked_patterns: list[str] = field(default_factory=list)

    # Fetcher options
    target_selector: str | None = None
    remove_selector: str | None = None
    timeout: int | None = None

    # Multi-tenancy
    account_id: str | None = None
    collection_id: str | None = None
    source_id: str | None = None

    def with_options(self, **options: Any) -> SourceConfig:
        """Create a copy with additional options merged.

        Args:
            **options: Options to merge into the config.

        Returns:
            New SourceConfig with merged options.
        """
        merged_options = {**self.options, **options}
        return SourceConfig(
            url=self.url,
            source_type=self.source_type,
            options=merged_options,
            max_urls=self.max_urls,
            max_depth=self.max_depth,
            allowed_patterns=self.allowed_patterns.copy(),
            blocked_patterns=self.blocked_patterns.copy(),
            target_selector=self.target_selector,
            remove_selector=self.remove_selector,
            timeout=self.timeout,
            account_id=self.account_id,
            collection_id=self.collection_id,
            source_id=self.source_id,
        )

    def with_tenant(
        self,
        account_id: str,
        collection_id: str | None = None,
        source_id: str | None = None,
    ) -> SourceConfig:
        """Create a copy with tenant information.

        Args:
            account_id: Account/tenant identifier.
            collection_id: Collection identifier.
            source_id: Source identifier.

        Returns:
            New SourceConfig with tenant information.
        """
        return SourceConfig(
            url=self.url,
            source_type=self.source_type,
            options=self.options.copy(),
            max_urls=self.max_urls,
            max_depth=self.max_depth,
            allowed_patterns=self.allowed_patterns.copy(),
            blocked_patterns=self.blocked_patterns.copy(),
            target_selector=self.target_selector,
            remove_selector=self.remove_selector,
            timeout=self.timeout,
            account_id=account_id,
            collection_id=collection_id,
            source_id=source_id,
        )

    @property
    def is_sitemap(self) -> bool:
        """Check if this is a sitemap source."""
        return self.source_type == "sitemap" or self.url.endswith("sitemap.xml")

    @property
    def is_website(self) -> bool:
        """Check if this is a website source."""
        return self.source_type == "website"

    @classmethod
    def from_url(cls, url: str, **kwargs: Any) -> SourceConfig:
        """Create a SourceConfig from a URL, auto-detecting source type.

        Args:
            url: The source URL.
            **kwargs: Additional configuration options.

        Returns:
            SourceConfig with auto-detected source type.
        """
        # Auto-detect source type from URL
        source_type = "website"
        if "sitemap" in url.lower() or url.endswith(".xml"):
            source_type = "sitemap"

        return cls(url=url, source_type=source_type, **kwargs)
