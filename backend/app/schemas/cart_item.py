from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
	cart_id: UUID
	product_id: UUID
	quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
	quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	cart_id: UUID
	product_id: UUID
	quantity: int
	unit_price: Decimal
	subtotal: Decimal
