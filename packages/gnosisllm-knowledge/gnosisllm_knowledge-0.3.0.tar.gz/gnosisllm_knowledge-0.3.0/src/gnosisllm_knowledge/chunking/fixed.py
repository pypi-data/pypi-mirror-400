"""Fixed-size text chunker."""

from __future__ import annotations

from typing import Any

from gnosisllm_knowledge.core.domain.document import TextChunk

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 4000  # Characters
DEFAULT_CHUNK_OVERLAP = 200  # Characters


class FixedSizeChunker:
    """Simple fixed-size text chunker.

    This chunker splits text into fixed-size chunks without regard for
    semantic boundaries. It's faster than sentence-aware chunking but
    may split words or sentences in the middle.

    For better results with natural language, use SentenceChunker.

    Example:
        ```python
        chunker = FixedSizeChunker(chunk_size=4000, chunk_overlap=200)
        chunks = chunker.chunk(long_text)
        ```

    Attributes:
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        """Initialize the chunker.

        Args:
            chunk_size: Target chunk size in characters.
            chunk_overlap: Overlap between consecutive chunks.
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    @property
    def name(self) -> str:
        """Return the chunker name."""
        return "fixed"

    @property
    def chunk_size(self) -> int:
        """Return the target chunk size."""
        return self._chunk_size

    @property
    def chunk_overlap(self) -> int:
        """Return the chunk overlap."""
        return self._chunk_overlap

    def chunk(self, text: str, **options: Any) -> list[TextChunk]:
        """Split text into fixed-size chunks.

        Args:
            text: The text to chunk.
            **options: Override options:
                - chunk_size: Override default chunk size
                - chunk_overlap: Override default overlap

        Returns:
            List of TextChunk objects.
        """
        # Get options with fallbacks
        chunk_size = options.get("chunk_size", self._chunk_size)
        chunk_overlap = options.get("chunk_overlap", self._chunk_overlap)

        if not text:
            return []

        text = text.strip()
        if len(text) <= chunk_size:
            return [
                TextChunk(
                    content=text,
                    index=0,
                    start_position=0,
                    end_position=len(text),
                )
            ]

        chunks: list[TextChunk] = []
        step = chunk_size - chunk_overlap
        chunk_index = 0

        for start_pos in range(0, len(text), step):
            end_pos = min(start_pos + chunk_size, len(text))
            chunk_content = text[start_pos:end_pos]

            if chunk_content.strip():
                chunks.append(
                    TextChunk(
                        content=chunk_content,
                        index=chunk_index,
                        start_position=start_pos,
                        end_position=end_pos,
                    )
                )
                chunk_index += 1

            # Stop if we've reached the end
            if end_pos >= len(text):
                break

        return chunks

    def estimate_chunks(self, text: str) -> int:
        """Estimate the number of chunks that would be created.

        Args:
            text: The text to estimate.

        Returns:
            Estimated number of chunks.
        """
        if not text:
            return 0

        text_len = len(text)
        if text_len <= self._chunk_size:
            return 1

        step = self._chunk_size - self._chunk_overlap
        return max(1, (text_len + step - 1) // step)
