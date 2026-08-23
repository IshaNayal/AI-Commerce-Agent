from decimal import Decimal
from uuid import uuid4

from backend.app.models.cart_item import CartItem
from backend.app.repositories.cart_item import CartItemRepository
from backend.app.repositories.cart import CartRepository
from backend.app.repositories.merchant import MerchantRepository
from backend.app.repositories.product import ProductRepository
from backend.app.schemas.cart import CartCreate
from backend.app.schemas.cart_item import (
    CartItemCreate,
    CartItemUpdate,
)
from backend.app.schemas.merchant import MerchantCreate
from backend.app.schemas.product import ProductCreate


def create_test_merchant(db):
    repository = MerchantRepository(db)

    data = MerchantCreate(
        name="Test Merchant",
        slug=f"merchant-{uuid4().hex[:8]}",
        email="merchant@example.com",
    )

    return repository.create(data)


def create_test_product(db, merchant_id):
    repository = ProductRepository(db)

    data = ProductCreate(
        merchant_id=merchant_id,
        name="Test Product",
        description="Test product",
        sku=f"SKU-{uuid4().hex[:8]}",
        price=Decimal("999.99"),
        currency="INR",
    )

    return repository.create(data)


def create_test_cart(db, merchant_id):
    repository = CartRepository(db)

    data = CartCreate(
        merchant_id=merchant_id,
        customer_id=uuid4(),
    )

    return repository.create(data)


def create_test_cart_item(
    db,
    cart_id,
    product_id,
    quantity=2,
):
    repository = CartItemRepository(db)

    data = CartItemCreate(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity,
    )

    return repository.create(data)


def test_create_cart_item(db):
    merchant = create_test_merchant(db)
    product = create_test_product(
        db,
        merchant.id,
    )
    cart = create_test_cart(
        db,
        merchant.id,
    )

    repository = CartItemRepository(db)

    data = CartItemCreate(
        cart_id=cart.id,
        product_id=product.id,
        quantity=2,
    )

    cart_item = repository.create(data)

    assert cart_item.id is not None
    assert cart_item.cart_id == cart.id
    assert cart_item.product_id == product.id
    assert cart_item.quantity == 2
    assert cart_item.unit_price == Decimal("999.99")


def test_create_cart_item_uses_product_price(db):
    merchant = create_test_merchant(db)
    product = create_test_product(
        db,
        merchant.id,
    )
    cart = create_test_cart(
        db,
        merchant.id,
    )

    repository = CartItemRepository(db)

    item = repository.create(
        CartItemCreate(
            cart_id=cart.id,
            product_id=product.id,
            quantity=3,
        )
    )

    assert item.unit_price == product.price


def test_get_by_id(db):
    merchant = create_test_merchant(db)
    product = create_test_product(
        db,
        merchant.id,
    )
    cart = create_test_cart(
        db,
        merchant.id,
    )

    item = create_test_cart_item(
        db,
        cart.id,
        product.id,
    )

    repository = CartItemRepository(db)

    result = repository.get_by_id(item.id)

    assert result is not None
    assert result.id == item.id


def test_get_by_id_returns_none(db):
    repository = CartItemRepository(db)

    result = repository.get_by_id(uuid4())

    assert result is None


def test_get_by_cart_and_product(db):
    merchant = create_test_merchant(db)
    product = create_test_product(
        db,
        merchant.id,
    )
    cart = create_test_cart(
        db,
        merchant.id,
    )

    item = create_test_cart_item(
        db,
        cart.id,
        product.id,
    )

    repository = CartItemRepository(db)

    result = repository.get_by_cart_and_product(
        cart.id,
        product.id,
    )

    assert result is not None
    assert result.id == item.id


def test_list_by_cart(db):
    merchant = create_test_merchant(db)

    product_a = create_test_product(
        db,
        merchant.id,
    )

    product_b = create_test_product(
        db,
        merchant.id,
    )

    cart = create_test_cart(
        db,
        merchant.id,
    )

    create_test_cart_item(
        db,
        cart.id,
        product_a.id,
        quantity=1,
    )

    create_test_cart_item(
        db,
        cart.id,
        product_b.id,
        quantity=2,
    )

    repository = CartItemRepository(db)

    items = repository.list_by_cart(
        cart.id
    )

    assert len(items) == 2

    assert all(
        item.cart_id == cart.id
        for item in items
    )


def test_update_cart_item_quantity(db):
    merchant = create_test_merchant(db)
    product = create_test_product(
        db,
        merchant.id,
    )
    cart = create_test_cart(
        db,
        merchant.id,
    )

    item = create_test_cart_item(
        db,
        cart.id,
        product.id,
        quantity=2,
    )

    repository = CartItemRepository(db)

    updated = repository.update(
        item,
        CartItemUpdate(
            quantity=5
        ),
    )

    assert updated.quantity == 5


def test_delete_cart_item(db):
    merchant = create_test_merchant(db)
    product = create_test_product(
        db,
        merchant.id,
    )
    cart = create_test_cart(
        db,
        merchant.id,
    )

    item = create_test_cart_item(
        db,
        cart.id,
        product.id,
    )

    repository = CartItemRepository(db)

    item_id = item.id

    repository.delete(item)

    result = repository.get_by_id(item_id)

    assert result is None


def test_cart_item_quantity_must_be_positive():
    from pydantic import ValidationError

    try:
        CartItemCreate(
            cart_id=uuid4(),
            product_id=uuid4(),
            quantity=0,
        )
        assert False
    except ValidationError:
        assert True