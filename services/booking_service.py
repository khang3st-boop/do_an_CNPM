from datetime import datetime

from repositories.booking_repository import BookingRepository
from repositories.reminder_repository import ReminderRepository
from repositories.room_repository import RoomRepository

VALID_STATUSES = ["confirmed", "checked_in", "checked_out", "cancelled"]


class BookingService:
    def __init__(self, db):
        self.repo = BookingRepository(db)
        self.room_repo = RoomRepository(db)
        self.reminder_repo = ReminderRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, booking_id: int):
        return self.repo.get_by_id(booking_id)

    def get_by_status(self, status: str):
        return self.repo.get_by_status(status)

    def create(self, guest_id: int, room_id: int,
               check_in_str: str, check_out_str: str,
               notes: str = "", total_price: float = 0,
               created_by_user_id: int = None):
        check_in, check_out, error = self._parse_dates(check_in_str, check_out_str)
        if error:
            return None, error

        conflict = self.repo.get_active_for_room(room_id)
        if conflict:
            return None, "Phong dang co khach hoac da duoc dat. Vui long chon phong khac."

        price, price_error = self._parse_price(total_price)
        if price_error:
            return None, price_error

        booking = self.repo.create(guest_id, room_id, check_in, check_out, notes, price)
        self.room_repo.update(room_id, status="occupied")
        if created_by_user_id:
            self._sync_booking_reminders(booking, created_by_user_id)
        return booking, None

    def update(self, booking_id: int, check_in_str: str, check_out_str: str,
               notes: str = "", total_price: float = 0,
               updated_by_user_id: int = None):
        booking = self.repo.get_by_id(booking_id)
        if not booking:
            return None, "Khong tim thay dat phong"
        check_in, check_out, error = self._parse_dates(check_in_str, check_out_str)
        if error:
            return None, error
        price, price_error = self._parse_price(total_price)
        if price_error:
            return None, price_error

        updated = self.repo.update(
            booking_id,
            CheckIn=check_in,
            CheckOut=check_out,
            Notes=notes,
            TotalPrice=price,
        )
        if updated_by_user_id:
            self._sync_booking_reminders(updated, updated_by_user_id)
        return updated, None

    def change_status(self, booking_id: int, new_status: str, current_role: str):
        if new_status not in VALID_STATUSES:
            return None, f"Trang thai khong hop le: {new_status}"
        booking = self.repo.get_by_id(booking_id)
        if not booking:
            return None, "Khong tim thay dat phong"

        updated = self.repo.update_status(booking_id, new_status)
        if new_status == "checked_in":
            self.room_repo.update(booking.RoomID, status="occupied")
        elif new_status in ("checked_out", "cancelled"):
            self.room_repo.update(booking.RoomID, status="available")

        return updated, None

    def delete(self, booking_id: int, current_role: str):
        if current_role not in ("admin", "manager"):
            return False, "Chi Admin/Manager moi co quyen xoa dat phong"
        booking = self.repo.get_by_id(booking_id)
        if not booking:
            return False, "Khong tim thay dat phong"
        if booking.Status in ("confirmed", "checked_in"):
            self.room_repo.update(booking.RoomID, status="available")
        self.repo.delete(booking_id)
        return True, None

    def _sync_booking_reminders(self, booking, user_id: int):
        room_number = booking.room.RoomNumber if booking.room else str(booking.RoomID)
        guest_name = booking.guest.FullName if booking.guest else str(booking.GuestID)
        reminder_data = [
            (
                "checkin",
                f"Check-in phong {room_number}",
                f"Khach {guest_name} nhan phong {room_number}",
                booking.CheckIn,
            ),
            (
                "checkout",
                f"Check-out phong {room_number}",
                f"Khach {guest_name} tra phong {room_number}",
                booking.CheckOut,
            ),
        ]
        for reminder_type, title, description, reminder_time in reminder_data:
            existing = self.reminder_repo.get_by_booking_type(booking.BookingID, reminder_type)
            if existing:
                self.reminder_repo.update(
                    existing.ReminderID,
                    title,
                    description,
                    reminder_time,
                    reminder_type,
                    booking.BookingID,
                )
            else:
                self.reminder_repo.create(
                    user_id,
                    title,
                    description,
                    reminder_time,
                    reminder_type,
                    booking.BookingID,
                )

    @staticmethod
    def _parse_dates(check_in_str: str, check_out_str: str):
        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%dT%H:%M")
            check_out = datetime.strptime(check_out_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return None, None, "Dinh dang ngay gio khong hop le"
        if check_out <= check_in:
            return None, None, "Ngay tra phong phai sau ngay nhan phong"
        return check_in, check_out, None

    @staticmethod
    def _parse_price(total_price):
        try:
            return float(total_price or 0), None
        except (TypeError, ValueError):
            return None, "Tong tien phai la so hop le"
