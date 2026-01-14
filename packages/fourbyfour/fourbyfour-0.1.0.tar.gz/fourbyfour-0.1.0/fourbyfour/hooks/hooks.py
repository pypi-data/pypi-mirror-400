from typing import Any, Optional
from urllib.parse import quote

from ..http import HttpClient
from .types import Delivery, Endpoint, SendWebhookResponse, WebhookStats


class Hooks:
    """Client for webhook operations."""

    def __init__(self, http: HttpClient):
        self._http = http

    def create_endpoint(
        self,
        name: str,
        url: str,
        *,
        events: Optional[list[str]] = None,
        description: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Endpoint:
        """Create a webhook endpoint."""
        data: dict[str, Any] = {"name": name, "url": url}
        if events is not None:
            data["events"] = events
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata

        response = self._http.post("/webhooks/endpoints", data)
        return Endpoint.from_dict(response)

    def list_endpoints(self) -> list[Endpoint]:
        """List all webhook endpoints."""
        response = self._http.get("/webhooks/endpoints")
        return [Endpoint.from_dict(e) for e in response["endpoints"]]

    def delete_endpoint(self, name: str) -> None:
        """Delete a webhook endpoint."""
        self._http.delete(f"/webhooks/endpoints/{quote(name, safe='')}")

    def get_deliveries(self, endpoint_name: str) -> list[Delivery]:
        """Get delivery history for an endpoint."""
        response = self._http.get(
            f"/webhooks/endpoints/{quote(endpoint_name, safe='')}/deliveries"
        )
        return [Delivery.from_dict(d) for d in response["deliveries"]]

    def send(
        self,
        event_type: str,
        payload: Any,
        *,
        endpoints: Optional[list[str]] = None,
    ) -> SendWebhookResponse:
        """Send a webhook event."""
        data: dict[str, Any] = {"event_type": event_type, "payload": payload}
        if endpoints is not None:
            data["endpoints"] = endpoints

        response = self._http.post("/webhooks", data)
        return SendWebhookResponse.from_dict(response)

    def stats(self) -> WebhookStats:
        """Get webhook statistics."""
        response = self._http.get("/webhooks/stats")
        return WebhookStats.from_dict(response)
