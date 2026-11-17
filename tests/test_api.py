from tests.conftest import make_user


def test_register_duplicate_email_returns_409(client):
    body = {"email": "a@example.com", "password": "password123"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 409


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/auth/register", json={"email": "a@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/login", data={"username": "a@example.com", "password": "wrong-pass"}
    )
    assert response.status_code == 401


def test_customer_cannot_create_category(client, session_factory):
    headers = make_user(client, session_factory, "customer@example.com")
    response = client.post("/categories", json={"name": "Phones"}, headers=headers)
    assert response.status_code == 403


def test_order_then_cancel_restores_stock(client, session_factory):
    admin = make_user(client, session_factory, "admin@example.com", admin=True)
    customer = make_user(client, session_factory, "buyer@example.com")

    category = client.post("/categories", json={"name": "Phones"}, headers=admin).json()
    product = client.post(
        "/products",
        json={
            "name": "Phone",
            "price": "500.00",
            "stock": 5,
            "category_id": category["id"],
        },
        headers=admin,
    ).json()

    order = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 2}]},
        headers=customer,
    )
    assert order.status_code == 201
    assert order.json()["total_amount"] == "1000.00"
    assert client.get(f"/products/{product['id']}").json()["stock"] == 3

    order_id = order.json()["id"]
    cancel = client.patch(f"/orders/{order_id}/cancel", headers=customer)
    assert cancel.status_code == 200
    assert client.get(f"/products/{product['id']}").json()["stock"] == 5

    again = client.patch(f"/orders/{order_id}/cancel", headers=customer)
    assert again.status_code == 409
    assert client.get(f"/products/{product['id']}").json()["stock"] == 5


def create_product(client, admin_headers, stock, price="500.00"):
    category = client.post(
        "/categories", json={"name": "Phones"}, headers=admin_headers
    ).json()
    return client.post(
        "/products",
        json={
            "name": "Phone",
            "price": price,
            "stock": stock,
            "category_id": category["id"],
        },
        headers=admin_headers,
    ).json()


def test_other_customer_cannot_cancel_order(client, session_factory):
    admin = make_user(client, session_factory, "admin@example.com", admin=True)
    customer_a = make_user(client, session_factory, "a@example.com")
    customer_b = make_user(client, session_factory, "b@example.com")
    product = create_product(client, admin, stock=5)

    order = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 2}]},
        headers=customer_a,
    )
    assert order.status_code == 201
    order_id = order.json()["id"]

    # customer B tries to cancel customer A's order
    response = client.patch(f"/orders/{order_id}/cancel", headers=customer_b)
    assert response.status_code == 404

    # nothing changed: stock is still reduced and the order is still pending
    assert client.get(f"/products/{product['id']}").json()["stock"] == 3
    orders = client.get("/orders", headers=customer_a).json()
    assert orders[0]["status"] == "pending"


def test_order_with_too_much_quantity_returns_409(client, session_factory):
    admin = make_user(client, session_factory, "admin@example.com", admin=True)
    customer = make_user(client, session_factory, "buyer@example.com")
    product = create_product(client, admin, stock=1)

    response = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 2}]},
        headers=customer,
    )
    assert response.status_code == 409

    # nothing changed: stock is untouched and no order was created
    assert client.get(f"/products/{product['id']}").json()["stock"] == 1
    assert client.get("/orders", headers=customer).json() == []
