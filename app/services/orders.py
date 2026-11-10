from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Product
from app.schemas.order import OrderCreate, OrderOut, OrderItemOut
from app.models import User

def place_order(db:Session , user: User, data: OrderCreate)-> Order:
    wanted: dict[int,int]={}
    for line in data.items:
        wanted[line.product_id]=wanted.get(line.product_id,0)+line.quantity

    stmt=(
        select(Product).where(Product.id.in_(wanted.keys())).order_by(Product.id).with_for_update()  
    )
    products={p.id:p for p in db.scalars(stmt).all()}

    for product_id, quantity in wanted.items():
        product=products.get(product_id)
        if product is None or not product.is_active:
            raise HTTPException(404, f"Product {product_id} not found")
        if product.stock < quantity:
            raise HTTPException(409, f"Not enough stock for product {product_id}")

    order= Order(user_id=user.id,total_amount=Decimal("0"))
    db.add(order)
    db.flush()
    total_amount=Decimal("0")
    for product_id, quantity in wanted.items():
        product=products.get(product_id)
        order_item=OrderItem(order_id=order.id , product_id=product.id , quantity=quantity , unit_price=product.price)
        db.add(order_item)
        total_amount+=product.price*quantity
        product.stock-=quantity
    order.total_amount=total_amount
    db.commit()
    db.refresh(order)
    return order