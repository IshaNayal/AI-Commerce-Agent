from decimal import Decimal
from uuid import uuid4

from backend.app.models.merchant import Merchant
from backend.app.repositories.product import ProductRepository
from backend.app.schemas.product import ProductCreate, ProductUpdate


def create_test_merchant(db) -> Merchant:
    merchant = Merchant(
        name="Test Merchant",
        slug=f"test-merchant-{uuid4()}",
        email="merchant@example.com",
    )

    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    return merchant


def create_test_product(
    db,
    merchant_id,
    sku: str="TEST-001",
):
    repository = ProductRepository(db)

    data = ProductCreate(
        merchant_id=merchant_id,
        name="Test Product",
        description="A test product",
        sku=sku,
        price=Decimal("999.99"),
        currency="INR",
    )

    return repository.create(
        merchant_id=merchant_id,
        data=data,
    )


def test_create_product(db):
    merchant = create_test_merchant(db)
    repository = ProductRepository(db)

    data = ProductCreate(
        merchant_id=merchant.id,
        name="Laptop",
        description="Test laptop",
        sku="LAPTOP-001",
        price=Decimal("50000.00"),
        currency="INR",
    )

    product = repository.create(
        merchant_id=merchant.id,
        data=data,
    )

    assert product.id is not None
    assert product.merchant_id == merchant.id
    assert product.name == "Laptop"
    assert product.description == "Test laptop"
    assert product.sku == "LAPTOP-001"
    assert product.price == Decimal("50000.00")
    assert product.currency == "INR"
    assert product.is_active is True


def test_get_by_id(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
    )

    repository = ProductRepository(db)

    result = repository.get_by_id(product.id)

    assert result is not None
    assert result.id == product.id
    assert result.name == "Test Product"


def test_get_by_id_returns_none_for_missing_product(db):
    repository = ProductRepository(db)

    result = repository.get_by_id(uuid4())

    assert result is None


def test_get_by_sku(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
        sku="PHONE-001",
    )

    repository = ProductRepository(db)

    result = repository.get_by_sku(
        merchant.id,
        "PHONE-001",
    )

    assert result is not None
    assert result.id == product.id
    assert result.sku == "PHONE-001"


def test_get_by_sku_is_scoped_to_merchant(db):
    merchant_a = create_test_merchant(db)
    merchant_b = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant_a.id,
        sku="SKU-001",
    )

    repository = ProductRepository(db)

    result_for_a = repository.get_by_sku(
        merchant_a.id,
        "SKU-001",
    )

    result_for_b = repository.get_by_sku(
        merchant_b.id,
        "SKU-001",
    )

    assert result_for_a is not None
    assert result_for_a.id == product.id

    assert result_for_b is None


def test_list_by_merchant(db):
    merchant_a = create_test_merchant(db)
    merchant_b = create_test_merchant(db)

    create_test_product(
        db,
        merchant_a.id,
        sku="A-001",
    )

    create_test_product(
        db,
        merchant_a.id,
        sku="A-002",
    )

    create_test_product(
        db,
        merchant_b.id,
        sku="B-001",
    )

    repository = ProductRepository(db)

    products = repository.list_by_merchant(
        merchant_a.id
    )

    assert len(products) == 2

    assert all(
        product.merchant_id == merchant_a.id
        for product in products
    )

    assert {
        product.sku
        for product in products
    } == {
        "A-001",
        "A-002",
    }


def test_list_by_merchant_pagination(db):
    merchant = create_test_merchant(db)

    create_test_product(
        db,
        merchant.id,
        sku="PAGE-001",
    )

    create_test_product(
        db,
        merchant.id,
        sku="PAGE-002",
    )

    create_test_product(
        db,
        merchant.id,
        sku="PAGE-003",
    )

    repository = ProductRepository(db)

    products = repository.list_by_merchant(
        merchant.id,
        skip=0,
        limit=2,
    )

    assert len(products) == 2


def test_update_product(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
        sku="UPDATE-001",
    )

    repository = ProductRepository(db)

    update_data = ProductUpdate(
        name="Updated Product",
        price=Decimal("1499.99"),
    )

    updated_product = repository.update(
        product,
        update_data,
    )

    assert updated_product.name == "Updated Product"
    assert updated_product.price == Decimal("1499.99")

    # Fields not included in the update should remain unchanged.
    assert updated_product.sku == "UPDATE-001"
    assert updated_product.description == "A test product"
    assert updated_product.currency == "INR"


def test_delete_product(db):
    merchant = create_test_merchant(db)

    product = create_test_product(
        db,
        merchant.id,
        sku="DELETE-001",
    )

    repository = ProductRepository(db)

    product_id = product.id

    repository.delete(product)

    result = repository.get_by_id(product_id)

    assert result is None
