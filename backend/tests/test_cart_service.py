from decimal import Decimal
from uuid import uuid4

import pytest

from backend.app.models.cart import CartStatus
from backend.app.repositories.cart import CartRepository
from backend.app.repositories.inventory import InventoryRepository
from backend.app.repositories.merchant import MerchantRepository
from backend.app.repositories.product import ProductRepository
from backend.app.schemas.cart import CartCreate, CartUpdate
from backend.app.schemas.inventory import InventoryCreate
from backend.app.schemas.merchant import MerchantCreate
from backend.app.schemas.product import ProductCreate
from backend.app.services.cart import CartService


def create_test_merchant(db):
    repository = MerchantRepository(db)

    return repository.create(
        MerchantCreate(
            name="Test Merchant",
            slug=f"merchant-{uuid4().hex[:8]}",
            email="merchant@example.com",
        )
    )


def create_test_product(db, merchant_id, price="999.99"):
    repository = ProductRepository(db)

    return repository.create(
        ProductCreate(
            merchant_id=merchant_id,
            name="Test Product",
            description="Test product",
            sku=f"SKU-{uuid4().hex[:8]}",
            price=Decimal(price),
            currency="INR",
        )
    )


def create_test_inventory(db, product_id, quantity=10):
    repository = InventoryRepository(db)

    return repository.create(
        InventoryCreate(
            product_id=product_id,
            quantity=quantity,
        )
    )


def create_test_cart(db, merchant_id, customer_id=None):
    repository = CartRepository(db)

    if customer_id is None:
        customer_id = uuid4()

    return repository.create(
        CartCreate(
            merchant_id=merchant_id,
            customer_id=customer_id,
        )
    )


# ============================================================
# Cart creation / retrieval
# ============================================================


def test_create_cart(db):
    merchant = create_test_merchant(db)
    service = CartService(db)

    customer_id = uuid4()

    cart = service.create_cart(
        CartCreate(
            merchant_id=merchant.id,
            customer_id=customer_id,
        )
    )

    assert cart.id is not None
    assert cart.merchant_id == merchant.id
    assert cart.customer_id == customer_id
    assert cart.status == CartStatus.ACTIVE


def test_create_cart_requires_existing_merchant(db):
    service = CartService(db)

    with pytest.raises(ValueError, match="does not exist"):
        service.create_cart(
            CartCreate(
                merchant_id=uuid4(),
                customer_id=uuid4(),
            )
        )


def test_get_cart(db):
    merchant = create_test_merchant(db)
    cart = create_test_cart(db, merchant.id)

    service = CartService(db)

    result = service.get_cart(cart.id)

    assert result is not None
    assert result.id == cart.id


def test_get_missing_cart(db):
    service = CartService(db)

    with pytest.raises(ValueError, match="does not exist"):
        service.list_items(uuid4())


def test_get_or_create_cart_returns_existing_cart(db):
    merchant = create_test_merchant(db)
    customer_id = uuid4()

    cart = create_test_cart(
        db,
        merchant.id,
        customer_id,
    )

    service = CartService(db)

    result = service.get_or_create_cart(
        merchant.id,
        customer_id,
    )

    assert result.id == cart.id


def test_get_or_create_cart_creates_new_cart(db):
    merchant = create_test_merchant(db)
    customer_id = uuid4()

    service = CartService(db)

    cart = service.get_or_create_cart(
        merchant.id,
        customer_id,
    )

    assert cart.id is not None
    assert cart.merchant_id == merchant.id
    assert cart.customer_id == customer_id
    assert cart.status == CartStatus.ACTIVE


# ============================================================
# Add item
# ============================================================


