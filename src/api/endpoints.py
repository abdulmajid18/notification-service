# src/api/endpoints.py
import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.schemas.notification import NotificationResponse, NotificationCreate

router = APIRouter(prefix="/api/v1", tags=["Notifications"])
logger = logging.getLogger(__name__)

@router.post(
    "/notifications/send",
    response_model=NotificationResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def send_notification(payload: NotificationCreate):
    try:
        logger.info(
            "Received notification request",
            extra={
                "payload": payload.model_dump(),
                "category": payload.category,
                "user_id": payload.user_id
            }
        )

        response = NotificationResponse(
            status="success",
            message="Notification queued",
            data=payload.model_dump()
        )

        logger.info(
            "Notification processed successfully",
            extra={"notification_id": "generated_id_here"}
        )
        return response

    except Exception as e:
        logger.error(
            "Notification processing failed",
            exc_info=e,
            extra={"payload": payload.model_dump()}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )