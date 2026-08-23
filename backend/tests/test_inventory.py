from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.app.schemas.inventory import InventoryCreate


def test_inventory_rejects_negative_quantity():
    with pytest.raises(ValidationError):
        InventoryCreate(
            product_id=uuid4(),
            quantity=-1,
        )