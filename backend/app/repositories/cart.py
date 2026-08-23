from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.cart import Cart, CartStatus
from ..schemas.cart import CartCreate, CartUpdate


class CartRepository:
    """
    Database access layer for Cart entities.

    The repository is responsible only for persistence:
    - creating carts
    - fetching carts
    - listing carts
    - updating carts
    - deleting carts

    Business rules should live in the service layer.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: CartCreate) -> Cart:
        """
        Create a new cart.
        """

        cart = Cart(
            merchant_id=data.merchant_id,
            customer_id=data.customer_id,
            status=CartStatus.ACTIVE,
        )

        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)

        return cart

    def get_by_id(self, cart_id: UUID) -> Cart | None:
        """
        Fetch a cart by its primary key.
        """

        statement = select(Cart).where(
            Cart.id == cart_id
        )

        return self.db.scalar(statement)

    def get_by_customer(
        self,
        merchant_id: UUID,
        customer_id: UUID,
    ) -> Cart | None:
        """
        Fetch an active cart belonging to a customer
        within a specific merchant.
        """

        statement = (
            select(Cart)
            .where(
                Cart.merchant_id == merchant_id,
                Cart.customer_id == customer_id,
                Cart.status == CartStatus.ACTIVE,
            )
            .order_by(Cart.created_at.desc())
        )

        return self.db.scalars(statement).first()

    def list_by_merchant(
        self,
        merchant_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Cart]:
        """
        Return carts belonging to a merchant.
        """

        statement = (
            select(Cart)
            .where(Cart.merchant_id == merchant_id)
            .offset(skip)
            .limit(limit)
            .order_by(Cart.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        cart: Cart,
        data: CartUpdate,
    ) -> Cart:
        """
        Update mutable cart fields.
        """

        update_data = data.model_dump(
            exclude_unset=True
        )

        

        for field, value in update_data.items():
            setattr(cart, field, value)

        self.db.commit()
        self.db.refresh(cart)

        return cart

    def delete(self, cart: Cart) -> None:
        """
        Delete a cart.
        """

        self.db.delete(cart)
        self.db.commit()