from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    category_id: int


class ProductUpdate(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=255)
    description: str
    price: Decimal = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=None, ge=0)
    category_id: int
    is_active: bool


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    category_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ProductPage(BaseModel):
   items: list[ProductOut]
   total : int 
   page : int 
   size : int 