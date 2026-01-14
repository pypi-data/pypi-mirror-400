"""Bounded streaming pipeline with backpressure support.

This module provides infrastructure for memory-efficient streaming pipelines
with bounded queues that apply backpressure when downstream processing is slow.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class PipelineConfig:
    """Configuration for streaming pipeline stages.

    Attributes:
        url_batch_size: Number of URLs to discover before yielding a batch.
        fetch_concurrency: Maximum parallel URL fetches.
        fetch_queue_size: Maximum URLs waiting to be fetched.
        index_batch_size: Documents per index batch.
        index_queue_size: Maximum docs waiting to be indexed.
        fetch_timeout_seconds: Timeout for each URL fetch.
        index_timeout_seconds: Timeout for each index batch.
    """

    # URL discovery
    url_batch_size: int = 100

    # Content fetching
    fetch_concurrency: int = 10
    fetch_queue_size: int = 50

    # Indexing
    index_batch_size: int = 100
    index_queue_size: int = 200

    # Timeouts
    fetch_timeout_seconds: float = 30.0
    index_timeout_seconds: float = 60.0


class BoundedQueue(Generic[T]):
    """Async queue with bounded size and backpressure.

    This queue provides backpressure: when full, put() blocks until space
    is available. This prevents memory from growing unboundedly when
    producers are faster than consumers.

    Example:
        ```python
        queue: BoundedQueue[str] = BoundedQueue(maxsize=10)

        # Producer task
        async def producer():
            for url in urls:
                await queue.put(url)  # Blocks if queue is full
            queue.close()

        # Consumer task
        async def consumer():
            async for item in queue:
                await process(item)
        ```
    """

    def __init__(self, maxsize: int = 0) -> None:
        """Initialize the bounded queue.

        Args:
            maxsize: Maximum queue size. 0 means unlimited (no backpressure).
        """
        self._queue: asyncio.Queue[T | None] = asyncio.Queue(maxsize=maxsize)
        self._closed = False
        self._consumer_count = 0

    async def put(self, item: T) -> None:
        """Put an item in the queue, blocking if full (backpressure).

        Args:
            item: The item to add to the queue.

        Raises:
            RuntimeError: If the queue has been closed.
        """
        if self._closed:
            raise RuntimeError("Queue is closed")
        await self._queue.put(item)

    def put_nowait(self, item: T) -> None:
        """Put an item without waiting (raises if full).

        Args:
            item: The item to add to the queue.

        Raises:
            RuntimeError: If the queue has been closed.
            asyncio.QueueFull: If the queue is full.
        """
        if self._closed:
            raise RuntimeError("Queue is closed")
        self._queue.put_nowait(item)

    async def get(self) -> T | None:
        """Get an item from the queue.

        Returns:
            The next item, or None if queue is closed and empty.
        """
        item = await self._queue.get()
        self._queue.task_done()
        return item

    def close(self) -> None:
        """Signal that no more items will be added.

        After closing, consumers will receive None when the queue
        is empty, signaling them to stop.
        """
        if not self._closed:
            self._closed = True
            # Put sentinel to unblock any waiting consumers
            try:
                self._queue.put_nowait(None)
            except asyncio.QueueFull:
                # Queue is full, consumer will eventually get the items
                pass

    @property
    def is_closed(self) -> bool:
        """Check if the queue has been closed."""
        return self._closed

    def qsize(self) -> int:
        """Return the current queue size."""
        return self._queue.qsize()

    def empty(self) -> bool:
        """Return True if the queue is empty."""
        return self._queue.empty()

    def full(self) -> bool:
        """Return True if the queue is full."""
        return self._queue.full()

    def __aiter__(self) -> AsyncIterator[T]:
        """Return async iterator for consuming items."""
        return self

    async def __anext__(self) -> T:
        """Get next item from queue.

        Raises:
            StopAsyncIteration: When queue is closed and empty.
        """
        item = await self.get()
        if item is None:
            raise StopAsyncIteration
        return item


class BatchCollector(Generic[T]):
    """Collects items into batches of a specified size.

    Useful for grouping streaming items into batches for
    efficient bulk processing.

    Example:
        ```python
        collector = BatchCollector[Document](batch_size=100)

        async for doc in document_stream:
            batch = collector.add(doc)
            if batch:
                await index_batch(batch)

        # Flush remaining items
        final_batch = collector.flush()
        if final_batch:
            await index_batch(final_batch)
        ```
    """

    def __init__(self, batch_size: int) -> None:
        """Initialize the batch collector.

        Args:
            batch_size: Number of items per batch.
        """
        self._batch_size = batch_size
        self._buffer: list[T] = []

    def add(self, item: T) -> list[T] | None:
        """Add an item to the current batch.

        Args:
            item: The item to add.

        Returns:
            A complete batch if batch_size is reached, otherwise None.
        """
        self._buffer.append(item)
        if len(self._buffer) >= self._batch_size:
            batch = self._buffer
            self._buffer = []
            return batch
        return None

    def flush(self) -> list[T] | None:
        """Flush any remaining items as a partial batch.

        Returns:
            The remaining items, or None if empty.
        """
        if self._buffer:
            batch = self._buffer
            self._buffer = []
            return batch
        return None

    @property
    def pending_count(self) -> int:
        """Return the number of items waiting in the buffer."""
        return len(self._buffer)
