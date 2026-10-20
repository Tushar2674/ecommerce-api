from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, require_admin
from app.schemas.category import CategoryCreate, CategoryOut
from app.services import categories as category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryOut,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, data)


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)