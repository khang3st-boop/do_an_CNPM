from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_admin_or_manager
from app.database import get_db
from app.models import MaintenanceResult, User
from app.schemas import MaintenanceResultUpdateRequest
from app.utils import api_response

router = APIRouter(
    prefix="/api/maintenance-results",
    tags=["maintenance-results"]
)


@router.put("/{result_id}")
def update_maintenance_result(
    result_id: int,
    request: MaintenanceResultUpdateRequest,
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

    result.title = request.title
    result.description = request.description
    result.result = request.result

    db.commit()
    db.refresh(result)

    return api_response(
        "Cập nhật kết quả bảo trì thành công",
        {
            "id": result.id,
            "title": result.title,
            "description": result.description,
            "result": result.result,
            "status": result.status,
        },
    )