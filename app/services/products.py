from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate


def _get_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def create_product(db: Session, data: ProductCreate) -> Product:
    if db.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product:
    product = _get_or_404(db, product_id)
    if not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = _get_or_404(db, product_id)

    changes = {}
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None or key == "description":
            changes[key] = value

    if "category_id" in changes and db.get(Category, changes["category_id"]) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in changes.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    product.is_active = False
    db.commit()
