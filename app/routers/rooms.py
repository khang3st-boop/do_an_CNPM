from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_admin_or_manager, require_room_viewer
from app.database import get_db
from app.models import Room, User
from app.schemas import ALLOWED_ROOM_STATUSES, RoomCreateRequest, RoomStatusRequest
from app.utils import api_response, room_to_dict


router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("")
def get_rooms(
    keyword: Optional[str] = None,
    status_filter: Optional[str] = None,
    room_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_room_viewer),
):
    query = db.query(Room)

    if keyword:
        query = query.filter(
            (Room.room_number.contains(keyword)) |
            (Room.room_type.contains(keyword))
        )

    if status_filter:
        status_filter = status_filter.strip().lower()
        if status_filter not in ALLOWED_ROOM_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Trạng thái phòng không hợp lệ",
            )
        query = query.filter(Room.status == status_filter)

    if room_type:
        room_type = room_type.strip()
        query = query.filter(Room.room_type == room_type)

    rooms = query.order_by(Room.room_number.asc()).all()

    return api_response(
        "Lấy danh sách phòng thành công",
        [room_to_dict(room) for room in rooms],
    )


@router.post("")
def create_room(
    request: RoomCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    existed_room = db.query(Room).filter(Room.room_number == request.room_number).first()

    if existed_room:
        raise HTTPException(
            status_code=400,
            detail="Số phòng đã tồn tại",
        )

    new_room = Room(
        room_number=request.room_number,
        floor=request.floor,
        room_type=request.room_type,
        capacity=request.capacity,
        price_per_night=request.price_per_night,
        status=request.status,
        note=request.note,
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return api_response(
        "Tạo phòng mới thành công",
        {
            "id": new_room.id,
            "room_number": new_room.room_number,
            "floor": new_room.floor,
            "room_type": new_room.room_type,
            "capacity": new_room.capacity,
            "price_per_night": new_room.price_per_night,
            "status": new_room.status,
            "note": new_room.note,
        },
    )


@router.patch("/{room_id}/status")
def update_room_status(
    room_id: int,
    request: RoomStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phòng",
        )

    room.status = request.status

    db.commit()
    db.refresh(room)

    return api_response(
        "Cập nhật trạng thái phòng thành công",
        {
            "id": room.id,
            "room_number": room.room_number,
            "status": room.status,
        },
    )


@router.patch("/{room_id}/deactivate")
def deactivate_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phòng",
        )

    room.status = "inactive"

    db.commit()
    db.refresh(room)

    return api_response(
        "Vô hiệu hóa phòng thành công",
        {
            "id": room.id,
            "room_number": room.room_number,
            "status": room.status,
        },
    )
