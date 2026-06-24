from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class Guest(Base):
    __tablename__ = "Guests"

    GuestID     = Column(Integer, primary_key=True, autoincrement=True)
    FullName    = Column(String(100), nullable=False)
    IDCard      = Column(String(20), unique=True)          # CMND / CCCD
    Phone       = Column(String(20))
    Email       = Column(String(100))
    Address     = Column(String(300))
    Nationality = Column(String(50), default="Việt Nam")
    CreatedAt   = Column(DateTime, default=datetime.now)

    bookings = relationship("Booking", back_populates="guest", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Guest {self.FullName}>"
