from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class Room(Base):
    __tablename__ = "Rooms"

    RoomID      = Column(Integer, primary_key=True, autoincrement=True)
    RoomNumber  = Column(String(20), nullable=False, unique=True)
    RoomType    = Column(String(50))          # Standard, Deluxe, VIP, Suite
    Status      = Column(String(20), default="available")  # available, occupied, maintenance
    Floor       = Column(Integer)
    Description = Column(String(500))
    CreatedAt   = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Room {self.RoomNumber} - {self.RoomType}>"
