"""Fetcher configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class FetcherConfig:
    """Base configuration for content fetchers.

    Attributes:
        timeout: Request timeout in seconds.
        user_agent: User-Agent header value.
        headers: Additional HTTP headers.
        max_retries: Maximum retry attempts.
        retry_delay: Delay between retries in seconds.
    """

    timeout: float = 30.0
    user_agent: str = "gnosisllm-knowledge/0.1.0"
    headers: dict[str, str] = field(default_factory=dict)
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class NeoreaderConfig:
    """Configuration for Neoreader content fetcher.

    Neoreader is a service that converts web pages to clean markdown,
    making content extraction easier for RAG systems.

    Attributes:
        host: Neoreader API host URL.
        api_key: API key for authentication.
        timeout: Request timeout in seconds.
        target_selector: CSS selector for main content extraction.
        remove_selector: CSS selector for elements to remove.
        with_images: Whether to include image references.
        with_links: Whether to include link references.
    """

    host: str = "http://localhost:3000"
    api_key: str | None = None
    timeout: float = 30.0
    target_selector: str | None = None
    remove_selector: str | None = None
    with_images: bool = False
    with_links: bool = True

    @classmethod
    def from_env(cls) -> NeoreaderConfig:
        """Create configuration from environment variables.

        Environment variables:
        - NEOREADER_HOST: API host URL
        - NEOREADER_API_KEY: API key
        - NEOREADER_TIMEOUT: Request timeout
        - NEOREADER_TARGET_SELECTOR: CSS selector for content
        - NEOREADER_REMOVE_SELECTOR: CSS selector for removal
        - NEOREADER_WITH_IMAGES: Include images (true/false)
        - NEOREADER_WITH_LINKS: Include links (true/false)

        Returns:
            NeoreaderConfig populated from environment.
        """
        return cls(
            host=os.getenv("NEOREADER_HOST", "http://localhost:3000"),
            api_key=os.getenv("NEOREADER_API_KEY"),
            timeout=float(os.getenv("NEOREADER_TIMEOUT", "30")),
            target_selector=os.getenv("NEOREADER_TARGET_SELECTOR"),
            remove_selector=os.getenv("NEOREADER_REMOVE_SELECTOR"),
            with_images=os.getenv("NEOREADER_WITH_IMAGES", "").lower() == "true",
            with_links=os.getenv("NEOREADER_WITH_LINKS", "true").lower() == "true",
        )
