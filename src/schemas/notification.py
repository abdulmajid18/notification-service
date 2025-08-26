import uuid
from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel, Field

from src.models.notification import Notification
from src.schemas.enums.notification import NotificationCategory, NotificationLevel, NotificationChannel


class NotificationCreate(BaseModel):
    user_id: int
    message: str = Field(..., max_length=500)
    category: NotificationCategory
    level: Optional[NotificationLevel] = None
    channels: Optional[List[NotificationChannel]] = None
    metadata: Optional[dict] = None

class NotificationResponse(BaseModel):
    status: str
    message: str
    data: dict

@dataclass
class NotificationEvent:
    notification_id: str
    user_id: int
    severity: str
    channel: str
    message: str
    category: str
    metadata: Optional[dict] = None
    routing_key: Optional[str] = None

    def __post_init__(self):
        self.routing_key = f"{self.severity}.{self.channel}"


def create_event_from_payload(payload: Notification) -> List[NotificationEvent]:
    """
    Convert a Notification ORM object into one or more NotificationEvents
    (one per channel).
    """
    events = []

    for channel in (payload.channels or ["email"]):
        event = NotificationEvent(
            notification_id=str(payload.id),
            user_id=payload.user_id,
            channel=str(channel.value),
            severity=payload.level,
            message=payload.message,
            category=payload.category.value if hasattr(payload.category, "value") else str(payload.category),
            metadata=payload.metadata or {}
        )
        events.append(event)

    return events