from datetime import datetime
from repositories.booking_repository import BookingRepository
from repositories.room_repository import RoomRepository

VALID_STATUSES = ["confirmed", "checked_in", "checked_out", "cancelled"]


class BookingService:
    def __init__(self, db):
        self.repo      = BookingRepository(db)
        self.room_repo = RoomRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, booking_id: int):
        return self.repo.get_by_id(booking_id)

    def get_by_status(self, status: str):
        return self.repo.get_by_status(status)

    def create(self, guest_id: int, room_id: int,
               check_in_str: str, check_out_str: str,
               notes: str = "", total_price: float = 0):
        check_in, check_out, error = self._parse_dates(check_in_str, check_out_str)
        if error:
            return None, error

        # Kiểm tra phòng có đang bị đặt không
        conflict = self.repo.get_active_for_room(room_id)
        if conflict:
            return None, "Phòng đang có khách hoặc đã được đặt. Vui lòng chọn phòng khác."

        price, price_error = self._parse_price(total_price)
        if price_error:
            return None, price_error

        b = self.repo.create(guest_id, room_id, check_in, check_out,
                             notes, price)
        # Cập nhật trạng thái phòng → occupied
        self.room_repo.update(room_id, status="occupied")
        return b, None

    def update(self, booking_id: int, check_in_str: str, check_out_str: str,
               notes: str = "", total_price: float = 0):
        b = self.repo.get_by_id(booking_id)
        if not b:
            return None, "Không tìm thấy đặt phòng"
        check_in, check_out, error = self._parse_dates(check_in_str, check_out_str)
        if error:
            return None, error
        price, price_error = self._parse_price(total_price)
        if price_error:
            return None, price_error

        updated = self.repo.update(
            booking_id,
            CheckIn=check_in, CheckOut=check_out,
            Notes=notes, TotalPrice=price
        )
        return updated, None

    def change_status(self, booking_id: int, new_status: str, current_role: str):
        if new_status not in VALID_STATUSES:
            return None, f"Trạng thái không hợp lệ: {new_status}"
        b = self.repo.get_by_id(booking_id)
        if not b:
            return None, "Không tìm thấy đặt phòng"

        updated = self.repo.update_status(booking_id, new_status)

        # Đồng bộ trạng thái phòng
        if new_status == "checked_in":
            self.room_repo.update(b.RoomID, status="occupied")
        elif new_status in ("checked_out", "cancelled"):
            self.room_repo.update(b.RoomID, status="available")

        return updated, None

    def delete(self, booking_id: int, current_role: str):
        if current_role not in ("admin", "manager"):
            return False, "Chỉ Admin/Manager mới có quyền xóa đặt phòng"
        b = self.repo.get_by_id(booking_id)
        if not b:
            return False, "Không tìm thấy đặt phòng"
        # Trả phòng về available nếu đang active
        if b.Status in ("confirmed", "checked_in"):
            self.room_repo.update(b.RoomID, status="available")
        self.repo.delete(booking_id)
        return True, None

    @staticmethod
    def _parse_dates(check_in_str: str, check_out_str: str):
        try:
            check_in  = datetime.strptime(check_in_str, "%Y-%m-%dT%H:%M")
            check_out = datetime.strptime(check_out_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return None, None, "Định dạng ngày giờ không hợp lệ"
        if check_out <= check_in:
            return None, None, "Ngày trả phòng phải sau ngày nhận phòng"
        return check_in, check_out, None


# Gắn helper ở cuối class bằng monkey assignment rõ ràng cho code cũ vẫn dễ đọc.
def _booking_parse_price(total_price):
    try:
        return float(total_price or 0), None
    except (TypeError, ValueError):
        return None, "Tổng tiền phải là số hợp lệ"

BookingService._parse_price = staticmethod(_booking_parse_price)
