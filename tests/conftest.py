from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app.models
from app.core.config import settings
from app.db.base import Base
from app.models.category import Category
from app.models.product import Product
from app.models.user import User

TEST_DB_URL = settings.database_url.rsplit("/",1)[0]+"/ecommerce_test"
assert TEST_DB_URL.endswith("_test"), "Test database URL must end with '_test' to prevent accidental data loss."

engine = create_engine(TEST_DB_URL,pool_pre_ping=True, pool_size=20)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def session_factory():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return TestingSessionLocal

@pytest.fixture()
def seed(session_factory):
    db = session_factory()
    category = Category(name="Test category")
    db.add(category)
    db.flush()

    product = Product(
        name="Last item", price=Decimal("100.00"), stock=1, category_id=category.id
    )
    users = [
        User(email=f"buyer{i}@example.com", password_hash="not-a-real-hash")
        for i in range(5)
    ]
    db.add(product)
    db.add_all(users)
    db.commit()

    data = {"product_id": product.id, "user_ids": [u.id for u in users]}
    db.close()
    return data