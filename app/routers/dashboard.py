from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_room_viewer
from app.database import get_db
from app.models import Notification, Reminder, User
from app.utils import api_response

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"]
)

@router.get("/statistics")
def get_notification_reminder_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_room_viewer),
):
    total_notifications = (
        db.query(Notification)
        .count()
    )

    active_notifications = (
        db.query(Notification)
        .filter(Notification.status == "active")
        .count()
    )

    total_reminders = (
        db.query(Reminder)
        .count()
    )

    pending_reminders = (
        db.query(Reminder)
        .filter(Reminder.status == "pending")
        .count()
    )

    completed_reminders = (
        db.query(Reminder)
        .filter(Reminder.status == "completed")
        .count()
    )

    return api_response(
        "Lấy thống kê thông báo và lịch nhắc thành công",
        {
            "notifications": {
                "total": total_notifications,
                "active": active_notifications,
            },
            "reminders": {
                "total": total_reminders,
                "pending": pending_reminders,
                "completed": completed_reminders,
            },
        },
    )