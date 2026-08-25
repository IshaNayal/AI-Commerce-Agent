from decimal import Decimal
import pytest
from uuid import uuid4

from backend.app.schemas.merchant import MerchantCreate
from backend.app.schemas.product import ProductCreate
from backend.app.services.merchant_services import MerchantService
from backend.app.services.product_service import ProductService
from backend.app.services.vector_service import VectorService


# Mock the embedding to return deterministic vectors based on text
def mock_get_embedding(self, text: str) -> list[float]:
    # Very naive mock: just some fake numbers
    if "shoes" in text.lower():
        return [0.9] * 1536
    elif "socks" in text.lower():
        return [0.8] * 1536
    return [0.1] * 1536


@pytest.fixture
def patch_embeddings(monkeypatch):
    monkeypatch.setattr(VectorService, "_get_embedding", mock_get_embedding)


def test_semantic_search(db, patch_embeddings):
    merchant = MerchantService(db).create(
        MerchantCreate(name="Shoe Store", slug="shoe-store-search", email="shoe@store.com")
    )
    
    product_service = ProductService(db)
    
    # Create products (this will automatically index them due to our mocked vector_service)
    p1 = product_service.create(ProductCreate(
        merchant_id=merchant.id,
        name="AeroRun Running Shoes",
        description="Lightweight breathable running shoes.",
        sku="RUN1",
        price=Decimal("49.99"),
        currency="USD"
    ))
    
    p2 = product_service.create(ProductCreate(
        merchant_id=merchant.id,
        name="Cotton Socks",
        description="Comfortable sports socks.",
        sku="SOCK1",
        price=Decimal("9.99"),
        currency="USD"
    ))
    
    # Test search
    results = product_service.search_products(query="running shoes", merchant_id=merchant.id, top_k=2)
    
    assert len(results) >= 1
    # Check if p1 or p2 came back
    ids = [r.id for r in results]
    assert p1.id in ids
