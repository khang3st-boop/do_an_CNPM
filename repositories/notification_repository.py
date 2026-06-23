from models.notification import Notification


def get_all(db):
    return db.query(Notification).order_by(Notification.created_at.desc()).all()


def get_by_id(db, notification_id):
    return db.query(Notification).filter(Notification.id == notification_id).first()


def create(db, notification):
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_read(db, notification):
    notification.status = "read"
    db.commit()
    db.refresh(notification)
    return notification

