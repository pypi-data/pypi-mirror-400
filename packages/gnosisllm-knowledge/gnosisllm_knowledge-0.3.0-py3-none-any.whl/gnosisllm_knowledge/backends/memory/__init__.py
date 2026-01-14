"""In-memory backend for testing."""

from gnosisllm_knowledge.backends.memory.indexer import MemoryIndexer
from gnosisllm_knowledge.backends.memory.searcher import MemorySearcher

__all__ = [
    "MemoryIndexer",
    "MemorySearcher",
]
