from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.app.schemas.product import ProductCreate


def test_product_create_valid():
    product = ProductCreate(
        merchant_id=uuid4(),
        name="Laptop",
        sku="LAP-001",
        price=Decimal("49999.99"),
    )

    assert product.name == "Laptop"
    assert product.price == Decimal("49999.99")


def test_product_rejects_negative_price():
    with pytest.raises(ValidationError):
        ProductCreate(
            merchant_id=uuid4(),
            name="Laptop",
            sku="LAP-001",
            price=Decimal("-100"),
        )