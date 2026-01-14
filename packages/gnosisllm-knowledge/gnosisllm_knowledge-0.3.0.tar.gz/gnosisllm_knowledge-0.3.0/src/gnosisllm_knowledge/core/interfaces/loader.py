"""Content loader protocol - Interface Segregation Principle."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.domain.document import Document
    from gnosisllm_knowledge.core.domain.result import LoadResult, ValidationResult


@runtime_checkable
class IContentLoader(Protocol):
    """Protocol for loading content from various sources.

    Content loaders are responsible for:
    - Fetching content from a source (URL, file, etc.)
    - Chunking content into documents
    - Supporting both batch and streaming loading

    Implementations should follow the Single Responsibility Principle
    and handle only content loading, not indexing.
    """

    @property
    def name(self) -> str:
        """Return the loader name for registry identification."""
        ...

    def supports(self, source: str) -> bool:
        """Check if this loader supports the given source.

        Args:
            source: The source URL or path.

        Returns:
            True if this loader can handle the source.
        """
        ...

    async def validate_source(self, source: str) -> ValidationResult:
        """Validate that the source is accessible and valid.

        Args:
            source: The source URL or path.

        Returns:
            ValidationResult with validation status and any errors.
        """
        ...

    async def load(self, source: str, **options: Any) -> LoadResult:
        """Load all documents from source.

        Args:
            source: The source URL or path.
            **options: Loader-specific options.

        Returns:
            LoadResult with loaded documents and metadata.
        """
        ...

    async def load_streaming(
        self,
        source: str,
        **options: Any,
    ) -> AsyncIterator[Document]:
        """Stream documents from source for memory-efficient processing.

        This method yields documents one at a time, which is more
        memory-efficient for large sources.

        Args:
            source: The source URL or path.
            **options: Loader-specific options.

        Yields:
            Document objects as they are loaded.
        """
        ...

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
            callback: Callback function called with each batch of documents.
            batch_size: Number of documents per batch.
            **options: Loader-specific options.

        Returns:
            Total number of documents loaded.
        """
        ...
