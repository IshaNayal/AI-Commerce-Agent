from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.cart_item import CartItem
from ..models.product import Product
from ..schemas.cart_item import (
    CartItemCreate,
    CartItemUpdate,
)


class CartItemRepository:
    """
    Database access layer for CartItem entities.

    Responsible for CRUD and cart-specific database queries.

    Business rules such as:
    - whether the cart is active
    - whether enough inventory exists
    - whether the product is active
    - whether checkout has started

    should eventually live in the service layer.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: CartItemCreate) -> CartItem:
        """
        Create a cart item using the product's current price.

        unit_price is deliberately NOT accepted from the request.
        """

        product = self.db.scalar(
            select(Product).where(
                Product.id == data.product_id
            )
        )

        if product is None:
            raise ValueError("Product not found")

        cart_item = CartItem(
            cart_id=data.cart_id,
            product_id=data.product_id,
            quantity=data.quantity,
            unit_price=product.price,
        )

        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)

        return cart_item

    def get_by_id(
        self,
        cart_item_id: UUID,
    ) -> CartItem | None:
        """
        Fetch a cart item by ID.
        """

        statement = select(CartItem).where(
            CartItem.id == cart_item_id
        )

        return self.db.scalar(statement)

    def get_by_cart_and_product(
        self,
        cart_id: UUID,
        product_id: UUID,
    ) -> CartItem | None:
        """
        Find a particular product inside a cart.
        """

        statement = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )

        return self.db.scalar(statement)

    def list_by_cart(
        self,
        cart_id: UUID,
    ) -> list[CartItem]:
        """
        Return all items belonging to a cart.
        """

        statement = (
            select(CartItem)
            .where(CartItem.cart_id == cart_id)
            .order_by(CartItem.created_at.asc())
        )

        return list(
            self.db.scalars(statement).all()
        )

    def update(
        self,
        cart_item: CartItem,
        data: CartItemUpdate,
    ) -> CartItem:
        """
        Update the quantity of a cart item.
        """

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(cart_item, field, value)

        self.db.commit()
        self.db.refresh(cart_item)

        return cart_item

    def delete(
        self,
        cart_item: CartItem,
    ) -> None:
        """
        Delete a cart item.
        """

        self.db.delete(cart_item)
        self.db.commit()