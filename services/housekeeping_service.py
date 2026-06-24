from datetime import datetime
from repositories.housekeeping_repository import (
    HousekeepingRepository,
    VALID_TASK_TYPES, VALID_TASK_STATUSES, VALID_PRIORITIES
)


class HousekeepingService:
    def __init__(self, db):
        self.repo = HousekeepingRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, task_id: int):
        return self.repo.get_by_id(task_id)

    def get_by_status(self, status: str):
        return self.repo.get_by_status(status)

    def get_by_staff(self, user_id: int):
        return self.repo.get_by_staff(user_id)

    def get_overdue(self):
        return self.repo.get_overdue()

    def create(self, room_id: int, assigned_to_id, task_type: str,
               description: str, scheduled_at_str: str, priority: str = "normal",
               current_role: str = "staff"):
        if current_role not in ("admin", "manager"):
            return None, "Chỉ Admin/Manager mới có quyền tạo công việc"
        error = self._validate(task_type, scheduled_at_str, priority)
        if error:
            return None, error
        scheduled_at = datetime.strptime(scheduled_at_str, "%Y-%m-%dT%H:%M")
        to_id = int(assigned_to_id) if assigned_to_id and str(assigned_to_id).strip().isdigit() else None
        t = self.repo.create(room_id, to_id, task_type, description or "", scheduled_at, priority)
        return t, None

    def update(self, task_id: int, task_type: str, description: str,
               scheduled_at_str: str, priority: str, assigned_to_id,
               current_role: str = "staff", room_id=None, result_note=None):
        if current_role not in ("admin", "manager"):
            return None, "Chỉ Admin/Manager mới có quyền sửa công việc"
        t = self.repo.get_by_id(task_id)
        if not t:
            return None, "Không tìm thấy công việc"
        error = self._validate(task_type, scheduled_at_str, priority)
        if error:
            return None, error
        scheduled_at = datetime.strptime(scheduled_at_str, "%Y-%m-%dT%H:%M")
        to_id = int(assigned_to_id) if assigned_to_id and str(assigned_to_id).strip().isdigit() else None
        updated = self.repo.update(
            task_id,
            RoomID=room_id,
            TaskType=task_type,
            Description=description or "",
            ScheduledAt=scheduled_at,
            Priority=priority,
            AssignedToID=to_id,
            ResultNote=result_note,
        )
        return updated, None

    def update_status(self, task_id: int, new_status: str, current_user_id: int,
                      current_role: str, result_note: str = None):
        """N1-9: Nhân viên cập nhật trạng thái công việc của chính họ; admin/manager cập nhật tất cả."""
        t = self.repo.get_by_id(task_id)
        if not t:
            return None, "Không tìm thấy công việc"
        if new_status not in VALID_TASK_STATUSES:
            return None, "Trạng thái không hợp lệ"
        # Staff chỉ cập nhật task được giao cho mình
        if current_role == "staff" and t.AssignedToID != current_user_id:
            return None, "Bạn chỉ có thể cập nhật công việc được giao cho mình"
        updated = self.repo.update_status(task_id, new_status, result_note)
        return updated, None

    def delete(self, task_id: int, current_role: str):
        if current_role not in ("admin", "manager"):
            return False, "Chỉ Admin/Manager mới có quyền xóa công việc"
        t = self.repo.get_by_id(task_id)
        if not t:
            return False, "Không tìm thấy công việc"
        self.repo.delete(task_id)
        return True, None

    def count_by_status(self):
        return self.repo.count_by_status()

    def count_overdue(self):
        return self.repo.count_overdue()

    @staticmethod
    def _validate(task_type: str, scheduled_at_str: str, priority: str):
        if task_type not in VALID_TASK_TYPES:
            return f"Loại công việc không hợp lệ. Chọn: {', '.join(VALID_TASK_TYPES)}"
        if not scheduled_at_str:
            return "Thời gian thực hiện không được để trống"
        try:
            datetime.strptime(scheduled_at_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return "Định dạng thời gian không hợp lệ"
        if priority not in VALID_PRIORITIES:
            return f"Mức độ ưu tiên không hợp lệ"
        return None
