from repositories.guest_notification_repository import GuestNotificationRepository

VALID_CHANNELS = ["system", "email", "sms"]


class GuestNotificationService:
    def __init__(self, db):
        self.repo = GuestNotificationRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_booking(self, booking_id: int):
        return self.repo.get_by_booking(booking_id)

    def get_by_id(self, notif_id: int):
        return self.repo.get_by_id(notif_id)

    def create(self, booking_id: int, subject: str, content: str, channel: str = "system"):
        if not subject or not subject.strip():
            return None, "Tiêu đề không được để trống"
        if not content or not content.strip():
            return None, "Nội dung không được để trống"
        if channel not in VALID_CHANNELS:
            channel = "system"
        n = self.repo.create(booking_id, subject.strip(), content.strip(), channel, "sent")
        return n, None

    def delete(self, notif_id: int):
        n = self.repo.get_by_id(notif_id)
        if not n:
            return False, "Không tìm thấy thông báo"
        self.repo.delete(notif_id)
        return True, None
