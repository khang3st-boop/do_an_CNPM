from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin_or_manager
from app.database import get_db
from app.models import Notification, NotificationRecipient, User
from app.schemas import (
    ALLOWED_NOTIFICATION_STATUSES,
    ALLOWED_NOTIFICATION_TYPES,
    NotificationCreateRequest,
)
from app.utils import api_response, notification_to_dict


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("")
def create_notification(
    request: NotificationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    recipient_ids = set(request.recipient_user_ids or [])

    if request.department:
        department_users = db.query(User).filter(
            User.department == request.department,
            User.status == "active",
        ).all()
        recipient_ids.update(user.id for user in department_users)

    if not recipient_ids:
        raise HTTPException(
            status_code=400,
            detail="Không tìm thấy người nhận thông báo",
        )

    recipients = db.query(User).filter(
        User.id.in_(recipient_ids),
        User.status == "active",
    ).all()
    found_recipient_ids = {user.id for user in recipients}
    missing_recipient_ids = recipient_ids - found_recipient_ids

    if missing_recipient_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy người nhận: {sorted(missing_recipient_ids)}",
        )

    notification = Notification(
        title=request.title,
        content=request.content,
        type=request.type,
        department=request.department,
        status="active",
        created_by=current_user.id,
    )

    db.add(notification)
    db.flush()

    db.add_all([
        NotificationRecipient(
            notification_id=notification.id,
            user_id=user.id,
            status="unread",
        )
        for user in recipients
    ])

    db.commit()
    db.refresh(notification)

    return api_response(
        "Tạo thông báo nội bộ thành công",
        notification_to_dict(
            notification,
            recipients=[
                {
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "status": "unread",
                    "read_at": None,
                }
                for user in recipients
            ],
        ),
    )


@router.get("")
def get_notifications(
    status_filter: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    query = db.query(Notification)

    if status_filter:
        status_filter = status_filter.strip().lower()
        if status_filter not in ALLOWED_NOTIFICATION_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Trạng thái thông báo không hợp lệ",
            )
        query = query.filter(Notification.status == status_filter)

    if type:
        type = type.strip().lower()
        if type not in ALLOWED_NOTIFICATION_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Loại thông báo không hợp lệ",
            )
        query = query.filter(Notification.type == type)

    notifications = query.order_by(Notification.id.desc()).all()
    data = []

    for notification in notifications:
        recipients = db.query(NotificationRecipient).filter(
            NotificationRecipient.notification_id == notification.id,
        ).all()
        item = notification_to_dict(notification)
        item["recipient_count"] = len(recipients)
        item["read_count"] = len([recipient for recipient in recipients if recipient.status == "read"])
        data.append(item)

    return api_response("Lấy danh sách thông báo thành công", data)


@router.get("/my")
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipient_rows = db.query(NotificationRecipient).filter(
        NotificationRecipient.user_id == current_user.id,
    ).order_by(NotificationRecipient.id.desc()).all()

    data = []
    for recipient in recipient_rows:
        notification = db.query(Notification).filter(
            Notification.id == recipient.notification_id,
            Notification.status == "active",
        ).first()
        if notification:
            data.append(notification_to_dict(notification, current_recipient=recipient))

    return api_response("Lấy thông báo của tôi thành công", data)


@router.get("/{notification_id}")
def get_notification_detail(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông báo",
        )

    if current_user.role in ["admin", "manager"]:
        recipient_rows = db.query(NotificationRecipient).filter(
            NotificationRecipient.notification_id == notification.id,
        ).all()
        recipient_user_ids = [recipient.user_id for recipient in recipient_rows]
        users = db.query(User).filter(User.id.in_(recipient_user_ids)).all() if recipient_user_ids else []
        users_by_id = {user.id: user for user in users}

        return api_response(
            "Lấy chi tiết thông báo thành công",
            notification_to_dict(
                notification,
                recipients=[
                    {
                        "user_id": recipient.user_id,
                        "name": users_by_id.get(recipient.user_id).name if users_by_id.get(recipient.user_id) else None,
                        "email": users_by_id.get(recipient.user_id).email if users_by_id.get(recipient.user_id) else None,
                        "status": recipient.status,
                        "read_at": recipient.read_at,
                    }
                    for recipient in recipient_rows
                ],
            ),
        )

    recipient = db.query(NotificationRecipient).filter(
        NotificationRecipient.notification_id == notification.id,
        NotificationRecipient.user_id == current_user.id,
    ).first()

    if not recipient or notification.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xem thông báo này",
        )

    return api_response(
        "Lấy chi tiết thông báo thành công",
        notification_to_dict(notification, current_recipient=recipient),
    )


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông báo",
        )

    if notification.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Thông báo đã bị vô hiệu hóa",
        )

    recipient = db.query(NotificationRecipient).filter(
        NotificationRecipient.notification_id == notification.id,
        NotificationRecipient.user_id == current_user.id,
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=403,
            detail="Bạn không phải người nhận thông báo này",
        )

    recipient.status = "read"
    recipient.read_at = datetime.utcnow()

    db.commit()
    db.refresh(recipient)

    return api_response(
        "Xác nhận đã đọc thông báo thành công",
        notification_to_dict(notification, current_recipient=recipient),
    )


@router.patch("/{notification_id}/deactivate")
def deactivate_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông báo",
        )

    notification.status = "inactive"

    db.commit()
    db.refresh(notification)

    return api_response(
        "Vô hiệu hóa thông báo thành công",
        notification_to_dict(notification),
    )
