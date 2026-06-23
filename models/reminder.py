from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.connection import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    room_id = Column(Integer, nullable=True, index=True)
    guest_name = Column(String(255), nullable=True)
    reminder_type = Column(String(50), default="general")
    reminder_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

