from uuid import UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.order import Order
from ..models.order_item import OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: UUID) -> Order | None:
        statement = select(Order).where(Order.id == order_id)
        return self.db.scalar(statement)

    def get_by_cart_id(self, cart_id: UUID) -> Order | None:
        statement = select(Order).where(Order.cart_id == cart_id)
        return self.db.scalar(statement)

    def list_by_merchant(self, merchant_id: UUID, skip: int = 0, limit: int = 100) -> list[Order]:
        statement = (
            select(Order)
            .where(Order.merchant_id == merchant_id)
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        return list(self.db.scalars(statement).all())
