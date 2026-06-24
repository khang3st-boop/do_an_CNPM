from datetime import datetime
from repositories.reminder_repository import ReminderRepository


class ReminderService:
    def __init__(self, db):
        self.repo = ReminderRepository(db)

    def get_all(self, user_id: int):
        return self.repo.get_all_by_user(user_id)

    def get_by_id(self, reminder_id: int, user_id: int):
        """Lấy reminder và kiểm tra quyền sở hữu."""
        r = self.repo.get_by_id(reminder_id)
        if r and r.UserID == user_id:
            return r
        return None

    def create(self, user_id: int, title: str, description: str, reminder_time_str: str,
               reminder_type: str = "custom", booking_id: int = None):
        error = self._validate(title, reminder_time_str)
        if error:
            return None, error
        reminder_time = datetime.strptime(reminder_time_str, "%Y-%m-%dT%H:%M")
        b_id = int(booking_id) if booking_id and str(booking_id).strip().isdigit() else None
        r = self.repo.create(user_id, title.strip(), description.strip(), reminder_time,
                             reminder_type, b_id)
        return r, None

    def update(self, reminder_id: int, user_id: int, title: str, description: str, reminder_time_str: str,
               reminder_type: str = "custom", booking_id: int = None):
        r = self.get_by_id(reminder_id, user_id)
        if not r:
            return None, "Không tìm thấy lịch nhắc hoặc bạn không có quyền sửa"
        error = self._validate(title, reminder_time_str)
        if error:
            return None, error
        reminder_time = datetime.strptime(reminder_time_str, "%Y-%m-%dT%H:%M")
        b_id = int(booking_id) if booking_id and str(booking_id).strip().isdigit() else None
        updated = self.repo.update(reminder_id, title.strip(), description.strip(), reminder_time,
                                   reminder_type, b_id)
        return updated, None

    def delete(self, reminder_id: int, user_id: int):
        r = self.get_by_id(reminder_id, user_id)
        if not r:
            return False, "Không tìm thấy lịch nhắc hoặc bạn không có quyền xóa"
        self.repo.delete(reminder_id)
        return True, None

    def get_upcoming(self, user_id: int, limit: int = 5):
        """Lấy các lịch nhắc sắp tới (chưa gửi) cho dashboard."""
        now = datetime.now()
        reminders = self.repo.get_all_by_user(user_id)
        return [r for r in reminders if r.ReminderTime >= now and r.Status == "Chưa đến hạn"][:limit]

    def update_status(self, reminder_id: int, user_id: int, status: str):
        r = self.get_by_id(reminder_id, user_id)
        if not r:
            return False, "Không tìm thấy lịch nhắc hoặc bạn không có quyền thao tác"
        self.repo.update_status(reminder_id, status)
        return True, None

    @staticmethod
    def _validate(title: str, reminder_time_str: str):
        if not title or not title.strip():
            return "Tiêu đề không được để trống"
        if not reminder_time_str:
            return "Thời gian nhắc không được để trống"
        try:
            datetime.strptime(reminder_time_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return "Định dạng thời gian không hợp lệ"
        return None
