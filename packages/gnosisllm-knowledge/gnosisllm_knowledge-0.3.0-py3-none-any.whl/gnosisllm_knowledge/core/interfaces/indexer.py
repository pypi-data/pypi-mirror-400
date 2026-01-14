"""Document indexer protocol - Interface Segregation Principle."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Sequence
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.domain.document import Document
    from gnosisllm_knowledge.core.domain.result import BatchResult, IndexResult


@runtime_checkable
class IDocumentIndexer(Protocol):
    """Protocol for indexing documents into a search backend.

    Document indexers are responsible for:
    - Generating embeddings for documents
    - Storing documents in the search backend
    - Managing index lifecycle (create, delete, refresh)
    - Handling bulk operations efficiently

    Implementations should follow the Interface Segregation Principle
    and provide focused methods for each operation type.
    """

    async def index(
        self,
        document: Document,
        index_name: str,
        **options: Any,
    ) -> IndexResult:
        """Index a single document.

        Args:
            document: The document to index.
            index_name: Target index name.
            **options: Backend-specific options.

        Returns:
            IndexResult with success/failure information.
        """
        ...

    async def bulk_index(
        self,
        documents: Sequence[Document],
        index_name: str,
        batch_size: int = 100,
        **options: Any,
    ) -> IndexResult:
        """Bulk index multiple documents efficiently.

        Args:
            documents: Documents to index.
            index_name: Target index name.
            batch_size: Number of documents per batch.
            **options: Backend-specific options.

        Returns:
            Aggregated IndexResult for all documents.
        """
        ...

    async def bulk_index_streaming(
        self,
        documents: AsyncIterator[Document],
        index_name: str,
        batch_size: int = 100,
        max_concurrent_batches: int = 3,
        on_batch_complete: Callable[[BatchResult], None] | None = None,
        **options: Any,
    ) -> IndexResult:
        """Stream-index documents with backpressure handling.

        Memory-efficient indexing for large document streams.

        Args:
            documents: Async iterator of documents.
            index_name: Target index name.
            batch_size: Number of documents per batch.
            max_concurrent_batches: Maximum concurrent batch operations.
            on_batch_complete: Callback called after each batch completes.
            **options: Backend-specific options.

        Returns:
            Aggregated IndexResult for all documents.
        """
        ...

    async def upsert(
        self,
        document: Document,
        index_name: str,
        **options: Any,
    ) -> IndexResult:
        """Upsert (update or insert) a document.

        Args:
            document: Document to upsert.
            index_name: Target index name.
            **options: Backend-specific options.

        Returns:
            IndexResult with operation status.
        """
        ...

    async def delete(
        self,
        doc_id: str,
        index_name: str,
    ) -> bool:
        """Delete a document by ID.

        Args:
            doc_id: Document ID to delete.
            index_name: Target index name.

        Returns:
            True if deleted, False if not found.
        """
        ...

    async def bulk_delete(
        self,
        doc_ids: Sequence[str],
        index_name: str,
    ) -> int:
        """Delete multiple documents by ID.

        Args:
            doc_ids: Document IDs to delete.
            index_name: Target index name.

        Returns:
            Number of documents deleted.
        """
        ...

    async def delete_by_source(
        self,
        source: str,
        index_name: str,
    ) -> int:
        """Delete all documents from a specific source.

        Args:
            source: Source identifier.
            index_name: Target index name.

        Returns:
            Number of documents deleted.
        """
        ...

    async def delete_by_query(
        self,
        query: dict[str, Any],
        index_name: str,
    ) -> int:
        """Delete documents matching a query.

        Args:
            query: Query dictionary in backend format.
            index_name: Target index name.

        Returns:
            Number of documents deleted.
        """
        ...

    async def ensure_index(
        self,
        index_name: str,
        **options: Any,
    ) -> bool:
        """Ensure index exists with proper mapping.

        Creates the index if it doesn't exist, or verifies
        the existing mapping is compatible.

        Args:
            index_name: Index name to ensure.
            **options: Index settings and mapping options.

        Returns:
            True if index exists or was created successfully.
        """
        ...

    async def delete_index(self, index_name: str) -> bool:
        """Delete an index.

        Args:
            index_name: Index name to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    async def refresh_index(self, index_name: str) -> bool:
        """Refresh index to make documents searchable.

        Args:
            index_name: Index name to refresh.

        Returns:
            True if refresh succeeded.
        """
        ...

    async def get_document(
        self,
        doc_id: str,
        index_name: str,
    ) -> Document | None:
        """Get a document by ID.

        Args:
            doc_id: Document ID to retrieve.
            index_name: Index name.

        Returns:
            Document if found, None otherwise.
        """
        ...

    async def document_exists(
        self,
        doc_id: str,
        index_name: str,
    ) -> bool:
        """Check if a document exists.

        Args:
            doc_id: Document ID to check.
            index_name: Index name.

        Returns:
            True if document exists.
        """
        ...
