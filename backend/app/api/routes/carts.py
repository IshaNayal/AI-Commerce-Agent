from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...database.dependencies import get_db
from ...schemas.cart import (
    CartCreate,
    CartResponse,
)
from ...schemas.cart_item import CartItemCreate, CartItemUpdate, CartItemResponse
from ...services.cart import CartService


router = APIRouter(
    prefix="/carts",
    tags=["Carts"],
)


@router.post(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_cart(
    data: CartCreate,
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        return service.create_cart(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{cart_id}",
    response_model=CartResponse,
)
def get_cart(
    cart_id: UUID,
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        return service.get_cart(cart_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{cart_id}/items",
    response_model=CartItemResponse,
)
def add_item_to_cart(
    cart_id: UUID,
    data: CartItemCreate,
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        return service.add_item(
            cart_id=cart_id,
            product_id=data.product_id,
            quantity=data.quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.put(
    "/{cart_id}/items/{product_id}",
    response_model=CartItemResponse,
)
def update_cart_item(
    cart_id: UUID,
    product_id: UUID,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        return service.update_item(
            cart_id=cart_id,
            product_id=product_id,
            quantity=data.quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{cart_id}/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_cart_item(
    cart_id: UUID,
    product_id: UUID,
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        service.remove_item(cart_id=cart_id, product_id=product_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return None