def test_add_item(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    item = service.add_item(
        cart.id,
        product.id,
        2,
    )

    assert item.cart_id == cart.id
    assert item.product_id == product.id
    assert item.quantity == 2
    assert item.unit_price == Decimal("999.99")


def test_add_item_does_not_decrement_inventory(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    inventory = create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    service.add_item(
        cart.id,
        product.id,
        3,
    )

    db.refresh(inventory)

    assert inventory.quantity == 10


def test_add_item_updates_existing_product_quantity(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    first = service.add_item(
        cart.id,
        product.id,
        2,
    )

    second = service.add_item(
        cart.id,
        product.id,
        3,
    )

    assert second.id == first.id
    assert second.quantity == 5


def test_add_item_rejects_insufficient_inventory(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=2,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="Insufficient inventory",
    ):
        service.add_item(
            cart.id,
            product.id,
            3,
        )


def test_add_item_rejects_missing_inventory(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="Inventory",
    ):
        service.add_item(
            cart.id,
            product.id,
            1,
        )


def test_add_item_rejects_missing_product(db):
    merchant = create_test_merchant(db)
    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        service.add_item(
            cart.id,
            uuid4(),
            1,
        )


def test_add_item_rejects_wrong_merchant_product(db):
    merchant_a = create_test_merchant(db)
    merchant_b = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant_b.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant_a.id,
    )

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="does not belong",
    ):
        service.add_item(
            cart.id,
            product.id,
            1,
        )


def test_add_item_rejects_zero_quantity(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        service.add_item(
            cart.id,
            product.id,
            0,
        )


# ============================================================
# Update item
# ============================================================


def test_update_item(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    service.add_item(
        cart.id,
        product.id,
        2,
    )

    updated = service.update_item(
        cart.id,
        product.id,
        5,
    )

    assert updated.quantity == 5


def test_update_item_rejects_insufficient_inventory(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=5,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    service.add_item(
        cart.id,
        product.id,
        2,
    )

    with pytest.raises(
        ValueError,
        match="Insufficient inventory",
    ):
        service.update_item(
            cart.id,
            product.id,
            6,
        )


def test_update_missing_item_fails(db):
    merchant = create_test_merchant(db)
    cart = create_test_cart(db, merchant.id)

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="not present",
    ):
        service.update_item(
            cart.id,
            uuid4(),
            2,
        )


# ============================================================
# Remove item
# ============================================================


def test_remove_item(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    service.add_item(
        cart.id,
        product.id,
        2,
    )

    service.remove_item(
        cart.id,
        product.id,
    )

    items = service.list_items(cart.id)

    assert items == []


def test_remove_missing_item_fails(db):
    merchant = create_test_merchant(db)
    cart = create_test_cart(db, merchant.id)

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="not present",
    ):
        service.remove_item(
            cart.id,
            uuid4(),
        )


# ============================================================
# Subtotal
# ============================================================


def test_calculate_subtotal(db):
    merchant = create_test_merchant(db)

    product_a = create_test_product(
        db,
        merchant.id,
        price="100.00",
    )

    product_b = create_test_product(
        db,
        merchant.id,
        price="250.50",
    )

    create_test_inventory(
        db,
        product_a.id,
        quantity=10,
    )

    create_test_inventory(
        db,
        product_b.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    service = CartService(db)

    service.add_item(
        cart.id,
        product_a.id,
        2,
    )

    service.add_item(
        cart.id,
        product_b.id,
        3,
    )

    subtotal = service.calculate_subtotal(
        cart.id
    )

    assert subtotal == Decimal("951.50")


def test_empty_cart_subtotal_is_zero(db):
    merchant = create_test_merchant(db)
    cart = create_test_cart(db, merchant.id)

    service = CartService(db)

    assert service.calculate_subtotal(
        cart.id
    ) == Decimal("0.00")


# ============================================================
# Cart state
# ============================================================


def test_cannot_add_item_to_checked_out_cart(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    cart_repository = CartRepository(db)

    cart_repository.update(
        cart,
        
        CartUpdate(
            status=CartStatus.CHECKED_OUT
        ),
    )
    

    service = CartService(db)

    with pytest.raises(
        ValueError,
        match="not active",
    ):
        service.add_item(
            cart.id,
            product.id,
            1,
        )