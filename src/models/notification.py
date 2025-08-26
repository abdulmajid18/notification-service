from sqlalchemy import Column, Integer, String, JSON, Boolean
from src.config.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    category = Column(String, nullable=False)
    level = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    extra_metadata = Column(JSON, nullable=True)
    channels = Column(JSON, nullable=False)
