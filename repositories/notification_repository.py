from models.notification import Notification
from sqlalchemy.orm import joinedload


class NotificationRepository:
    def __init__(self, db):
        self.db = db

    def create(self, reminder_id: int):
        n = Notification(ReminderID=reminder_id, Status="sent", IsRead=0)
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return n

    def get_unread_by_user(self, user_id: int):
        from models.reminder import Reminder
        return (
            self.db.query(Notification)
            .options(joinedload(Notification.reminder))
            .join(Reminder)
            .filter(Reminder.UserID == user_id, Notification.IsRead == 0)
            .all()
        )

    def mark_read(self, notification_id: int):
        n = self.db.query(Notification).filter(Notification.NotificationID == notification_id).first()
        if n:
            n.IsRead = 1
            self.db.commit()
        return n
