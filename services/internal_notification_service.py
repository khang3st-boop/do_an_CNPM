from repositories.internal_notification_repository import InternalNotificationRepository

VALID_PRIORITIES = ["low", "normal", "high", "urgent"]
VALID_DEPARTMENTS = ["management", "reception", "housekeeping", "maintenance", "general"]


class InternalNotificationService:
    def __init__(self, db):
        self.repo = InternalNotificationRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_for_user(self, user_id: int, department: str = ""):
        return self.repo.get_for_user(user_id, department)

    def get_by_id(self, notif_id: int):
        return self.repo.get_by_id(notif_id)

    def count_unread(self, user_id: int, department: str = "") -> int:
        return self.repo.count_unread(user_id, department)

    def create(self, from_user_id: int, to_user_id, title: str,
               content: str, priority: str = "normal", to_department: str = None):
        if not title or not title.strip():
            return None, "Tieu de khong duoc de trong"
        if not content or not content.strip():
            return None, "Noi dung khong duoc de trong"
        if priority not in VALID_PRIORITIES:
            priority = "normal"

        to_id = int(to_user_id) if to_user_id and str(to_user_id).isdigit() else None
        dept = to_department if to_department in VALID_DEPARTMENTS else None
        n = self.repo.create(from_user_id, to_id, title.strip(), content.strip(), priority, dept)
        return n, None

    def mark_read(self, notif_id: int, user_id: int):
        return self.repo.mark_read(notif_id, user_id)

    def delete(self, notif_id: int, current_user_id: int, current_role: str):
        n = self.repo.get_by_id(notif_id)
        if not n:
            return False, "Khong tim thay thong bao"
        if n.FromUserID != current_user_id and current_role != "admin":
            return False, "Ban khong co quyen xoa thong bao nay"
        self.repo.delete(notif_id)
        return True, None
