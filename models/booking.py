from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime


class Booking(Base):
    __tablename__ = "Bookings"

    BookingID   = Column(Integer, primary_key=True, autoincrement=True)
    GuestID     = Column(Integer, ForeignKey("Guests.GuestID"), nullable=False)
    RoomID      = Column(Integer, ForeignKey("Rooms.RoomID"), nullable=False)
    CheckIn     = Column(DateTime, nullable=False)
    CheckOut    = Column(DateTime, nullable=False)
    Status      = Column(String(30), default="confirmed")  # confirmed, checked_in, checked_out, cancelled
    Notes       = Column(String(500))
    TotalPrice  = Column(Numeric(12, 2), default=0)
    CreatedAt   = Column(DateTime, default=datetime.now)

    guest    = relationship("Guest", back_populates="bookings")
    room     = relationship("Room")
    reminders = relationship("Reminder", back_populates="booking", cascade="all, delete-orphan")
    guest_notifications = relationship("GuestNotification", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Booking {self.BookingID} | Guest {self.GuestID} | Room {self.RoomID}>"
