"""OpenSearch Agentic Memory backend."""

from gnosisllm_knowledge.backends.opensearch.memory.client import OpenSearchMemoryClient
from gnosisllm_knowledge.backends.opensearch.memory.config import MemoryConfig
from gnosisllm_knowledge.backends.opensearch.memory.setup import MemorySetup, SetupStatus

__all__ = [
    "MemoryConfig",
    "MemorySetup",
    "OpenSearchMemoryClient",
    "SetupStatus",
]
