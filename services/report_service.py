from repositories.booking_repository import BookingRepository
from repositories.room_repository import RoomRepository
from repositories.guest_repository import GuestRepository
from repositories.reminder_repository import ReminderRepository
from repositories.housekeeping_repository import HousekeepingRepository
from repositories.user_repository import UserRepository
from repositories.internal_notification_repository import InternalNotificationRepository
from repositories.guest_notification_repository import GuestNotificationRepository


class ReportService:
    """N1-10: Tổng hợp số liệu thống kê toàn hệ thống."""

    def __init__(self, db):
        self.db = db
        self.booking_repo       = BookingRepository(db)
        self.room_repo          = RoomRepository(db)
        self.guest_repo         = GuestRepository(db)
        self.reminder_repo      = ReminderRepository(db)
        self.hk_repo            = HousekeepingRepository(db)
        self.user_repo          = UserRepository(db)
        self.internal_repo      = InternalNotificationRepository(db)
        self.guest_notif_repo   = GuestNotificationRepository(db)

    def get_summary(self) -> dict:
        rooms    = self.room_repo.get_all()
        guests   = self.guest_repo.get_all()
        bookings = self.booking_repo.get_all()
        users    = self.user_repo.get_all()
        hk_tasks = self.hk_repo.get_all()

        # Phòng theo trạng thái
        room_status = {}
        for r in rooms:
            room_status[r.Status] = room_status.get(r.Status, 0) + 1

        # Đặt phòng theo trạng thái
        booking_status = self.booking_repo.count_by_status()

        # Công việc theo trạng thái
        task_status = self.hk_repo.count_by_status()
        overdue_tasks = self.hk_repo.count_overdue()

        # Reminder
        from repositories.reminder_repository import ReminderRepository
        from models.reminder import Reminder
        all_reminders = self.db.query(Reminder).all()
        reminder_status = {}
        for r in all_reminders:
            reminder_status[r.Status] = reminder_status.get(r.Status, 0) + 1

        internal_notifications = self.internal_repo.get_all()
        guest_notifications = self.guest_notif_repo.get_all()
        guest_notif_status = {}
        guest_notif_channel = {}
        for n in guest_notifications:
            guest_notif_status[n.Status] = guest_notif_status.get(n.Status, 0) + 1
            guest_notif_channel[n.Channel] = guest_notif_channel.get(n.Channel, 0) + 1

        return {
            # Tổng quan
            "total_rooms":    len(rooms),
            "total_guests":   len(guests),
            "total_bookings": len(bookings),
            "total_users":    len(users),
            "total_tasks":    len(hk_tasks),
            "total_reminders": len(all_reminders),
            "total_internal_notifications": len(internal_notifications),
            "total_guest_notifications": len(guest_notifications),
            "overdue_tasks": overdue_tasks,

            # Chi tiết
            "room_status":    room_status,
            "booking_status": booking_status,
            "task_status":    task_status,
            "reminder_status": reminder_status,
            "guest_notif_status": guest_notif_status,
            "guest_notif_channel": guest_notif_channel,

            # Top phòng (by booking count)
            "top_rooms": self._top_rooms(bookings),

            # Booking gần đây (5 cái)
            "recent_bookings": sorted(bookings, key=lambda b: b.CreatedAt, reverse=True)[:5],
        }

    def _top_rooms(self, bookings, top_n: int = 5):
        counts = {}
        for b in bookings:
            counts[b.RoomID] = counts.get(b.RoomID, 0) + 1
        sorted_rooms = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result = []
        for room_id, cnt in sorted_rooms:
            r = self.room_repo.get_by_id(room_id)
            if r:
                result.append({"room": r, "count": cnt})
        return result
