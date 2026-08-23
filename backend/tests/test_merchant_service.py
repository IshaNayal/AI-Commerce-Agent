from uuid import uuid4

import pytest

from backend.app.schemas.merchant import MerchantCreate, MerchantUpdate
from backend.app.services.merchant_service import MerchantService


def merchant_data(
    slug: str = "test-merchant",
) -> MerchantCreate:
    return MerchantCreate(
        name="Test Merchant",
        slug=slug,
        email="merchant@example.com",
    )


def test_create_merchant(db):
    service = MerchantService(db)

    merchant = service.create_merchant(
        merchant_data()
    )

    assert merchant.id is not None
    assert merchant.name == "Test Merchant"
    assert merchant.slug == "test-merchant"
    assert merchant.email == "merchant@example.com"
    assert merchant.is_active is True


def test_create_duplicate_slug_fails(db):
    service = MerchantService(db)

    service.create_merchant(
        merchant_data("duplicate")
    )

    with pytest.raises(ValueError):
        service.create_merchant(
            merchant_data("duplicate")
        )


def test_get_merchant(db):
    service = MerchantService(db)

    created = service.create_merchant(
        merchant_data()
    )

    result = service.get_merchant(created.id)

    assert result is not None
    assert result.id == created.id


def test_get_missing_merchant(db):
    service = MerchantService(db)

    result = service.get_merchant(uuid4())

    assert result is None


def test_list_merchants(db):
    service = MerchantService(db)

    service.create_merchant(
        merchant_data("merchant-a")
    )

    service.create_merchant(
        merchant_data("merchant-b")
    )

    result = service.list_merchants()

    assert len(result) == 2


def test_update_merchant(db):
    service = MerchantService(db)

    merchant = service.create_merchant(
        merchant_data()
    )

    updated = service.update_merchant(
        merchant.id,
        MerchantUpdate(
            name="Updated Merchant"
        ),
    )

    assert updated is not None
    assert updated.name == "Updated Merchant"


def test_update_missing_merchant(db):
    service = MerchantService(db)

    result = service.update_merchant(
        uuid4(),
        MerchantUpdate(
            name="Updated"
        ),
    )

    assert result is None


def test_delete_merchant(db):
    service = MerchantService(db)

    merchant = service.create_merchant(
        merchant_data()
    )

    deleted = service.delete_merchant(
        merchant.id
    )

    assert deleted is True

    assert service.get_merchant(
        merchant.id
    ) is None


def test_delete_missing_merchant(db):
    service = MerchantService(db)

    deleted = service.delete_merchant(uuid4())

    assert deleted is False