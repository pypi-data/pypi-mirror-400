"""Sentence-aware text chunker."""

from __future__ import annotations

import re
from typing import Any

from gnosisllm_knowledge.core.domain.document import TextChunk

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 8000  # Characters (fits ~2000 tokens)
DEFAULT_CHUNK_OVERLAP = 200  # Characters
DEFAULT_MIN_CHUNK_SIZE = 100  # Characters


class SentenceChunker:
    """Text chunker that respects sentence boundaries.

    This chunker splits text into chunks while trying to keep sentences
    intact. It finds sentence boundaries and creates chunks of approximately
    the target size without breaking sentences in the middle.

    Example:
        ```python
        chunker = SentenceChunker(chunk_size=4000, chunk_overlap=200)
        chunks = chunker.chunk(long_text)
        for chunk in chunks:
            print(f"Chunk {chunk.index}: {chunk.length} chars")
        ```

    Attributes:
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks.
        min_chunk_size: Minimum chunk size to create.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE,
    ) -> None:
        """Initialize the chunker.

        Args:
            chunk_size: Target chunk size in characters.
            chunk_overlap: Overlap between consecutive chunks.
            min_chunk_size: Minimum chunk size to create.
        """
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._min_chunk_size = min_chunk_size

    @property
    def name(self) -> str:
        """Return the chunker name."""
        return "sentence"

    @property
    def chunk_size(self) -> int:
        """Return the target chunk size."""
        return self._chunk_size

    @property
    def chunk_overlap(self) -> int:
        """Return the chunk overlap."""
        return self._chunk_overlap

    def chunk(self, text: str, **options: Any) -> list[TextChunk]:
        """Split text into chunks respecting sentence boundaries.

        Args:
            text: The text to chunk.
            **options: Override options:
                - chunk_size: Override default chunk size
                - chunk_overlap: Override default overlap
                - min_chunk_size: Override minimum size

        Returns:
            List of TextChunk objects.
        """
        # Get options with fallbacks
        chunk_size = options.get("chunk_size", self._chunk_size)
        chunk_overlap = options.get("chunk_overlap", self._chunk_overlap)
        min_chunk_size = options.get("min_chunk_size", self._min_chunk_size)

        # Clean and normalize text
        text = self._clean_text(text)

        if not text or len(text) < min_chunk_size:
            if text:
                return [
                    TextChunk(
                        content=text,
                        index=0,
                        start_position=0,
                        end_position=len(text),
                    )
                ]
            return []

        # Find sentence boundaries
        boundaries = self._find_sentence_boundaries(text)

        chunks: list[TextChunk] = []
        start_pos = 0
        chunk_index = 0

        while start_pos < len(text):
            # Find the end position for this chunk
            end_pos = min(start_pos + chunk_size, len(text))

            # If we're not at the end, find a good boundary
            if end_pos < len(text):
                # Find the nearest sentence boundary before end_pos
                best_boundary = self._find_best_boundary(
                    boundaries, start_pos, end_pos, chunk_size
                )
                if best_boundary:
                    end_pos = best_boundary

            # Extract chunk content
            chunk_content = text[start_pos:end_pos].strip()

            if len(chunk_content) >= min_chunk_size:
                chunks.append(
                    TextChunk(
                        content=chunk_content,
                        index=chunk_index,
                        start_position=start_pos,
                        end_position=end_pos,
                    )
                )
                chunk_index += 1

            # Move to next chunk position with overlap
            if end_pos >= len(text):
                break

            # Calculate next start position
            start_pos = max(start_pos + 1, end_pos - chunk_overlap)

            # Ensure we're making progress
            if start_pos >= end_pos:
                start_pos = end_pos

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

        # Account for overlap
        effective_chunk_size = self._chunk_size - self._chunk_overlap
        if effective_chunk_size <= 0:
            effective_chunk_size = self._chunk_size

        return max(1, (text_len + effective_chunk_size - 1) // effective_chunk_size)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Raw text.

        Returns:
            Cleaned text.
        """
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove non-printable characters (except newlines)
        text = "".join(c for c in text if c.isprintable() or c in "\n\t")
        return text.strip()

    def _find_sentence_boundaries(self, text: str) -> list[int]:
        """Find sentence boundary positions in text.

        Args:
            text: The text to analyze.

        Returns:
            List of positions after sentence endings.
        """
        boundaries: list[int] = []

        # Pattern for sentence endings: .!? followed by space or end
        # Also handle paragraph breaks
        pattern = r"[.!?]+[\s\n]+|[\n]{2,}"

        for match in re.finditer(pattern, text):
            boundaries.append(match.end())

        return boundaries

    def _find_best_boundary(
        self,
        boundaries: list[int],
        start_pos: int,
        end_pos: int,
        chunk_size: int,
    ) -> int | None:
        """Find the best sentence boundary for chunking.

        Tries to find a boundary close to end_pos but not too close
        to start_pos.

        Args:
            boundaries: List of sentence boundaries.
            start_pos: Chunk start position.
            end_pos: Desired end position.
            chunk_size: Target chunk size.

        Returns:
            Best boundary position or None if none found.
        """
        min_pos = start_pos + (chunk_size // 2)  # Don't split too early
        best = None

        for boundary in boundaries:
            if boundary <= start_pos:
                continue
            if boundary > end_pos:
                break
            if boundary >= min_pos:
                best = boundary

        return best
