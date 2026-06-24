from models.internal_notification import InternalNotification
from sqlalchemy.orm import joinedload


class InternalNotificationRepository:
    def __init__(self, db):
        self.db = db

    def _with_relations(self):
        return self.db.query(InternalNotification).options(
            joinedload(InternalNotification.sender),
            joinedload(InternalNotification.receiver),
        )

    def get_all(self):
        return (
            self._with_relations()
            .order_by(InternalNotification.CreatedAt.desc())
            .all()
        )

    def get_for_user(self, user_id: int):
        """Lấy thông báo dành cho user_id hoặc broadcast (ToUserID=None)."""
        return (
            self._with_relations()
            .filter(
                (InternalNotification.ToUserID == user_id)
                | (InternalNotification.ToUserID == None)  # noqa: E711
            )
            .order_by(InternalNotification.CreatedAt.desc())
            .all()
        )

    def get_by_id(self, notif_id: int):
        return self._with_relations().filter(
            InternalNotification.NotifID == notif_id
        ).first()

    def create(self, from_user_id: int, to_user_id, title: str,
               content: str, priority: str = "normal"):
        n = InternalNotification(
            FromUserID=from_user_id, ToUserID=to_user_id,
            Title=title, Content=content, Priority=priority
        )
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return self.get_by_id(n.NotifID)

    def mark_read(self, notif_id: int):
        n = self.db.query(InternalNotification).filter(InternalNotification.NotifID == notif_id).first()
        if n:
            n.IsRead = True
            self.db.commit()
        return self.get_by_id(notif_id)

    def delete(self, notif_id: int):
        n = self.db.query(InternalNotification).filter(InternalNotification.NotifID == notif_id).first()
        if n:
            self.db.delete(n)
            self.db.commit()
        return n

    def count_unread(self, user_id: int) -> int:
        return (
            self.db.query(InternalNotification)
            .filter(
                InternalNotification.IsRead == False,  # noqa: E712
                (InternalNotification.ToUserID == user_id)
                | (InternalNotification.ToUserID == None)  # noqa: E711
            )
            .count()
        )
