import pytest


@pytest.fixture
def user_id(client):
    return client.post(
        "/auth/register",
        json={"username": "johndoe", "email": "john@example.com", "password": "Str0ngPass!"},
    ).json()["id"]


@pytest.fixture
def product_id(client):
    return client.post("/products", json={"name": "Widget", "price": 10.0, "stock": 20}).json()["id"]


def test_create_order_success(client, user_id, product_id):
    resp = client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 2}]},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "confirmed"
    assert body["subtotal"] == 20.0


def test_create_order_unknown_user_returns_400(client, product_id):
    resp = client.post(
        "/orders",
        json={"user_id": 999, "items": [{"product_id": product_id, "quantity": 1}]},
    )
    assert resp.status_code == 400


def test_create_order_unknown_product_returns_400(client, user_id):
    resp = client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": 999, "quantity": 1}]},
    )
    assert resp.status_code == 400


def test_create_order_zero_quantity_rejected_by_schema(client, user_id, product_id):
    resp = client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 0}]},
    )
    assert resp.status_code == 422  # pydantic gt=0 constraint


def test_create_order_insufficient_stock_returns_400(client, user_id, product_id):
    resp = client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 999}]},
    )
    assert resp.status_code == 400


def test_get_order_not_found_returns_404(client):
    resp = client.get("/orders/999")
    assert resp.status_code == 404


def test_get_order_found(client, user_id, product_id):
    created = client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 1}]},
    ).json()
    resp = client.get(f"/orders/{created['id']}")
    assert resp.status_code == 200


def test_cancel_order_success(client, user_id, product_id):
    created = client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 1}]},
    ).json()
    resp = client.post(f"/orders/{created['id']}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


def test_cancel_order_twice_returns_400(client, user_id, product_id):
    created = client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 1}]},
    ).json()
    client.post(f"/orders/{created['id']}/cancel")
    resp = client.post(f"/orders/{created['id']}/cancel")
    assert resp.status_code == 400


def test_cancel_order_not_found_returns_400(client):
    resp = client.post("/orders/999/cancel")
    assert resp.status_code == 400
