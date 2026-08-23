from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...database.dependencies import get_db
from ...schemas.merchant import (
    MerchantCreate,
    MerchantResponse,
    MerchantUpdate,
)
from ...services.merchant_service import MerchantService


router = APIRouter(
    prefix="/merchants",
    tags=["Merchants"],
)


@router.post(
    "",
    response_model=MerchantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_merchant(
    data: MerchantCreate,
    db: Session = Depends(get_db),
):
    service = MerchantService(db)

    try:
        return service.create_merchant(data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[MerchantResponse],
)
def list_merchants(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = MerchantService(db)

    return service.list_merchants(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{merchant_id}",
    response_model=MerchantResponse,
)
def get_merchant(
    merchant_id: UUID,
    db: Session = Depends(get_db),
):
    service = MerchantService(db)

    merchant = service.get_merchant(merchant_id)

    if merchant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    return merchant


@router.patch(
    "/{merchant_id}",
    response_model=MerchantResponse,
)
def update_merchant(
    merchant_id: UUID,
    data: MerchantUpdate,
    db: Session = Depends(get_db),
):
    service = MerchantService(db)

    try:
        merchant = service.update_merchant(
            merchant_id,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if merchant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    return merchant


@router.delete(
    "/{merchant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_merchant(
    merchant_id: UUID,
    db: Session = Depends(get_db),
):
    service = MerchantService(db)

    deleted = service.delete_merchant(merchant_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    return None