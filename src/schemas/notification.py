import uuid
from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel, Field

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


def create_event_from_payload(payload: NotificationCreate) -> List[NotificationEvent]:
    """
    Convert NotificationCreate request into one or more NotificationEvents
    (one per channel).
    """
    events = []
    notification_id = str(uuid.uuid4())

    level = payload.level.value if payload.level else NotificationLevel.NON_CRITICAL.value

    for channel in (payload.channels or [NotificationChannel.EMAIL]):
        event = NotificationEvent(
            notification_id=notification_id,
            user_id=payload.user_id,
            channel=str(channel.value),
            severity=level,
            message=payload.message,
            category=payload.category.value,
            metadata=payload.metadata or {}
        )
        events.append(event)

    return events