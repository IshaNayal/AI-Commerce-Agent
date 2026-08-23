from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    merchant_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sku: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    merchant_id: UUID
    name: str
    description: str | None
    sku: str
    price: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime