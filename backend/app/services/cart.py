from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.cart import Cart, CartStatus
from ..models.cart_item import CartItem
from ..repositories.cart import CartRepository
from ..repositories.cart_item import CartItemRepository
from ..repositories.inventory import InventoryRepository
from ..repositories.product import ProductRepository
from ..repositories.merchant import MerchantRepository
from ..schemas.cart import CartCreate, CartUpdate
from ..schemas.cart_item import CartItemCreate, CartItemUpdate


class CartService:
    """
    Business logic for shopping carts.

    Responsibilities:
    - Create and retrieve carts
    - Validate cart ownership
    - Add products to carts
    - Update cart item quantities
    - Remove cart items
    - Validate product availability
    - Validate inventory availability
    - Calculate cart subtotal

    Inventory is NOT decremented when an item is added to a cart.
    Inventory reservation/decrement belongs to checkout.
    """

    def __init__(self, db: Session):
        self.cart_repository = CartRepository(db)
        self.cart_item_repository = CartItemRepository(db)
        self.product_repository = ProductRepository(db)
        self.inventory_repository = InventoryRepository(db)
        self.merchant_repository = MerchantRepository(db)

    # ---------------------------------------------------------
    # Cart retrieval
    # ---------------------------------------------------------

    def get_cart(
        self,
        cart_id: UUID,
    ) -> Cart | None:
        """Return a cart by ID."""
        return self.cart_repository.get_by_id(cart_id)

    def get_or_create_cart(
        self,
        merchant_id: UUID,
        customer_id: UUID,
    ) -> Cart:
        """
        Return the customer's active cart for a merchant.

        If no active cart exists, create one.
        """

        self._validate_merchant(merchant_id)

        existing_cart = self.cart_repository.get_by_customer(
            merchant_id=merchant_id,
            customer_id=customer_id,
        )

        if existing_cart is not None:
            return existing_cart

        return self.cart_repository.create(
            CartCreate(
                merchant_id=merchant_id,
                customer_id=customer_id,
            )
        )

    def create_cart(
        self,
        data: CartCreate,
    ) -> Cart:
        """Create a new active cart."""

        self._validate_merchant(data.merchant_id)

        return self.cart_repository.create(data)

    # ---------------------------------------------------------
    # Add item
    # ---------------------------------------------------------

    def add_item(
        self,
        cart_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> CartItem:
        """
        Add a product to an active cart.

        Business rules:
        1. Cart must exist.
        2. Cart must be active.
        3. Quantity must be positive.
        4. Product must exist.
        5. Product must be active.
        6. Product must belong to the cart's merchant.
        7. Inventory must exist.
        8. Inventory must be sufficient.
        9. Duplicate products update the existing cart item.
        """

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        cart = self._get_active_cart(cart_id)

        product = self.product_repository.get_by_id(product_id)

        if product is None:
            raise ValueError(
                f"Product '{product_id}' does not exist"
            )

        if not product.is_active:
            raise ValueError(
                "Cannot add an inactive product to cart"
            )

        if product.merchant_id != cart.merchant_id:
            raise ValueError(
                "Product does not belong to this cart's merchant"
            )

        inventory = self.inventory_repository.get_by_product_id(
            product_id
        )

        if inventory is None:
            raise ValueError(
                f"Inventory for product '{product_id}' does not exist"
            )

        existing_item = (
            self.cart_item_repository.get_by_cart_and_product(
                cart_id,
                product_id,
            )
        )

        if existing_item is not None:
            new_quantity = existing_item.quantity + quantity

            if inventory.quantity < new_quantity:
                raise ValueError(
                    f"Insufficient inventory. "
                    f"Available: {inventory.quantity}, "
                    f"requested: {new_quantity}"
                )

            return self.cart_item_repository.update(
                existing_item,
                CartItemUpdate(
                    quantity=new_quantity
                ),
            )

        if inventory.quantity < quantity:
            raise ValueError(
                f"Insufficient inventory. "
                f"Available: {inventory.quantity}, "
                f"requested: {quantity}"
            )

        return self.cart_item_repository.create(
            CartItemCreate(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
            )
        )

    # ---------------------------------------------------------
    # Update item
    # ---------------------------------------------------------

    def update_item(
        self,
        cart_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> CartItem:
        """
        Replace the quantity of an existing cart item.

        Inventory is only checked, not decremented.
        """

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        self._get_active_cart(cart_id)

        item = (
            self.cart_item_repository.get_by_cart_and_product(
                cart_id,
                product_id,
            )
        )

        if item is None:
            raise ValueError(
                "Product is not present in this cart"
            )

        inventory = self.inventory_repository.get_by_product_id(
            product_id
        )

        if inventory is None:
            raise ValueError(
                f"Inventory for product '{product_id}' does not exist"
            )

        if inventory.quantity < quantity:
            raise ValueError(
                f"Insufficient inventory. "
                f"Available: {inventory.quantity}, "
                f"requested: {quantity}"
            )

        return self.cart_item_repository.update(
            item,
            CartItemUpdate(
                quantity=quantity
            ),
        )

    # ---------------------------------------------------------
    # Remove item
    # ---------------------------------------------------------

    def remove_item(
        self,
        cart_id: UUID,
        product_id: UUID,
    ) -> None:
        """
        Remove a product from an active cart.
        """

        self._get_active_cart(cart_id)

        item = (
            self.cart_item_repository.get_by_cart_and_product(
                cart_id,
                product_id,
            )
        )

        if item is None:
            raise ValueError(
                "Product is not present in this cart"
            )

        self.cart_item_repository.delete(item)

    # ---------------------------------------------------------
    # Cart items
    # ---------------------------------------------------------

    def list_items(
        self,
        cart_id: UUID,
    ) -> list[CartItem]:
        """Return all items in a cart."""

        self._get_cart(cart_id)

        return self.cart_item_repository.list_by_cart(
            cart_id
        )

    # ---------------------------------------------------------
    # Subtotal
    # ---------------------------------------------------------

    def calculate_subtotal(
        self,
        cart_id: UUID,
    ) -> Decimal:
        """
        Calculate the cart subtotal using the captured
        CartItem.unit_price.

        This deliberately does NOT read the current Product.price.
        """

        items = self.list_items(cart_id)

        return sum(
            (
                item.unit_price * item.quantity
                for item in items
            ),
            Decimal("0.00"),
        )

    # ---------------------------------------------------------
    # Cart state
    # ---------------------------------------------------------

    def update_cart_status(
        self,
        cart_id: UUID,
        status: CartStatus,
    ) -> Cart:
        """
        Update the cart status.

        Checkout workflow will later enforce stricter
        state transitions.
        """

        cart = self._get_cart(cart_id)

        return self.cart_repository.update(
            cart,
            CartUpdate(status=status),
        )

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _get_cart(
        self,
        cart_id: UUID,
    ) -> Cart:
        cart = self.cart_repository.get_by_id(cart_id)

        if cart is None:
            raise ValueError(
                f"Cart '{cart_id}' does not exist"
            )

        return cart

    def _get_active_cart(
        self,
        cart_id: UUID,
    ) -> Cart:
        cart = self._get_cart(cart_id)

        if cart.status != CartStatus.ACTIVE:
            raise ValueError(
                "Cart is not active"
            )

        return cart

    def _validate_merchant(
        self,
        merchant_id: UUID,
    ) -> None:
        merchant = self.merchant_repository.get_by_id(
            merchant_id
        )

        if merchant is None:
            raise ValueError(
                f"Merchant '{merchant_id}' does not exist"
            )

        if not merchant.is_active:
            raise ValueError(
                "Cannot create or use a cart for an inactive merchant"
            )