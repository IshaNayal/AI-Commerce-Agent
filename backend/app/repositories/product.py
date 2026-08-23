from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        data: ProductCreate,
        merchant_id: UUID | None = None,
    ) -> Product:
        if merchant_id is not None and merchant_id != data.merchant_id:
            raise ValueError("merchant_id must match data.merchant_id")

        product = Product(
            merchant_id=data.merchant_id,
            name=data.name,
            description=data.description,
            sku=data.sku,
            price=data.price,
            currency=data.currency,
        )

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        return product

    def get_by_id(
        self,
        product_id: UUID,
    ) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id
        )

        return self.db.scalar(statement)

    def get_by_sku(
        self,
        merchant_id: UUID,
        sku: str,
    ) -> Product | None:
        statement = select(Product).where(
            Product.merchant_id == merchant_id,
            Product.sku == sku,
        )

        return self.db.scalar(statement)

    def list_by_merchant(
        self,
        merchant_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.merchant_id == merchant_id)
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        product: Product,
        data: ProductUpdate,
    ) -> Product:
        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)

        return product

    def delete(
        self,
        product: Product,
    ) -> None:
        self.db.delete(product)
        self.db.commit()