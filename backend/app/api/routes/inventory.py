from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.dependencies import get_db
from ...schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
)
from ...services.inventory_service import InventoryService


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory(
    data: InventoryCreate,
    db: Session = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return service.create(data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/product/{product_id}",
    response_model=InventoryResponse,
)
def get_inventory_by_product(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    service = InventoryService(db)

    inventory = service.get_by_product_id(product_id)

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found",
        )

    return inventory


@router.patch(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def update_inventory(
    inventory_id: UUID,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
):
    service = InventoryService(db)

    inventory = service.get_by_id(inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found",
        )

    try:
        return service.update(
            inventory,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/product/{product_id}/increase",
    response_model=InventoryResponse,
)
def increase_stock(
    product_id: UUID,
    quantity: int,
    db: Session = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return service.increase_stock(product_id, quantity)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/product/{product_id}/decrease",
    response_model=InventoryResponse,
)
def decrease_stock(
    product_id: UUID,
    quantity: int,
    db: Session = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return service.decrease_stock(product_id, quantity)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
