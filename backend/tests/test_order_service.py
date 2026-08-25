from decimal import Decimal
import pytest

from backend.app.schemas.merchant import MerchantCreate
from backend.app.schemas.product import ProductCreate
from backend.app.schemas.inventory import InventoryCreate, InventoryUpdate
from backend.app.schemas.cart import CartCreate
from backend.app.services.merchant_services import MerchantService
from backend.app.services.product_service import ProductService
from backend.app.services.inventory_service import InventoryService
from backend.app.services.cart import CartService
from backend.app.services.order_service import OrderService
from backend.app.models.order import OrderStatus
from backend.app.models.cart import CartStatus


def setup_cart_scenario(db, inventory_quantity=10, cart_quantity=2):
    merchant = MerchantService(db).create(
        MerchantCreate(name="Test", slug="test-order", email="test@test.com")
    )
    product = ProductService(db).create(
        ProductCreate(merchant_id=merchant.id, name="Item", description="desc", sku="SKU1", price=Decimal("100.00"), currency="INR")
    )
    InventoryService(db).create(
        InventoryCreate(product_id=product.id, quantity=inventory_quantity)
    )
    
    cart_service = CartService(db)
    # The API service usually creates customer_id, we will generate one
    from uuid import uuid4
    customer_id = uuid4()
    
    cart = cart_service.create_cart(CartCreate(merchant_id=merchant.id, customer_id=customer_id))
    cart_service.add_item(cart_id=cart.id, product_id=product.id, quantity=cart_quantity)
    
    return merchant, product, cart


def test_checkout_success(db):
    merchant, product, cart = setup_cart_scenario(db, inventory_quantity=10, cart_quantity=2)
    
    order_service = OrderService(db)
    order = order_service.checkout(cart.id)
    
    assert order.status == OrderStatus.PENDING
    assert order.subtotal == Decimal("200.00")
    assert order.cart_id == cart.id
    
    # Check inventory was deducted
    inventory_service = InventoryService(db)
    inventory = inventory_service.get_by_product_id(product.id)
    assert inventory.quantity == 8
    
    # Check cart is checked out
    cart_service = CartService(db)
    updated_cart = cart_service.get_cart(cart.id)
    assert updated_cart.status == CartStatus.CHECKED_OUT


def test_checkout_insufficient_inventory(db):
    merchant, product, cart = setup_cart_scenario(db, inventory_quantity=10, cart_quantity=2)
    
    # Simulate someone else buying the product so inventory drops to 1
    inventory_service = InventoryService(db)
    inventory = inventory_service.get_by_product_id(product.id)
    inventory_service.update(inventory, InventoryUpdate(quantity=1))
    
    order_service = OrderService(db)
    with pytest.raises(ValueError, match="Insufficient inventory"):
        order_service.checkout(cart.id)
        
    # Check inventory was NOT deducted
    inventory_service = InventoryService(db)
    inventory = inventory_service.get_by_product_id(product.id)
    assert inventory.quantity == 1
    
    # Check cart is still active
    cart_service = CartService(db)
    updated_cart = cart_service.get_cart(cart.id)
    assert updated_cart.status == CartStatus.ACTIVE


def test_checkout_empty_cart(db):
    merchant = MerchantService(db).create(
        MerchantCreate(name="Test", slug="test-empty", email="test@empty.com")
    )
    cart_service = CartService(db)
    from uuid import uuid4
    cart = cart_service.create_cart(CartCreate(merchant_id=merchant.id, customer_id=uuid4()))
    
    order_service = OrderService(db)
    with pytest.raises(ValueError, match="empty cart"):
        order_service.checkout(cart.id)
