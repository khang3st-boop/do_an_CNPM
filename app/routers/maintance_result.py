from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_room_viewer
from app.database import get_db
from app.models import MaintenanceResult, User
from app.utils import api_response, maintenance_result_to_dict

router = APIRouter(
    prefix="/api/maintenance-results",
    tags=["maintenance-results"]
)
@router.get("")
def get_maintenance_results(
    room_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    result_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_room_viewer),
):
    query = db.query(MaintenanceResult)

    if room_id:
        query = query.filter(
            MaintenanceResult.room_id == room_id
        )

    if status_filter:
        query = query.filter(
            MaintenanceResult.status == status_filter
        )

    if result_filter:
        query = query.filter(
            MaintenanceResult.result == result_filter
        )

    results = (
        query
        .order_by(MaintenanceResult.created_at.desc())
        .all()
    )

    return api_response(
        "Lấy danh sách kết quả bảo trì thành công",
        [
            maintenance_result_to_dict(item)
            for item in results
        ],
    )