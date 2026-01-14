"""Knowledge indexing service."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

from gnosisllm_knowledge.core.domain.document import Document, DocumentStatus
from gnosisllm_knowledge.core.domain.result import IndexResult, LoadResult
from gnosisllm_knowledge.core.domain.source import SourceConfig
from gnosisllm_knowledge.core.events.emitter import EventEmitter
from gnosisllm_knowledge.core.events.types import (
    BatchCompletedEvent,
    BatchStartedEvent,
    DocumentIndexedEvent,
    EventType,
)
from gnosisllm_knowledge.core.exceptions import IndexError, LoadError

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.interfaces.chunker import ITextChunker
    from gnosisllm_knowledge.core.interfaces.indexer import IDocumentIndexer
    from gnosisllm_knowledge.core.interfaces.loader import IContentLoader

logger = logging.getLogger(__name__)


class KnowledgeIndexingService:
    """Service for loading, chunking, and indexing knowledge documents.

    Orchestrates the document ingestion pipeline from source to index.

    Example:
        ```python
        service = KnowledgeIndexingService(
            loader=WebsiteLoader(fetcher),
            chunker=SentenceChunker(),
            indexer=OpenSearchIndexer(client, config),
        )

        # Load and index from a URL
        result = await service.load_and_index(
            source="https://docs.example.com",
            index_name="knowledge",
            collection_id="docs",
        )
        ```
    """

    def __init__(
        self,
        loader: IContentLoader,
        chunker: ITextChunker,
        indexer: IDocumentIndexer,
        events: EventEmitter | None = None,
    ) -> None:
        """Initialize the indexing service.

        Args:
            loader: Content loader for fetching documents.
            chunker: Text chunker for splitting documents.
            indexer: Document indexer for storing documents.
            events: Optional event emitter for progress tracking.

        Note:
            Embeddings are generated automatically by OpenSearch ingest pipeline.
            No Python-side embedding function is needed.
        """
        self._loader = loader
        self._chunker = chunker
        self._indexer = indexer
        self._events = events or EventEmitter()

    @property
    def events(self) -> EventEmitter:
        """Get the event emitter."""
        return self._events

    async def load_and_index(
        self,
        source: str,
        index_name: str,
        *,
        account_id: str | None = None,
        collection_id: str | None = None,
        source_id: str | None = None,
        batch_size: int = 100,
        **options: Any,
    ) -> IndexResult:
        """Load content from source and index it with streaming.

        Uses streaming to process and index documents as they're fetched,
        avoiding memory issues with large sitemaps.

        Args:
            source: Source URL or path.
            index_name: Target index name.
            account_id: Account ID for multi-tenancy.
            collection_id: Collection ID.
            source_id: Source ID (auto-generated if not provided).
            batch_size: Documents per batch for indexing.
            **options: Additional loader/indexer options.

        Returns:
            Index result with counts.
        """
        source_id = source_id or str(uuid.uuid4())
        document_defaults = options.pop("document_defaults", {})

        # Emit batch started event
        await self._events.emit_async(
            BatchStartedEvent(
                batch_index=0,
                batch_size=batch_size,
                total_batches=0,  # Unknown for streaming
            ),
        )

        total_indexed = 0
        total_failed = 0
        errors: list[str] = []
        batch: list[Document] = []
        batch_index = 0

        try:
            # Stream documents and index in batches as they arrive
            # Note: Loader already chunks content, so we don't re-chunk here
            async for doc in self._loader.load_streaming(source, **options):
                # Enrich document with tenant info
                enriched_doc = Document(
                    content=doc.content,
                    source=source,
                    doc_id=doc.doc_id,
                    url=doc.url,
                    title=doc.title,
                    account_id=account_id,
                    collection_id=collection_id,
                    source_id=source_id,
                    chunk_index=doc.chunk_index,
                    total_chunks=doc.total_chunks,
                    parent_doc_id=doc.parent_doc_id,
                    status=DocumentStatus.INDEXED,
                    metadata=doc.metadata,
                    **document_defaults,
                )

                batch.append(enriched_doc)

                # Index batch when full
                if len(batch) >= batch_size:
                    result = await self._index_batch(batch, index_name)
                    total_indexed += result.indexed_count
                    total_failed += result.failed_count
                    if result.errors:
                        errors.extend(result.errors)
                    batch = []
                    batch_index += 1
                    logger.info(f"Indexed batch {batch_index}: {total_indexed} total documents")

            # Index remaining documents
            if batch:
                result = await self._index_batch(batch, index_name)
                total_indexed += result.indexed_count
                total_failed += result.failed_count
                if result.errors:
                    errors.extend(result.errors)

            # Emit batch completed event
            await self._events.emit_async(
                BatchCompletedEvent(
                    batch_index=batch_index,
                    success_count=total_indexed,
                    failure_count=total_failed,
                ),
            )

            logger.info(f"Completed indexing from {source}: {total_indexed} documents")

            return IndexResult(
                success=total_failed == 0,
                indexed_count=total_indexed,
                failed_count=total_failed,
                errors=errors if errors else [],
            )

        except Exception as e:
            logger.error(f"Failed to load and index from {source}: {e}")
            raise IndexError(
                message=f"Failed to index from {source}",
                details={"source": source},
                cause=e,
            ) from e

    async def index_documents(
        self,
        documents: list[Document],
        index_name: str,
        *,
        chunk: bool = True,
        batch_size: int = 100,
        **options: Any,
    ) -> IndexResult:
        """Index a list of documents.

        Args:
            documents: Documents to index.
            index_name: Target index name.
            chunk: Whether to chunk documents.
            batch_size: Documents per batch.
            **options: Additional indexer options.

        Returns:
            Index result.
        """
        total_indexed = 0
        total_failed = 0
        errors: list[str] = []
        batch: list[Document] = []

        for doc in documents:
            if chunk:
                # Chunk the document
                chunks = self._chunker.chunk(doc.content)

                for i, chunk_obj in enumerate(chunks):
                    chunk_doc = Document(
                        content=chunk_obj.content,
                        source=doc.source,
                        doc_id=f"{doc.doc_id}-chunk-{i}",
                        url=doc.url,
                        title=doc.title,
                        account_id=doc.account_id,
                        collection_id=doc.collection_id,
                        source_id=doc.source_id,
                        chunk_index=i,
                        total_chunks=len(chunks),
                        parent_doc_id=doc.doc_id,
                        status=DocumentStatus.INDEXED,
                        metadata=doc.metadata,
                    )
                    batch.append(chunk_doc)
            else:
                batch.append(doc)

            # Index batch when full
            if len(batch) >= batch_size:
                result = await self._index_batch(batch, index_name)
                total_indexed += result.indexed_count
                total_failed += result.failed_count
                if result.errors:
                    errors.extend(result.errors)
                batch = []

        # Index remaining
        if batch:
            result = await self._index_batch(batch, index_name)
            total_indexed += result.indexed_count
            total_failed += result.failed_count
            if result.errors:
                errors.extend(result.errors)

        return IndexResult(
            success=total_failed == 0,
            indexed_count=total_indexed,
            failed_count=total_failed,
            errors=errors if errors else [],
        )

    async def delete_source(
        self,
        source_id: str,
        index_name: str,
        account_id: str | None = None,
    ) -> int:
        """Delete all documents from a source.

        Args:
            source_id: Source ID to delete.
            index_name: Index name.
            account_id: Optional account filter.

        Returns:
            Count of deleted documents.
        """
        from gnosisllm_knowledge.backends.opensearch.queries import (
            build_delete_by_source_query,
        )

        query = build_delete_by_source_query(source_id, account_id)
        return await self._indexer.delete_by_query(query, index_name)

    async def delete_collection(
        self,
        collection_id: str,
        index_name: str,
        account_id: str | None = None,
    ) -> int:
        """Delete all documents from a collection.

        Args:
            collection_id: Collection ID to delete.
            index_name: Index name.
            account_id: Optional account filter.

        Returns:
            Count of deleted documents.
        """
        from gnosisllm_knowledge.backends.opensearch.queries import (
            build_delete_by_collection_query,
        )

        query = build_delete_by_collection_query(collection_id, account_id)
        return await self._indexer.delete_by_query(query, index_name)

    async def reindex_source(
        self,
        source: str,
        source_id: str,
        index_name: str,
        *,
        account_id: str | None = None,
        collection_id: str | None = None,
        **options: Any,
    ) -> IndexResult:
        """Reindex a source by deleting and re-loading.

        Args:
            source: Source URL or path.
            source_id: Existing source ID.
            index_name: Index name.
            account_id: Account ID.
            collection_id: Collection ID.
            **options: Additional options.

        Returns:
            Index result.
        """
        # Delete existing documents
        await self.delete_source(source_id, index_name, account_id)

        # Re-index
        return await self.load_and_index(
            source=source,
            index_name=index_name,
            account_id=account_id,
            collection_id=collection_id,
            source_id=source_id,
            **options,
        )

    async def _index_batch(
        self,
        documents: list[Document],
        index_name: str,
    ) -> IndexResult:
        """Index a batch of documents.

        Args:
            documents: Documents to index.
            index_name: Target index.

        Returns:
            Batch index result.
        """
        result = await self._indexer.bulk_index(documents, index_name)

        # Emit events for indexed documents
        for doc in documents:
            if result.success:
                await self._events.emit_async(
                    DocumentIndexedEvent(
                        doc_id=doc.doc_id,
                        index_name=index_name,
                        success=True,
                    ),
                )

        return result
