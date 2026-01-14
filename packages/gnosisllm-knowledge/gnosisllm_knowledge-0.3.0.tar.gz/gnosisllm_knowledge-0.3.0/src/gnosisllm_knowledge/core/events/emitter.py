"""Event emitter for knowledge module (Observer pattern)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from gnosisllm_knowledge.core.events.types import Event, EventType

T = TypeVar("T")

# Event handler types
SyncEventHandler = Callable[["Event"], None]
AsyncEventHandler = Callable[["Event"], Awaitable[None]]
EventHandler = SyncEventHandler | AsyncEventHandler


class EventEmitter:
    """Event emitter for decoupled communication (Observer pattern).

    Supports both synchronous and asynchronous event handlers.
    Handlers can be registered for specific event types or for all events.

    Example:
        ```python
        emitter = EventEmitter()

        @emitter.on(EventType.DOCUMENT_LOADED)
        def on_loaded(event: Event) -> None:
            print(f"Loaded: {event.data['url']}")

        @emitter.on(EventType.DOCUMENT_INDEXED)
        async def on_indexed(event: Event) -> None:
            await log_to_service(event)

        # Emit events
        emitter.emit(DocumentLoadedEvent(url="https://example.com"))
        await emitter.emit_async(DocumentIndexedEvent(doc_id="123"))
        ```
    """

    def __init__(self) -> None:
        """Initialize the event emitter."""
        self._handlers: dict[EventType, list[EventHandler]] = {}
        self._global_handlers: list[EventHandler] = []
        self._logger = logging.getLogger(__name__)

    def on(
        self,
        *event_types: EventType,
    ) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register an event handler.

        Can be used with one or more event types.

        Args:
            *event_types: Event types to listen for.
                If empty, handler is called for all events.

        Returns:
            Decorator function that registers the handler.

        Example:
            ```python
            @emitter.on(EventType.DOCUMENT_LOADED)
            def handler(event): ...

            @emitter.on(EventType.LOAD_STARTED, EventType.LOAD_COMPLETED)
            def multi_handler(event): ...

            @emitter.on()  # All events
            def global_handler(event): ...
            ```
        """

        def decorator(handler: EventHandler) -> EventHandler:
            if event_types:
                for event_type in event_types:
                    self.add_handler(event_type, handler)
            else:
                self._global_handlers.append(handler)
            return handler

        return decorator

    def add_handler(self, event_type: EventType, handler: EventHandler) -> None:
        """Register an event handler for a specific event type.

        Args:
            event_type: Event type to listen for.
            handler: Handler function to call.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def remove_handler(self, event_type: EventType, handler: EventHandler) -> None:
        """Remove an event handler.

        Args:
            event_type: Event type the handler was registered for.
            handler: Handler to remove.
        """
        if event_type in self._handlers:
            with contextlib.suppress(ValueError):
                self._handlers[event_type].remove(handler)

    def off(self, event_type: EventType, handler: EventHandler) -> None:
        """Alias for remove_handler."""
        self.remove_handler(event_type, handler)

    def emit(self, event: Event) -> None:
        """Emit an event synchronously.

        Calls all registered handlers for the event type.
        Async handlers are scheduled but not awaited.

        Args:
            event: The event to emit.
        """
        handlers = self._get_handlers(event.event_type)
        for handler in handlers:
            try:
                result = handler(event)
                # Schedule async handlers
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)
            except Exception as e:
                self._logger.error(f"Event handler error: {e}")

    async def emit_async(self, event: Event) -> None:
        """Emit an event asynchronously.

        Awaits all handlers, including async ones.

        Args:
            event: The event to emit.
        """
        handlers = self._get_handlers(event.event_type)
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                self._logger.error(f"Event handler error: {e}")

    async def emit_parallel(self, event: Event) -> None:
        """Emit an event and run handlers in parallel.

        All handlers are executed concurrently.

        Args:
            event: The event to emit.
        """
        handlers = self._get_handlers(event.event_type)
        tasks: list[Awaitable[None]] = []

        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    tasks.append(result)
            except Exception as e:
                self._logger.error(f"Event handler error: {e}")

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    self._logger.error(f"Async handler error: {result}")

    def _get_handlers(self, event_type: EventType) -> list[EventHandler]:
        """Get all handlers for an event type.

        Args:
            event_type: Event type to get handlers for.

        Returns:
            List of handlers (specific + global).
        """
        specific = self._handlers.get(event_type, [])
        return specific + self._global_handlers

    def clear(self) -> None:
        """Clear all event handlers."""
        self._handlers.clear()
        self._global_handlers.clear()

    def clear_type(self, event_type: EventType) -> None:
        """Clear handlers for a specific event type.

        Args:
            event_type: Event type to clear handlers for.
        """
        if event_type in self._handlers:
            self._handlers[event_type].clear()

    def handler_count(self, event_type: EventType | None = None) -> int:
        """Get the number of registered handlers.

        Args:
            event_type: Specific event type, or None for total.

        Returns:
            Number of handlers.
        """
        if event_type is None:
            return sum(len(h) for h in self._handlers.values()) + len(
                self._global_handlers
            )
        return len(self._handlers.get(event_type, [])) + len(self._global_handlers)
