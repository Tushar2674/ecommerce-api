import os
import random
import uuid

from locust import HttpUser, between, task

PRODUCT_ID = int(os.environ.get("PRODUCT_ID", "1"))


class Shopper(HttpUser):
    """Browses the catalogue: read-only traffic."""

    wait_time = between(0.1, 0.5)

    @task(5)
    def list_products(self):
        page = random.randint(1, 5)
        self.client.get(f"/products?page={page}&size=20", name="GET /products")

    @task(2)
    def list_by_price(self):
        self.client.get(
            "/products?sort=price_asc&min_price=100&max_price=500&size=20",
            name="GET /products (filtered)",
        )

    @task(1)
    def get_one(self):
        self.client.get(f"/products/{PRODUCT_ID}", name="GET /products/{id}")


class Buyer(HttpUser):
    """Every user buys 1 unit of the same product: the worst case for row locking."""

    wait_time = between(0.1, 0.5)

    def on_start(self):
        email = f"load{uuid.uuid4().hex[:10]}@example.com"
        self.client.post(
            "/auth/register",
            json={"email": email, "password": "password123"},
            name="setup: register",
        )
        response = self.client.post(
            "/auth/login",
            data={"username": email, "password": "password123"},
            name="setup: login",
        )
        self.headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    @task
    def order(self):
        self.client.post(
            "/orders",
            json={"items": [{"product_id": PRODUCT_ID, "quantity": 1}]},
            headers=self.headers,
            name="POST /orders",
        )
