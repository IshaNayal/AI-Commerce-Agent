from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...database.dependencies import get_db
from ...schemas.order import OrderResponse
from ...services.order_service import OrderService


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/checkout/{cart_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def checkout(
    cart_id: UUID,
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    try:
        return service.checkout(cart_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    order = service.order_repository.get_by_id(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.get(
    "/merchants/{merchant_id}",
    response_model=list[OrderResponse],
)
def list_merchant_orders(
    merchant_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = OrderService(db)

    return service.order_repository.list_by_merchant(
        merchant_id=merchant_id,
        skip=skip,
        limit=limit,
    )
