from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogCreate(BaseModel):
    merchant_id: UUID | None = None
    action: str
    entity_type: str | None = None
    entity_id: UUID | None = None
    details: dict[str, Any] = {}


class AuditLogResponse(BaseModel):
    id: UUID
    merchant_id: UUID | None
    action: str
    entity_type: str | None
    entity_id: UUID | None
    details: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
