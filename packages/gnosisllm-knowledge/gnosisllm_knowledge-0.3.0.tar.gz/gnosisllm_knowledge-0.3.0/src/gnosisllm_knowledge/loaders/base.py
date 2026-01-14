"""Base loader with common functionality (Template Method Pattern)."""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from typing import Any

from gnosisllm_knowledge.core.domain.document import Document
from gnosisllm_knowledge.core.domain.result import LoadResult, ValidationResult
from gnosisllm_knowledge.core.events.emitter import EventEmitter
from gnosisllm_knowledge.core.events.types import DocumentLoadedEvent, EventType
from gnosisllm_knowledge.core.interfaces.chunker import ITextChunker
from gnosisllm_knowledge.core.interfaces.fetcher import IContentFetcher

# Default concurrency for parallel URL fetching
DEFAULT_MAX_CONCURRENT = 10


class BaseLoader(ABC):
    """Base class for content loaders (Template Method Pattern).

    This class provides common functionality for loading content from
    various sources. Subclasses implement the `_get_urls` method to
    define how URLs are discovered from the source.

    Features:
    - Parallel URL fetching with configurable concurrency
    - Streaming support for memory-efficient processing
    - Event emission for progress tracking
    - Automatic chunking of fetched content
    - Configurable options per source type

    Example:
        ```python
        class MyLoader(BaseLoader):
            @property
            def name(self) -> str:
                return "my-loader"

            def supports(self, source: str) -> bool:
                return source.startswith("my://")

            async def _get_urls(self, source: str, **options) -> list[str]:
                # Return list of URLs to fetch
                return [source.replace("my://", "https://")]
        ```
    """

    def __init__(
        self,
        fetcher: IContentFetcher,
        chunker: ITextChunker,
        config: dict[str, Any] | None = None,
        event_emitter: EventEmitter | None = None,
    ) -> None:
        """Initialize the loader with dependencies.

        Args:
            fetcher: Content fetcher for retrieving URL content.
            chunker: Text chunker for splitting content into documents.
            config: Optional configuration dictionary.
            event_emitter: Optional event emitter for progress events.
        """
        self._fetcher = fetcher
        self._chunker = chunker
        self._config = config or {}
        self._events = event_emitter or EventEmitter()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._max_concurrent = self._config.get("max_concurrent", DEFAULT_MAX_CONCURRENT)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the loader name for registry identification."""
        ...

    @abstractmethod
    def supports(self, source: str) -> bool:
        """Check if this loader supports the given source.

        Args:
            source: The source URL or path.

        Returns:
            True if this loader can handle the source.
        """
        ...

    @abstractmethod
    async def _get_urls(self, source: str, **options: Any) -> list[str]:
        """Get list of URLs to process from the source.

        This method is implemented by subclasses to define how
        URLs are discovered from the source.

        Args:
            source: The source URL or path.
            **options: Loader-specific options.

        Returns:
            List of URLs to fetch and process.
        """
        ...

    async def validate_source(self, source: str) -> ValidationResult:
        """Validate that the source is accessible and valid.

        Default implementation checks if fetcher can reach the source.
        Subclasses can override for specific validation logic.

        Args:
            source: The source URL or path.

        Returns:
            ValidationResult with validation status.
        """
        try:
            # Check if we can get URLs from source
            urls = await self._get_urls(source)
            if not urls:
                return ValidationResult(
                    valid=False,
                    message=f"No URLs found in source: {source}",
                )
            return ValidationResult(
                valid=True,
                message=f"Source valid with {len(urls)} URLs",
                metadata={"url_count": len(urls)},
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                message=str(e),
                errors=[str(e)],
            )

    async def load(self, source: str, **options: Any) -> LoadResult:
        """Load all documents from source with parallel URL fetching.

        Args:
            source: The source URL or path.
            **options: Loader-specific options.

        Returns:
            LoadResult with loaded documents and metadata.
        """
        import time

        start_time = time.time()
        documents: list[Document] = []
        urls_processed = 0
        urls_failed = 0

        try:
            urls = await self._get_urls(source, **options)

            if not urls:
                return LoadResult(
                    source=source,
                    source_type=self.name,
                    success=True,
                    documents=[],
                    duration_ms=(time.time() - start_time) * 1000,
                )

            self._logger.info(
                f"Loading {len(urls)} URLs with concurrency={self._max_concurrent}"
            )

            # Use semaphore to limit concurrent fetches
            semaphore = asyncio.Semaphore(self._max_concurrent)

            async def fetch_with_semaphore(url: str) -> list[Document]:
                async with semaphore:
                    return await self._load_url(url, source, **options)

            # Process all URLs in parallel (limited by semaphore)
            results = await asyncio.gather(
                *[fetch_with_semaphore(url) for url in urls],
                return_exceptions=True,
            )

            # Flatten results, handling exceptions gracefully
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self._logger.error(f"Failed to load URL {urls[i]}: {result}")
                    urls_failed += 1
                elif isinstance(result, list):
                    documents.extend(result)
                    urls_processed += 1

            duration_ms = (time.time() - start_time) * 1000

            return LoadResult(
                source=source,
                source_type=self.name,
                success=True,
                documents=documents,
                duration_ms=duration_ms,
                urls_processed=urls_processed,
                urls_failed=urls_failed,
                bytes_loaded=sum(len(d.content) for d in documents),
            )

        except Exception as e:
            self._logger.error(f"Load failed: {e}")
            return LoadResult(
                source=source,
                source_type=self.name,
                success=False,
                documents=[],
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def load_streaming(
        self,
        source: str,
        **options: Any,
    ) -> AsyncIterator[Document]:
        """Stream documents from source for memory-efficient processing.

        Yields documents as they are loaded, allowing for immediate
        processing without waiting for all documents to load.

        Args:
            source: The source URL or path.
            **options: Loader-specific options.

        Yields:
            Document objects as they are loaded.
        """
        urls = await self._get_urls(source, **options)

        if not urls:
            return

        self._logger.info(
            f"Streaming {len(urls)} URLs with concurrency={self._max_concurrent}"
        )

        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def fetch_with_semaphore(url: str) -> tuple[str, list[Document]]:
            async with semaphore:
                docs = await self._load_url(url, source, **options)
                return (url, docs)

        # Create tasks for all URLs
        tasks = [asyncio.create_task(fetch_with_semaphore(url)) for url in urls]

        # Process results as they complete (streaming behavior)
        for coro in asyncio.as_completed(tasks):
            try:
                url, url_docs = await coro
                for doc in url_docs:
                    yield doc
            except Exception as e:
                self._logger.error(f"Failed to load URL: {e}")

    async def load_with_callback(
        self,
        source: str,
        callback: Callable[[list[Document]], Any],
        batch_size: int = 5,
        **options: Any,
    ) -> int:
        """Load documents with a callback for batch processing.

        Args:
            source: The source URL or path.
            callback: Callback function called with each batch.
            batch_size: Number of documents per batch.
            **options: Loader-specific options.

        Returns:
            Total number of documents loaded.
        """
        urls = await self._get_urls(source, **options)

        if not urls:
            return 0

        self._logger.info(
            f"Streaming {len(urls)} URLs with concurrency={self._max_concurrent}"
        )

        total = 0
        batch: list[Document] = []
        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def fetch_with_semaphore(url: str) -> tuple[str, list[Document]]:
            async with semaphore:
                docs = await self._load_url(url, source, **options)
                return (url, docs)

        # Create tasks for all URLs
        tasks = [asyncio.create_task(fetch_with_semaphore(url)) for url in urls]

        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            try:
                url, url_docs = await coro
                batch.extend(url_docs)

                # Stream batches as they fill up
                while len(batch) >= batch_size:
                    await self._invoke_callback(callback, batch[:batch_size])
                    total += batch_size
                    batch = batch[batch_size:]

            except Exception as e:
                self._logger.error(f"Failed to load URL: {e}")

        # Flush remaining batch
        if batch:
            await self._invoke_callback(callback, batch)
            total += len(batch)

        return total

    async def _invoke_callback(
        self, callback: Callable[[list[Document]], Any], documents: list[Document]
    ) -> None:
        """Invoke callback, handling both sync and async callbacks.

        Args:
            callback: The callback function to invoke.
            documents: List of documents to pass to callback.
        """
        import inspect

        result = callback(documents)
        if inspect.iscoroutine(result):
            await result

    async def _load_url(
        self,
        url: str,
        source: str,
        **options: Any,
    ) -> list[Document]:
        """Load and chunk content from a single URL.

        Args:
            url: The URL to fetch.
            source: The original source identifier.
            **options: Loader-specific options.

        Returns:
            List of Document objects from the URL.
        """
        try:
            result = await self._fetcher.fetch(url, **options)
            chunks = self._chunker.chunk(result.content)

            documents: list[Document] = []
            for chunk in chunks:
                doc = Document(
                    content=chunk.content,
                    source=source,
                    url=url,
                    title=result.title,
                    chunk_index=chunk.index,
                    total_chunks=len(chunks),
                    metadata={
                        "loader": self.name,
                        "fetch_url": url,
                        "content_type": result.content_type,
                    },
                )
                documents.append(doc)

            # Emit event
            self._events.emit(
                DocumentLoadedEvent(
                    url=url,
                    source=source,
                    chunks_count=len(chunks),
                    content_length=len(result.content),
                )
            )

            return documents

        except Exception as e:
            self._logger.error(f"Failed to load URL {url}: {e}")
            self._events.emit(
                type(
                    "Event",
                    (),
                    {"event_type": EventType.ERROR, "data": {"url": url, "error": str(e)}},
                )()  # type: ignore[arg-type]
            )
            return []
