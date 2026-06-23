from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_reminder_manager
from app.database import get_db
from app.models import Guest, Room, User
from app.schemas import GuestCreateRequest, GuestUpdateRequest
from app.utils import api_response, guest_to_dict


router = APIRouter(prefix="/api/guests", tags=["guests"])


def get_room_or_404(room_id: int, db: Session) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Khong tim thay phong",
        )

    if not room.is_active or room.status == "inactive":
        raise HTTPException(
            status_code=400,
            detail="Phong da bi vo hieu hoa",
        )

    return room


@router.post("")
def create_guest(
    request: GuestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reminder_manager),
):
    room = get_room_or_404(request.room_id, db)

    guest = Guest(
        full_name=request.full_name,
        phone=request.phone,
        email=request.email,
        identity_number=request.identity_number,
        room_id=request.room_id,
        check_in_date=request.check_in_date,
        check_out_date=request.check_out_date,
        is_active=True,
    )

    db.add(guest)
    db.commit()
    db.refresh(guest)

    return api_response(
        "Tao thong tin khach luu tru thanh cong",
        guest_to_dict(guest, room),
    )


@router.patch("/{guest_id}")
def update_guest(
    guest_id: int,
    request: GuestUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reminder_manager),
):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()

    if not guest:
        raise HTTPException(
            status_code=404,
            detail="Khong tim thay khach luu tru",
        )

    update_data = request.model_dump(exclude_unset=True)

    if "room_id" in update_data and update_data["room_id"] is not None:
        get_room_or_404(update_data["room_id"], db)

    check_in_date = update_data.get("check_in_date", guest.check_in_date)
    check_out_date = update_data.get("check_out_date", guest.check_out_date)

    if check_out_date and check_out_date <= check_in_date:
        raise HTTPException(
            status_code=400,
            detail="Ngay check-out phai lon hon ngay check-in",
        )

    for field, value in update_data.items():
        setattr(guest, field, value)

    db.commit()
    db.refresh(guest)

    room = db.query(Room).filter(Room.id == guest.room_id).first()

    return api_response(
        "Cap nhat thong tin khach luu tru thanh cong",
        guest_to_dict(guest, room),
    )
