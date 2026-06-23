from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_reminder_manager
from app.database import get_db
from app.models import Reminder, Room, User
from app.schemas import (
    ALLOWED_REMINDER_STATUSES,
    ALLOWED_REMINDER_TYPES,
    ReminderCreateRequest,
    ReminderStatusRequest,
)
from app.utils import api_response, reminder_to_dict


router = APIRouter(prefix="/api/reminders", tags=["reminders"])


@router.post("")
def create_reminder(
    request: ReminderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reminder_manager),
):
    room = db.query(Room).filter(Room.id == request.room_id).first()

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phòng",
        )

    if room.status == "inactive":
        raise HTTPException(
            status_code=400,
            detail="Không thể tạo lịch nhắc cho phòng đã vô hiệu hóa",
        )

    assigned_user = db.query(User).filter(
        User.id == request.assigned_user_id,
        User.status == "active",
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhân viên được giao",
        )

    reminder = Reminder(
        title=request.title,
        content=request.content,
        room_id=request.room_id,
        guest_name=request.guest_name,
        reminder_type=request.reminder_type,
        reminder_time=request.reminder_time,
        assigned_user_id=request.assigned_user_id,
        status="pending",
        created_by=current_user.id,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return api_response(
        "Tạo lịch nhắc thành công",
        reminder_to_dict(reminder, room=room, assigned_user=assigned_user),
    )


@router.get("")
def get_reminders(
    status_filter: Optional[str] = None,
    reminder_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reminder_manager),
):
    query = db.query(Reminder)

    if status_filter:
        status_filter = status_filter.strip().lower()
        if status_filter not in ALLOWED_REMINDER_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Trạng thái lịch nhắc không hợp lệ",
            )
        query = query.filter(Reminder.status == status_filter)

    if reminder_type:
        reminder_type = reminder_type.strip().lower()
        if reminder_type not in ALLOWED_REMINDER_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Loại lịch nhắc không hợp lệ",
            )
        query = query.filter(Reminder.reminder_type == reminder_type)

    reminders = query.order_by(Reminder.reminder_time.asc()).all()
    data = []

    for reminder in reminders:
        room = db.query(Room).filter(Room.id == reminder.room_id).first()
        assigned_user = db.query(User).filter(User.id == reminder.assigned_user_id).first()
        data.append(reminder_to_dict(reminder, room=room, assigned_user=assigned_user))

    return api_response("Lấy danh sách lịch nhắc thành công", data)


@router.get("/my")
def get_my_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reminders = db.query(Reminder).filter(
        Reminder.assigned_user_id == current_user.id,
    ).order_by(Reminder.reminder_time.asc()).all()
    data = []

    for reminder in reminders:
        room = db.query(Room).filter(Room.id == reminder.room_id).first()
        data.append(reminder_to_dict(reminder, room=room, assigned_user=current_user))

    return api_response("Lấy lịch nhắc của tôi thành công", data)


@router.get("/overdue")
def get_overdue_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Reminder).filter(
        Reminder.reminder_time < datetime.utcnow(),
        Reminder.status.in_(["pending", "in_progress"]),
    )

    if current_user.role not in ["admin", "manager", "receptionist"]:
        query = query.filter(Reminder.assigned_user_id == current_user.id)

    reminders = query.order_by(Reminder.reminder_time.asc()).all()
    data = []

    for reminder in reminders:
        room = db.query(Room).filter(Room.id == reminder.room_id).first()
        assigned_user = db.query(User).filter(User.id == reminder.assigned_user_id).first()
        data.append(reminder_to_dict(reminder, room=room, assigned_user=assigned_user))

    return api_response("Lấy danh sách lịch nhắc quá hạn thành công", data)


@router.patch("/{reminder_id}/status")
def update_reminder_status(
    reminder_id: int,
    request: ReminderStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()

    if not reminder:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch nhắc",
        )

    can_manage_all = current_user.role in ["admin", "manager", "receptionist"]
    if not can_manage_all and reminder.assigned_user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền cập nhật lịch nhắc này",
        )

    reminder.status = request.status

    db.commit()
    db.refresh(reminder)

    room = db.query(Room).filter(Room.id == reminder.room_id).first()
    assigned_user = db.query(User).filter(User.id == reminder.assigned_user_id).first()

    return api_response(
        "Cập nhật trạng thái lịch nhắc thành công",
        reminder_to_dict(reminder, room=room, assigned_user=assigned_user),
    )
