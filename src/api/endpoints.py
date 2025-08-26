# src/api/endpoints.py
import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.config.database.database import AsyncSessionLocal
from src.models.notification import Notification
from src.schemas.notification import NotificationResponse, NotificationCreate, create_event_from_payload
from src.services.rabbitmq.connection import rabbitmq_connection

router = APIRouter(prefix="/api/v1", tags=["Notifications"])
logger = logging.getLogger(__name__)

@router.post(
    "/notifications/send",
    response_model=NotificationResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def send_notification(payload: NotificationCreate):
    async with AsyncSessionLocal() as session:
        try:
            notification = Notification(
                user_id=payload.user_id,
                message=payload.message,
                category=payload.category.value if hasattr(payload.category, "value") else str(payload.category),
                level=payload.level.value if hasattr(payload.level, "value") else str(payload.level),
                channels=[c.value if hasattr(c, "value") else str(c) for c in (payload.channels or ["email"])],
                extra_metadata=payload.metadata,
            )

            session.add(notification)
            await session.commit()
            await session.refresh(notification)

            response = NotificationResponse(
                status="success",
                message="Notification queued",
                data={**payload.model_dump(), "id": notification.id}
            )

            logger.info(
                "Notification saved successfully",
                extra={"notification_id": notification.id}
            )

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(
                "Notification DB save failed",
                exc_info=e,
                extra={"payload": payload.model_dump()}
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Database error"}
            )

        try:
            events = create_event_from_payload(notification)
            for event in events:
                rabbitmq_connection.send_notification(event)
        except Exception as e:
            logger.error("Failed to send RabbitMQ event", exc_info=e)
