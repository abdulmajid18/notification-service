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
