"""Text chunker protocol - Single Responsibility Principle."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.domain.document import TextChunk


@runtime_checkable
class ITextChunker(Protocol):
    """Protocol for chunking text into smaller pieces.

    Text chunkers are responsible for:
    - Splitting large text into embedding-friendly chunks
    - Preserving semantic boundaries (sentences, paragraphs)
    - Handling overlap between chunks
    - Maintaining position information

    Implementations should follow the Single Responsibility Principle
    and handle only text chunking, not fetching or indexing.
    """

    @property
    def name(self) -> str:
        """Return the chunker name for identification."""
        ...

    @property
    def chunk_size(self) -> int:
        """Return the target chunk size in characters."""
        ...

    @property
    def chunk_overlap(self) -> int:
        """Return the overlap between chunks in characters."""
        ...

    def chunk(self, text: str, **options: Any) -> list[TextChunk]:
        """Split text into chunks suitable for embedding.

        Args:
            text: The text to chunk.
            **options: Chunker-specific options like:
                - chunk_size: Override default chunk size
                - chunk_overlap: Override default overlap
                - preserve_sentences: Keep sentences intact

        Returns:
            List of TextChunk objects with content and position info.
        """
        ...

    def estimate_chunks(self, text: str) -> int:
        """Estimate the number of chunks that would be created.

        Args:
            text: The text to estimate.

        Returns:
            Estimated number of chunks.
        """
        ...
