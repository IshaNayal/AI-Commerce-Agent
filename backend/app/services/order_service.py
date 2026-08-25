from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session

from ..models.order import Order, OrderStatus
from ..models.order_item import OrderItem
from ..models.cart import CartStatus
from ..repositories.cart import CartRepository
from ..repositories.cart_item import CartItemRepository
from ..repositories.inventory import InventoryRepository
from ..repositories.order import OrderRepository


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.cart_repository = CartRepository(db)
        self.cart_item_repository = CartItemRepository(db)
        self.inventory_repository = InventoryRepository(db)
        self.order_repository = OrderRepository(db)

    def checkout(self, cart_id: UUID) -> Order:
        """
        Check out a cart to create an order.
        This operation must be atomic.
        """
        cart = self.cart_repository.get_by_id(cart_id)
        if not cart:
            raise ValueError(f"Cart '{cart_id}' does not exist")

        if cart.status != CartStatus.ACTIVE:
            raise ValueError("Cart is already checked out or abandoned")

        cart_items = self.cart_item_repository.list_by_cart(cart_id)
        if not cart_items:
            raise ValueError("Cannot checkout an empty cart")

        subtotal = Decimal("0.00")
        
        # We will manually manage the transaction here to avoid partial commits.
        try:
            # Create Order
            order = Order(
                merchant_id=cart.merchant_id,
                customer_id=cart.customer_id,
                cart_id=cart.id,
                status=OrderStatus.PENDING,
                currency="INR", # Hardcoded for now based on default
                subtotal=Decimal("0.00") # Temporary
            )
            self.db.add(order)
            self.db.flush() # Get order.id

            for cart_item in cart_items:
                product = cart_item.product
                
                # Lock inventory row for update
                inventory = self.inventory_repository.get_by_product_id_for_update(product.id)
                if not inventory or inventory.quantity < cart_item.quantity:
                    raise ValueError(f"Insufficient inventory for product '{product.name}'")
                
                # Deduct inventory
                inventory.quantity -= cart_item.quantity
                
                # Create Order Item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    unit_price=product.price
                )
                self.db.add(order_item)
                
                # Add to subtotal
                subtotal += (product.price * cart_item.quantity)

            order.subtotal = subtotal
            cart.status = CartStatus.CHECKED_OUT
            
            self.db.commit()
            self.db.refresh(order)
            return order

        except Exception as e:
            self.db.rollback()
            raise e
