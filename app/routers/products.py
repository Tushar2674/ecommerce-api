from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.cache import cache_get, cache_set, products_version
from app.deps import get_db, require_admin
from app.schemas.products import ProductCreate, ProductOut, ProductPage, ProductUpdate
from app.services import products as product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductOut,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, data)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_product(db, product_id)


@router.put(
    "/{product_id}",
    response_model=ProductOut,
    dependencies=[Depends(require_admin)],
)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    return product_service.update_product(db, product_id, data)


@router.delete(
    "/{product_id}",
    status_code=204,
    dependencies=[Depends(require_admin)],
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_service.delete_product(db, product_id)


@router.get("", response_model=ProductPage)
def list_products(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    category_id: int | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    sort: Literal["newest", "price_asc", "price_desc", "name"] = "newest",
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    key = (
        f"products:list:v{products_version()}:{search}:{category_id}:"
        f"{min_price}:{max_price}:{sort}:{page}:{size}"
    )
    cached = cache_get(key)
    if cached is not None:
        return cached

    result = product_service.list_products(
        db,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        size=size,
    )
    payload = ProductPage.model_validate(result).model_dump(mode="json")
    cache_set(key, payload)
    return payload
