from fastapi import APIRouter , Depends , Query 
from sqlalchemy.orm import Session

from app.deps import get_db , require_admin
from app.schemas.audit_logs import AuditLogOut
from app.services import audit_logs as audit_service

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)]
)


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    entity: str | None = None,
    entity_id: int | None = None,
    user_id: int | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return audit_service.list_logs(db, entity, entity_id, user_id, page, size)