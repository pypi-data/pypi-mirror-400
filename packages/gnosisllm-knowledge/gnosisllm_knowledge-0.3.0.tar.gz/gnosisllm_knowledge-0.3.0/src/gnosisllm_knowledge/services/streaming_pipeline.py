"""Streaming indexing pipeline with bounded memory.

This module provides the StreamingIndexingPipeline that orchestrates
the load -> index pipeline with guaranteed bounded memory usage.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from gnosisllm_knowledge.core.domain.document import Document, DocumentStatus
from gnosisllm_knowledge.core.domain.result import IndexResult
from gnosisllm_knowledge.core.events.emitter import EventEmitter
from gnosisllm_knowledge.core.events.types import (
    BatchCompletedEvent,
    StreamingCompletedEvent,
    StreamingProgressEvent,
)
from gnosisllm_knowledge.core.streaming.pipeline import PipelineConfig

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.interfaces.indexer import IDocumentIndexer
    from gnosisllm_knowledge.loaders.sitemap import SitemapLoader


@dataclass
class StreamingProgress:
    """Progress tracking for streaming operations.

    Attributes:
        urls_discovered: Total URLs discovered so far.
        urls_processed: URLs that have been fetched and processed.
        documents_indexed: Documents successfully indexed.
        documents_failed: Documents that failed to index.
        current_phase: Current pipeline phase (discovering, fetching, indexing, completed).
        memory_estimate_mb: Estimated current memory usage in MB.
    """

    urls_discovered: int = 0
    urls_processed: int = 0
    documents_indexed: int = 0
    documents_failed: int = 0
    current_phase: str = "initializing"
    memory_estimate_mb: float = 0.0


@dataclass
class StreamingPipelineResult:
    """Result of a streaming pipeline execution.

    Attributes:
        success: Whether the pipeline completed successfully.
        indexed_count: Total documents indexed.
        failed_count: Total documents that failed.
        urls_processed: Total URLs processed.
        batches_processed: Number of batches processed.
        duration_ms: Total duration in milliseconds.
        errors: List of errors encountered.
    """

    success: bool
    indexed_count: int = 0
    failed_count: int = 0
    urls_processed: int = 0
    batches_processed: int = 0
    duration_ms: float = 0.0
    errors: list[dict[str, Any]] = field(default_factory=list)


class StreamingIndexingPipeline:
    """Orchestrates streaming load -> index pipeline with bounded memory.

    This pipeline ensures:
    1. URLs are discovered and processed in batches
    2. Documents are indexed immediately after fetching
    3. Memory is freed between batches
    4. Progress is tracked and emitted as events
    5. Errors don't stop the entire pipeline

    Memory Guarantees:
    - URL storage: O(url_batch_size)
    - Document storage: O(index_batch_size)
    - In-flight fetches: O(fetch_concurrency * avg_page_size)
    - Total: Bounded, independent of sitemap size

    Example:
        ```python
        pipeline = StreamingIndexingPipeline(
            loader=sitemap_loader,
            indexer=opensearch_indexer,
            config=PipelineConfig(
                url_batch_size=50,
                fetch_concurrency=10,
                index_batch_size=100,
            ),
        )

        result = await pipeline.execute(
            source="https://example.com/sitemap.xml",
            index_name="knowledge-account123",
            account_id="account123",
        )
        ```
    """

    def __init__(
        self,
        loader: SitemapLoader,
        indexer: IDocumentIndexer,
        config: PipelineConfig | None = None,
        events: EventEmitter | None = None,
    ) -> None:
        """Initialize the streaming pipeline.

        Args:
            loader: Sitemap loader instance.
            indexer: Document indexer instance.
            config: Pipeline configuration.
            events: Event emitter for progress events.
        """
        self._loader = loader
        self._indexer = indexer
        self._config = config or PipelineConfig()
        self._events = events or EventEmitter()
        self._logger = logging.getLogger(__name__)
        self._progress = StreamingProgress()

    async def execute(
        self,
        source: str,
        index_name: str,
        *,
        account_id: str | None = None,
        collection_id: str | None = None,
        collection_name: str | None = None,
        source_id: str | None = None,
        **options: Any,
    ) -> IndexResult:
        """Execute the streaming pipeline.

        Args:
            source: Sitemap URL.
            index_name: Target OpenSearch index.
            account_id: For multi-tenancy filtering.
            collection_id: Collection within account.
            collection_name: Collection name for display.
            source_id: Source identifier.
            **options: Additional loader options.

        Returns:
            Aggregated index result.
        """
        start_time = time.time()
        self._progress = StreamingProgress(current_phase="starting")
        await self._emit_progress()

        batch_count = 0

        # Create index callback that enriches and indexes documents
        async def index_batch(documents: list[Document]) -> IndexResult:
            nonlocal batch_count

            enriched = [
                self._enrich_document(
                    doc,
                    source=source,
                    account_id=account_id,
                    collection_id=collection_id,
                    collection_name=collection_name,
                    source_id=source_id,
                )
                for doc in documents
            ]

            batch_start = time.time()
            result = await self._indexer.bulk_index(enriched, index_name)
            batch_duration = (time.time() - batch_start) * 1000

            self._progress.documents_indexed += result.indexed_count
            self._progress.documents_failed += result.failed_count
            self._progress.current_phase = "indexing"
            await self._emit_progress()

            # Emit batch completed event
            self._events.emit(
                BatchCompletedEvent(
                    batch_index=batch_count,
                    success_count=result.indexed_count,
                    failure_count=result.failed_count,
                    duration_ms=batch_duration,
                )
            )
            batch_count += 1

            return result

        # Execute streaming load with indexing
        self._progress.current_phase = "processing"
        await self._emit_progress()

        try:
            result = await self._loader.load_streaming_with_indexing(
                source=source,
                index_callback=index_batch,
                url_batch_size=self._config.url_batch_size,
                doc_batch_size=self._config.index_batch_size,
                config=self._config,
                **options,
            )
        except Exception as e:
            self._logger.exception(f"Streaming pipeline failed: {e}")
            duration_ms = (time.time() - start_time) * 1000
            return IndexResult(
                success=False,
                indexed_count=self._progress.documents_indexed,
                failed_count=self._progress.documents_failed,
                error_message=str(e),
                duration_ms=duration_ms,
            )

        duration_ms = (time.time() - start_time) * 1000
        self._progress.current_phase = "completed"
        await self._emit_progress()

        # Emit completion event
        self._events.emit(
            StreamingCompletedEvent(
                total_urls=self._progress.urls_processed,
                total_documents=result.indexed_count + result.failed_count,
                indexed_count=result.indexed_count,
                failed_count=result.failed_count,
                duration_ms=duration_ms,
            )
        )

        return IndexResult(
            success=result.failed_count == 0,
            indexed_count=result.indexed_count,
            failed_count=result.failed_count,
            errors=result.errors,
            duration_ms=duration_ms,
        )

    def _enrich_document(
        self,
        doc: Document,
        source: str,
        account_id: str | None,
        collection_id: str | None,
        collection_name: str | None,
        source_id: str | None,
    ) -> Document:
        """Add tenant and source info to document.

        Args:
            doc: Original document.
            source: Source URL.
            account_id: Account identifier.
            collection_id: Collection identifier.
            collection_name: Collection name for display.
            source_id: Source identifier.

        Returns:
            New Document with tenant info.
        """
        return Document(
            content=doc.content,
            source=source,
            doc_id=doc.doc_id,
            url=doc.url,
            title=doc.title,
            account_id=account_id,
            collection_id=collection_id,
            collection_name=collection_name,
            source_id=source_id,
            chunk_index=doc.chunk_index,
            total_chunks=doc.total_chunks,
            parent_doc_id=doc.parent_doc_id,
            status=DocumentStatus.INDEXED,
            metadata=doc.metadata,
        )

    async def _emit_progress(self) -> None:
        """Emit progress event."""
        await self._events.emit_async(
            StreamingProgressEvent(
                urls_discovered=self._progress.urls_discovered,
                urls_processed=self._progress.urls_processed,
                documents_indexed=self._progress.documents_indexed,
                documents_failed=self._progress.documents_failed,
                phase=self._progress.current_phase,
                memory_mb=self._progress.memory_estimate_mb,
            )
        )

    @property
    def progress(self) -> StreamingProgress:
        """Get current progress."""
        return self._progress
