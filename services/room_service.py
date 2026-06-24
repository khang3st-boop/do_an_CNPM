from repositories.room_repository import RoomRepository

VALID_STATUSES  = ["available", "occupied", "maintenance"]
VALID_TYPES     = ["Standard", "Deluxe", "VIP", "Suite"]


class RoomService:
    def __init__(self, db):
        self.repo = RoomRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, room_id: int):
        return self.repo.get_by_id(room_id)

    def get_by_status(self, status: str):
        return self.repo.get_by_status(status)

    def create(self, room_number: str, room_type: str, floor: int, description: str = ""):
        error = self._validate(room_number, room_type, floor)
        if error:
            return None, error
        if self.repo.get_by_number(room_number):
            return None, f"Phòng {room_number} đã tồn tại"
        room = self.repo.create(room_number, room_type, int(floor), description)
        return room, None

    def update(self, room_id: int, room_type: str = None, status: str = None,
               floor: int = None, description: str = None):
        if not self.repo.get_by_id(room_id):
            return None, "Không tìm thấy phòng"
        if room_type and room_type not in VALID_TYPES:
            return None, f"Loại phòng không hợp lệ. Chọn: {', '.join(VALID_TYPES)}"
        if status and status not in VALID_STATUSES:
            return None, f"Trạng thái không hợp lệ. Chọn: {', '.join(VALID_STATUSES)}"
        room = self.repo.update(room_id, room_type=room_type, status=status,
                                floor=int(floor) if floor else None, description=description)
        return room, None

    def delete(self, room_id: int, current_user_role: str):
        if current_user_role not in ("admin", "manager"):
            return False, "Chỉ Admin/Manager mới có quyền xóa phòng"
        if not self.repo.get_by_id(room_id):
            return False, "Không tìm thấy phòng"
        self.repo.delete(room_id)
        return True, None

    @staticmethod
    def _validate(room_number, room_type, floor):
        if not room_number or not room_number.strip():
            return "Số phòng không được để trống"
        if room_type not in VALID_TYPES:
            return f"Loại phòng không hợp lệ. Chọn: {', '.join(VALID_TYPES)}"
        try:
            if int(floor) < 1:
                return "Tầng phải lớn hơn 0"
        except (TypeError, ValueError):
            return "Tầng phải là số nguyên"
        return None
