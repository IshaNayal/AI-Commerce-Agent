from uuid import UUID

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from ..models.cart import CartStatus

class CartCreate(BaseModel):
    merchant_id: UUID
    customer_id: UUID


class CartUpdate(BaseModel):
    status: CartStatus | None = None


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    merchant_id: UUID
    customer_id: UUID
    status: CartStatus
    created_at: datetime
    updated_at: datetime