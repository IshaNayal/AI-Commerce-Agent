from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.inventory import Inventory
from ..schemas.inventory import InventoryCreate, InventoryUpdate


class InventoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: InventoryCreate) -> Inventory:
        inventory = Inventory(
            product_id=data.product_id,
            quantity=data.quantity,
        )

        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def get_by_id(
        self,
        inventory_id: UUID,
    ) -> Inventory | None:

        statement = select(Inventory).where(
            Inventory.id == inventory_id
        )

        return self.db.scalar(statement)

    def get_by_product_id(
        self,
        product_id: UUID,
    ) -> Inventory | None:

        statement = select(Inventory).where(
            Inventory.product_id == product_id
        )

        return self.db.scalar(statement)

    def get_by_product_id_for_update(
        self,
        product_id: UUID,
    ) -> Inventory | None:
        """
        Fetch inventory while locking the database row.

        FOR UPDATE prevents another transaction from modifying
        this inventory row until the current transaction completes.

        This is used for atomic stock reservation.
        """

        statement = (
            select(Inventory)
            .where(
                Inventory.product_id == product_id
            )
            .with_for_update()
        )

        return self.db.scalar(statement)

    def update(
        self,
        inventory: Inventory,
        data: InventoryUpdate,
    ) -> Inventory:

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(inventory, field, value)

        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def save(
        self,
        inventory: Inventory,
    ) -> Inventory:

        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def delete(
        self,
        inventory: Inventory,
    ) -> None:

        self.db.delete(inventory)
        self.db.commit()