from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="staff")
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(50), unique=True, index=True, nullable=False)
    floor = Column(Integer, nullable=True)
    room_type = Column(String(100), default="Standard")
    capacity = Column(Integer, default=2)
    price_per_night = Column(Float, default=0)
    status = Column(String(50), default="available")
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="general")
    department = Column(String(100), nullable=True)
    status = Column(String(50), default="active")
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String(50), default="unread")
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    room_id = Column(Integer, nullable=False, index=True)
    guest_name = Column(String(255), nullable=False)
    reminder_type = Column(String(50), nullable=False)
    reminder_time = Column(DateTime, nullable=False)
    assigned_user_id = Column(Integer, nullable=False, index=True)
    status = Column(String(50), default="pending")
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MaintenanceResult(Base):
    __tablename__ = "maintenance_results"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    result = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)