"""Result domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.domain.document import Document


@dataclass
class LoadResult:
    """Result of a load operation.

    Attributes:
        source: The source that was loaded (URL, file path, etc.).
        source_type: Type of source (website, sitemap, file, etc.).
        documents: List of loaded documents.
        success: Whether the operation succeeded.
        error_message: Error message if operation failed.
        duration_ms: Duration of the operation in milliseconds.
        metadata: Additional metadata about the load operation.
        urls_processed: Number of URLs processed (for multi-URL sources).
        urls_failed: Number of URLs that failed to load.
        bytes_loaded: Total bytes of content loaded.
    """

    source: str
    source_type: str
    success: bool
    documents: list[Document] = field(default_factory=list)
    error_message: str | None = None
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    urls_processed: int = 0
    urls_failed: int = 0
    bytes_loaded: int = 0

    @property
    def document_count(self) -> int:
        """Return the number of loaded documents."""
        return len(self.documents)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate for multi-URL loads."""
        total = self.urls_processed + self.urls_failed
        if total == 0:
            return 1.0 if self.success else 0.0
        return self.urls_processed / total


@dataclass
class IndexResult:
    """Result of an indexing operation.

    Attributes:
        success: Whether the operation succeeded.
        document_id: ID of the indexed document (single doc operation).
        index_name: Name of the index where documents were stored.
        indexed_count: Number of documents successfully indexed.
        failed_count: Number of documents that failed to index.
        error_message: Error message if operation failed completely.
        duration_ms: Duration of the operation in milliseconds.
        failed_doc_ids: List of document IDs that failed to index.
        errors: List of error details for failed documents.
    """

    success: bool
    document_id: str | None = None
    index_name: str | None = None
    indexed_count: int = 0
    failed_count: int = 0
    error_message: str | None = None
    duration_ms: float = 0.0
    failed_doc_ids: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total_attempted(self) -> int:
        """Return total documents attempted to index."""
        return self.indexed_count + self.failed_count

    @property
    def success_rate(self) -> float:
        """Calculate the success rate."""
        total = self.total_attempted
        if total == 0:
            return 1.0 if self.success else 0.0
        return self.indexed_count / total

    def merge(self, other: IndexResult) -> IndexResult:
        """Merge two IndexResults into one.

        Useful for combining batch results.

        Args:
            other: Another IndexResult to merge with.

        Returns:
            New IndexResult combining both results.
        """
        return IndexResult(
            index_name=self.index_name,
            indexed_count=self.indexed_count + other.indexed_count,
            failed_count=self.failed_count + other.failed_count,
            success=self.success and other.success,
            error_message=(
                f"{self.error_message}; {other.error_message}"
                if self.error_message and other.error_message
                else self.error_message or other.error_message
            ),
            duration_ms=self.duration_ms + other.duration_ms,
            failed_doc_ids=self.failed_doc_ids + other.failed_doc_ids,
            errors=self.errors + other.errors,
        )


@dataclass
class BatchResult:
    """Result of a batch operation.

    Attributes:
        total: Total items processed.
        succeeded: Number of successful operations.
        failed: Number of failed operations.
        duration_ms: Duration of the batch operation in milliseconds.
        errors: List of errors that occurred.
    """

    total: int
    succeeded: int
    failed: int
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate for this batch."""
        total = self.total
        if total == 0:
            return 1.0
        return self.succeeded / total


@dataclass
class ValidationResult:
    """Result of a validation operation.

    Attributes:
        valid: Whether the content/source is valid.
        message: Descriptive message about the validation.
        errors: List of validation errors if any.
        warnings: List of validation warnings if any.
        metadata: Additional validation metadata.
    """

    valid: bool
    message: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(cls, message: str = "Validation passed") -> ValidationResult:
        """Create a successful validation result."""
        return cls(valid=True, message=message)

    @classmethod
    def failure(cls, message: str, errors: list[str] | None = None) -> ValidationResult:
        """Create a failed validation result."""
        return cls(valid=False, message=message, errors=errors or [])

    def add_error(self, error: str) -> ValidationResult:
        """Add an error and return self for chaining."""
        self.errors.append(error)
        self.valid = False
        return self

    def add_warning(self, warning: str) -> ValidationResult:
        """Add a warning and return self for chaining."""
        self.warnings.append(warning)
        return self
