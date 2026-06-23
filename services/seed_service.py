from datetime import datetime, timedelta

from models.notification import Notification
from models.reminder import Reminder
from models.room import Room
from repositories import notification_repository, reminder_repository, room_repository
from services.auth_service import ensure_admin_account


def seed_default_data(db):
    ensure_admin_account(db)

    if not room_repository.get_by_room_number(db, "101"):
        room_repository.create(
            db,
            Room(
                room_number="101",
                room_type="Standard",
                floor=1,
                capacity=2,
                price_per_night=500000,
                status="available",
                is_active=True,
            ),
        )

    if not db.query(Notification).first():
        notification_repository.create(
            db,
            Notification(
                title="Thông báo họp giao ban",
                content="Họp giao ban tại quầy lễ tân lúc 08:00.",
                department="management",
                status="unread",
            ),
        )

    if not db.query(Reminder).first():
        reminder_repository.create(
            db,
            Reminder(
                title="Nhắc check-in phòng 101",
                content="Chuẩn bị hồ sơ check-in cho khách.",
                room_id=room_repository.get_by_room_number(db, "101").id,
                guest_name="Khách mẫu",
                reminder_type="check-in",
                reminder_time=datetime.utcnow() + timedelta(hours=2),
                status="pending",
            ),
        )

