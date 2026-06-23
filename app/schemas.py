from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


ALLOWED_USER_ROLES = ["admin", "manager", "receptionist", "housekeeping", "technician", "staff"]
ALLOWED_USER_STATUSES = ["active", "locked"]
ALLOWED_ROOM_STATUSES = ["available", "occupied", "maintenance", "inactive"]
ALLOWED_NOTIFICATION_TYPES = ["general", "urgent", "maintenance", "policy", "event"]
ALLOWED_NOTIFICATION_STATUSES = ["active", "inactive"]
ALLOWED_RECIPIENT_STATUSES = ["unread", "read"]
ALLOWED_REMINDER_TYPES = ["check-in", "check-out"]
ALLOWED_REMINDER_STATUSES = ["pending", "in_progress", "completed", "cancelled"]


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Email không hợp lệ")
        return value


class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    role: str = "staff"
    department: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("department", "phone", mode="before")
    @classmethod
    def strip_optional_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value or None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Email không hợp lệ")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str):
        value = value.strip().lower()
        if value not in ALLOWED_USER_ROLES:
            raise ValueError("Vai trò không hợp lệ")
        return value


class RoomCreateRequest(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=50)
    floor: Optional[int] = Field(default=None, ge=0)
    room_type: str = Field(default="Standard", min_length=2, max_length=100)
    capacity: int = Field(default=2, ge=1)
    price_per_night: float = Field(default=0, ge=0)
    status: str = "available"
    note: Optional[str] = None

    @field_validator("room_number", "room_type", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("note", mode="before")
    @classmethod
    def strip_optional_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value or None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.strip().lower()
        if value not in ALLOWED_ROOM_STATUSES:
            raise ValueError("Trạng thái phòng không hợp lệ")
        return value


class RoomStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.strip().lower()
        if value not in ALLOWED_ROOM_STATUSES:
            raise ValueError("Trạng thái phòng không hợp lệ")
        return value


class NotificationCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field(..., min_length=2)
    type: str = "general"
    recipient_user_ids: Optional[List[int]] = None
    department: Optional[str] = Field(default=None, max_length=100)

    @field_validator("title", "content", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("department", mode="before")
    @classmethod
    def strip_optional_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value or None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str):
        value = value.strip().lower()
        if value not in ALLOWED_NOTIFICATION_TYPES:
            raise ValueError("Loại thông báo không hợp lệ")
        return value

    @field_validator("recipient_user_ids")
    @classmethod
    def validate_recipient_user_ids(cls, value):
        if value is None:
            return value
        unique_ids = []
        for user_id in value:
            if user_id <= 0:
                raise ValueError("ID người nhận không hợp lệ")
            if user_id not in unique_ids:
                unique_ids.append(user_id)
        return unique_ids

    @model_validator(mode="after")
    def validate_target(self):
        if not self.recipient_user_ids and not self.department:
            raise ValueError("Cần chọn recipient_user_ids hoặc department")
        return self


class ReminderCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: Optional[str] = None
    room_id: int = Field(..., ge=1)
    guest_name: str = Field(..., min_length=2, max_length=255)
    reminder_type: str
    reminder_time: datetime
    assigned_user_id: int = Field(..., ge=1)

    @field_validator("title", "guest_name", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("content", mode="before")
    @classmethod
    def strip_optional_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value or None

    @field_validator("reminder_type")
    @classmethod
    def validate_reminder_type(cls, value: str):
        value = value.strip().lower()
        if value not in ALLOWED_REMINDER_TYPES:
            raise ValueError("Loại lịch nhắc không hợp lệ")
        return value


class ReminderStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.strip().lower()
        if value not in ALLOWED_REMINDER_STATUSES:
            raise ValueError("Trạng thái lịch nhắc không hợp lệ")
        return value
