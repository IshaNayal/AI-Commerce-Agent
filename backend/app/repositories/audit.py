from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.audit import AuditLog
from ..schemas.audit import AuditLogCreate


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: AuditLogCreate) -> AuditLog:
        audit_log = AuditLog(
            merchant_id=data.merchant_id,
            action=data.action,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            details=data.details,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def list_by_merchant(self, merchant_id: UUID, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .where(AuditLog.merchant_id == merchant_id)
            .offset(skip)
            .limit(limit)
            .order_by(AuditLog.created_at.desc())
        )

        return list(self.db.scalars(statement).all())
