from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from database.connection import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(50), unique=True, nullable=False, index=True)
    room_type = Column(String(100), default="Standard")
    floor = Column(Integer, nullable=True)
    capacity = Column(Integer, default=2)
    price_per_night = Column(Float, default=0)
    status = Column(String(50), default="available")
    is_active = Column(Boolean, default=True, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

