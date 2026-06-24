from models.housekeeping_task import HousekeepingTask
from datetime import datetime
from sqlalchemy.orm import joinedload


VALID_TASK_TYPES   = ["cleaning", "maintenance", "inspection", "setup"]
VALID_TASK_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_PRIORITIES   = ["low", "normal", "high", "urgent"]


class HousekeepingRepository:
    def __init__(self, db):
        self.db = db

    def _with_relations(self):
        return self.db.query(HousekeepingTask).options(
            joinedload(HousekeepingTask.room),
            joinedload(HousekeepingTask.assigned_to),
        )

    def get_all(self):
        return (
            self._with_relations()
            .order_by(HousekeepingTask.ScheduledAt.asc())
            .all()
        )

    def get_by_id(self, task_id: int):
        return self._with_relations().filter(HousekeepingTask.TaskID == task_id).first()

    def get_by_status(self, status: str):
        return (
            self._with_relations()
            .filter(HousekeepingTask.Status == status)
            .order_by(HousekeepingTask.ScheduledAt.asc())
            .all()
        )

    def get_by_room(self, room_id: int):
        return (
            self._with_relations()
            .filter(HousekeepingTask.RoomID == room_id)
            .order_by(HousekeepingTask.ScheduledAt.desc())
            .all()
        )

    def get_by_staff(self, user_id: int):
        return (
            self._with_relations()
            .filter(HousekeepingTask.AssignedToID == user_id)
            .order_by(HousekeepingTask.ScheduledAt.asc())
            .all()
        )

    def create(self, room_id: int, assigned_to_id, task_type: str,
               description: str, scheduled_at: datetime, priority: str = "normal"):
        t = HousekeepingTask(
            RoomID=room_id, AssignedToID=assigned_to_id,
            TaskType=task_type, Description=description,
            ScheduledAt=scheduled_at, Priority=priority,
            Status="pending"
        )
        self.db.add(t)
        self.db.commit()
        self.db.refresh(t)
        return self.get_by_id(t.TaskID)

    def update(self, task_id: int, **kwargs):
        t = self.db.query(HousekeepingTask).filter(HousekeepingTask.TaskID == task_id).first()
        if not t:
            return None
        for field, value in kwargs.items():
            if value is not None:
                setattr(t, field, value)
        self.db.commit()
        return self.get_by_id(task_id)

    def update_status(self, task_id: int, status: str):
        t = self.db.query(HousekeepingTask).filter(HousekeepingTask.TaskID == task_id).first()
        if t:
            t.Status = status
            if status == "done":
                t.CompletedAt = datetime.now()
            self.db.commit()
        return self.get_by_id(task_id)

    def delete(self, task_id: int):
        t = self.db.query(HousekeepingTask).filter(HousekeepingTask.TaskID == task_id).first()
        if t:
            self.db.delete(t)
            self.db.commit()
        return t

    def count_by_status(self):
        from sqlalchemy import func
        rows = (
            self.db.query(HousekeepingTask.Status, func.count(HousekeepingTask.TaskID))
            .group_by(HousekeepingTask.Status)
            .all()
        )
        return {row[0]: row[1] for row in rows}
