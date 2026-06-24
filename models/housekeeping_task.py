from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class HousekeepingTask(Base):
    """N1-8: Lịch dọn phòng và bảo trì."""
    __tablename__ = "HousekeepingTasks"

    TaskID       = Column(Integer, primary_key=True, autoincrement=True)
    RoomID       = Column(Integer, ForeignKey("Rooms.RoomID"), nullable=False)
    AssignedToID = Column(Integer, ForeignKey("Users.UserID"), nullable=True)
    TaskType     = Column(String(50), nullable=False)   # cleaning, maintenance, inspection, setup
    Status       = Column(String(30), default="pending")  # pending, in_progress, done, cancelled
    Priority     = Column(String(20), default="normal")   # low, normal, high, urgent
    Description  = Column(Text)
    ResultNote   = Column(Text)
    ScheduledAt  = Column(DateTime, nullable=False)
    CompletedAt  = Column(DateTime, nullable=True)
    CreatedAt    = Column(DateTime, default=datetime.now)

    room        = relationship("Room")
    assigned_to = relationship("User")

    def __repr__(self):
        return f"<HousekeepingTask {self.TaskType} | Room {self.RoomID}>"
