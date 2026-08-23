from uuid import UUID

from sqlalchemy.orm import Session

from ..repositories.merchant import MerchantRepository
from ..models.merchant import Merchant
from ..schemas.merchant import MerchantCreate, MerchantUpdate


class MerchantService:
    """
    Business logic for merchant operations.

    The service layer sits between the API and repository.
    """

    def __init__(self, db: Session):
        self.repository = MerchantRepository(db)

    def create_merchant(self, data: MerchantCreate) -> Merchant:
        """
        Create a merchant after applying business rules.
        """

        # Prevent duplicate merchant slugs.
        existing = self.repository.get_by_slug(data.slug)

        if existing:
            raise ValueError(
                f"Merchant with slug '{data.slug}' already exists."
            )

        return self.repository.create(data)

    def create(self, data: MerchantCreate) -> Merchant:
        return self.create_merchant(data)

    def get_merchant(self, merchant_id: UUID) -> Merchant | None:
        """
        Retrieve a merchant by ID.
        """

        return self.repository.get_by_id(merchant_id)

    def get_by_id(self, merchant_id: UUID) -> Merchant | None:
        return self.get_merchant(merchant_id)

    def list_merchants(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Merchant]:
        """
        Return merchants with pagination.
        """

        return self.repository.list(
            skip=skip,
            limit=limit,
        )

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Merchant]:
        return self.list_merchants(skip=skip, limit=limit)

    def update_merchant(
        self,
        merchant_id: UUID,
        data: MerchantUpdate,
    ) -> Merchant | None:
        """
        Update an existing merchant.
        """

        merchant = self.repository.get_by_id(merchant_id)

        if merchant is None:
            return None

        # If slug is being changed, make sure the new slug
        # doesn't belong to another merchant.
        if data.slug is not None:
            existing = self.repository.get_by_slug(data.slug)

            if existing and existing.id != merchant.id:
                raise ValueError(
                    f"Merchant with slug '{data.slug}' already exists."
                )

        return self.repository.update(
            merchant,
            data,
        )

    def update(
        self,
        merchant: Merchant,
        data: MerchantUpdate,
    ) -> Merchant | None:
        return self.update_merchant(merchant.id, data)

    def delete_merchant(
        self,
        merchant_id: UUID,
    ) -> bool:
        """
        Delete a merchant.

        Returns:
            True  -> merchant deleted
            False -> merchant not found
        """

        merchant = self.repository.get_by_id(merchant_id)

        if merchant is None:
            return False

        self.repository.delete(merchant)

        return True

    def get_by_slug(self, slug: str) -> Merchant | None:
        return self.repository.get_by_slug(slug)

    def delete(self, merchant: Merchant) -> None:
        self.repository.delete(merchant)