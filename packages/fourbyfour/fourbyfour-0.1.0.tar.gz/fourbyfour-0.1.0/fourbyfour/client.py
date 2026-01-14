from typing import Any, Optional

from .hooks import Hooks
from .http import HttpClient
from .notifications import Notifications
from .stream import Stream

DEFAULT_BASE_URL = "https://api.fourbyfour.dev"


class Fourbyfour:
    """
    Fourbyfour SDK client.

    Usage:
        client = Fourbyfour(api_key="sk_...")

        # Stream
        client.stream.topics.create("my-events")
        client.stream.topics.produce("my-events", value={"data": "test"})

        # Notifications
        client.notifications.send(NotificationChannel.EMAIL, "user@example.com", "Hello!")

        # Hooks
        client.hooks.create_endpoint("my-hook", "https://example.com/webhook")
        client.hooks.send("order.created", {"order_id": 123})
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        if not api_key:
            raise ValueError("api_key is required")

        self._http = HttpClient(
            base_url=base_url or DEFAULT_BASE_URL,
            api_key=api_key,
            timeout=timeout,
        )

        self.stream = Stream(self._http)
        self.notifications = Notifications(self._http)
        self.hooks = Hooks(self._http)

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self) -> "Fourbyfour":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
