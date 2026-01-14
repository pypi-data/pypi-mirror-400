"""Event system for decoupled communication (Observer pattern)."""

from gnosisllm_knowledge.core.events.emitter import EventEmitter
from gnosisllm_knowledge.core.events.types import (
    BatchCompletedEvent,
    BatchStartedEvent,
    DocumentIndexedEvent,
    DocumentLoadedEvent,
    Event,
    EventType,
    SitemapDiscoveryEvent,
)

__all__ = [
    "Event",
    "EventType",
    "EventEmitter",
    "DocumentLoadedEvent",
    "DocumentIndexedEvent",
    "SitemapDiscoveryEvent",
    "BatchStartedEvent",
    "BatchCompletedEvent",
]
