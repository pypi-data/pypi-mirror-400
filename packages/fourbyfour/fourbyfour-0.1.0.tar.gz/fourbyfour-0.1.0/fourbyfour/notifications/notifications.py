from typing import Any, Optional
from urllib.parse import quote

from ..http import HttpClient
from .types import (
    NotificationChannel,
    NotificationStats,
    SendNotificationResponse,
    Template,
)


class Notifications:
    """Client for notification operations."""

    def __init__(self, http: HttpClient):
        self._http = http

    def send(
        self,
        channel: NotificationChannel,
        recipient: str,
        body: str,
        *,
        subject: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> SendNotificationResponse:
        """Send a notification."""
        data: dict[str, Any] = {
            "channel": channel.value,
            "recipient": recipient,
            "body": body,
        }
        if subject is not None:
            data["subject"] = subject
        if metadata is not None:
            data["metadata"] = metadata

        response = self._http.post("/notifications", data)
        return SendNotificationResponse.from_dict(response)

    def send_from_template(
        self,
        template_name: str,
        recipient: str,
        variables: dict[str, str],
    ) -> SendNotificationResponse:
        """Send a notification using a template."""
        response = self._http.post(
            "/notifications/template",
            {
                "template_name": template_name,
                "recipient": recipient,
                "variables": variables,
            },
        )
        return SendNotificationResponse.from_dict(response)

    def create_template(
        self,
        name: str,
        channel: NotificationChannel,
        body_template: str,
        *,
        subject_template: Optional[str] = None,
        default_metadata: Optional[dict[str, str]] = None,
    ) -> Template:
        """Create a notification template."""
        data: dict[str, Any] = {
            "name": name,
            "channel": channel.value,
            "body_template": body_template,
        }
        if subject_template is not None:
            data["subject_template"] = subject_template
        if default_metadata is not None:
            data["default_metadata"] = default_metadata

        response = self._http.post("/notifications/templates", data)
        return Template.from_dict(response)

    def list_templates(self) -> list[Template]:
        """List all notification templates."""
        response = self._http.get("/notifications/templates")
        return [Template.from_dict(t) for t in response["templates"]]

    def delete_template(self, name: str) -> None:
        """Delete a notification template."""
        self._http.delete(f"/notifications/templates/{quote(name, safe='')}")

    def stats(self) -> NotificationStats:
        """Get notification statistics."""
        response = self._http.get("/notifications/stats")
        return NotificationStats.from_dict(response)
