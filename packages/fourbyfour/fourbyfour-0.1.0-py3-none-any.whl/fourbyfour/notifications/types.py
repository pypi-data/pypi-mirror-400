from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


@dataclass
class SendNotificationResponse:
    notification_id: str
    channel: NotificationChannel
    status: NotificationStatus

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SendNotificationResponse":
        return cls(
            notification_id=data["notification_id"],
            channel=NotificationChannel(data["channel"]),
            status=NotificationStatus(data["status"]),
        )


@dataclass
class Template:
    template_id: str
    name: str
    channel: NotificationChannel
    body_template: str
    enabled: bool
    created_at: str
    subject_template: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Template":
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            channel=NotificationChannel(data["channel"]),
            body_template=data["body_template"],
            enabled=data["enabled"],
            created_at=data["created_at"],
            subject_template=data.get("subject_template"),
        )


@dataclass
class ChannelStats:
    sent: int
    delivered: int
    failed: int
    delivery_rate: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChannelStats":
        return cls(
            sent=data["sent"],
            delivered=data["delivered"],
            failed=data["failed"],
            delivery_rate=data["delivery_rate"],
        )


@dataclass
class NotificationStats:
    tenant_id: str
    by_channel: dict[str, ChannelStats]
    total_sent: int
    total_delivered: int
    total_failed: int
    delivery_rate: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NotificationStats":
        return cls(
            tenant_id=data["tenant_id"],
            by_channel={k: ChannelStats.from_dict(v) for k, v in data["by_channel"].items()},
            total_sent=data["total_sent"],
            total_delivered=data["total_delivered"],
            total_failed=data["total_failed"],
            delivery_rate=data["delivery_rate"],
        )
