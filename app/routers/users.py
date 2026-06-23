from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import hash_password, require_admin_or_manager
from app.database import get_db
from app.models import User
from app.schemas import ALLOWED_USER_ROLES, ALLOWED_USER_STATUSES, UserCreateRequest
from app.utils import api_response, user_to_dict


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
def get_users(
    keyword: Optional[str] = None,
    role: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    query = db.query(User)

    if keyword:
        query = query.filter(
            (User.name.contains(keyword)) |
            (User.email.contains(keyword)) |
            (User.phone.contains(keyword))
        )

    if role:
        role = role.strip().lower()
        if role not in ALLOWED_USER_ROLES:
            raise HTTPException(
                status_code=400,
                detail="Vai trò không hợp lệ",
            )
        query = query.filter(User.role == role)

    if status_filter:
        status_filter = status_filter.strip().lower()
        if status_filter not in ALLOWED_USER_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Trạng thái tài khoản không hợp lệ",
            )
        query = query.filter(User.status == status_filter)

    users = query.order_by(User.id.desc()).all()

    return api_response(
        "Lấy danh sách tài khoản thành công",
        [user_to_dict(user) for user in users],
    )


@router.post("")
def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    existed_user = db.query(User).filter(User.email == request.email).first()

    if existed_user:
        raise HTTPException(
            status_code=400,
            detail="Email đã tồn tại",
        )

    new_user = User(
        name=request.name,
        email=request.email,
        password=hash_password(request.password),
        role=request.role,
        department=request.department,
        phone=request.phone,
        status="active",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return api_response(
        "Tạo tài khoản nhân viên thành công",
        {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "department": new_user.department,
            "phone": new_user.phone,
            "status": new_user.status,
        },
    )


@router.patch("/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Không thể tự khóa tài khoản của chính mình",
        )

    user.status = "locked" if user.status == "active" else "active"

    db.commit()
    db.refresh(user)

    return api_response(
        "Cập nhật trạng thái tài khoản thành công",
        {
            "id": user.id,
            "email": user.email,
            "status": user.status,
        },
    )
