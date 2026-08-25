from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.product import Product
from ..repositories.product import ProductRepository
from ..repositories.merchant import MerchantRepository
from ..schemas.product import ProductCreate, ProductUpdate
from .vector_service import VectorService


class ProductService:
    """
    Business logic for products.

    The service layer coordinates:
        ProductRepository
        MerchantRepository

    It is responsible for business rules, while repositories
    are responsible for database access.
    """

    def __init__(self, db: Session):
        self.product_repository = ProductRepository(db)
        self.merchant_repository = MerchantRepository(db)
        self.vector_service = VectorService()

    def create(self, data: ProductCreate) -> Product:
        """
        Create a new product.

        Business rules:
        1. Merchant must exist.
        2. Merchant must be active.
        3. SKU must be unique for that merchant.
        4. Price must not be negative.
        """

        # ---------------------------------------------------------
        # 1. Check merchant exists
        # ---------------------------------------------------------

        merchant = self.merchant_repository.get_by_id(
            data.merchant_id
        )

        if merchant is None:
            raise ValueError(
                f"Merchant '{data.merchant_id}' does not exist"
            )

        # ---------------------------------------------------------
        # 2. Check merchant is active
        # ---------------------------------------------------------

        if not merchant.is_active:
            raise ValueError(
                "Cannot create a product for an inactive merchant"
            )

        # ---------------------------------------------------------
        # 3. Validate price
        # ---------------------------------------------------------

        if data.price < Decimal("0"):
            raise ValueError(
                "Product price cannot be negative"
            )

        # ---------------------------------------------------------
        # 4. Check SKU uniqueness within merchant
        # ---------------------------------------------------------

        existing_product = self.product_repository.get_by_sku(
            merchant_id=data.merchant_id,
            sku=data.sku,
        )

        if existing_product is not None:
            raise ValueError(
                f"Product with SKU '{data.sku}' "
                f"already exists for this merchant"
            )

        # ---------------------------------------------------------
        # 5. Create product
        # ---------------------------------------------------------

        product = self.product_repository.create(data)
        try:
            self.vector_service.index_product(product)
        except Exception:
            pass # Fails gracefully if Chroma is not ready
        return product

    def get_by_id(
        self,
        product_id: UUID,
    ) -> Product | None:
        """
        Get a product by ID.
        """

        return self.product_repository.get_by_id(
            product_id
        )

    def get_by_sku(
        self,
        merchant_id: UUID,
        sku: str,
    ) -> Product | None:
        """
        Get a product by SKU within a specific merchant.

        SKU uniqueness is scoped to a merchant.
        """

        return self.product_repository.get_by_sku(
            merchant_id=merchant_id,
            sku=sku,
        )

    def list_by_merchant(
        self,
        merchant_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        """
        Return products belonging to a merchant.
        """

        # ---------------------------------------------------------
        # Validate pagination
        # ---------------------------------------------------------

        if skip < 0:
            raise ValueError(
                "skip cannot be negative"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        if limit > 100:
            raise ValueError(
                "limit cannot exceed 100"
            )

        # ---------------------------------------------------------
        # Check merchant exists
        # ---------------------------------------------------------

        merchant = self.merchant_repository.get_by_id(
            merchant_id
        )

        if merchant is None:
            raise ValueError(
                f"Merchant '{merchant_id}' does not exist"
            )

        return self.product_repository.list_by_merchant(
            merchant_id=merchant_id,
            skip=skip,
            limit=limit,
        )

    def update(
        self,
        product: Product,
        data: ProductUpdate,
    ) -> Product:
        """
        Update a product.

        Business rules:
        - New SKU must remain unique for this merchant.
        - Price cannot be negative.
        """

        # ---------------------------------------------------------
        # Validate price if it is being changed
        # ---------------------------------------------------------

        if (
            data.price is not None
            and data.price < Decimal("0")
        ):
            raise ValueError(
                "Product price cannot be negative"
            )

        # ---------------------------------------------------------
        # Validate SKU if it is being changed
        # ---------------------------------------------------------

        if data.sku is not None:

            existing_product = (
                self.product_repository.get_by_sku(
                    merchant_id=product.merchant_id,
                    sku=data.sku,
                )
            )

            if (
                existing_product is not None
                and existing_product.id != product.id
            ):
                raise ValueError(
                    f"Product with SKU '{data.sku}' "
                    f"already exists for this merchant"
                )

        updated_product = self.product_repository.update(product, data)
        try:
            self.vector_service.index_product(updated_product)
        except Exception:
            pass # Fails gracefully
        return updated_product

    def delete(
        self,
        product: Product,
    ) -> None:
        """
        Delete a product.
        """

        self.product_repository.delete(product)

    def search_products(self, query: str, merchant_id: UUID, top_k: int = 5) -> list[Product]:
        """
        Perform semantic search for products.
        """
        try:
            product_ids = self.vector_service.semantic_search(query, merchant_id, top_k)
        except Exception:
            return []
            
        if not product_ids:
            return []
            
        # Fetch products from DB
        products = []
        for pid in product_ids:
            p = self.get_by_id(pid)
            if p:
                products.append(p)
        return products