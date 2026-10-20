from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate


def create_category(db: Session, data: CategoryCreate) -> Category:
    existing = db.execute(
        select(Category).where(Category.name == data.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")

    category = Category(name=data.name, description=data.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_categories(db: Session) -> list[Category]:
    return list(db.execute(select(Category).order_by(Category.name)).scalars().all())