from repositories.booking_repository import BookingRepository
from repositories.guest_notification_repository import GuestNotificationRepository

VALID_CHANNELS = ["system", "email", "sms"]


class GuestNotificationService:
    def __init__(self, db):
        self.repo = GuestNotificationRepository(db)
        self.booking_repo = BookingRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_booking(self, booking_id: int):
        return self.repo.get_by_booking(booking_id)

    def get_by_id(self, notif_id: int):
        return self.repo.get_by_id(notif_id)

    def create(self, booking_id: int, subject: str, content: str, channel: str = "system"):
        if not subject or not subject.strip():
            return None, "Tieu de khong duoc de trong"
        if not content or not content.strip():
            return None, "Noi dung khong duoc de trong"
        if channel not in VALID_CHANNELS:
            channel = "system"

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            return None, "Khong tim thay dat phong"

        status = "sent"
        guest = booking.guest
        if channel == "email" and not getattr(guest, "Email", None):
            status = "failed"
            content = f"{content.strip()}\n\n[He thong] Khach chua co email nen chua the gui email that."
        elif channel == "sms" and not getattr(guest, "Phone", None):
            status = "failed"
            content = f"{content.strip()}\n\n[He thong] Khach chua co so dien thoai nen chua the gui SMS that."

        n = self.repo.create(booking_id, subject.strip(), content.strip(), channel, status)
        return n, None

    def delete(self, notif_id: int):
        n = self.repo.get_by_id(notif_id)
        if not n:
            return False, "Khong tim thay thong bao"
        self.repo.delete(notif_id)
        return True, None
