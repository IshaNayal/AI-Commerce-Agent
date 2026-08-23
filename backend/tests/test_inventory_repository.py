from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from backend.app.models.inventory import Inventory
from backend.app.models.product import Product
from backend.app.repositories.inventory import InventoryRepository
from backend.app.repositories.merchant import MerchantRepository
from backend.app.repositories.product import ProductRepository
from backend.app.schemas.inventory import InventoryCreate, InventoryUpdate
from backend.app.schemas.merchant import MerchantCreate
from backend.app.schemas.product import ProductCreate


def create_test_merchant(db):
    repository = MerchantRepository(db)

    data = MerchantCreate(
        name="Test Merchant",
        slug=f"test-merchant-{uuid4().hex[:8]}",
        email=f"test-{uuid4().hex[:8]}@example.com",
    )

    return repository.create(data)


def create_test_product(db, merchant_id):
    repository = ProductRepository(db)

    data = ProductCreate(
        merchant_id=merchant_id,
        name="Test Product",
        description="Product for inventory tests",
        sku=f"TEST-{uuid4().hex[:8]}",
        price=Decimal("999.99"),
        currency="INR",
    )

    return repository.create(data)


def create_test_inventory(db, product_id, quantity=10):
    repository = InventoryRepository(db)

    data = InventoryCreate(
        product_id=product_id,
        quantity=quantity,
    )

    return repository.create(data)


def test_create_inventory(db):
    merchant = create_test_merchant(db)
    product = create_test_product(db, merchant.id)

    repository = InventoryRepository(db)

    data = InventoryCreate(
        product_id=product.id,
        quantity=25,
    )

    inventory = repository.create(data)

    assert inventory.id is not None
    assert isinstance(inventory.id, UUID)
    assert inventory.product_id == product.id
    assert inventory.quantity == 25


def test_get_by_id(db):
    merchant = create_test_merchant(db)
    product = create_test_product(db, merchant.id)

    inventory = create_test_inventory(
        db,
        product.id,
        quantity=15,
    )

    repository = InventoryRepository(db)

    result = repository.get_by_id(inventory.id)

    assert result is not None
    assert result.id == inventory.id
    assert result.product_id == product.id
    assert result.quantity == 15


def test_get_by_id_returns_none_for_unknown_id(db):
    repository = InventoryRepository(db)

    result = repository.get_by_id(uuid4())

    assert result is None


def test_get_by_product_id(db):
    merchant = create_test_merchant(db)
    product = create_test_product(db, merchant.id)

    inventory = create_test_inventory(
        db,
        product.id,
        quantity=20,
    )

    repository = InventoryRepository(db)

    result = repository.get_by_product_id(product.id)

    assert result is not None
    assert result.id == inventory.id
    assert result.product_id == product.id
    assert result.quantity == 20


def test_get_by_product_id_returns_none_for_unknown_product(db):
    repository = InventoryRepository(db)

    result = repository.get_by_product_id(uuid4())

    assert result is None


def test_update_inventory(db):
    merchant = create_test_merchant(db)
    product = create_test_product(db, merchant.id)

    inventory = create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    repository = InventoryRepository(db)

    data = InventoryUpdate(
        quantity=50,
    )

    updated_inventory = repository.update(
        inventory,
        data,
    )

    assert updated_inventory.id == inventory.id
    assert updated_inventory.product_id == product.id
    assert updated_inventory.quantity == 50


def test_update_inventory_with_unset_fields(db):
    merchant = create_test_merchant(db)
    product = create_test_product(db, merchant.id)

    inventory = create_test_inventory(
        db,
        product.id,
        quantity=30,
    )

    repository = InventoryRepository(db)

    data = InventoryUpdate()

    updated_inventory = repository.update(
        inventory,
        data,
    )

    assert updated_inventory.quantity == 30


def test_create_inventory_rejects_negative_quantity():
    with pytest.raises(Exception):
        InventoryCreate(
            product_id=uuid4(),
            quantity=-1,
        )


def test_delete_inventory(db):
    merchant = create_test_merchant(db)
    product = create_test_product(db, merchant.id)

    inventory = create_test_inventory(
        db,
        product.id,
        quantity=10,
    )

    repository = InventoryRepository(db)

    inventory_id = inventory.id

    repository.delete(inventory)

    result = repository.get_by_id(inventory_id)

    assert result is None