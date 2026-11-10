from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.services import orders as order_service

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("",response_model=OrderOut,status_code=201)
def place_order(
    data:OrderCreate,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user),
):
    return order_service.place_order(db,user,data)