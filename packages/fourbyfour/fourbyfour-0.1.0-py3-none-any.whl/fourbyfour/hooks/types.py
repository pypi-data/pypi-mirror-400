from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class WebhookDeliveryStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Endpoint:
    endpoint_id: str
    name: str
    url: str
    secret: str
    events: list[str]
    enabled: bool
    created_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Endpoint":
        return cls(
            endpoint_id=data["endpoint_id"],
            name=data["name"],
            url=data["url"],
            secret=data["secret"],
            events=data["events"],
            enabled=data["enabled"],
            created_at=data["created_at"],
        )


@dataclass
class DeliveryInfo:
    delivery_id: str
    endpoint_name: str
    status: WebhookDeliveryStatus

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeliveryInfo":
        return cls(
            delivery_id=data["delivery_id"],
            endpoint_name=data["endpoint_name"],
            status=WebhookDeliveryStatus(data["status"]),
        )


@dataclass
class SendWebhookResponse:
    event_id: str
    deliveries: list[DeliveryInfo]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SendWebhookResponse":
        return cls(
            event_id=data["event_id"],
            deliveries=[DeliveryInfo.from_dict(d) for d in data["deliveries"]],
        )


@dataclass
class Delivery:
    delivery_id: str
    endpoint_name: str
    event_type: str
    status: WebhookDeliveryStatus
    retry_count: int
    created_at: str
    response_status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Delivery":
        return cls(
            delivery_id=data["delivery_id"],
            endpoint_name=data["endpoint_name"],
            event_type=data["event_type"],
            status=WebhookDeliveryStatus(data["status"]),
            retry_count=data["retry_count"],
            created_at=data["created_at"],
            response_status_code=data.get("response_status_code"),
            duration_ms=data.get("duration_ms"),
            error_message=data.get("error_message"),
        )


@dataclass
class EndpointStats:
    deliveries: int
    successful: int
    failed: int
    success_rate: float
    avg_duration_ms: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EndpointStats":
        return cls(
            deliveries=data["deliveries"],
            successful=data["successful"],
            failed=data["failed"],
            success_rate=data["success_rate"],
            avg_duration_ms=data["avg_duration_ms"],
        )


@dataclass
class WebhookStats:
    tenant_id: str
    by_endpoint: dict[str, EndpointStats]
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float
    avg_duration_ms: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WebhookStats":
        return cls(
            tenant_id=data["tenant_id"],
            by_endpoint={k: EndpointStats.from_dict(v) for k, v in data["by_endpoint"].items()},
            total_deliveries=data["total_deliveries"],
            successful_deliveries=data["successful_deliveries"],
            failed_deliveries=data["failed_deliveries"],
            success_rate=data["success_rate"],
            avg_duration_ms=data["avg_duration_ms"],
        )
