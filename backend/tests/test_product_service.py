from decimal import Decimal
from uuid import uuid4

import pytest

from backend.app.schemas.merchant import MerchantCreate
from backend.app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)
from backend.app.services.merchant_service import MerchantService
from backend.app.services.product_service import ProductService


def create_test_merchant(db, slug="test-merchant"):
    service = MerchantService(db)

    return service.create(
        MerchantCreate(
            name="Test Merchant",
            slug=slug,
            email=f"{slug}@example.com",
        )
    )


def create_test_product(
    db,
    merchant_id,
    sku="TEST-001",
):
    service = ProductService(db)

    return service.create(
        ProductCreate(
            merchant_id=merchant_id,
            name="Test Product",
            description="A test product",
            sku=sku,
            price=Decimal("999.99"),
            currency="INR",
        )
    )


def test_create_product(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    assert product.id is not None
    assert product.merchant_id == merchant.id
    assert product.name == "Test Product"
    assert product.sku == "TEST-001"
    assert product.price == Decimal("999.99")


def test_create_product_requires_existing_merchant(db):
    service = ProductService(db)

    with pytest.raises(ValueError):
        service.create(
            ProductCreate(
                merchant_id=uuid4(),
                name="Test Product",
                description="Test",
                sku="TEST-001",
                price=Decimal("999.99"),
                currency="INR",
            )
        )


def test_duplicate_sku_fails(db):
    merchant = create_test_merchant(db)

    create_test_product(
        db,
        merchant.id,
        sku="DUPLICATE-001",
    )

    service = ProductService(db)

    with pytest.raises(ValueError):
        service.create(
            ProductCreate(
                merchant_id=merchant.id,
                name="Another Product",
                description="Another product",
                sku="DUPLICATE-001",
                price=Decimal("100.00"),
                currency="INR",
            )
        )


def test_get_by_id(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    service = ProductService(db)

    result = service.get_by_id(product.id)

    assert result is not None
    assert result.id == product.id


def test_get_by_sku(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
        sku="PHONE-001",
    )

    service = ProductService(db)

    result = service.get_by_sku(
        merchant.id,
        "PHONE-001",
    )

    assert result is not None
    assert result.id == product.id


def test_list_by_merchant(db):
    merchant = create_test_merchant(db)

    create_test_product(
        db,
        merchant.id,
        sku="PRODUCT-001",
    )

    create_test_product(
        db,
        merchant.id,
        sku="PRODUCT-002",
    )

    service = ProductService(db)

    products = service.list_by_merchant(
        merchant.id
    )

    assert len(products) == 2


def test_update_product(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    service = ProductService(db)

    updated = service.update(
        product,
        ProductUpdate(
            name="Updated Product",
            price=Decimal("1299.99"),
        ),
    )

    assert updated.name == "Updated Product"
    assert updated.price == Decimal("1299.99")


def test_update_duplicate_sku_fails(db):
    merchant = create_test_merchant(db)

    product_one = create_test_product(
        db,
        merchant.id,
        sku="PRODUCT-001",
    )

    create_test_product(
        db,
        merchant.id,
        sku="PRODUCT-002",
    )

    service = ProductService(db)

    with pytest.raises(ValueError):
        service.update(
            product_one,
            ProductUpdate(
                sku="PRODUCT-002"
            ),
        )


def test_delete_product(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    product_id = product.id

    service = ProductService(db)

    service.delete(product)

    result = service.get_by_id(product_id)

    assert result is None