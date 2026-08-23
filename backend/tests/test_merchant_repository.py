from uuid import uuid4

from backend.app.repositories.merchant import MerchantRepository
from backend.app.schemas.merchant import MerchantCreate, MerchantUpdate


def test_create_merchant(db):
    repository = MerchantRepository(db)

    data = MerchantCreate(
        name="Test Merchant",
        slug=f"test-{uuid4()}",
        email="test@example.com",
    )

    merchant = repository.create(data)

    assert merchant.id is not None
    assert merchant.name == "Test Merchant"
    assert merchant.email == "test@example.com"


def test_get_merchant_by_id(db):
    repository = MerchantRepository(db)

    data = MerchantCreate(
        name="Test Merchant",
        slug=f"test-{uuid4()}",
        email="test@example.com",
    )

    created = repository.create(data)

    merchant = repository.get_by_id(created.id)

    assert merchant is not None
    assert merchant.id == created.id


def test_get_merchant_by_slug(db):
    repository = MerchantRepository(db)

    slug = f"test-{uuid4()}"

    data = MerchantCreate(
        name="Test Merchant",
        slug=slug,
        email="test@example.com",
    )

    repository.create(data)

    merchant = repository.get_by_slug(slug)

    assert merchant is not None
    assert merchant.slug == slug


def test_update_merchant(db):
    repository = MerchantRepository(db)

    data = MerchantCreate(
        name="Old Name",
        slug=f"test-{uuid4()}",
        email="test@example.com",
    )

    merchant = repository.create(data)

    updated = repository.update(
        merchant,
        MerchantUpdate(name="New Name"),
    )

    assert updated.name == "New Name"


def test_delete_merchant(db):
    repository = MerchantRepository(db)

    data = MerchantCreate(
        name="Test Merchant",
        slug=f"test-{uuid4()}",
        email="test@example.com",
    )

    merchant = repository.create(data)
    merchant_id = merchant.id

    repository.delete(merchant)

    assert repository.get_by_id(merchant_id) is None