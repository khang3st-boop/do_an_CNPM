from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_admin_or_manager
from app.database import get_db
from app.models import MaintenanceResult, User
from app.utils import api_response

router = APIRouter(
    prefix="/api/maintenance-results",
    tags=["maintenance-results"]
)


@router.patch("/{result_id}/deactivate")
def deactivate_maintenance_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    result = (
        db.query(MaintenanceResult)
        .filter(MaintenanceResult.id == result_id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy kết quả bảo trì",
        )

    result.status = "inactive"

    db.commit()
    db.refresh(result)

    return api_response(
        "Vô hiệu hóa kết quả bảo trì thành công",
        {
            "id": result.id,
            "status": result.status,
        },
    )