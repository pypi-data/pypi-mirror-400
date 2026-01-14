from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Topic:
    """Represents a stream topic."""

    name: str
    partitions: int
    retention_hours: int
    created_at: str
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Topic":
        return cls(
            name=data["name"],
            partitions=data["partitions"],
            retention_hours=data["retention_hours"],
            created_at=data["created_at"],
            description=data.get("description"),
        )


@dataclass
class ProduceResponse:
    """Response from producing an event."""

    topic: str
    partition: int
    offset: int
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProduceResponse":
        return cls(
            topic=data["topic"],
            partition=data["partition"],
            offset=data["offset"],
            timestamp=data["timestamp"],
        )


@dataclass
class Record:
    """A single event record."""

    topic: str
    partition: int
    offset: int
    value: Any
    timestamp: str
    key: Optional[str] = None
    headers: Optional[dict[str, str]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Record":
        return cls(
            topic=data["topic"],
            partition=data["partition"],
            offset=data["offset"],
            value=data["value"],
            timestamp=data["timestamp"],
            key=data.get("key"),
            headers=data.get("headers"),
        )


@dataclass
class ConsumeResponse:
    """Response from consuming events."""

    records: list[Record]
    next_offset: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConsumeResponse":
        return cls(
            records=[Record.from_dict(r) for r in data["records"]],
            next_offset=data["next_offset"],
        )


@dataclass
class TopicStats:
    """Statistics for a topic."""

    name: str
    total_events: int
    total_bytes: int
    events_per_second: float
    last_event_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TopicStats":
        return cls(
            name=data["name"],
            total_events=data["total_events"],
            total_bytes=data["total_bytes"],
            events_per_second=data["events_per_second"],
            last_event_at=data.get("last_event_at"),
        )
