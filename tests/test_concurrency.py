import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException
from sqlalchemy import func, select

from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderItemCreate
from app.services.orders import place_order


def test_last_item_is_sold_only_once(seed, session_factory):
    product_id = seed["product_id"]
    user_ids = seed["user_ids"]
    barrier = threading.Barrier(len(user_ids))

    def buy(user_id: int):
        db = session_factory()
        try:
            user = db.get(User, user_id)
            data = OrderCreate(
                items=[OrderItemCreate(product_id=product_id, quantity=1)]
            )
            barrier.wait()
            place_order(db, user, data)
            return "ok"
        except HTTPException as exc:
            return exc.status_code
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=len(user_ids)) as pool:
        results = list(pool.map(buy, user_ids))

    assert results.count("ok") == 1
    assert results.count(409) == len(user_ids) - 1

    db = session_factory()
    assert db.get(Product, product_id).stock == 0
    assert db.scalar(select(func.count()).select_from(Order)) == 1
    db.close()