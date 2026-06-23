from datetime import datetime

from models.reminder import Reminder


def get_due_reminders(db):
    return (
        db.query(Reminder)
        .filter(Reminder.status == "pending", Reminder.reminder_time <= datetime.utcnow())
        .order_by(Reminder.reminder_time.asc())
        .all()
    )

