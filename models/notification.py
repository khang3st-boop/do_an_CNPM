from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.connection import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    department = Column(String(100), nullable=True)
    status = Column(String(50), default="unread")
    created_at = Column(DateTime, default=datetime.utcnow)

