from uuid import UUID

from sqlalchemy.orm import Session

from ..models.inventory import Inventory
from ..repositories.inventory import InventoryRepository
from ..repositories.product import ProductRepository
from ..schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
)


class InventoryService:
    """
    Business logic for product inventory.

    Responsibilities:
    - Create inventory for a product
    - Retrieve inventory
    - Update inventory
    - Increase stock
    - Decrease stock
    - Check stock availability

    Repositories handle database access.
    This service handles business rules.
    """

    def __init__(self, db: Session):
        self.inventory_repository = InventoryRepository(db)
        self.product_repository = ProductRepository(db)

    # ---------------------------------------------------------
    # Create inventory
    # ---------------------------------------------------------

    def create(
        self,
        data: InventoryCreate,
    ) -> Inventory:
        """
        Create inventory for a product.

        Business rules:
        1. Product must exist.
        2. Product must be active.
        3. Product cannot have multiple inventory records.
        4. Initial quantity cannot be negative.
        """

        # Check product exists
        product = self.product_repository.get_by_id(
            data.product_id
        )

        if product is None:
            raise ValueError(
                f"Product '{data.product_id}' does not exist"
            )

        # Check product is active
        if not product.is_active:
            raise ValueError(
                "Cannot create inventory for an inactive product"
            )

        # Check inventory doesn't already exist
        existing_inventory = (
            self.inventory_repository.get_by_product_id(
                data.product_id
            )
        )

        if existing_inventory is not None:
            raise ValueError(
                "Inventory already exists for this product"
            )

        # Validate quantity
        if data.quantity < 0:
            raise ValueError(
                "Inventory quantity cannot be negative"
            )

        return self.inventory_repository.create(data)

    # ---------------------------------------------------------
    # Get by ID
    # ---------------------------------------------------------

    def get_by_id(
        self,
        inventory_id: UUID,
    ) -> Inventory | None:
        """
        Retrieve inventory by inventory ID.
        """

        return self.inventory_repository.get_by_id(
            inventory_id
        )

    # ---------------------------------------------------------
    # Get by product
    # ---------------------------------------------------------

    def get_by_product_id(
        self,
        product_id: UUID,
    ) -> Inventory | None:
        """
        Retrieve inventory belonging to a product.
        """

        return self.inventory_repository.get_by_product_id(
            product_id
        )

    # ---------------------------------------------------------
    # Update inventory
    # ---------------------------------------------------------

    def update(
        self,
        inventory: Inventory,
        data: InventoryUpdate,
    ) -> Inventory:
        """
        Update inventory.

        Quantity cannot become negative.
        """

        if data.quantity is not None and data.quantity < 0:
            raise ValueError(
                "Inventory quantity cannot be negative"
            )

        return self.inventory_repository.update(
            inventory,
            data,
        )

    # ---------------------------------------------------------
    # Check stock
    # ---------------------------------------------------------

    def check_stock(
        self,
        product_id: UUID,
        quantity: int,
    ) -> bool:
        """
        Check whether enough inventory exists.

        Returns True if sufficient stock exists.
        """

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        inventory = self.inventory_repository.get_by_product_id(
            product_id
        )

        if inventory is None:
            return False

        return inventory.quantity >= quantity

    # ---------------------------------------------------------
    # Increase stock
    # ---------------------------------------------------------

    def increase_stock(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Inventory:
        """
        Increase available inventory.
        """

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        inventory = self.inventory_repository.get_by_product_id(
            product_id
        )

        if inventory is None:
            raise ValueError(
                f"Inventory for product '{product_id}' does not exist"
            )

        inventory.quantity += quantity

        return self.inventory_repository.save(
            inventory
        )

    # ---------------------------------------------------------
    # Decrease stock
    # ---------------------------------------------------------

    def decrease_stock(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Inventory:
        """
        Decrease available inventory.

        The quantity can never become negative.
        """

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        inventory = self.inventory_repository.get_by_product_id(
            product_id
        )

        if inventory is None:
            raise ValueError(
                f"Inventory for product '{product_id}' does not exist"
            )

        # Prevent overselling
        if inventory.quantity < quantity:
            raise ValueError(
                f"Insufficient inventory. "
                f"Available: {inventory.quantity}, "
                f"requested: {quantity}"
            )

        inventory.quantity -= quantity

        return self.inventory_repository.save(
            inventory
        )

    def reserve_stock(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Inventory:
        """Reserve inventory while locking the inventory row."""

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        inventory = (
            self.inventory_repository
            .get_by_product_id_for_update(product_id)
        )

        if inventory is None:
            raise ValueError(
                f"Inventory for product '{product_id}' does not exist"
            )

        if inventory.quantity < quantity:
            raise ValueError(
                f"Insufficient inventory. "
                f"Available: {inventory.quantity}, "
                f"requested: {quantity}"
            )

        inventory.quantity -= quantity
        self.inventory_repository.db.flush()

        return inventory
