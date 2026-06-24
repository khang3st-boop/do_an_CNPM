from models.guest_notification import GuestNotification
from models.booking import Booking
from sqlalchemy.orm import joinedload


class GuestNotificationRepository:
    def __init__(self, db):
        self.db = db

    def _with_relations(self):
        return self.db.query(GuestNotification).options(
            joinedload(GuestNotification.booking).joinedload(Booking.guest),
            joinedload(GuestNotification.booking).joinedload(Booking.room),
        )

    def get_all(self):
        return (
            self._with_relations()
            .order_by(GuestNotification.SentAt.desc())
            .all()
        )

    def get_by_booking(self, booking_id: int):
        return (
            self._with_relations()
            .filter(GuestNotification.BookingID == booking_id)
            .order_by(GuestNotification.SentAt.desc())
            .all()
        )

    def get_by_id(self, notif_id: int):
        return self._with_relations().filter(
            GuestNotification.GuestNotifID == notif_id
        ).first()

    def create(self, booking_id: int, subject: str, content: str,
               channel: str = "system", status: str = "sent"):
        n = GuestNotification(
            BookingID=booking_id, Subject=subject, Content=content,
            Channel=channel, Status=status
        )
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return self.get_by_id(n.GuestNotifID)

    def delete(self, notif_id: int):
        n = self.db.query(GuestNotification).filter(GuestNotification.GuestNotifID == notif_id).first()
        if n:
            self.db.delete(n)
            self.db.commit()
        return n
