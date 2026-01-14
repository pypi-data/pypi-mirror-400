"""Document domain models."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class DocumentStatus(Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


@dataclass
class Document:
    """Represents a document to be indexed.

    This is the core domain object that flows through the knowledge pipeline.
    Documents are created by loaders, processed by chunkers, and stored by indexers.

    Attributes:
        content: The main text content of the document.
        source: Source identifier (URL, file path, etc.).
        doc_id: Unique identifier. Auto-generated from content hash if not provided.
        title: Optional document title.
        url: URL where the document was fetched from.
        metadata: Arbitrary metadata dictionary.

        Multi-tenancy fields:
            account_id: Account/tenant identifier.
            collection_id: Collection the document belongs to.
            source_id: Source identifier within the collection.

        Chunking info:
            chunk_index: Index of this chunk (0-based).
            total_chunks: Total number of chunks for the parent document.
            parent_doc_id: Reference to the original document ID.

        Quality and validation:
            quality_score: Quality score from 0.0 to 1.0.
            language: Detected language code (ISO 639-1).
            content_hash: SHA-256 hash for deduplication.
            word_count: Number of words in content.

        Status:
            status: Current processing status.

        PII handling:
            pii_detected: Whether PII was detected.
            pii_redacted: Whether PII was redacted.

        Timestamps:
            created_at: When the document was created.
            updated_at: When the document was last updated.
            indexed_at: When the document was indexed.
    """

    content: str
    source: str
    doc_id: str | None = None
    title: str | None = None
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # Multi-tenancy fields
    account_id: str | None = None
    collection_id: str | None = None
    collection_name: str | None = None  # For display in aggregations
    source_id: str | None = None

    # Chunking info
    chunk_index: int | None = None
    total_chunks: int | None = None
    parent_doc_id: str | None = None

    # Quality and validation
    quality_score: float | None = None
    language: str | None = None
    content_hash: str | None = None
    word_count: int | None = None

    # Status
    status: DocumentStatus = DocumentStatus.PENDING

    # PII handling
    pii_detected: bool = False
    pii_redacted: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    indexed_at: datetime | None = None

    def __post_init__(self) -> None:
        """Generate doc_id and content_hash if not provided."""
        if not self.content:
            raise ValueError("Document content cannot be empty")

        # Generate content hash for deduplication
        if self.content_hash is None:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()

        # Generate doc_id from content hash if not provided
        if self.doc_id is None:
            self.doc_id = f"{self.source}#{self.content_hash[:16]}"

        # Calculate word count
        if self.word_count is None:
            self.word_count = len(self.content.split())

    def with_chunk_info(
        self,
        chunk_index: int,
        total_chunks: int,
        parent_doc_id: str | None = None,
    ) -> Document:
        """Create a new document with chunk information.

        Args:
            chunk_index: Index of this chunk (0-based).
            total_chunks: Total number of chunks.
            parent_doc_id: Reference to the original document ID.

        Returns:
            New Document instance with chunk information set.
        """
        return Document(
            content=self.content,
            source=self.source,
            doc_id=None,  # Will be regenerated
            title=self.title,
            url=self.url,
            metadata=self.metadata.copy(),
            account_id=self.account_id,
            collection_id=self.collection_id,
            collection_name=self.collection_name,
            source_id=self.source_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            parent_doc_id=parent_doc_id or self.doc_id,
            quality_score=self.quality_score,
            language=self.language,
            status=self.status,
            pii_detected=self.pii_detected,
            pii_redacted=self.pii_redacted,
            created_at=self.created_at,
        )

    def with_tenant(
        self,
        account_id: str,
        collection_id: str | None = None,
        collection_name: str | None = None,
        source_id: str | None = None,
    ) -> Document:
        """Create a new document with tenant information.

        Args:
            account_id: Account/tenant identifier.
            collection_id: Collection identifier.
            collection_name: Collection name for display.
            source_id: Source identifier.

        Returns:
            New Document instance with tenant information set.
        """
        return Document(
            content=self.content,
            source=self.source,
            doc_id=self.doc_id,
            title=self.title,
            url=self.url,
            metadata=self.metadata.copy(),
            account_id=account_id,
            collection_id=collection_id or self.collection_id,
            collection_name=collection_name or self.collection_name,
            source_id=source_id or self.source_id,
            chunk_index=self.chunk_index,
            total_chunks=self.total_chunks,
            parent_doc_id=self.parent_doc_id,
            quality_score=self.quality_score,
            language=self.language,
            content_hash=self.content_hash,
            word_count=self.word_count,
            status=self.status,
            pii_detected=self.pii_detected,
            pii_redacted=self.pii_redacted,
            created_at=self.created_at,
            updated_at=self.updated_at,
            indexed_at=self.indexed_at,
        )

    @property
    def is_chunk(self) -> bool:
        """Check if this document is a chunk of a larger document."""
        return self.chunk_index is not None and self.total_chunks is not None

    @property
    def is_multi_tenant(self) -> bool:
        """Check if this document has tenant information."""
        return self.account_id is not None


@dataclass
class TextChunk:
    """Represents a chunk of text from a document.

    Text chunks are created by chunkers to split large documents into
    smaller, embedding-friendly pieces.

    Attributes:
        content: The text content of the chunk.
        index: Index of this chunk (0-based).
        start_position: Start position in the original text.
        end_position: End position in the original text.
        metadata: Optional metadata for the chunk.
    """

    content: str
    index: int
    start_position: int
    end_position: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def length(self) -> int:
        """Return the length of the chunk content."""
        return len(self.content)

    def __post_init__(self) -> None:
        """Validate chunk data."""
        if self.start_position < 0:
            raise ValueError("start_position must be non-negative")
        if self.end_position < self.start_position:
            raise ValueError("end_position must be >= start_position")
        if self.index < 0:
            raise ValueError("index must be non-negative")
