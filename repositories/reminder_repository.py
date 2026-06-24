from models.reminder import Reminder
from models.booking import Booking
from datetime import datetime
from sqlalchemy.orm import joinedload


class ReminderRepository:
    def __init__(self, db):
        self.db = db

    def _with_relations(self):
        return self.db.query(Reminder).options(
            joinedload(Reminder.booking).joinedload(Booking.guest),
            joinedload(Reminder.booking).joinedload(Booking.room),
        )

    def get_all_by_user(self, user_id: int):
        return (
            self._with_relations()
            .filter(Reminder.UserID == user_id)
            .order_by(Reminder.ReminderTime.asc())
            .all()
        )

    def get_by_id(self, reminder_id: int):
        return self._with_relations().filter(Reminder.ReminderID == reminder_id).first()

    def get_by_booking_type(self, booking_id: int, reminder_type: str):
        return (
            self.db.query(Reminder)
            .filter(
                Reminder.BookingID == booking_id,
                Reminder.ReminderType == reminder_type,
            )
            .first()
        )

    def create(self, user_id: int, title: str, description: str, reminder_time: datetime,
               reminder_type: str = "custom", booking_id: int = None):
        r = Reminder(
            UserID=user_id,
            BookingID=booking_id,
            Title=title,
            Description=description,
            ReminderType=reminder_type,
            ReminderTime=reminder_time,
            Status="Chưa đến hạn",
        )
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def update(self, reminder_id: int, title: str, description: str, reminder_time: datetime,
               reminder_type: str = "custom", booking_id: int = None):
        r = self.db.query(Reminder).filter(Reminder.ReminderID == reminder_id).first()
        if r:
            r.BookingID = booking_id
            r.Title = title
            r.Description = description
            r.ReminderType = reminder_type
            r.ReminderTime = reminder_time
            r.Status = "Chưa đến hạn"
            self.db.commit()
        return self.get_by_id(reminder_id)

    def delete(self, reminder_id: int):
        r = self.db.query(Reminder).filter(Reminder.ReminderID == reminder_id).first()
        if r:
            self.db.delete(r)
            self.db.commit()
        return r

    def get_pending_due(self):
        """Lấy các reminder đã đến giờ và chưa gửi."""
        now = datetime.now()
        return (
            self.db.query(Reminder)
            .filter(Reminder.ReminderTime <= now, Reminder.Status == "Chưa đến hạn")
            .all()
        )

    def get_overdue_reminders(self):
        """Lấy các reminder 'Đã nhắc' mà đã quá hạn 24h."""
        from datetime import timedelta
        overdue_time = datetime.now() - timedelta(hours=24)
        return (
            self.db.query(Reminder)
            .filter(Reminder.ReminderTime <= overdue_time, Reminder.Status == "Đã nhắc")
            .all()
        )

    def mark_sent(self, reminder_id: int):
        r = self.db.query(Reminder).filter(Reminder.ReminderID == reminder_id).first()
        if r:
            r.Status = "Đã nhắc"
            self.db.commit()
        return r

    def update_status(self, reminder_id: int, status: str):
        r = self.db.query(Reminder).filter(Reminder.ReminderID == reminder_id).first()
        if r:
            r.Status = status
            self.db.commit()
        return r
