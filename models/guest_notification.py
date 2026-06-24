from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class GuestNotification(Base):
    """N1-6: Thông báo gửi tới khách hàng."""
    __tablename__ = "GuestNotifications"

    GuestNotifID = Column(Integer, primary_key=True, autoincrement=True)
    BookingID    = Column(Integer, ForeignKey("Bookings.BookingID"), nullable=False)
    Subject      = Column(String(200), nullable=False)
    Content      = Column(Text, nullable=False)
    Channel      = Column(String(30), default="system")   # system, email, sms
    Status       = Column(String(20), default="sent")     # draft, sent, failed
    SentAt       = Column(DateTime, default=datetime.now)
    CreatedAt    = Column(DateTime, default=datetime.now)

    booking = relationship("Booking", back_populates="guest_notifications")

    def __repr__(self):
        return f"<GuestNotif {self.Subject}>"
