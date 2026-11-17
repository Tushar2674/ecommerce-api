from sqlalchemy.orm import Session
from app.models.audit_logs import AuditLog
from sqlalchemy import select


def log_action(
    db: Session, user_id: int | None, action: str, entity: str, entity_id: int | None
) -> None:
    db.add(AuditLog(user_id=user_id, action=action, entity=entity, entity_id=entity_id))


def list_logs(db, entity, entity_id, user_id, page, size) -> list[AuditLog]:
    stmt = select(AuditLog)
    if entity is not None:
        stmt = stmt.where(AuditLog.entity == entity)
    if entity_id is not None:
        stmt = stmt.where(AuditLog.entity_id == entity_id)
    if user_id is not None:
        stmt = stmt.where(AuditLog.user_id == user_id)

    stmt = stmt.order_by(AuditLog.id.desc()).offset((page - 1) * size).limit(size)
    return list(db.execute(stmt).scalars().all())
