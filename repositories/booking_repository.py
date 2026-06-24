from models.booking import Booking
from datetime import datetime
from sqlalchemy.orm import joinedload


class BookingRepository:
    def __init__(self, db):
        self.db = db

    def _with_relations(self):
        return self.db.query(Booking).options(
            joinedload(Booking.guest),
            joinedload(Booking.room),
        )

    def get_all(self):
        return (
            self._with_relations()
            .order_by(Booking.CheckIn.desc())
            .all()
        )

    def get_by_id(self, booking_id: int):
        return self._with_relations().filter(Booking.BookingID == booking_id).first()

    def get_by_guest(self, guest_id: int):
        return (
            self._with_relations()
            .filter(Booking.GuestID == guest_id)
            .order_by(Booking.CheckIn.desc())
            .all()
        )

    def get_by_room(self, room_id: int):
        return (
            self._with_relations()
            .filter(Booking.RoomID == room_id)
            .order_by(Booking.CheckIn.desc())
            .all()
        )

    def get_by_status(self, status: str):
        return (
            self._with_relations()
            .filter(Booking.Status == status)
            .order_by(Booking.CheckIn.asc())
            .all()
        )

    def get_active_for_room(self, room_id: int):
        """Lấy booking đang active (confirmed/checked_in) của phòng."""
        return (
            self.db.query(Booking)
            .filter(
                Booking.RoomID == room_id,
                Booking.Status.in_(["confirmed", "checked_in"])
            )
            .first()
        )

    def create(self, guest_id: int, room_id: int, check_in: datetime,
               check_out: datetime, notes: str = "", total_price: float = 0):
        b = Booking(
            GuestID=guest_id, RoomID=room_id,
            CheckIn=check_in, CheckOut=check_out,
            Notes=notes, TotalPrice=total_price,
            Status="confirmed"
        )
        self.db.add(b)
        self.db.commit()
        self.db.refresh(b)
        return self.get_by_id(b.BookingID)

    def update_status(self, booking_id: int, status: str):
        b = self.db.query(Booking).filter(Booking.BookingID == booking_id).first()
        if b:
            b.Status = status
            self.db.commit()
        return self.get_by_id(booking_id)

    def update(self, booking_id: int, **kwargs):
        b = self.db.query(Booking).filter(Booking.BookingID == booking_id).first()
        if not b:
            return None
        for field, value in kwargs.items():
            if value is not None:
                setattr(b, field, value)
        self.db.commit()
        return self.get_by_id(booking_id)

    def delete(self, booking_id: int):
        b = self.db.query(Booking).filter(Booking.BookingID == booking_id).first()
        if b:
            self.db.delete(b)
            self.db.commit()
        return b

    def count_by_status(self):
        """Trả về dict {status: count} — dùng cho báo cáo N1-10."""
        from sqlalchemy import func
        rows = (
            self.db.query(Booking.Status, func.count(Booking.BookingID))
            .group_by(Booking.Status)
            .all()
        )
        return {row[0]: row[1] for row in rows}
