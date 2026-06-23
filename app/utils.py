from typing import Optional

from app.models import Notification, NotificationRecipient, Reminder, Room, User


def api_response(message: str, data=None):
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def user_to_dict(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "phone": user.phone,
        "status": user.status,
        "created_at": user.created_at,
    }


def room_to_dict(room: Room):
    return {
        "id": room.id,
        "room_number": room.room_number,
        "floor": room.floor,
        "room_type": room.room_type,
        "capacity": room.capacity,
        "price_per_night": room.price_per_night,
        "status": room.status,
        "note": room.note,
        "created_at": room.created_at,
    }


def notification_to_dict(
    notification: Notification,
    recipients=None,
    current_recipient: Optional[NotificationRecipient] = None,
):
    data = {
        "id": notification.id,
        "title": notification.title,
        "content": notification.content,
        "type": notification.type,
        "department": notification.department,
        "status": notification.status,
        "created_by": notification.created_by,
        "created_at": notification.created_at,
    }

    if recipients is not None:
        data["recipients"] = recipients

    if current_recipient is not None:
        data["recipient_status"] = current_recipient.status
        data["read_at"] = current_recipient.read_at

    return data


def reminder_to_dict(
    reminder: Reminder,
    room: Optional[Room] = None,
    assigned_user: Optional[User] = None,
):
    return {
        "id": reminder.id,
        "title": reminder.title,
        "content": reminder.content,
        "room_id": reminder.room_id,
        "room_number": room.room_number if room else None,
        "guest_name": reminder.guest_name,
        "reminder_type": reminder.reminder_type,
        "reminder_time": reminder.reminder_time,
        "assigned_user_id": reminder.assigned_user_id,
        "assigned_user_name": assigned_user.name if assigned_user else None,
        "status": reminder.status,
        "created_by": reminder.created_by,
        "created_at": reminder.created_at,
    }
