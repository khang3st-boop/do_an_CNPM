from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "Users"

    UserID    = Column(Integer, primary_key=True, autoincrement=True)
    Username  = Column(String(50), nullable=False, unique=True)
    PasswordHash = Column(String(256), nullable=False)
    Email     = Column(String(100))
    Role      = Column(String(20), default="staff")
    CreatedAt = Column(DateTime, default=datetime.now)

    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.Username}>"
