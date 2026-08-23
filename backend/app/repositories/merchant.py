from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.merchant import Merchant
from ..schemas.merchant import MerchantCreate, MerchantUpdate


class MerchantRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: MerchantCreate) -> Merchant:
        merchant = Merchant(
            name=data.name,
            slug=data.slug,
            email=data.email,
        )

        self.db.add(merchant)
        self.db.commit()
        self.db.refresh(merchant)

        return merchant

    def get_by_id(self, merchant_id: UUID) -> Merchant | None:
        statement = select(Merchant).where(
            Merchant.id == merchant_id
        )

        return self.db.scalar(statement)

    def get_by_slug(self, slug: str) -> Merchant | None:
        statement = select(Merchant).where(
            Merchant.slug == slug
        )

        return self.db.scalar(statement)

    def list(
        self,
        skip: int=0,
        limit: int=100,
    ) -> list[Merchant]:
        statement = (
            select(Merchant)
            .offset(skip)
            .limit(limit)
            .order_by(Merchant.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        merchant: Merchant,
        data: MerchantUpdate,
    ) -> Merchant:

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(merchant, field, value)

        self.db.commit()
        self.db.refresh(merchant)

        return merchant

    def delete(self, merchant: Merchant) -> None:
        self.db.delete(merchant)
        self.db.commit()
