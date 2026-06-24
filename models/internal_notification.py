from database.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime


class InternalNotification(Base):
    """N1-5: Thông báo nội bộ giữa các nhân viên."""
    __tablename__ = "InternalNotifications"

    NotifID    = Column(Integer, primary_key=True, autoincrement=True)
    FromUserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    ToUserID   = Column(Integer, ForeignKey("Users.UserID"), nullable=True)   # None = gửi tất cả
    ToDepartment = Column(String(50), nullable=True)
    Title      = Column(String(200), nullable=False)
    Content    = Column(String(1000), nullable=False)
    IsRead     = Column(Boolean, default=False)
    Priority   = Column(String(20), default="normal")   # low, normal, high, urgent
    CreatedAt  = Column(DateTime, default=datetime.now)

    sender   = relationship("User", foreign_keys=[FromUserID])
    receiver = relationship("User", foreign_keys=[ToUserID])

    def __repr__(self):
        return f"<InternalNotif {self.Title}>"


class InternalNotificationRead(Base):
    __tablename__ = "InternalNotificationReads"

    ReadID  = Column(Integer, primary_key=True, autoincrement=True)
    NotifID = Column(Integer, ForeignKey("InternalNotifications.NotifID"), nullable=False)
    UserID  = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    ReadAt  = Column(DateTime, default=datetime.now)
