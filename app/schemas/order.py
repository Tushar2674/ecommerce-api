from datetime import datetime 
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    user_id: int
    total_amount: Decimal = Field(gt=0)
    items: list[OrderItemCreate] = Field(min_length=1)

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal

class OrderOut(BaseModel):
    model_config= ConfigDict(from_attributes=True)

    id: int
    user_id : int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemOut]