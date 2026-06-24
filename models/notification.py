from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Notification(Base):
    __tablename__ = "Notifications"

    NotificationID = Column(Integer, primary_key=True, autoincrement=True)
    ReminderID     = Column(Integer, ForeignKey("Reminders.ReminderID"), nullable=False)
    SentTime       = Column(DateTime, default=datetime.now)
    Status         = Column(String(20), default="sent")
    IsRead         = Column(Integer, default=0) # SQLite/SQL Server compatible boolean

    reminder = relationship("Reminder", back_populates="notifications")
