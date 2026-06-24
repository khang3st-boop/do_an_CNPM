from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Reminder(Base):
    __tablename__ = "Reminders"

    ReminderID    = Column(Integer, primary_key=True, autoincrement=True)
    UserID        = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    BookingID     = Column(Integer, ForeignKey("Bookings.BookingID"), nullable=True)  # N1-7: liên kết booking
    Title         = Column(String(200), nullable=False)
    Description   = Column(String(500))
    ReminderType  = Column(String(30), default="custom")  # checkin, checkout, cleaning, custom
    ReminderTime  = Column(DateTime, nullable=False)
    Status        = Column(String(50), default="Chưa đến hạn")
    CreatedAt     = Column(DateTime, default=datetime.now)

    user          = relationship("User", back_populates="reminders")
    booking       = relationship("Booking", back_populates="reminders")
    notifications = relationship("Notification", back_populates="reminder", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reminder {self.Title} @ {self.ReminderTime}>"
