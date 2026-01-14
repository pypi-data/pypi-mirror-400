"""In-memory document indexer for testing."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Sequence

from gnosisllm_knowledge.core.domain.document import Document
from gnosisllm_knowledge.core.domain.result import BatchResult, IndexResult


class MemoryIndexer:
    """In-memory document indexer for testing.

    Stores documents in a dictionary for fast testing without
    requiring an external OpenSearch instance.

    Example:
        ```python
        indexer = MemoryIndexer()

        # Index documents
        await indexer.index(document, "test-index")

        # Bulk index
        await indexer.bulk_index(documents, "test-index")

        # Get stored documents
        docs = indexer.get_all("test-index")
        ```
    """

    def __init__(
        self,
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        """Initialize the memory indexer.

        Args:
            embedding_fn: Optional function to generate embeddings.
        """
        self._indices: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        self._embedding_fn = embedding_fn

    async def index(
        self,
        document: Document,
        index_name: str,
        **options: Any,
    ) -> IndexResult:
        """Index a single document.

        Args:
            document: Document to index.
            index_name: Target index name.
            **options: Additional options.

        Returns:
            Index result.
        """
        doc_body = self._prepare_document(document)

        if self._embedding_fn and "embedding" not in doc_body:
            doc_body["embedding"] = self._embedding_fn(document.content)

        self._indices[index_name][document.doc_id] = doc_body

        return IndexResult(
            success=True,
            document_id=document.doc_id,
            index_name=index_name,
            indexed_count=1,
            failed_count=0,
        )

    async def bulk_index(
        self,
        documents: Sequence[Document],
        index_name: str,
        **options: Any,
    ) -> IndexResult:
        """Index multiple documents.

        Args:
            documents: Documents to index.
            index_name: Target index name.
            **options: Additional options.

        Returns:
            Index result.
        """
        indexed = 0
        for doc in documents:
            await self.index(doc, index_name)
            indexed += 1

        return IndexResult(
            success=True,
            index_name=index_name,
            indexed_count=indexed,
            failed_count=0,
        )

    async def bulk_index_streaming(
        self,
        documents: AsyncIterator[Document],
        index_name: str,
        *,
        batch_size: int = 500,
        max_concurrent_batches: int = 3,
        on_batch_complete: Callable[[BatchResult], None] | None = None,
    ) -> IndexResult:
        """Stream-index documents.

        Args:
            documents: Async iterator of documents.
            index_name: Target index name.
            batch_size: Documents per batch.
            max_concurrent_batches: Ignored for memory backend.
            on_batch_complete: Callback for batch completion.

        Returns:
            Index result.
        """
        indexed = 0
        batch_num = 0
        current_batch: list[Document] = []

        async for doc in documents:
            current_batch.append(doc)

            if len(current_batch) >= batch_size:
                batch_num += 1
                await self.bulk_index(current_batch, index_name)
                indexed += len(current_batch)

                if on_batch_complete:
                    on_batch_complete(
                        BatchResult(
                            total=len(current_batch),
                            succeeded=len(current_batch),
                            failed=0,
                        )
                    )

                current_batch = []

        # Process remaining
        if current_batch:
            batch_num += 1
            await self.bulk_index(current_batch, index_name)
            indexed += len(current_batch)

            if on_batch_complete:
                on_batch_complete(
                    BatchResult(
                        total=len(current_batch),
                        succeeded=len(current_batch),
                        failed=0,
                    )
                )

        return IndexResult(
            success=True,
            index_name=index_name,
            indexed_count=indexed,
            failed_count=0,
        )

    async def upsert(
        self,
        document: Document,
        index_name: str,
    ) -> IndexResult:
        """Upsert a document.

        Args:
            document: Document to upsert.
            index_name: Target index name.

        Returns:
            Index result.
        """
        return await self.index(document, index_name)

    async def delete(
        self,
        doc_id: str,
        index_name: str,
    ) -> bool:
        """Delete a document by ID.

        Args:
            doc_id: Document ID.
            index_name: Index name.

        Returns:
            True if deleted.
        """
        if index_name in self._indices and doc_id in self._indices[index_name]:
            del self._indices[index_name][doc_id]
            return True
        return False

    async def bulk_delete(
        self,
        doc_ids: Sequence[str],
        index_name: str,
    ) -> int:
        """Delete multiple documents.

        Args:
            doc_ids: Document IDs.
            index_name: Index name.

        Returns:
            Count of deleted documents.
        """
        deleted = 0
        for doc_id in doc_ids:
            if await self.delete(doc_id, index_name):
                deleted += 1
        return deleted

    async def delete_by_query(
        self,
        query: dict[str, Any],
        index_name: str,
    ) -> int:
        """Delete documents matching query.

        Simple implementation that checks filter terms.

        Args:
            query: Query dictionary with filters.
            index_name: Index name.

        Returns:
            Count of deleted documents.
        """
        if index_name not in self._indices:
            return 0

        filters = query.get("query", {}).get("bool", {}).get("filter", [])
        to_delete = []

        for doc_id, doc in self._indices[index_name].items():
            matches = True
            for f in filters:
                if "term" in f:
                    for field, value in f["term"].items():
                        if doc.get(field) != value:
                            matches = False
                            break
            if matches:
                to_delete.append(doc_id)

        for doc_id in to_delete:
            del self._indices[index_name][doc_id]

        return len(to_delete)

    async def ensure_index(
        self,
        index_name: str,
        **options: Any,
    ) -> bool:
        """Ensure index exists.

        Args:
            index_name: Index name.
            **options: Ignored.

        Returns:
            True if created.
        """
        if index_name not in self._indices:
            self._indices[index_name] = {}
            return True
        return False

    async def delete_index(self, index_name: str) -> bool:
        """Delete an index.

        Args:
            index_name: Index to delete.

        Returns:
            True if deleted.
        """
        if index_name in self._indices:
            del self._indices[index_name]
            return True
        return False

    async def refresh_index(self, index_name: str) -> bool:
        """Refresh index (no-op for memory).

        Args:
            index_name: Index name.

        Returns:
            Always True.
        """
        return True

    def get_all(self, index_name: str) -> list[dict[str, Any]]:
        """Get all documents in an index.

        Args:
            index_name: Index name.

        Returns:
            List of document dictionaries.
        """
        return list(self._indices.get(index_name, {}).values())

    def get_by_id(self, doc_id: str, index_name: str) -> dict[str, Any] | None:
        """Get document by ID.

        Args:
            doc_id: Document ID.
            index_name: Index name.

        Returns:
            Document dictionary or None.
        """
        return self._indices.get(index_name, {}).get(doc_id)

    def count(self, index_name: str) -> int:
        """Count documents in index.

        Args:
            index_name: Index name.

        Returns:
            Document count.
        """
        return len(self._indices.get(index_name, {}))

    def clear_all(self) -> None:
        """Clear all indices."""
        self._indices.clear()

    def _prepare_document(self, document: Document) -> dict[str, Any]:
        """Prepare document for storage.

        Args:
            document: Document to prepare.

        Returns:
            Dictionary for storage.
        """
        content_hash = document.content_hash
        if not content_hash:
            content_hash = hashlib.sha256(document.content.encode()).hexdigest()

        now = datetime.now(timezone.utc)

        return {
            "id": document.doc_id,
            "content": document.content,
            "url": document.url,
            "title": document.title,
            "source": document.source,
            "account_id": document.account_id,
            "collection_id": document.collection_id,
            "source_id": document.source_id,
            "chunk_index": document.chunk_index,
            "total_chunks": document.total_chunks,
            "parent_doc_id": document.parent_doc_id,
            "quality_score": document.quality_score,
            "language": document.language,
            "content_hash": content_hash,
            "word_count": document.word_count or len(document.content.split()),
            "status": document.status.value,
            "pii_detected": document.pii_detected,
            "pii_redacted": document.pii_redacted,
            "metadata": document.metadata,
            "created_at": document.created_at.isoformat() if document.created_at else now.isoformat(),
            "indexed_at": now.isoformat(),
        }
