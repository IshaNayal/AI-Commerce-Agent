from uuid import uuid4

import pytest

from backend.app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
)
from backend.app.schemas.merchant import MerchantCreate
from backend.app.schemas.product import ProductCreate
from backend.app.services.inventory_service import InventoryService
from backend.app.services.merchant_service import MerchantService
from backend.app.services.product_service import ProductService


def create_merchant(db):
    service = MerchantService(db)

    return service.create(
        MerchantCreate(
            name="Test Merchant",
            slug=f"merchant-{uuid4().hex[:8]}",
            email=f"{uuid4().hex[:8]}@example.com",
        )
    )


def create_product(db, merchant_id):
    service = ProductService(db)

    return service.create(
        ProductCreate(
            merchant_id=merchant_id,
            name="Test Product",
            description="Test product",
            sku=f"SKU-{uuid4().hex[:8]}",
            price=999,
            currency="INR",
        )
    )


def create_inventory(db, product_id, quantity=10):
    service = InventoryService(db)

    return service.create(
        InventoryCreate(
            product_id=product_id,
            quantity=quantity,
        )
    )


def test_create_inventory(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    service = InventoryService(db)

    inventory = service.create(
        InventoryCreate(
            product_id=product.id,
            quantity=10,
        )
    )

    assert inventory.id is not None
    assert inventory.product_id == product.id
    assert inventory.quantity == 10


def test_create_inventory_requires_existing_product(db):
    service = InventoryService(db)

    with pytest.raises(ValueError):
        service.create(
            InventoryCreate(
                product_id=uuid4(),
                quantity=10,
            )
        )


def test_duplicate_inventory_fails(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    create_inventory(
        db,
        product.id,
        quantity=10,
    )

    service = InventoryService(db)

    with pytest.raises(ValueError):
        service.create(
            InventoryCreate(
                product_id=product.id,
                quantity=20,
            )
        )


def test_get_inventory_by_product(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    inventory = create_inventory(
        db,
        product.id,
        quantity=15,
    )

    service = InventoryService(db)

    result = service.get_by_product_id(
        product.id
    )

    assert result is not None
    assert result.id == inventory.id
    assert result.quantity == 15


def test_check_stock_returns_true_when_available(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    create_inventory(
        db,
        product.id,
        quantity=10,
    )

    service = InventoryService(db)

    assert service.check_stock(
        product.id,
        5,
    ) is True


def test_check_stock_returns_false_when_insufficient(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    create_inventory(
        db,
        product.id,
        quantity=10,
    )

    service = InventoryService(db)

    assert service.check_stock(
        product.id,
        11,
    ) is False


def test_increase_stock(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    create_inventory(
        db,
        product.id,
        quantity=10,
    )

    service = InventoryService(db)

    inventory = service.increase_stock(
        product.id,
        5,
    )

    assert inventory.quantity == 15


def test_decrease_stock(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    create_inventory(
        db,
        product.id,
        quantity=10,
    )

    service = InventoryService(db)

    inventory = service.decrease_stock(
        product.id,
        3,
    )

    assert inventory.quantity == 7


def test_decrease_stock_prevents_overselling(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    create_inventory(
        db,
        product.id,
        quantity=5,
    )

    service = InventoryService(db)

    with pytest.raises(ValueError):
        service.decrease_stock(
            product.id,
            6,
        )


def test_negative_inventory_update_fails(db):
    merchant = create_merchant(db)
    product = create_product(db, merchant.id)

    inventory = create_inventory(
        db,
        product.id,
        quantity=10,
    )

    service = InventoryService(db)

    with pytest.raises(ValueError):
        service.update(
            inventory,
            InventoryUpdate(
                quantity=-1,
            ),
        )