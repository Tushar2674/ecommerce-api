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
from fastapi.testclient import TestClient
from sqlalchemy import update

from app.deps import get_db
from app.main import app


TEST_DB_URL = settings.database_url.rsplit("/", 1)[0] + "/ecommerce_test"
assert TEST_DB_URL.endswith("_test"), (
    "Test database URL must end with '_test' to prevent accidental data loss."
)

engine = create_engine(TEST_DB_URL, pool_pre_ping=True, pool_size=20)
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


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_user(client, session_factory, email, password="password123", admin=False):
    client.post("/auth/register", json={"email": email, "password": password})
    if admin:
        db = session_factory()
        db.execute(update(User).where(User.email == email).values(role="admin"))
        db.commit()
        db.close()
    response = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
