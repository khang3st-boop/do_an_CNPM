from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from models.internal_notification import InternalNotification, InternalNotificationRead


class InternalNotificationRepository:
    def __init__(self, db):
        self.db = db

    def _with_relations(self):
        return self.db.query(InternalNotification).options(
            joinedload(InternalNotification.sender),
            joinedload(InternalNotification.receiver),
        )

    def _target_filter(self, user_id: int, department: str = ""):
        return or_(
            InternalNotification.ToUserID == user_id,
            and_(
                InternalNotification.ToUserID == None,  # noqa: E711
                InternalNotification.ToDepartment == None,  # noqa: E711
            ),
            and_(
                InternalNotification.ToUserID == None,  # noqa: E711
                InternalNotification.ToDepartment == department,
            ),
        )

    def _read_ids(self, user_id: int):
        rows = (
            self.db.query(InternalNotificationRead.NotifID)
            .filter(InternalNotificationRead.UserID == user_id)
            .all()
        )
        return {row[0] for row in rows}

    def _attach_read_state(self, notifications, user_id: int):
        read_ids = self._read_ids(user_id)
        for notif in notifications:
            notif.UserRead = notif.NotifID in read_ids
        return notifications

    def get_all(self):
        return (
            self._with_relations()
            .order_by(InternalNotification.CreatedAt.desc())
            .all()
        )

    def get_for_user(self, user_id: int, department: str = ""):
        notifications = (
            self._with_relations()
            .filter(self._target_filter(user_id, department))
            .order_by(InternalNotification.CreatedAt.desc())
            .all()
        )
        return self._attach_read_state(notifications, user_id)

    def get_by_id(self, notif_id: int):
        return self._with_relations().filter(
            InternalNotification.NotifID == notif_id
        ).first()

    def create(self, from_user_id: int, to_user_id, title: str,
               content: str, priority: str = "normal", to_department: str = None):
        n = InternalNotification(
            FromUserID=from_user_id,
            ToUserID=to_user_id,
            ToDepartment=to_department,
            Title=title,
            Content=content,
            Priority=priority,
        )
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return self.get_by_id(n.NotifID)

    def mark_read(self, notif_id: int, user_id: int):
        exists = (
            self.db.query(InternalNotificationRead)
            .filter(
                InternalNotificationRead.NotifID == notif_id,
                InternalNotificationRead.UserID == user_id,
            )
            .first()
        )
        if not exists:
            self.db.add(InternalNotificationRead(
                NotifID=notif_id,
                UserID=user_id,
                ReadAt=datetime.now(),
            ))
            self.db.commit()
        return self.get_by_id(notif_id)

    def delete(self, notif_id: int):
        n = self.db.query(InternalNotification).filter(InternalNotification.NotifID == notif_id).first()
        if n:
            self.db.delete(n)
            self.db.commit()
        return n

    def count_unread(self, user_id: int, department: str = "") -> int:
        read_subquery = (
            self.db.query(InternalNotificationRead.NotifID)
            .filter(InternalNotificationRead.UserID == user_id)
        )
        return (
            self.db.query(InternalNotification)
            .filter(self._target_filter(user_id, department))
            .filter(~InternalNotification.NotifID.in_(read_subquery))
            .count()
        )
