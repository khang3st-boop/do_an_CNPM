from repositories.internal_notification_repository import InternalNotificationRepository

VALID_PRIORITIES = ["low", "normal", "high", "urgent"]


class InternalNotificationService:
    def __init__(self, db):
        self.repo = InternalNotificationRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_for_user(self, user_id: int):
        return self.repo.get_for_user(user_id)

    def get_by_id(self, notif_id: int):
        return self.repo.get_by_id(notif_id)

    def count_unread(self, user_id: int) -> int:
        return self.repo.count_unread(user_id)

    def create(self, from_user_id: int, to_user_id, title: str,
               content: str, priority: str = "normal"):
        if not title or not title.strip():
            return None, "Tiêu đề không được để trống"
        if not content or not content.strip():
            return None, "Nội dung không được để trống"
        if priority not in VALID_PRIORITIES:
            priority = "normal"
        # to_user_id = None nghĩa là gửi tất cả (broadcast)
        to_id = int(to_user_id) if to_user_id and str(to_user_id).isdigit() else None
        n = self.repo.create(from_user_id, to_id, title.strip(), content.strip(), priority)
        return n, None

    def mark_read(self, notif_id: int):
        return self.repo.mark_read(notif_id)

    def delete(self, notif_id: int, current_user_id: int, current_role: str):
        n = self.repo.get_by_id(notif_id)
        if not n:
            return False, "Không tìm thấy thông báo"
        if n.FromUserID != current_user_id and current_role != "admin":
            return False, "Bạn không có quyền xóa thông báo này"
        self.repo.delete(notif_id)
        return True, None
