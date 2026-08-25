from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from ..models.audit import AuditLog
from ..repositories.audit import AuditRepository
from ..schemas.audit import AuditLogCreate


class AuditService:
    def __init__(self, db: Session):
        self.audit_repository = AuditRepository(db)

    def log_action(
        self,
        action: str,
        merchant_id: UUID | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        """
        Record an action in the audit log.
        """
        data = AuditLogCreate(
            merchant_id=merchant_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
        )
        return self.audit_repository.create(data)

    def list_by_merchant(self, merchant_id: UUID, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """
        Retrieve audit logs for a specific merchant.
        """
        return self.audit_repository.list_by_merchant(merchant_id, skip, limit)
