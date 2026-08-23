from uuid import uuid4

from backend.app.models.cart import CartStatus
from backend.app.repositories.cart import CartRepository
from backend.app.schemas.cart import CartCreate, CartUpdate
from backend.app.schemas.merchant import MerchantCreate
from backend.app.repositories.merchant import MerchantRepository


def create_test_merchant(db):
    repository = MerchantRepository(db)

    data = MerchantCreate(
        name="Test Merchant",
        slug=f"test-merchant-{uuid4().hex[:8]}",
        email="merchant@example.com",
    )

    return repository.create(data)


def create_test_cart(db, merchant_id, customer_id=None):
    repository = CartRepository(db)

    if customer_id is None:
        customer_id = uuid4()

    data = CartCreate(
        merchant_id=merchant_id,
        customer_id=customer_id,
    )

    return repository.create(data)


def test_create_cart(db):
    merchant = create_test_merchant(db)

    repository = CartRepository(db)

    customer_id = uuid4()

    data = CartCreate(
        merchant_id=merchant.id,
        customer_id=customer_id,
    )

    cart = repository.create(data)

    assert cart.id is not None
    assert cart.merchant_id == merchant.id
    assert cart.customer_id == customer_id
    assert cart.status == CartStatus.ACTIVE


def test_get_by_id(db):
    merchant = create_test_merchant(db)

    cart = create_test_cart(
        db,
        merchant.id,
    )

    repository = CartRepository(db)

    result = repository.get_by_id(cart.id)

    assert result is not None
    assert result.id == cart.id


def test_get_by_id_returns_none(db):
    repository = CartRepository(db)

    result = repository.get_by_id(uuid4())

    assert result is None


def test_get_by_customer(db):
    merchant = create_test_merchant(db)

    customer_id = uuid4()

    cart = create_test_cart(
        db,
        merchant.id,
        customer_id,
    )

    repository = CartRepository(db)

    result = repository.get_by_customer(
        merchant.id,
        customer_id,
    )

    assert result is not None
    assert result.id == cart.id


def test_get_by_customer_is_scoped_to_merchant(db):
    merchant_a = create_test_merchant(db)
    merchant_b = create_test_merchant(db)

    customer_id = uuid4()

    create_test_cart(
        db,
        merchant_a.id,
        customer_id,
    )

    repository = CartRepository(db)

    result = repository.get_by_customer(
        merchant_b.id,
        customer_id,
    )

    assert result is None


def test_list_by_merchant(db):
    merchant_a = create_test_merchant(db)
    merchant_b = create_test_merchant(db)

    create_test_cart(db, merchant_a.id)
    create_test_cart(db, merchant_a.id)
    create_test_cart(db, merchant_b.id)

    repository = CartRepository(db)

    carts = repository.list_by_merchant(
        merchant_a.id
    )

    assert len(carts) == 2

    for cart in carts:
        assert cart.merchant_id == merchant_a.id


def test_list_by_merchant_pagination(db):
    merchant = create_test_merchant(db)

    create_test_cart(db, merchant.id)
    create_test_cart(db, merchant.id)
    create_test_cart(db, merchant.id)

    repository = CartRepository(db)

    carts = repository.list_by_merchant(
        merchant.id,
        skip=1,
        limit=1,
    )

    assert len(carts) == 1


def test_update_cart(db):
    merchant = create_test_merchant(db)

    cart = create_test_cart(
        db,
        merchant.id,
    )

    repository = CartRepository(db)

    updated = repository.update(
        cart,
        CartUpdate(
            status=CartStatus.CHECKED_OUT
        ),
    )

    assert updated.status == CartStatus.CHECKED_OUT


def test_delete_cart(db):
    merchant = create_test_merchant(db)

    cart = create_test_cart(
        db,
        merchant.id,
    )

    repository = CartRepository(db)

    cart_id = cart.id

    repository.delete(cart)

    result = repository.get_by_id(cart_id)

    assert result is None