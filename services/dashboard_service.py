from datetime import datetime

from models.guest import Guest
from models.notification import Notification
from models.reminder import Reminder
from models.room import Room
from models.user import User


def get_dashboard_stats(db):
    return {
        "users": db.query(User).count(),
        "rooms": db.query(Room).filter(Room.is_active == True).count(),
        "guests": db.query(Guest).filter(Guest.is_active == True).count(),
        "pending_reminders": db.query(Reminder).filter(Reminder.status == "pending").count(),
        "notifications": db.query(Notification).count(),
        "overdue_reminders": (
            db.query(Reminder)
            .filter(Reminder.status == "pending", Reminder.reminder_time < datetime.utcnow())
            .count()
        ),
    }

