from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum
from src.schemas.enums.notification import NotificationCategory, NotificationLevel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    message = Column(String(500))
    category = Column(Enum(NotificationCategory))
    level = Column(Enum(NotificationLevel))
    is_read = Column(Boolean, default=False)
    metadata = Column(JSON)
    channels = Column(JSON)
