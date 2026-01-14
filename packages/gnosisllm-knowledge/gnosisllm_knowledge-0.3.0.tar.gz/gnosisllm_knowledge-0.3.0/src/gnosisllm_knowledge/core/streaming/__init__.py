"""Streaming pipeline configuration and utilities.

This module provides infrastructure for memory-efficient streaming
pipelines with bounded queues and backpressure support.

Example:
    ```python
    from gnosisllm_knowledge.core.streaming import (
        PipelineConfig,
        BoundedQueue,
        BatchCollector,
    )

    # Configure pipeline for large sitemap processing
    config = PipelineConfig(
        url_batch_size=50,
        fetch_concurrency=10,
        index_batch_size=100,
    )

    # Use bounded queue for backpressure
    queue: BoundedQueue[str] = BoundedQueue(maxsize=100)
    ```
"""

from gnosisllm_knowledge.core.streaming.pipeline import (
    BatchCollector,
    BoundedQueue,
    PipelineConfig,
)

__all__ = [
    "BatchCollector",
    "BoundedQueue",
    "PipelineConfig",
]
