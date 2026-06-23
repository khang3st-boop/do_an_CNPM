from models.reminder import Reminder


def get_all(db):
    return db.query(Reminder).order_by(Reminder.reminder_time.asc()).all()


def get_by_id(db, reminder_id):
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()


def create(db, reminder):
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def update_status(db, reminder, status):
    reminder.status = status
    db.commit()
    db.refresh(reminder)
    return reminder

