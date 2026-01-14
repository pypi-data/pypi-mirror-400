from typing import Any, Optional
from urllib.parse import quote

from ..http import HttpClient
from .types import ConsumeResponse, ProduceResponse, Topic, TopicStats


class Topics:
    """Client for stream topic operations."""

    def __init__(self, http: HttpClient):
        self._http = http

    def create(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        partitions: Optional[int] = None,
        retention_hours: Optional[int] = None,
    ) -> Topic:
        """Create a new topic."""
        data: dict[str, Any] = {"name": name}
        if description is not None:
            data["description"] = description
        if partitions is not None:
            data["partitions"] = partitions
        if retention_hours is not None:
            data["retention_hours"] = retention_hours

        response = self._http.post("/topics", data)
        return Topic.from_dict(response)

    def list(self) -> list[Topic]:
        """List all topics."""
        response = self._http.get("/topics")
        return [Topic.from_dict(t) for t in response["topics"]]

    def get(self, name: str) -> Topic:
        """Get a topic by name."""
        response = self._http.get(f"/topics/{quote(name, safe='')}")
        return Topic.from_dict(response)

    def delete(self, name: str) -> None:
        """Delete a topic."""
        self._http.delete(f"/topics/{quote(name, safe='')}")

    def produce(
        self,
        name: str,
        value: Any,
        *,
        key: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> ProduceResponse:
        """Produce an event to a topic."""
        data: dict[str, Any] = {"value": value}
        if key is not None:
            data["key"] = key
        if headers is not None:
            data["headers"] = headers

        response = self._http.post(f"/topics/{quote(name, safe='')}/produce", data)
        return ProduceResponse.from_dict(response)

    def consume(
        self,
        name: str,
        group: str,
        *,
        partition: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> ConsumeResponse:
        """Consume events from a topic."""
        response = self._http.get(
            f"/topics/{quote(name, safe='')}/consume",
            params={"group": group, "partition": partition, "limit": limit},
        )
        return ConsumeResponse.from_dict(response)

    def commit_offset(
        self,
        name: str,
        group: str,
        partition: int,
        offset: int,
    ) -> None:
        """Commit consumer offset."""
        self._http.post(
            f"/topics/{quote(name, safe='')}/offsets",
            {"group": group, "partition": partition, "offset": offset},
        )

    def stats(self, name: str) -> TopicStats:
        """Get topic statistics."""
        response = self._http.get(f"/topics/{quote(name, safe='')}/stats")
        return TopicStats.from_dict(response)
